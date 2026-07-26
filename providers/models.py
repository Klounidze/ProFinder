from django.db import models
from django.conf import settings
from django.utils import timezone


class Provider(models.Model):
    full_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    description = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='providers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def calculate_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(provider=self)
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            self.rating = round(avg, 1)
            self.save()
        return self.rating

    def __str__(self):
        return self.full_name
