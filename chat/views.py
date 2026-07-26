from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from providers.models import Provider
from .models import Chat, Message
import json


@login_required
def get_or_create_chat_with_provider(request, provider_id):
    """Получить или создать чат с владельцем поставщика"""
    try:
        provider = get_object_or_404(Provider, id=provider_id)

        if not provider.created_by:
            return JsonResponse({'error': 'У этого объявления нет владельца'}, status=400)

        provider_owner = provider.created_by

        if provider_owner == request.user:
            return JsonResponse({'error': 'Нельзя написать самому себе'}, status=400)

        chat = Chat.objects.filter(
            Q(user1=request.user, user2=provider_owner) |
            Q(user1=provider_owner, user2=request.user)
        ).first()

        if not chat:
            chat = Chat.objects.create(
                user1=min(request.user, provider_owner, key=lambda x: x.id),
                user2=max(request.user, provider_owner, key=lambda x: x.id)
            )

        return JsonResponse({
            'chat_id': chat.id,
            'other_user': {
                'id': provider_owner.id,
                'username': provider_owner.username
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages(request, chat_id):
    """Получение сообщений чата"""
    chat = get_object_or_404(Chat, id=chat_id)

    if chat.user1 != request.user and chat.user2 != request.user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    messages = Message.objects.filter(chat=chat).order_by('created_at')
    data = [{
        'id': m.id,
        'sender_id': m.sender.id,
        'sender_name': m.sender.username,
        'content': m.content,
        'is_read': m.is_read,
        'created_at': m.created_at.isoformat(),
        'created_at_formatted': m.created_at.strftime('%d.%m.%Y %H:%M')
    } for m in messages]

    return JsonResponse(data, safe=False)


@login_required
def send_message(request, chat_id):
    """Отправка сообщения"""
    chat = get_object_or_404(Chat, id=chat_id)

    if chat.user1 != request.user and chat.user2 != request.user:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()

        if not content:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )

        return JsonResponse({
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.username,
            'content': message.content,
            'is_read': message.is_read,
            'created_at': message.created_at.isoformat(),
            'created_at_formatted': message.created_at.strftime('%d.%m.%Y %H:%M')
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_notifications_count(request):
    """Получение количества непрочитанных сообщений"""
    try:
        unread_count = request.user.get_unread_count()
        return JsonResponse({'unread_count': unread_count})
    except Exception:
        return JsonResponse({'unread_count': 0})


@login_required
def mark_all_read(request):
    """Отметить все сообщения как прочитанные"""
    try:
        for chat in request.user.get_all_chats():
            chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)