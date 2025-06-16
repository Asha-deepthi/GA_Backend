# backend/users/views.py
from django.shortcuts import redirect
import uuid
import secrets  # --- NEW: Import Python's library for generating secure random strings ---
import string   # --- NEW: To define the characters for the password ---
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser, Candidate, Role
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    EmailOrPhoneLoginSerializer, 
    UnifiedSignupSerializer,          # NEW
    ImportCandidateSerializer,      # NEW
    #SetPasswordSerializer           # NEW
)
from django.contrib.auth import get_user_model

User = get_user_model()

#class SendVerificationEmailView(APIView):
#    permission_classes = [AllowAny]

#    def post(self, request):
#        email = request.data.get('email')
#        phone = request.data.get('phone') 
#        password = request.data.get('password')

#        if not email or not password:
#            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

#        user, created = CustomUser.objects.get_or_create(email=email)
#        phone = request.data.get('phone')

#        if created:
#            user.phone = phone
#            user.set_password(password)
#            user.email_verification_uuid = uuid.uuid4()
#            user.is_active = False  # keep it active but not verified
#            user.save()
#        elif user.is_email_verified:
#            return Response({"message": "Email already verified."}, status=status.HTTP_200_OK)

#        if not user.email_verification_uuid:
#            user.email_verification_uuid = uuid.uuid4()
#            user.save()

#        verification_link = f"{settings.BACKEND_URL}/api/verify-email/{user.email_verification_uuid}/"

#        print("\n🔗 Email Verification Link (for development):")
#        print(verification_link)
#        print()

#        try:
#            send_mail(
#                subject="Verify your email address",
#                message=(
#                    f"Hello {user.email},\n\n"
#                    f"Please verify your email by clicking the link below:\n"
#                    f"{verification_link}\n\n"
#                    "If you did not request this, please ignore this email."
#                ),
#               from_email=settings.DEFAULT_FROM_EMAIL,
#                recipient_list=[user.email],
#                fail_silently=False,
#            )
#        except Exception as e:
#            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#        return Response({"message": "Verification email sent."}, status=status.HTTP_200_OK)

# This single view replaces your old SendVerificationEmailView
class UnifiedSignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UnifiedSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        phone = serializer.validated_data.get('phone')

        # Try to find if a user was already invited with this email
        user = User.objects.filter(email=email).first()

        # --- SCENARIO 1: Candidate is completing their registration ---
        if user and user.role == Role.CANDIDATE and not user.is_active:
            user.set_password(password)
            user.is_active = True
            user.is_email_verified = True # They are verified by having access to the email
            user.save()
            return Response({"message": "Registration complete! You can now log in."}, status=status.HTTP_200_OK)

        # --- SCENARIO 2: User already exists and is active ---
        if user:
            return Response({"error": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # --- SCENARIO 3: New Admin is signing up ---
        new_admin = User.objects.create_user(
            email=email,
            password=password,
            phone=phone,
            role=Role.ADMIN,
            is_active=False # Admins must verify their email
        )
        
        verification_link = f"{settings.BACKEND_URL}/api/verify-email/{new_admin.email_verification_uuid}/"
        try:
            send_mail(
                subject="Verify your Admin account",
                message=f"Hello,\n\nPlease verify your admin account by clicking the link:\n{verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_admin.email],
            )
        except Exception as e:
            new_admin.delete()
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Admin account created. Please check your email to verify."}, status=status.HTTP_201_CREATED)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uuid):
        try:
            user = CustomUser.objects.get(email_verification_uuid=uuid)

            if user.is_email_verified:
                return redirect(f"{settings.FRONTEND_URL}/login")  # Already verified

            user.is_email_verified = True
            user.is_active = True
            user.save()

            return redirect(f"{settings.FRONTEND_URL}/login")  # Redirect after successful verification

        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid or expired verification link."}, status=status.HTTP_400_BAD_REQUEST)

# --- MODIFIED: This view now auto-generates the password for the candidate ---
class ImportCandidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'ADMIN':
            return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ImportCandidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        email = validated_data['email']

        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # --- NEW: Auto-generate a secure password ---
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(10)) # Creates a 10-character password

        # Now, create the user with the generated password
        try:
            user = User.objects.create_user(
                email=email,
                password=password, # Use the auto-generated password
                phone=validated_data.get('phone'),
                role=Role.CANDIDATE,
                is_active=True,
                is_email_verified=True
            )
            # Create the linked candidate profile
            Candidate.objects.create(user=user, name=validated_data['name'])

        except Exception as e:
            return Response({'error': f'Failed to create user: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- Email sending logic is the same, but now uses the generated password ---
        login_link = f"{settings.FRONTEND_URL}/login"
        try:
            send_mail(
                subject="Your Account Details for the Assessment Platform",
                message=(
                    f"Hello {validated_data['name']},\n\n"
                    f"An account has been created for you on our assessment platform. Please use the following credentials to log in.\n\n"
                    f"Email: {user.email}\n"
                    f"Password: {password}\n\n" # Send the auto-generated password
                    f"Click here to log in:\n{login_link}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception as e:
            user.delete() # Clean up if email fails
            return Response({"error": f"Failed to send invitation email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": f"Candidate {user.email} created successfully. Login details have been sent."}, status=status.HTTP_201_CREATED)

# --- NEW: A public view for a candidate to set their password from the email link ---
#class SetPasswordView(APIView):
#    permission_classes = [AllowAny]

#    def post(self, request, uuid):
#        serializer = SetPasswordSerializer(data=request.data)
#        if not serializer.is_valid():
#            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#        try:
#            user = CustomUser.objects.get(email_verification_uuid=uuid, is_active=False)
            
#            user.set_password(serializer.validated_data['password'])
#            user.is_active = True
#            user.is_email_verified = True # Setting password also verifies them
#            user.save()
            
#            return Response({'message': 'Password set successfully. You can now log in.'}, status=status.HTTP_200_OK)
#        except CustomUser.DoesNotExist:
#            return Response({'error': 'Invalid or expired link.'}, status=status.HTTP_404_NOT_FOUND)

class EmailOrPhoneLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailOrPhoneLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)