def notifications(request):
    unread_count = 0
    notifications_list = []

    if request.user.is_authenticated:
        unread_count = request.user.get_unread_count()
        notifications_list = request.user.get_notifications()

    return {
        'unread_count': unread_count,
        'notifications_list': notifications_list
    }