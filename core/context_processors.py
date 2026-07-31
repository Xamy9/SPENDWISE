
from .models import Notification


def notification_context(request):
    """
    Makes notifications available in every template.
    """

    if request.user.is_authenticated:

        latest_notifications = (
            Notification.objects
            .filter(user=request.user)
            .order_by("-created_at")[:5]
        )

        unread_notifications_count = (
            Notification.objects
            .filter(
                user=request.user,
                is_read=False,
            )
            .count()
        )

    else:

        latest_notifications = []

        unread_notifications_count = 0

    return {
        "latest_notifications": latest_notifications,
        "unread_notifications_count": unread_notifications_count,
    }