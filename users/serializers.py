#backen/users/serializers.py
from rest_framework import serializers
from .models import CustomUser, Candidate, Role 
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

User = get_user_model()

#class UserSignupSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = CustomUser
#        fields = ['email', 'phone', 'password']
#        extra_kwargs = {'password': {'write_only': True}}

#    def create(self, validated_data):
#        return CustomUser.objects.create_user(**validated_data)

#class EmailOrPhoneLoginSerializer(serializers.Serializer):
#    identifier = serializers.CharField()
#    password = serializers.CharField(write_only=True)
#    remember_me = serializers.BooleanField(default=False)

#    def validate(self, data):
#        identifier = data.get("identifier")
#        password = data.get("password")
#        remember_me = data.get("remember_me", False)

#        try:
#            user = User.objects.get(Q(email=identifier) | Q(phone=identifier))
#        except User.DoesNotExist:
#            raise serializers.ValidationError("User with given email or phone does not exist")

#        if not user.check_password(password):
#            raise serializers.ValidationError("Invalid password")

#        if not user.is_active:
#            raise serializers.ValidationError("Account is not active")

        # Generate token
#        refresh = RefreshToken.for_user(user)
#        if remember_me:
#            refresh.set_exp(lifetime=timedelta(days=7))
#            refresh.access_token.set_exp(lifetime=timedelta(hours=1))
#        else:
#            refresh.set_exp(lifetime=timedelta(days=1))
#            refresh.access_token.set_exp(lifetime=timedelta(minutes=5))

#        return {
#            "refresh": str(refresh),
#            "access": str(refresh.access_token),
#            "user": {
#                "id": user.id,
#                "email": user.email,
#                "phone": user.phone,
#           }
#        }

# --- MODIFIED: This is now specifically for ADMIN self-signup ---
class UnifiedSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # When an admin signs up through this form, their role is automatically set.
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone'),
            role=Role.ADMIN, # Automatically assign ADMIN role
            is_active=False # Stays inactive until email verification
        )
        return user

# --- NEW: Serializer for YOU (the admin) to import a candidate ---
class ImportCandidateSerializer(serializers.ModelSerializer):
    # This field will be used to create the Candidate profile
    name = serializers.CharField(max_length=200, write_only=True)

    class Meta:
        model = CustomUser
        # The admin only provides these fields. No password!
        fields = ['email', 'phone', 'name']

    def create(self, validated_data):
        name = validated_data.pop('name')
        
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})

        # Create the user account, without a password, and with the CANDIDATE role
        user = User.objects.create_user(
            email=validated_data['email'],
            phone=validated_data.get('phone'),
            role=Role.CANDIDATE,
            is_active=False # Inactive until they set their password
        )
        # Create the linked candidate profile
        Candidate.objects.create(user=user, name=name)
        return user

# --- NEW: Serializer for the candidate to set their password ---
#class SetPasswordSerializer(serializers.Serializer):
#    password = serializers.CharField(write_only=True, min_length=8)

class EmailOrPhoneLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, data):
        identifier = data.get("identifier")
        password = data.get("password")

        # Find the user by their email. This is safer than using authenticate
        # if the backend isn't configured perfectly.
        try:
            user = CustomUser.objects.get(email=identifier)
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("Account is not active.")

        # If we reach here, the user is valid.
        refresh = RefreshToken.for_user(user)

        # --- THIS IS THE FIX ---
        # 1. Start with the base user data.
        user_data = {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
        }

        # 2. Add the 'name' based on the user's role.
        if user.role == Role.ADMIN:
            # For an ADMIN, the name can be a generic title.
            user_data['name'] = "Admin"
            refresh['name'] = "Admin" # Add to token
            
        elif user.role == Role.CANDIDATE:
            # For a CANDIDATE, get the name from the linked profile.
            try:
                user_data['name'] = user.candidate_profile.name
                refresh['name'] = user.candidate_profile.name # Add to token
            except Candidate.DoesNotExist:
                user_data['name'] = "Candidate" # Fallback
                refresh['name'] = "Candidate"
        
        # Add the role to the token payload
        refresh['role'] = user.role
        # --- END OF FIX ---

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data,
        }