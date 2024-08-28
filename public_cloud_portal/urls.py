"""
URL configuration for public_cloud_portal project.

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
from django.contrib import admin
from django.urls import path, include
from . import views #go to current directory and grab views from there


urlpatterns = [
    path('', include('billow.urls')),
    path('billow/', include('django.contrib.auth.urls')),
    path('gcp_app/', include('gcp_app.urls')),
    path('aws_app/', include('aws_app.urls')),
    path('', views.HomePage.as_view(), name='home'),
    path('base', views.LoggedPage.as_view(), name='base'),
    path('index_billow', views.LogoutPage.as_view(), name='index_billow'),
    path('admin/', admin.site.urls),
]
