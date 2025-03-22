from typing import List
from live_chat_message import LiveChatMessage

# Holds all of the messages that are obtained from Twitch
class LiveChat:
    def __init__(self):
        self.messages: List[LiveChatMessage] = []

    # TODO: Call the Twitch API, convert all messages to LiveChatMessage objects,
    # And then add the ones that are not already in self.messages to self.messages
    def add_messages_from_source(self):
        pass
        
    
    def most_recent_message(self):
        return self.messages[-1] if len(self.messages) >= 1 else None
    