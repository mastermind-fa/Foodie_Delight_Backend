from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from sslcommerz_lib import SSLCOMMERZ
from foods.models import Order, CartItem, OrderItem
from foods.serializers import OrderSerializer
import uuid
from rest_framework import status  # Make sure this import is at the top of your file
from django.conf import settings
from django.shortcuts import redirect
from customers.models import Customer
from django.contrib.auth.models import User
from django.shortcuts import render	
from django.shortcuts import get_object_or_404

class PaymentViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        # SSLCommerz configuration
        sslcz_settings = {
            'store_id': 'maste679cfa8ec592d',
            'store_pass': 'maste679cfa8ec592d@ssl',
            'issandbox': True
        }
        sslcz = SSLCOMMERZ(sslcz_settings)
        
        # Generate unique transaction ID
        tran_id = str(uuid.uuid4())[:10].replace('-', '').upper()
        
        # Extract and set default request data
        # user_id = request.data.get('user')
        # total_amount = request.data.get('total_amount', 0.26)
        # currency = request.data.get('currency', "BDT")
        # name = request.data.get('name', "name")
        # email = request.data.get('email', "test@test.com")
        # phone_no = request.data.get('phone_no', "01700000000")
        # address_line_1 = request.data.get('address_line_1', "customer address")
        # address_line_2 = request.data.get('address_line_2', "customer address")
        # city = request.data.get('city', "Dhaka")
        # country = request.data.get('country', "Bangladesh")
        # postal_code = request.data.get('postal_code', "14141")
        # payment_type = request.data.get('payment_type', "Online Payment")
        # state = request.data.get('state', "state")
        
        
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items:
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new order
        order = Order.objects.create(customer=request.user, total_price=0, status="Pending")

        # Calculate total price and add items to the order
        total_price = 0
        for cart_item in cart_items:
            food_item = cart_item.food_item
            quantity = cart_item.quantity
            OrderItem.objects.create(order=order, food_item=food_item, quantity=quantity)
            total_price += food_item.price * quantity

        # Update the order's total price
        order.total_price = total_price
        order.save()

        # Clear the user's cart after placing the order
        cart_items.delete()

        # Return the created order details
        serializer = OrderSerializer(order)

        # Define callback URLs
        success_url = request.build_absolute_uri(f'/payment/success/?tran_id={tran_id}&order_id={order.id}')
        
        fail_url = request.build_absolute_uri('/payment/fail/')
        cancel_url = request.build_absolute_uri('/payment/cancel/')
        # Create payment information payload
        post_body = {
            'total_amount': total_price,
            'currency': 'BDT',
            'tran_id': tran_id,
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'emi_option': 0,
            'cus_user' : request.user,
            'cus_name': request.user.username,
            'cus_email': request.user.email,
            'cus_phone': "123456789",  # Replace with user's phone number if available
            'cus_add1': "N/A",
            'cus_city': "Dhaka",
            'cus_country': "Bangladesh",
            'shipping_method': "NO",
            'multi_card_name': "",
            'num_of_item': len(cart_items),
            'product_name': "Test",
            'product_category': "tasty food",
            'product_profile': "general",
            'order_id': order.id,
        }
        print(f'customer: {request.user} order: {order.id}')

        try:
            
            response = sslcz.createSession(post_body)
            if response.get('status') == 'SUCCESS' and 'GatewayPageURL' in response:
                return Response({"url": response['GatewayPageURL']})
            return Response({"error": "Unable to create payment session"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def success(self, request):
        try:
            # Extract parameters
            
            order_id = request.query_params.get('order_id')
            # print(f'customer: {customer} order: {order_id}')
            order = get_object_or_404(Order, id=order_id)
            if not order:
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

            order.status = "Paid"  # Update order status
            order.save()
            return redirect('https://foodie-delight-frontend.vercel.app/order.html')

        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        order_id = request.query_params.get('order_id')
            # print(f'customer: {customer} order: {order_id}')
        order = get_object_or_404(Order, id=order_id)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.status = "Cancelled"  # Update order status
        order.save()
        return render(request, 'payments/cancel.html')
    
    @action(detail=False, methods=['post'])
    def fail(self, request):
        order_id = request.query_params.get('order_id')
            # print(f'customer: {customer} order: {order_id}')
        order = get_object_or_404(Order, id=order_id)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.status = "Cancelled"  # Update order status
        order.save()
        return render(request, 'payments/fail.html')