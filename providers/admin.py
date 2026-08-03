# providers/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Provider, ProviderPhoto


class ProviderPhotoInline(admin.TabularInline):
    model = ProviderPhoto
    extra = 1
    fields = ['image', 'caption', 'is_main', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url)
        return '-'

    image_preview.short_description = 'Превью'


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'category', 'country', 'city', 'rating', 'is_verified', 'is_active',
                    'created_at']
    list_filter = ['category', 'country', 'is_verified', 'is_active', 'created_at']
    search_fields = ['full_name', 'category', 'description', 'tags', 'country', 'city', 'address']
    readonly_fields = ['rating', 'created_at', 'updated_at']
    ordering = ['-rating', '-created_at']
    inlines = [ProviderPhotoInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'category', 'rating', 'is_verified', 'is_active')
        }),
        ('Контакты', {
            'fields': ('phone', 'email', 'address', 'country', 'city')
        }),
        ('Дополнительно', {
            'fields': ('description', 'tags', 'experience_years', 'price_from', 'price_to')
        }),
        ('Владелец', {
            'fields': ('created_by',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['verify_providers', 'unverify_providers', 'activate_providers', 'deactivate_providers']

    def verify_providers(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} специалистов верифицировано.')

    verify_providers.short_description = 'Верифицировать выбранных специалистов'

    def unverify_providers(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f'{queryset.count()} специалистов деверифицировано.')

    unverify_providers.short_description = 'Снять верификацию с выбранных специалистов'

    def activate_providers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} специалистов активировано.')

    activate_providers.short_description = 'Активировать выбранных специалистов'

    def deactivate_providers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} специалистов деактивировано.')

    deactivate_providers.short_description = 'Деактивировать выбранных специалистов'


@admin.register(ProviderPhoto)
class ProviderPhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'caption', 'is_main', 'image_preview', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['provider__full_name', 'caption']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url)
        return '-'

    image_preview.short_description = 'Превью'