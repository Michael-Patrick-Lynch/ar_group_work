from typing import List
from twitchio.ext import commands
from datetime import datetime
from live_chat_message import LiveChatMessage
import requests
import os

class LiveChat(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.environ.get("TWITCH_ACCESS_TOKEN"),
            client_id=os.environ.get("TWITCH_CLIENT_ID"),    
            prefix='!',
            initial_channels=[os.environ.get("TWITCH_CHANNEL_NAME")],    
        )
        self.messages: List[LiveChatMessage] = []
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')  
        self.huggingface_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

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

            response = self.generate_huggingface_response(message.content)
            await message.channel.send(f"[AI] {response}")  

    def generate_huggingface_response(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are Chooble's friendly Twitch chat assistant named HelperBot. 
        Your personality: helpful, slightly silly but not too random, and always positive.
        Keep responses between 5-15 words, maintain context, and answer questions properly.
        
        User: {text}
        Assistant:"""
        
        payload = {
            "inputs": prompt,  
            "parameters": {
                "max_new_tokens": 100,  
                "temperature": 0.5,    
                "return_full_text": False,
                "repetition_penalty": 1.2  
            }
        }
        
        try:
            response = requests.post(
                self.huggingface_api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result[0]['generated_text'].strip()
        
        except Exception as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return "Whoops! My brain glitched. Try again?"

    def most_recent_message(self):
        return self.messages[-1] if self.messages else None

print("Starting the Bot: ")
live_chat = LiveChat()
live_chat.run()