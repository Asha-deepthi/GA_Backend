"""
URL configuration for backend_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#backend/backend_project/urls.py
#from django.contrib import admin
#from django.urls import path, include
#from test_creation.accounts.views import SendVerificationEmailView

#urlpatterns = [
 #   path('admin/', admin.site.urls),
 #  path('api/test-creation/', include('test_creation.urls')),
 #   path('api/', include('test_creation.accounts.urls')),  # include account endpoints

#backend/backend_project/urls.py
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
#from users.views import SendVerificationEmailView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/test-creation/', include('test_creation.urls')),
    path('api/test-execution/', include('test_execution.urls')),
    #path('api/signup/', SendVerificationEmailView.as_view(), name='signup')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
