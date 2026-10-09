class NotificationNotFoundError(Exception):
    def __init__(self, notification_id: str):
        super().__init__(f"Notification {notification_id} not found")
