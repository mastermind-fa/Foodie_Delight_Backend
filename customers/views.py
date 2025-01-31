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
            confirm_link = f"https://foodie-delight-backend-eta.vercel.app/active/{uid}/{token}"
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
        serializer = serializers.UserLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                customer = Customer.objects.get(user=user)
                login(request, user)

                is_customer = hasattr(user, 'customer')
                return Response({
                    'token': token.key,
                    'user_id': customer.id,
                    'username': user.username,
                    'email': user.email,
                    'is_customer': is_customer
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class UserLogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('login')
        
        
class UserProfileView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            customer = Customer.objects.get(id=user_id)  # Fetch the customer profile
            profile_data = {
                "id": customer.id,
                "user": customer.user.username,  # Username
                "first_name": customer.user.first_name,  # First name
                "last_name": customer.user.last_name,  # Last name
                "phone": customer.phone,  # Phone number
                "address": customer.address,  # Address
            }
            return Response(profile_data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)
    
