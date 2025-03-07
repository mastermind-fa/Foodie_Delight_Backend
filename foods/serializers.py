from rest_framework import serializers
from .models import Category, FoodItem, Order, OrderItem, Review, CartItem

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

# Food Item Serializer
class FoodItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested serializer to show category details
    # category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Allow category ID for write operations

    class Meta:
        model = FoodItem
        fields = ['id', 'category', 'name', 'description', 'price', 'pre_discount_price','image', 'is_special']

# Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'quantity']

# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer = serializers.StringRelatedField(read_only=True)  # Display username instead of ID

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price', 'status', 'created_at', 'estimated_delivery_time', 'items']

# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(read_only=True)  # Display username instead of ID
    food_item = serializers.StringRelatedField(read_only=True)  # Display food item name

    class Meta:
        model = Review
        fields = ['id', 'customer', 'food_item', 'rating', 'comment', 'created_at']



class CartItemSerializer(serializers.ModelSerializer):
    food_item = FoodItemSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'food_item', 'quantity']
        
        
        

