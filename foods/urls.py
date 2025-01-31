from django.urls import path
from .views import (
    CategoryListAPIView,
    FoodItemListAPIView, FoodItemDetailAPIView,
    OrderListCreateAPIView, OrderDetailAPIView,
    ReviewListCreateAPIView, FoodItemsByCategoryAPIView,
    CartAPIView, CartItemDetailAPIView,
    CheckoutAPIView, SpecialsListAPIView
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),

    # Food Items
    path('food-items/', FoodItemListAPIView.as_view(), name='food-item-list'),
    path('food-items/<int:pk>/', FoodItemDetailAPIView.as_view(), name='food-item-detail'),

    # Orders
    path('orders/', OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path('categories/<slug:category_slug>/food-items/', FoodItemsByCategoryAPIView.as_view(), name='food-items-by-category'),

    # Reviews
    path('food-items/<int:food_item_id>/reviews/', ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path("cart/", CartAPIView.as_view(), name="cart"),
    path("cart/<int:cart_item_id>/", CartItemDetailAPIView.as_view(), name="cart-item"),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path("specials/", SpecialsListAPIView.as_view(), name="specials-list"),
    
    
]
