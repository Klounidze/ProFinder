# users/api_views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .models import User, Favorite
from .serializers import (
    UserSerializer, UserDetailSerializer, UserRegisterSerializer,
    UserProfileUpdateSerializer
)
from providers.models import Provider
from providers.serializers import ProviderSerializer
from reviews.models import Review
from chat.models import Message


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Вход в систему"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').lower()
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })

        return Response(
            {'error': 'Неверное имя пользователя или пароль'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Получение и обновление профиля пользователя"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserProfileUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(UserDetailSerializer(instance).data)


class UserStatsView(APIView):
    """Статистика пользователя"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        stats = {
            'reviews_count': Review.objects.filter(user=user).count(),
            'approved_reviews': Review.objects.filter(user=user, is_approved=True).count(),
            'pending_reviews': Review.objects.filter(user=user, is_approved=False).count(),
            'messages_count': Message.objects.filter(sender=user).count(),
            'unread_count': user.get_unread_count(),
            'providers_count': user.providers.count(),
            'favorites_count': Favorite.objects.filter(user=user).count()
        }

        return Response(stats)


class FavoriteListView(APIView):
    """Список избранных специалистов"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        providers = [fav.provider for fav in favorites]
        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data)


class FavoriteToggleView(APIView):
    """Добавление/удаление из избранного"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, provider_id):
        provider = get_object_or_404(Provider, id=provider_id, is_active=True)

        favorite = Favorite.objects.filter(
            user=request.user,
            provider=provider
        ).first()

        if favorite:
            favorite.delete()
            is_favorite = False
            message = 'Удалено из избранного'
        else:
            Favorite.objects.create(user=request.user, provider=provider)
            is_favorite = True
            message = 'Добавлено в избранное'

        return Response({
            'is_favorite': is_favorite,
            'message': message,
            'favorites_count': Favorite.objects.filter(provider=provider).count()
        })


class FavoriteCheckView(APIView):
    """Проверка, находится ли специалист в избранном"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, provider_id):
        is_favorite = Favorite.objects.filter(
            user=request.user,
            provider_id=provider_id
        ).exists()
        return Response({'is_favorite': is_favorite})