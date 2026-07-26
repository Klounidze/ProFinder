from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # API для чатов
    path('api/with_provider/<int:provider_id>/', views.get_or_create_chat_with_provider, name='get_or_create_chat'),
    path('api/<int:chat_id>/messages/', views.get_messages, name='get_messages'),
    path('api/<int:chat_id>/send/', views.send_message, name='send_message'),

    # API для уведомлений
    path('api/notifications/count/', views.get_notifications_count, name='notifications_count'),
    path('api/mark_all_read/', views.mark_all_read, name='mark_all_read'),
]