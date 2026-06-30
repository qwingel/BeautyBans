"""
URL configuration for beautybans project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views, logout
from django.urls import include, path
from django.shortcuts import redirect
from .public_views import public_bans, public_admins

def logout_view(request):
    logout(request)
    return redirect('login')

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('servers:list')
    else:
        return redirect('public_bans')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('bans/', public_bans, name='public_bans'),
    path('admin-list/', public_admins, name='public_admins'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('servers/', include('servers.urls')),
    path('admins/', include('admins.urls')),
    path('punishments/', include('punishments.urls')),
]
