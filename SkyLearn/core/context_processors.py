from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        return {
            'unread_notifications': unread_notifications[:5],
            'unread_notifications_count': unread_notifications.count(),
            'all_notifications': Notification.objects.filter(user=request.user)[:10]
        }
    return {
        'unread_notifications': [],
        'unread_notifications_count': 0,
        'all_notifications': []
    }
