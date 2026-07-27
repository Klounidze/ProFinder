from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.index, name='index'),
    path('login/', user_views.user_login, name='login'),
    path('register/', user_views.user_register, name='register'),
    path('logout/', user_views.user_logout, name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('profile/edit/', user_views.edit_profile, name='edit_profile'),
    path('search/', user_views.search_providers, name='search'),
    path('add/', user_views.add_provider, name='add_provider'),
    path('provider/<int:provider_id>/', user_views.provider_detail, name='provider_detail'),
    path('provider/<int:provider_id>/review/', user_views.add_review, name='add_review'),
    path('provider/<int:provider_id>/add_photo/', user_views.add_provider_photo, name='add_provider_photo'),
    path('provider/photo/<int:photo_id>/delete/', user_views.delete_provider_photo, name='delete_provider_photo'),
    path('chat/', include('chat.urls')),
    path('users/', include('users.urls')),
    path('reviews/', include('reviews.urls')),
    path('providers/', include('providers.urls')),
]

# Для отдачи медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)