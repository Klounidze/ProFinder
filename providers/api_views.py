# providers/api_views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from .models import Provider, ProviderPhoto
from .serializers import (
    ProviderSerializer, ProviderCreateSerializer,
    ProviderPhotoSerializer, ProviderPhotoCreateSerializer
)
from .services import GeocodingService
from reviews.serializers import ReviewSerializer


class ProviderListView(generics.ListAPIView):
    serializer_class = ProviderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Provider.objects.filter(is_active=True)

        # Фильтры
        country = self.request.query_params.get('country')
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        city = self.request.query_params.get('city')
        min_rating = self.request.query_params.get('min_rating')
        max_rating = self.request.query_params.get('max_rating')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        experience = self.request.query_params.get('experience')

        # Сортировка
        sort_by = self.request.query_params.get('sort_by', 'rating')
        sort_order = self.request.query_params.get('sort_order', 'desc')

        if country:
            queryset = queryset.filter(country__icontains=country)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search)
            )
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        if max_rating:
            queryset = queryset.filter(rating__lte=float(max_rating))
        if price_min:
            queryset = queryset.filter(price_from__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price_to__lte=float(price_max))
        if experience:
            queryset = queryset.filter(experience_years__gte=int(experience))

        # Сортировка
        if sort_by == 'rating':
            order = '-rating' if sort_order == 'desc' else 'rating'
        elif sort_by == 'created_at':
            order = '-created_at' if sort_order == 'desc' else 'created_at'
        elif sort_by == 'name':
            order = '-full_name' if sort_order == 'desc' else 'full_name'
        elif sort_by == 'price':
            order = '-price_from' if sort_order == 'desc' else 'price_from'
        elif sort_by == 'experience':
            order = '-experience_years' if sort_order == 'desc' else 'experience_years'
        else:
            order = '-rating'

        return queryset.order_by(order)


class ProviderCreateView(generics.CreateAPIView):
    """Создание нового специалиста с автоматическим геокодингом"""
    serializer_class = ProviderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)

        # Автоматическое определение координат
        if instance.address:
            lat, lon, full_address = GeocodingService.get_coordinates(instance.address)
            if lat and lon:
                instance.latitude = lat
                instance.longitude = lon
                instance.address_full = full_address or instance.address
                instance.save(update_fields=['latitude', 'longitude', 'address_full'])
                print(f"📍 Координаты определены для {instance.full_name}: {lat}, {lon}")
            else:
                print(f"⚠️ Не удалось определить координаты для {instance.full_name}")


class ProviderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о специалисте с обновлением координат"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        provider = self.get_object()
        serializer = self.get_serializer(provider)
        data = serializer.data

        reviews = provider.reviews.filter(is_approved=True)
        data['reviews'] = ReviewSerializer(reviews, many=True).data

        photos = provider.photos.all()
        data['photos'] = ProviderPhotoSerializer(photos, many=True).data

        if request.user.is_authenticated:
            from users.models import Favorite
            data['is_favorite'] = Favorite.objects.filter(
                user=request.user,
                provider=provider
            ).exists()
        else:
            data['is_favorite'] = False

        return Response(data)

    def update(self, request, *args, **kwargs):
        provider = self.get_object()

        if provider.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'У вас нет прав на редактирование'},
                status=status.HTTP_403_FORBIDDEN
            )

        response = super().update(request, *args, **kwargs)

        # Если изменился адрес, обновляем координаты
        if 'address' in request.data and request.data['address']:
            new_address = request.data['address']
            if provider.address != new_address or not provider.latitude:
                lat, lon, full_address = GeocodingService.get_coordinates(new_address)
                if lat and lon:
                    provider.latitude = lat
                    provider.longitude = lon
                    provider.address_full = full_address or new_address
                    provider.save(update_fields=['latitude', 'longitude', 'address_full'])
                    print(f"📍 Координаты обновлены для {provider.full_name}: {lat}, {lon}")
                else:
                    print(f"⚠️ Не удалось обновить координаты для {provider.full_name}")

        return response

    def destroy(self, request, *args, **kwargs):
        provider = self.get_object()

        if provider.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'У вас нет прав на удаление'},
                status=status.HTTP_403_FORBIDDEN
            )

        provider.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProviderPhotoUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, provider_id):
        provider = get_object_or_404(Provider, id=provider_id)

        if provider.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'У вас нет прав на добавление фото'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProviderPhotoCreateSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(provider=provider)

            if provider.photos.count() == 1:
                photo.is_main = True
                photo.save()

            return Response(ProviderPhotoSerializer(photo).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProviderPhotoDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, photo_id):
        photo = get_object_or_404(ProviderPhoto, id=photo_id)
        provider = photo.provider

        if provider.created_by != request.user and not request.user.is_staff:
            return Response(
                {'error': 'У вас нет прав на удаление фото'},
                status=status.HTTP_403_FORBIDDEN
            )

        photo.image.delete(save=False)
        photo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProviderCategoriesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        categories = Provider.objects.values_list('category', flat=True).distinct()
        categories = list(set(list(categories) + settings.CATEGORIES))
        categories.sort()
        return Response(categories)


class ProviderMapView(APIView):
    """Получение данных для карты с координатами"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        providers = Provider.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False
        )

        data = [{
            'id': p.id,
            'full_name': p.full_name,
            'category': p.category,
            'latitude': float(p.latitude),
            'longitude': float(p.longitude),
            'address': p.address_full or p.address,
            'rating': p.rating,
            'is_verified': p.is_verified,
        } for p in providers]

        return Response(data)


class ProviderGeocodeView(APIView):
    """Ручной геокодинг адреса"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        address = request.data.get('address')
        provider_id = request.data.get('provider_id')

        if not address:
            return Response(
                {'error': 'Адрес не указан'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lat, lon, full_address = GeocodingService.get_coordinates(address)

        if lat and lon and provider_id:
            provider = get_object_or_404(Provider, id=provider_id)
            if provider.created_by == request.user or request.user.is_staff:
                provider.latitude = lat
                provider.longitude = lon
                provider.address_full = full_address or address
                provider.save(update_fields=['latitude', 'longitude', 'address_full'])

        return Response({
            'latitude': lat,
            'longitude': lon,
            'address': full_address or address
        })


class ProviderGeocodeAllView(APIView):
    """Массовое геокодирование всех специалистов без координат"""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        import time

        providers = Provider.objects.filter(
            latitude__isnull=True,
            longitude__isnull=True,
            address__isnull=False
        ).exclude(address='')

        count = providers.count()

        if count == 0:
            return Response({
                'success': True,
                'message': 'Все специалисты уже имеют координаты.',
                'processed': 0
            })

        success_count = 0
        errors = []

        for provider in providers:
            if provider.address:
                lat, lon, full = GeocodingService.get_coordinates(provider.address)
                if lat and lon:
                    provider.latitude = lat
                    provider.longitude = lon
                    provider.address_full = full or provider.address
                    provider.save(update_fields=['latitude', 'longitude', 'address_full'])
                    success_count += 1
                else:
                    errors.append({
                        'id': provider.id,
                        'name': provider.full_name,
                        'address': provider.address
                    })
                time.sleep(1)  # Задержка для соблюдения лимитов Nominatim

        return Response({
            'success': True,
            'processed': count,
            'success_count': success_count,
            'errors': errors,
            'message': f'Успешно обработано {success_count} из {count} специалистов.'
        })