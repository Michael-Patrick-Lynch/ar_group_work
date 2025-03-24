from typing import List
from twitchio.ext import commands
from datetime import datetime
from live_chat_message import LiveChatMessage

class LiveChat(commands.Bot):
    def __init__(self):
        super().__init__(
            token='oauth:eqyatj40wiqt7vm3p1f22ybn3c353f', 
            client_id='tp5puymwizeqsqsyyv22tcoq3to08v',     
            prefix='!',
            initial_channels=['chooble_']         
        )
        self.messages: List[LiveChatMessage] = []

    async def event_ready(self):
        print(f"\nConnected to the channel.")

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

print("Starting the Bot: ")
live_chat = LiveChat()
live_chat.run()