from django.urls import path
from . import views, api

app_name = 'punishments'

urlpatterns = [
    path('', views.punishments_list, name='list'),
    path('add/', views.punishment_add, name='add'),
    path('<int:pk>/edit/', views.punishment_edit, name='edit'),
    path('<int:pk>/delete/', views.punishment_delete, name='delete'),
    path('<int:pk>/unban/', views.punishment_unban, name='unban'),

    # API
    path('api/check/', api.check_player, name='api_check_player'),
    path('api/add/', api.add_punishment, name='api_add_punishment'),
    path('api/remove/', api.remove_punishment, name='api_remove_punishment'),
]
