#backen/users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from datetime import timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta


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

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

class EmailOrPhoneLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")
        remember_me = data.get("remember_me", False)

        try:
            user = User.objects.get(Q(email=identifier) | Q(phone=identifier))
        except User.DoesNotExist:
            raise serializers.ValidationError("User with given email or phone does not exist")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password")

        if not user.is_active:
            raise serializers.ValidationError("Account is not active")

        # Generate token
        refresh = RefreshToken.for_user(user)
        if remember_me:
            refresh.set_exp(lifetime=timedelta(days=7))
            refresh.access_token.set_exp(lifetime=timedelta(hours=1))
        else:
            refresh.set_exp(lifetime=timedelta(days=1))
            refresh.access_token.set_exp(lifetime=timedelta(minutes=5))

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
            }
        }