from django.urls import path
from .views import (
    CategoryListAPIView, CategoryCreateAPIView, CategoryDetailAPIView,
    FoodItemListAPIView, FoodItemDetailAPIView, FoodItemCreateAPIView,
    OrderListCreateAPIView, OrderDetailAPIView, AllOrderAPIView,
    ReviewListCreateAPIView, FoodItemsByCategoryAPIView,
    CartAPIView, CartItemDetailAPIView,
    CheckoutAPIView, SpecialsListAPIView
)

urlpatterns = [
    # Category URLs
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateAPIView.as_view(), name='category-create'),  # Admin-only
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),  # Admin-only

    # Food Item URLs
    path('food-items/', FoodItemListAPIView.as_view(), name='food-item-list'),
    path('food-items/create/', FoodItemCreateAPIView.as_view(), name='food-item-create'),  # Admin-only
    path('food-items/<int:pk>/', FoodItemDetailAPIView.as_view(), name='food-item-detail'),  # Combined GET, PUT, DELETE

    # Food Items by Category
    path('categories/<slug:category_slug>/food-items/', FoodItemsByCategoryAPIView.as_view(), name='food-items-by-category'),

    # Order URLs
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    # List all orders
    path('admin/orders/', AllOrderAPIView.as_view(), name='all-orders'),

    # Retrieve or update a specific order
    path('admin/orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),

    # Review URLs
    path('food-items/<int:food_item_id>/reviews/', ReviewListCreateAPIView.as_view(), name='review-list-create'),

    # Cart URLs
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('cart/<int:cart_item_id>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),

    # Checkout URL
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),

    # Specials URL
    path('specials/', SpecialsListAPIView.as_view(), name='specials-list'),
]