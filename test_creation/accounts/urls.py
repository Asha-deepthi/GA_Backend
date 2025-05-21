#backend/test_creation/accounts/urls.py
from django.urls import path
from .views import SignupView, ActivateUserView, LoginView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
]