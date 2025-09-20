from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False)
        all_notifications = Notification.objects.filter(user=request.user)[:10]  # limit to 10 latest
        # if unread.count() > 5:

        return {
            "unread_count": unread.count(),
            "unread_notifications": unread,
            "all_notifications": all_notifications,
        }
    return {
        "unread_count": 0,
        "unread_notifications": [],
        "all_notifications": []
    }
