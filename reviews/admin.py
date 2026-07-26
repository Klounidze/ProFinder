from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'provider', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    search_fields = ['provider__full_name', 'user__username', 'comment']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        for review in queryset:
            review.provider.calculate_rating()
        self.message_user(request, f'{queryset.count()} отзывов одобрено.')
    approve_reviews.short_description = 'Одобрить выбранные отзывы'