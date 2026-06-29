from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    path('', views.admins_list, name='admins_list'),
    path('add/', views.admin_add, name='admin_add'),
    path('<int:pk>/edit/', views.admin_edit, name='admin_edit'),
    path('<int:pk>/delete/', views.admin_delete, name='admin_delete'),

    path('groups/', views.groups_list, name='groups_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),

    path('permissions/', views.permissions_list, name='permissions_list'),
    path('permissions/add/', views.permission_add, name='permission_add'),
    path('permissions/<int:pk>/edit/', views.permission_edit, name='permission_edit'),
    path('permissions/<int:pk>/delete/', views.permission_delete, name='permission_delete'),
]
