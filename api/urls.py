# api/urls.py

from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from users.api_views import (
    RegisterView, LoginView, ProfileView, UserStatsView,
    FavoriteListView, FavoriteToggleView, FavoriteCheckView
)
from providers.api_views import (
    ProviderListView, ProviderCreateView, ProviderDetailView,
    ProviderPhotoUploadView, ProviderPhotoDeleteView,
    ProviderCategoriesView, ProviderMapView, ProviderGeocodeView,
    ProviderGeocodeAllView  # ← НОВЫЙ ИМПОРТ
)
from reviews.api_views import ReviewCreateView, ReviewListView, ReviewDetailView
from chat.api_views import (
    ChatListCreateView, ChatWithProviderView, MessageListView,
    MessageCreateView, UnreadCountView, MarkAllReadView
)

urlpatterns = [
    # ===== Аутентификация =====
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/login/', LoginView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),

    # ===== Пользователи =====
    path('users/profile/', ProfileView.as_view(), name='api_profile'),
    path('users/stats/', UserStatsView.as_view(), name='api_user_stats'),

    # ===== Избранное =====
    path('favorites/', FavoriteListView.as_view(), name='api_favorites'),
    path('favorites/<int:provider_id>/toggle/', FavoriteToggleView.as_view(), name='api_favorite_toggle'),
    path('favorites/<int:provider_id>/check/', FavoriteCheckView.as_view(), name='api_favorite_check'),

    # ===== Специалисты =====
    path('providers/', ProviderListView.as_view(), name='api_providers_list'),
    path('providers/create/', ProviderCreateView.as_view(), name='api_providers_create'),
    path('providers/categories/', ProviderCategoriesView.as_view(), name='api_categories'),
    path('providers/map/', ProviderMapView.as_view(), name='api_providers_map'),
    path('providers/geocode/', ProviderGeocodeView.as_view(), name='api_geocode'),
    path('providers/geocode-all/', ProviderGeocodeAllView.as_view(), name='api_geocode_all'),  # ← НОВЫЙ ЭНДПОИНТ
    path('providers/<int:id>/', ProviderDetailView.as_view(), name='api_provider_detail'),
    path('providers/<int:provider_id>/photos/', ProviderPhotoUploadView.as_view(), name='api_photo_upload'),
    path('providers/photos/<int:photo_id>/delete/', ProviderPhotoDeleteView.as_view(), name='api_photo_delete'),

    # ===== Отзывы =====
    path('providers/<int:provider_id>/reviews/', ReviewListView.as_view(), name='api_reviews_list'),
    path('providers/<int:provider_id>/reviews/create/', ReviewCreateView.as_view(), name='api_review_create'),
    path('reviews/<int:id>/', ReviewDetailView.as_view(), name='api_review_detail'),

    # ===== Чаты =====
    path('chats/', ChatListCreateView.as_view(), name='api_chats_list'),
    path('chats/provider/<int:provider_id>/', ChatWithProviderView.as_view(), name='api_chat_provider'),
    path('chats/<int:chat_id>/messages/', MessageListView.as_view(), name='api_messages_list'),
    path('chats/<int:chat_id>/messages/send/', MessageCreateView.as_view(), name='api_message_send'),
    path('chats/unread/count/', UnreadCountView.as_view(), name='api_unread_count'),
    path('chats/mark-all-read/', MarkAllReadView.as_view(), name='api_mark_all_read'),
]