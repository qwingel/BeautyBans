from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    path('', views.servers_list, name='list'),
    path('add/', views.server_add, name='add'),
    path('<int:pk>/edit/', views.server_edit, name='edit'),
    path('<int:pk>/delete/', views.server_delete, name='delete'),
]
