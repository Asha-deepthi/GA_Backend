#backen/users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

#from django.contrib.auth import get_user_model
#from django.contrib.auth.password_validation import validate_password

#User = get_user_model()

#class UserSerializer(serializers.ModelSerializer):
#    class Meta:
#       model = User
#       fields = ['id', 'username', 'email', 'role']

#class RegisterSerializer(serializers.ModelSerializer):
#    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#    password2 = serializers.CharField(write_only=True, required=True)

#    class Meta:
#        model = User
#        fields = ['username', 'email', 'password', 'password2', 'role']

#    def validate(self, attrs):
#        if attrs['password'] != attrs['password2']:
#            raise serializers.ValidationError({"password": "Passwords don't match"})
#        return attrs

#    def create(self, validated_data):
#        validated_data.pop('password2')
#        user = User.objects.create_user(**validated_data)
#        return user

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Account not activated.")
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    remember_me = False  # default

    def validate(self, attrs):
        self.remember_me = self.context['request'].data.get('remember_me', False)
        data = super().validate(attrs)

        # Create refresh token with custom expiry if remember_me is True
        refresh = RefreshToken.for_user(self.user)

        if self.remember_me:
            refresh.set_exp(lifetime=timedelta(days=7))  # 7 days refresh token
            refresh.access_token.set_exp(lifetime=timedelta(hours=1))  # 1 hour access token
        else:
            refresh.set_exp(lifetime=timedelta(days=1))  # default 1 day refresh token
            refresh.access_token.set_exp(lifetime=timedelta(minutes=5))  # default 5 minutes access token

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
