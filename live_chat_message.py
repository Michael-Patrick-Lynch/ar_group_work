from datetime import datetime

class LiveChatMessage:
    def __init__(self, username: str, body: str, timestamp: datetime):
        self.username = username
        self.body = body
        self.timestamp = timestamp