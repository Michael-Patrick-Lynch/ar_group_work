class LiveChatMessage:
    def __init__(self, username: str, body: str, timestamp: str):
        self.username = username
        self.body = body
        self.timestamp = timestamp
    
    def __str__(self):
        return f"{self.timestamp} - {self.username}: {self.body}"