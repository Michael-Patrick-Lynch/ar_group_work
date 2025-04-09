import asyncio
from typing import List, Dict
from twitchio.ext import commands
from datetime import datetime
from live_chat_message import LiveChatMessage
import requests
import os
import re
from PIL import Image
from io import BytesIO
from text_to_speech import synthesize_speech_azure

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
        self.file_counter = 1
        self.possible_emotions = [
            "talking", "irish jig", "excited", "groovy", "frustrated", "sad", "proud", 
            "fight", "hat tip", "sing", "stinky", "catwalk" , "zombie", "siuu"
        ]

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

            detected_emotion = self.detect_emotion(message.content)
            print(f"Detected emotion: {detected_emotion}")

            await asyncio.sleep(1)

            image_urls = self.extract_image_urls(message.content)
            if image_urls:
                try:
                    caption = self.analyze_image(image_urls[0])
                    friendly_response = self.generate_huggingface_response(
                        f"Respond to this image description in a friendly, chatty way as a Twitch bot without using any emojis: {caption}"
                    )
                    response_text = f"[AI] {friendly_response} [{detected_emotion}]"
                    #await message.channel.send(response_text)
                    
                    self.save_response_files(friendly_response, detected_emotion)
                    
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    error_text = f"[AI] I saw an image but couldn't understand it! [{detected_emotion}]"
                    #await message.channel.send(error_text)
                    
                    self.save_response_files("I saw an image but couldn't understand it!", detected_emotion)
            else:
                response = self.generate_huggingface_response(message.content)
                response_text = f"[AI] {response} [{detected_emotion}]"
                #await message.channel.send(response_text)
                
                self.save_response_files(response, detected_emotion)

    def save_response_files(self, text: str, emotion: str):
        file_num = f"{self.file_counter:05d}"
        
        text_filename = f"{file_num}.txt"
        with open(text_filename, 'w') as f:
            f.write(emotion)
        
        audio_filename = f"{file_num}.mp3"
        synthesize_speech_azure(text, audio_filename)
        
        self.file_counter += 1

    def detect_emotion(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        emotion_list = ", ".join(self.possible_emotions)
        prompt = f"""Analyze the following message and select the most appropriate choice from this list: {emotion_list}.
        Only respond with the single most appropriate choice from the list.

        Message: "{text}"
        Choice:"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 20,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.huggingface_text_api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            emotion = result[0]['generated_text'].strip().lower()
            return emotion if emotion in self.possible_emotions else "excited"
            
        except Exception as e:
            print(f"Error detecting emotion: {str(e)}")
            return "excited"

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

    def generate_huggingface_response(self, text: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.huggingface_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""You are Chooble's friendly Twitch chat assistant named HelperBot. 
        Your personality: helpful, slightly silly but not too random, and always positive.
        Keep responses between 5-15 words, maintain context, and answer questions properly without using any emojis.
        When responding to images, be descriptive and engaging.
        
        User: {text}
        Assistant:"""
        
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