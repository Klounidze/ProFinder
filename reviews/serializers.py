# reviews/serializers.py

from rest_framework import serializers
from .models import Review
from users.serializers import UserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    rating_stars = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'provider', 'user', 'user_name', 'rating', 'rating_stars',
                  'comment', 'is_approved', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'is_approved', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.username

    def get_rating_stars(self, obj):
        return '⭐' * obj.rating


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value