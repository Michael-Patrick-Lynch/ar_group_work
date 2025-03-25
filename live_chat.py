from typing import List
from twitchio.ext import commands
from datetime import datetime
from live_chat_message import LiveChatMessage
import os

class LiveChat(commands.Bot):
    def __init__(self):
        print("Connecting to Twitch livechat: ")
        super().__init__(
            token=os.environ.get("TWITCH_ACCESS_TOKEN"),
            client_id=os.environ.get("TWITCH_CLIENT_ID"),
            prefix='!',
            initial_channels=[os.environ.get("TWITCH_CHANNEL_NAME")],  
        )
        self.messages: List[LiveChatMessage] = []

    async def event_ready(self):
        print("Connected to the channel")

    async def event_message(self, message):
        if message.echo or not message.author:
            return 
        
        live_chat_message = LiveChatMessage(
            username=message.author.name,
            body=message.content,
            timestamp=datetime.now()
        )

        if live_chat_message not in self.messages:
            self.messages.append(live_chat_message)
            print(f"{live_chat_message.timestamp} - {live_chat_message.username}: {live_chat_message.body}")

    def most_recent_message(self):
        return self.messages[-1] if self.messages else None
