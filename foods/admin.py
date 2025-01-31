from django.contrib import admin
from .models import Category, FoodItem, Order, OrderItem, Review, CartItem

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# Food Item Admin
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_special')
    list_filter = ('category', 'is_special')
    search_fields = ('name', 'category__name')

# Order Item Inline (To show order items inside an order)
admin.site.register(OrderItem)
admin.site.register(Order)
# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('customer', 'food_item', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('customer__username', 'food_item__name')

admin.site.register(CartItem)