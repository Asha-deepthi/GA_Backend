#from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
#from django.urls import path

#urlpatterns = [
#   path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#   path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#]

#backend/users/urls.py
import uuid
from django.urls import path
from .views import SendVerificationEmailView, VerifyEmailView, CustomTokenObtainPairView

urlpatterns = [
    path('send-verification-email/', SendVerificationEmailView.as_view(), name='send_verification_email'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('verify-email/<uuid:uuid>/', VerifyEmailView.as_view(), name='verify_email'),
]
