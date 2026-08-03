# providers/models.py

from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def provider_photo_path(instance, filename):
    """Путь для сохранения фото портфолио"""
    return f'providers/provider_{instance.provider.id}/{filename}'


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

    # Дополнительные поля
    experience_years = models.IntegerField(
        default=0,
        verbose_name='Опыт работы (лет)'
    )
    price_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Цена от'
    )
    price_to = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Цена до'
    )

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []

    def calculate_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(provider=self, is_approved=True)
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            self.rating = round(avg, 1)
            self.save(update_fields=['rating'])
        return self.rating

    def get_main_photo(self):
        photo = self.photos.filter(is_main=True).first()
        if photo:
            return photo
        return self.photos.first()

    def __str__(self):
        return self.full_name


class ProviderPhoto(models.Model):
    """Фото портфолио специалиста"""
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=provider_photo_path)
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.provider.full_name}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.provider.photos.exists():
            self.is_main = True

        if self.image:
            self._process_image()

        super().save(*args, **kwargs)

    def _process_image(self):
        """Обработка и оптимизация фото"""
        try:
            img = Image.open(self.image)

            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            max_size = 1200
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            self.image = InMemoryUploadedFile(
                output,
                'ImageField',
                self.image.name.replace('.', '_optimized.'),
                'image/jpeg',
                sys.getsizeof(output),
                None
            )
        except Exception as e:
            print(f"Ошибка обработки фото: {e}")