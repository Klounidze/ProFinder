from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


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
        """Получить список уведомлений (последние непрочитанные сообщения)"""
        from chat.models import Message
        notifications = []
        for chat in self.get_all_chats():
            unread_messages = chat.messages.filter(
                is_read=False
            ).exclude(sender=self).order_by('-created_at')
            for msg in unread_messages[:3]:  # По 3 последних из каждого чата
                notifications.append({
                    'chat_id': chat.id,
                    'sender_name': msg.sender.username,
                    'content': msg.content[:100] + ('...' if len(msg.content) > 100 else ''),
                    'created_at': msg.created_at,
                    'is_read': msg.is_read,
                    'other_user_id': chat.get_other_user(self).id,
                    'other_user_name': chat.get_other_user(self).username
                })
        # Сортируем по времени (сначала новые)
        notifications.sort(key=lambda x: x['created_at'], reverse=True)
        return notifications[:20]  # Максимум 20 уведомлений

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()
        super().save(*args, **kwargs)