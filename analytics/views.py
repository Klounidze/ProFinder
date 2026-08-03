# analytics/views.py

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from users.models import User
from providers.models import Provider
from reviews.models import Review
from chat.models import Message
import json


@staff_member_required
def dashboard(request):
    """Дашборд аналитики"""
    context = get_dashboard_data()
    return render(request, 'admin/analytics/dashboard.html', context)


def get_dashboard_data():
    """Сбор данных для дашборда"""

    # Общая статистика
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_providers = Provider.objects.count()
    active_providers = Provider.objects.filter(is_active=True).count()
    total_reviews = Review.objects.count()
    approved_reviews = Review.objects.filter(is_approved=True).count()
    total_messages = Message.objects.count()

    # Динамика за последние 30 дней
    thirty_days_ago = timezone.now() - timedelta(days=30)

    daily_users = User.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        {'date': "date(created_at)"}
    ).values('date').annotate(count=Count('id')).order_by('date')

    daily_providers = Provider.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        {'date': "date(created_at)"}
    ).values('date').annotate(count=Count('id')).order_by('date')

    daily_reviews = Review.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        {'date': "date(created_at)"}
    ).values('date').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).order_by('date')

    # Популярные категории
    categories_stats = Provider.objects.values('category').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).order_by('-count')[:10]

    # Рейтинг специалистов
    top_providers = Provider.objects.filter(
        is_active=True
    ).annotate(
        reviews_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(
        reviews_count__gt=0
    ).order_by('-avg_rating')[:10]

    # Активность чатов
    chats_activity = Message.objects.filter(
        created_at__gte=thirty_days_ago
    ).extra(
        {'date': "date(created_at)"}
    ).values('date').annotate(count=Count('id')).order_by('date')

    # Конверсия
    users_with_providers = User.objects.filter(providers__isnull=False).distinct().count()
    users_with_reviews = User.objects.filter(reviews__isnull=False).distinct().count()

    return {
        'total_users': total_users,
        'active_users': active_users,
        'total_providers': total_providers,
        'active_providers': active_providers,
        'total_reviews': total_reviews,
        'approved_reviews': approved_reviews,
        'total_messages': total_messages,
        'daily_users': json.dumps(list(daily_users)),
        'daily_providers': json.dumps(list(daily_providers)),
        'daily_reviews': json.dumps(list(daily_reviews)),
        'categories_stats': list(categories_stats),
        'top_providers': top_providers,
        'chats_activity': json.dumps(list(chats_activity)),
        'users_with_providers': users_with_providers,
        'users_with_reviews': users_with_reviews,
    }