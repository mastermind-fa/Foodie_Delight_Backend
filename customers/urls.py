from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter() 

router.register('list', views.CustomerViewset) 
urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('active/<uid64>/<token>/', views.ActivateAccountView.as_view(), name = 'activate'),
    path('details/<int:user_id>/', views.UserProfileView.as_view(), name='user-profile'),
    # path('api/user-id/', views.UserIDView.as_view(), name='customer-list'),
]