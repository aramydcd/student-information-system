from .models import Notification

def create_notification(user, message):
    """
    Helper to create a notification for a user.
    """
    Notification.objects.create(
        user=user,
        message=message
    )
