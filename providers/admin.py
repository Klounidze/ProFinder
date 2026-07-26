from django.contrib import admin
from .models import Provider

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'category', 'country', 'rating', 'is_verified', 'is_active']
    list_filter = ['category', 'country', 'is_verified', 'is_active']
    search_fields = ['full_name', 'category', 'description', 'tags']
    actions = ['verify_providers', 'activate_providers']

    def verify_providers(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} специалистов верифицировано.')
    verify_providers.short_description = 'Верифицировать выбранных специалистов'

    def activate_providers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} специалистов активировано.')
    activate_providers.short_description = 'Активировать выбранных специалистов'