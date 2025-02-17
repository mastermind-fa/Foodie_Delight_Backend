from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

# Create a router and register the PaymentViewSet with it
router = DefaultRouter()
router.register(r'payment', PaymentViewSet, basename='payment')

# Include the router's URLs in the urlpatterns
urlpatterns = [
    path('', include(router.urls)),
]