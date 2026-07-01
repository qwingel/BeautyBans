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
from django.conf import settings
from .public_views import public_bans, public_admins

def logout_view(request):
    logout(request)
    return redirect('login')

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('servers:list')
    else:
        return redirect('public_bans')

_urlpatterns = [
    path('', home_redirect, name='home'),

    # Публичные страницы
    path('banlist/', public_bans, name='public_bans'),
    path('admins/', public_admins, name='public_admins'),

    # Авторизация
    path('adminpanel/login/', auth_views.LoginView.as_view(), name='login'),
    path('adminpanel/logout/', logout_view, name='logout'),

    # Django admin (для разработки)
    path('admin/', admin.site.urls),

    # Админ-панель
    path('adminpanel/servers/', include('servers.urls')),
    path('adminpanel/administration/', include('admins.urls')),
    path('adminpanel/punishments/', include('punishments.urls')),
]

# Поддержка URL_PREFIX для установки в подкаталог
if settings.URL_PREFIX:
    urlpatterns = [
        path(settings.URL_PREFIX.lstrip('/') + '/', include(_urlpatterns)),
    ]
else:
    urlpatterns = _urlpatterns
