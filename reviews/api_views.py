# reviews/api_views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from providers.models import Provider


class ReviewCreateView(generics.CreateAPIView):
    """Создание отзыва"""
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        provider_id = self.kwargs.get('provider_id')
        provider = get_object_or_404(Provider, id=provider_id, is_active=True)

        # Проверяем, не оставлял ли пользователь уже отзыв
        if Review.objects.filter(provider=provider, user=request.user).exists():
            return Response(
                {'error': 'Вы уже оставляли отзыв на этого специалиста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(provider=provider, user=request.user)

        # Обновляем рейтинг
        provider.calculate_rating()

        # Отправляем уведомление
        from users.email_utils import send_new_review_notification
        send_new_review_notification(review)

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ReviewListView(generics.ListAPIView):
    """Список отзывов на специалиста"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        provider_id = self.kwargs.get('provider_id')
        provider = get_object_or_404(Provider, id=provider_id)
        return provider.reviews.filter(is_approved=True)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация об отзыве"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        provider = review.provider
        review.delete()
        provider.calculate_rating()
        return Response(status=status.HTTP_204_NO_CONTENT)