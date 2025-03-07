from django.shortcuts import render
from rest_framework import viewsets
from . import models
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
# for sending email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect
from rest_framework import status
from customers.models import Customer


class CustomerViewset(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

class UserRegistrationApiView(APIView):
    serializer_class = serializers.RegistrationSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            print(user)
            token = default_token_generator.make_token(user)
            print("token ", token)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            print("uid ", uid)
            confirm_link = f"https://foodie-delight-backend-eta.vercel.app/customer/active/{uid}/{token}"
            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {'confirm_link' : confirm_link})
            
            email = EmailMultiAlternatives(email_subject , '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()
            return Response("Check your mail for confirmation")
        return Response(serializer.errors)


class ActivateAccountView(APIView):
    def get(self, request, uid64, token):
        try:
            uid = urlsafe_base64_decode(uid64).decode()
            user = User._default_manager.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            user = None
        
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response("Email Confirmed", status=status.HTTP_200_OK)
        else:
            return Response("Invalid Link", status=status.HTTP_400_BAD_REQUEST)
    



class UserLoginApiView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)

                # Check if the user is an admin (superuser)
                is_admin = user.is_superuser

                # Check if the user is a customer
                is_customer = hasattr(user, 'customer')

                # Prepare the response data
                response_data = {
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_admin': is_admin,
                    'is_customer': is_customer,
                }

                # Add customer-specific data if the user is a customer
                if is_customer:
                    customer = Customer.objects.get(user=user)
                    response_data['phone'] = customer.phone
                    response_data['address'] = customer.address

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class UserLogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('login')
        
        


class UserProfileView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            # Fetch the user by user_id
            user = User.objects.get(id=user_id)
            
            # Check if the user is an admin (superuser)
            if user.is_superuser:
                profile_data = {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "role": "admin",
                }
                return Response(profile_data, status=status.HTTP_200_OK)
            
            # Check if the user is a customer
            elif hasattr(user, 'customer'):
                customer = user.customer
                profile_data = {
                    "id": customer.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": customer.phone,
                    "address": customer.address,
                    "role": "customer",
                }
                return Response(profile_data, status=status.HTTP_200_OK)
            
            # If the user is neither admin nor customer
            else:
                return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    

    