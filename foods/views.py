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
        food_item = get_object_or_404(FoodItem, pk=pk)
        serializer = FoodItemSerializer(food_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

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



#