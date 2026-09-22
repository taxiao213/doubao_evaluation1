class NotificationService:
    """通知存根：记录事件而非真实发送。"""

    def __init__(self):
        self.sent = []

    def notify(self, channel: str, message: str):
        self.sent.append((channel, message))
        return True
