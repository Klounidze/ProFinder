# users/serializers.py

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Favorite


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'is_active', 'created_at']
        read_only_fields = ['id', 'is_active', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    unread_count = serializers.SerializerMethodField()
    providers_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'is_active',
                  'created_at', 'last_login', 'unread_count', 'providers_count',
                  'reviews_count', 'favorites_count']

    def get_unread_count(self, obj):
        return obj.get_unread_count()

    def get_providers_count(self, obj):
        return obj.providers.count()

    def get_reviews_count(self, obj):
        return obj.reviews.count()

    def get_favorites_count(self, obj):
        return obj.favorites.count()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data.get('phone', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'avatar']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'provider', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']