# backend/test_creation/accounts/views.py
from django.shortcuts import redirect
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.permissions import AllowAny
from .models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = CustomUser.objects.get_or_create(email=email)

        if created:
            user.set_password(password)
            user.email_verification_uuid = uuid.uuid4()
            user.is_active = False  # keep it active but not verified
            user.save()
        elif user.is_email_verified:
            return Response({"message": "Email already verified."}, status=status.HTTP_200_OK)

        if not user.email_verification_uuid:
            user.email_verification_uuid = uuid.uuid4()
            user.save()

        verification_link = f"{settings.BACKEND_URL}/api/verify-email/{user.email_verification_uuid}/"

        print("\n🔗 Email Verification Link (for development):")
        print(verification_link)
        print()

        try:
            send_mail(
                subject="Verify your email address",
                message=(
                    f"Hello {user.email},\n\n"
                    f"Please verify your email by clicking the link below:\n"
                    f"{verification_link}\n\n"
                    "If you did not request this, please ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Verification email sent."}, status=status.HTTP_200_OK)

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
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer