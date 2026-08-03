# chat/api_views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, MessageCreateSerializer
from providers.models import Provider
from users.email_utils import send_new_message_notification

User = get_user_model()


class ChatListCreateView(APIView):
    """Список чатов пользователя"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        chats = request.user.get_all_chats()
        serializer = ChatSerializer(chats, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'Не указан ID пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        other_user = get_object_or_404(User, id=user_id)

        if other_user == request.user:
            return Response(
                {'error': 'Нельзя создать чат с самим собой'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chat = Chat.objects.filter(
            Q(user1=request.user, user2=other_user) |
            Q(user1=other_user, user2=request.user)
        ).first()

        if not chat:
            chat = Chat.objects.create(
                user1=min(request.user, other_user, key=lambda x: x.id),
                user2=max(request.user, other_user, key=lambda x: x.id)
            )

        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)


class ChatWithProviderView(APIView):
    """Получить или создать чат с владельцем специалиста"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, provider_id):
        provider = get_object_or_404(Provider, id=provider_id)

        if not provider.created_by:
            return Response(
                {'error': 'У этого специалиста нет владельца'},
                status=status.HTTP_400_BAD_REQUEST
            )

        other_user = provider.created_by

        if other_user == request.user:
            return Response(
                {'error': 'Нельзя создать чат с самим собой'},
                status=status.HTTP_400_BAD_REQUEST
            )

        chat = Chat.objects.filter(
            Q(user1=request.user, user2=other_user) |
            Q(user1=other_user, user2=request.user)
        ).first()

        if not chat:
            chat = Chat.objects.create(
                user1=min(request.user, other_user, key=lambda x: x.id),
                user2=max(request.user, other_user, key=lambda x: x.id)
            )

        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)


class MessageListView(generics.ListAPIView):
    """Список сообщений в чате"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)

        # Проверяем доступ
        if chat.user1 != self.request.user and chat.user2 != self.request.user:
            return Message.objects.none()

        messages = Message.objects.filter(chat=chat).order_by('created_at')

        # Помечаем сообщения как прочитанные
        messages.filter(is_read=False).exclude(sender=self.request.user).update(is_read=True)

        return messages


class MessageCreateView(APIView):
    """Отправка сообщения"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)

        # Проверяем доступ
        if chat.user1 != request.user and chat.user2 != request.user:
            return Response(
                {'error': 'Нет доступа к этому чату'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=serializer.validated_data['content']
            )

            # Отправляем уведомление
            send_new_message_notification(message)

            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UnreadCountView(APIView):
    """Количество непрочитанных сообщений"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = request.user.get_unread_count()
        return Response({'unread_count': count})


class MarkAllReadView(APIView):
    """Отметить все сообщения как прочитанные"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        for chat in request.user.get_all_chats():
            chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        return Response({'success': True})