# users/email_utils.py

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_email_notification(subject, template_name, context, recipient_list):
    """Отправка email-уведомления с HTML-шаблоном"""
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


def send_new_message_notification(message):
    """Уведомление о новом сообщении"""
    try:
        chat = message.chat
        recipient = chat.get_other_user(message.sender)

        if not recipient.email:
            return False

        subject = f"💬 Новое сообщение от {message.sender.username}"

        context = {
            'sender': message.sender,
            'recipient': recipient,
            'message': message,
            'chat_id': chat.id,
            'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
            'message_preview': message.content[:100] + ('...' if len(message.content) > 100 else '')
        }

        return send_email_notification(
            subject=subject,
            template_name='emails/new_message.html',
            context=context,
            recipient_list=[recipient.email]
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False


def send_new_review_notification(review):
    """Уведомление о новом отзыве"""
    try:
        provider = review.provider
        recipient = provider.created_by

        if not recipient.email:
            return False

        subject = f"⭐ Новый отзыв о {provider.full_name}"

        context = {
            'review': review,
            'provider': provider,
            'recipient': recipient,
            'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
            'rating_stars': '⭐' * review.rating
        }

        return send_email_notification(
            subject=subject,
            template_name='emails/new_review.html',
            context=context,
            recipient_list=[recipient.email]
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False


def send_welcome_email(user):
    """Приветственное письмо новому пользователю"""
    if not user.email:
        return False

    subject = "Добро пожаловать в ProFinder! 🎉"

    context = {
        'user': user,
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    }

    return send_email_notification(
        subject=subject,
        template_name='emails/welcome.html',
        context=context,
        recipient_list=[user.email]
    )


def send_provider_added_notification(provider):
    """Уведомление о добавлении нового специалиста (для администратора)"""
    from users.models import User
    admins = User.objects.filter(is_superuser=True)

    if not admins.exists():
        return False

    subject = f"🆕 Новый специалист: {provider.full_name}"

    context = {
        'provider': provider,
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'admin_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/admin/providers/provider/"
    }

    admin_emails = [admin.email for admin in admins if admin.email]
    if not admin_emails:
        return False

    return send_email_notification(
        subject=subject,
        template_name='emails/new_provider.html',
        context=context,
        recipient_list=admin_emails
    )