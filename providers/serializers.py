# providers/serializers.py

from rest_framework import serializers
from .models import Provider, ProviderPhoto


class ProviderPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProviderPhoto
        fields = ['id', 'image', 'image_url', 'caption', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ProviderSerializer(serializers.ModelSerializer):
    tags_list = serializers.SerializerMethodField()
    main_photo = serializers.SerializerMethodField()
    rating_stars = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = [
            'id', 'full_name', 'category', 'phone', 'email', 'address',
            'country', 'city', 'rating', 'rating_stars', 'description',
            'tags', 'tags_list', 'is_verified', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'main_photo', 'reviews_count', 'is_favorite',
            'latitude', 'longitude', 'address_full',
            'experience_years', 'price_from', 'price_to'
        ]
        read_only_fields = ['id', 'rating', 'created_at', 'updated_at']

    def get_tags_list(self, obj):
        return obj.get_tags_list()

    def get_main_photo(self, obj):
        photo = obj.get_main_photo()
        if photo:
            return ProviderPhotoSerializer(photo).data
        return None

    def get_rating_stars(self, obj):
        return '⭐' * int(obj.rating) if obj.rating else ''

    def get_reviews_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from users.models import Favorite
            return Favorite.objects.filter(user=request.user, provider=obj).exists()
        return False


class ProviderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            'full_name', 'category', 'phone', 'email', 'address',
            'country', 'city', 'description', 'tags',
            'experience_years', 'price_from', 'price_to'
        ]


class ProviderPhotoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderPhoto
        fields = ['image', 'caption', 'is_main']