from django.conf import settings


def notifications(request):
    unread_count = 0
    notifications_list = []

    if request.user.is_authenticated:
        try:
            unread_count = request.user.get_unread_count()
            notifications_list = request.user.get_notifications()
        except AttributeError:
            # Если метод не существует, просто игнорируем
            pass

    return {
        'unread_count': unread_count,
        'notifications_list': notifications_list
    }