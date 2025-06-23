#backend/users/urls.py
#import uuid
#from django.urls import path
#from .views import SendVerificationEmailView, VerifyEmailView, EmailOrPhoneLoginView

#urlpatterns = [
#    path('send-verification-email/', SendVerificationEmailView.as_view(), name='send_verification_email'),
#    #path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
#    path('verify-email/<uuid:uuid>/', VerifyEmailView.as_view(), name='verify_email'),
#     path('login/', EmailOrPhoneLoginView.as_view(), name='email-or-phone-login'),
#]

# backend/users/urls.py

import uuid
from django.urls import path
from .views import (
    UnifiedSignupView,      # The new smart signup view
    VerifyEmailView, 
    EmailOrPhoneLoginView,
    ImportCandidateView,
    CurrentCandidateAPIView,
    ListCandidatesAPIView
)
from rest_framework_simplejwt.views import TokenObtainPairView
from users.views import CustomTokenObtainPairView  # your custom view

urlpatterns = [
    # The main signup URL for both Admins and Candidates completing registration
    path('signup/', UnifiedSignupView.as_view(), name='unified-signup'),
    
    # URL for Admins to verify their email
    path('verify-email/<uuid:uuid>/', VerifyEmailView.as_view(), name='verify-email'), 
    
    # URL for Admins to import candidates
    path('import-candidate/', ImportCandidateView.as_view(), name='import-candidate'),

    # The login URL for everyone
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),

    path('me/', CurrentCandidateAPIView.as_view(), name='current-candidate'),

    path('candidates/', ListCandidatesAPIView.as_view(), name='list-candidates'),

]