import asyncio
from typing import List
from twitchio.ext import commands
from datetime import datetime
from live_chat_message import LiveChatMessage
import requests
import os
import re
from PIL import Image
from io import BytesIO
import sys

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
        self.huggingface_text_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        self.huggingface_image_api_url = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
        emotions = ["happy", "sad", "angry", "bored", "goofy", "excited"]

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

            await asyncio.sleep(1)

            image_urls = self.extract_image_urls(message.content)
            if image_urls:
            
                try:
                    caption = self.analyze_image(image_urls[0])
                    friendly_response = self.generate_huggingface_response(
                        f"Respond to this image description in a friendly, chatty way as a Twitch bot: {caption}"
                    )

                    await message.channel.send(f"[AI] {friendly_response}")

                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    await message.channel.send("[AI] I saw an image but couldn't understand it!")

            else:
                response = self.generate_huggingface_response(message.content)
                await message.channel.send(f"[AI] {response}")  


    def extract_image_urls(self, text: str) -> List[str]:
        url_pattern = r'(https?:\/\/[^\s]+\.(?:jpg|jpeg|png|gif|webp))'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        return [url.split('?')[0] for url in urls]  

    def analyze_image(self, image_url: str) -> str:
        try:
            response = requests.get(
                image_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=5
            )
            response.raise_for_status()

            Image.open(BytesIO(response.content)).verify()

            hf_response = requests.post(
                self.huggingface_image_api_url,
                headers={"Authorization": f"Bearer {self.huggingface_api_key}"},
                data=response.content,
                timeout=10
            )
            hf_response.raise_for_status()
            return hf_response.json()[0]['generated_text']

        except Exception as e:
            print(f"Image error: {str(e)}")
            return "An image"

    def generate_huggingface_response(self, text: str, emotions = ["sad", "sad", "angry", "bored", "goofy", "excited"]) -> str:
        print("entering func", file=sys.stderr, flush=True)
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Pretend to be deppressed.
        Keep responses between 5-15 words, maintain context, and answer questions.
        At the end of every single response, pick the most appropriate emotion from this list (appropriate based on how someone would feel if they recieved a livechat like you did or saw the image you saw, be willing to express a full range of emotions. Don't just pick happy emotion every time! Be willing to express negative emotions)
        "sad", "angry", "bored", "goofy", "excited",
        and put that emotion into the response as $ <emotion> $ replacing <emotion> with the relvant emotion.
        When responding to images, be descriptive.
        
        User: {text}
        Assistant:"""
        print("testssss")
        print(prompt)
        
        payload = {
            "inputs": prompt,  
            "parameters": {
                "max_new_tokens": 100,  
                "temperature": 0.7,    
                "return_full_text": False,
                "repetition_penalty": 1.2  
            }
        }
        
        try:
            response = requests.post(
                self.huggingface_text_api_url,
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            return result[0]['generated_text'].strip()
        
        except Exception as e:
            print(f"Error calling Hugging Face API: {str(e)}")
            return "Whoops! My brain glitched. Try again?"
        

    
    
    def most_recent_message(self):
        return self.messages[-1] if self.messages else None

print("Starting the Bot...")
live_chat = LiveChat()
live_chat.run()