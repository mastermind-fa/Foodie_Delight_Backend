from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Category, FoodItem, Order, OrderItem, Review, CartItem
from .serializers import CategorySerializer, FoodItemSerializer, OrderSerializer, ReviewSerializer, CartItemSerializer

# Category List View
class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Food Item List and Detail Views
from django.db.models import Q

class FoodItemListAPIView(APIView):
    def get(self, request):
        food_items = FoodItem.objects.all()
        category_slug = request.query_params.get('category')
        search_query = request.query_params.get('search', "")  # Get search query

        if category_slug:
            food_items = food_items.filter(category__slug=category_slug)

        if search_query:  # Apply search filter if search_query exists
            food_items = food_items.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class FoodItemsByCategoryAPIView(APIView):
    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        food_items = FoodItem.objects.filter(category=category)
        serializer = FoodItemSerializer(food_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FoodItemDetailAPIView(APIView):
    def get(self, request, pk):
        # Handle GET request (retrieve food item details)
        food_item = get_object_or_404(FoodItem, pk=pk)
        serializer = FoodItemSerializer(food_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        # Handle PUT request (update food item details) - Admin only
        if not request.user.is_staff:  # Ensure only admin can update
            return Response({'error': 'You do not have permission to perform this action'}, status=status.HTTP_403_FORBIDDEN)

        food_item = get_object_or_404(FoodItem, pk=pk)
        serializer = FoodItemSerializer(food_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Handle DELETE request (delete food item) - Admin only
        if not request.user.is_staff:  # Ensure only admin can delete
            return Response({'error': 'You do not have permission to perform this action'}, status=status.HTTP_403_FORBIDDEN)

        food_item = get_object_or_404(FoodItem, pk=pk)
        food_item.delete()
        return Response({'message': 'Food item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    

# Order List and Create View
class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({'error': 'Order must contain at least one item'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        order = Order.objects.create(customer=request.user, total_price=0)

        for item in items:
            food_item = get_object_or_404(FoodItem, id=item['food_item'])
            quantity = int(item.get('quantity', 1))
            OrderItem.objects.create(order=order, food_item=food_item, quantity=quantity)
            total_price += food_item.price * quantity

        order.total_price = total_price
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Order Detail View (Retrieve, Update, Delete)
class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = get_object_or_404(Order, id=pk, customer=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        order = get_object_or_404(Order, id=pk, customer=request.user)
        if order.status != "Pending":
            return Response({'error': 'Only pending orders can be deleted'}, status=status.HTTP_400_BAD_REQUEST)
        order.delete()
        return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Review List and Create View
class ReviewListCreateAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, food_item_id):
        reviews = Review.objects.filter(food_item_id=food_item_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, food_item_id):
        food_item = get_object_or_404(FoodItem, id=food_item_id)
        existing_review = Review.objects.filter(customer=request.user, food_item=food_item).first()
        if existing_review:
            return Response({'error': 'You have already reviewed this item'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user, food_item=food_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        food_item_id = request.data.get("food_item_id")
        quantity = request.data.get("quantity")
        print(food_item_id, quantity)

        food_item = get_object_or_404(FoodItem, id=food_item_id)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, food_item=food_item,
            defaults={"quantity": quantity}  # Set quantity when creating
        )

        if not created:
            cart_item.quantity += int(quantity)
            print(cart_item.quantity)
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(APIView):
    #permission_classes = [IsAuthenticated]

    def put(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        cart_item.quantity = request.data.get("quantity", cart_item.quantity)
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    def delete(self, request, cart_item_id):
        cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
        cart_item.delete()
        return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)
    
    
class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Fetch all cart items for the logged-in user
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items:
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new order
        order = Order.objects.create(customer=request.user, total_price=0)

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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SpecialsListAPIView(APIView):
    def get(self, request):
        specials = FoodItem.objects.filter(is_special=True)
        serializer = FoodItemSerializer(specials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Category, FoodItem, Order, OrderItem, Review, CartItem
from .serializers import CategorySerializer, FoodItemSerializer, OrderSerializer, ReviewSerializer, CartItemSerializer

# Admin-only views for managing categories
class CategoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Admin-only views for managing food items
class FoodItemCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = FoodItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer
from datetime import datetime

# View for listing all orders
class AllOrderAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminUser]  # Only admins can access this view

    def get(self, request):
        # Retrieve all orders from all users
        orders = Order.objects.all().order_by('-created_at')  # Sort by most recent
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# View for handling individual orders
class OrderDetailAPIView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminUser]  # Only admins can access this view

    def get(self, request, pk):
        # Retrieve a single order by ID
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        # Update the status or estimated_delivery_time of a specific order
        order = get_object_or_404(Order, pk=pk)
        new_status = request.data.get('status')
        new_estimated_delivery_time = request.data.get('estimated_delivery_time')

        # Validate and update status
        if new_status:
            if new_status not in dict(Order.STATUS_CHOICES).keys():
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            order.status = new_status

        # Validate and update estimated_delivery_time
        if new_estimated_delivery_time:
            try:
                # Parse the datetime string (e.g., "2023-10-15T14:30:00Z")
                parsed_time = datetime.strptime(new_estimated_delivery_time, "%Y-%m-%dT%H:%M:%SZ")
                order.estimated_delivery_time = parsed_time
            except ValueError:
                return Response({'error': 'Invalid datetime format. Use "YYYY-MM-DDTHH:MM:SSZ".'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the updated order
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)