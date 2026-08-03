# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def user_avatar_path(instance, filename):
    """Путь для сохранения аватара пользователя"""
    return f'avatars/user_{instance.id}/{filename}'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Telegram
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Telegram ID'
    )
    telegram_notifications = models.BooleanField(
        default=True,
        verbose_name='Уведомления в Telegram'
    )

    def __str__(self):
        return self.username

    def get_unread_count(self):
        from chat.models import Message
        unread = 0
        for chat in self.get_all_chats():
            unread += chat.messages.filter(is_read=False).exclude(sender=self).count()
        return unread

    def get_all_chats(self):
        from chat.models import Chat
        return Chat.objects.filter(
            models.Q(user1=self) | models.Q(user2=self)
        ).order_by('-updated_at')

    def get_notifications(self):
        from chat.models import Message
        notifications = []
        for chat in self.get_all_chats():
            unread_messages = chat.messages.filter(
                is_read=False
            ).exclude(sender=self).order_by('-created_at')
            for msg in unread_messages[:3]:
                notifications.append({
                    'chat_id': chat.id,
                    'sender_name': msg.sender.username,
                    'content': msg.content[:100] + ('...' if len(msg.content) > 100 else ''),
                    'created_at': msg.created_at,
                    'is_read': msg.is_read,
                    'other_user_id': chat.get_other_user(self).id,
                    'other_user_name': chat.get_other_user(self).username
                })
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        return notifications[:20]

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()

        if self.avatar and self.pk:
            self._process_avatar()

        super().save(*args, **kwargs)

    def _process_avatar(self):
        """Обработка и оптимизация аватара"""
        try:
            img = Image.open(self.avatar)

            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            size = min(img.size)
            left = (img.width - size) // 2
            top = (img.height - size) // 2
            img = img.crop((left, top, left + size, top + size))

            img = img.resize((200, 200), Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            self.avatar = InMemoryUploadedFile(
                output,
                'ImageField',
                self.avatar.name.replace('.', '_processed.'),
                'image/jpeg',
                sys.getsizeof(output),
                None
            )
        except Exception as e:
            print(f"Ошибка обработки аватара: {e}")


class Favorite(models.Model):
    """Избранные специалисты"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    provider = models.ForeignKey(
        'providers.Provider',
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'provider']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.provider.full_name}"