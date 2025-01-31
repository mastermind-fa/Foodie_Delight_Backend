# serializers.py
from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)
    class Meta:
        model = models.Customer
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(required=True, write_only=True)  # Add phone field
    address = serializers.CharField(required=True, write_only=True)  # Add address field

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'phone', 'address']
    
    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        password2 = self.validated_data['confirm_password']
        phone = self.validated_data['phone']  # Get phone from validated data
        address = self.validated_data['address']  # Get address from validated data
        
        if password != password2:
            raise serializers.ValidationError({'error': "Password Doesn't Match"})
        
        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': "Email Already exists"})
        
        # Create the User instance
        account = User(username=username, email=email, first_name=first_name, last_name=last_name)
        account.set_password(password)
        account.is_active = False
        account.save()
        
        # Create the corresponding Customer instance with phone and address
        models.Customer.objects.create(
            user=account,
            phone=phone,  # Set phone from the request
            address=address  # Set address from the request
        )
        
        return account

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)