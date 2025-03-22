from typing import List
from openai import OpenAI
import requests
import json

client = OpenAI()

def generate_next_statement(developer_prompt, context):
    try:
        messages = construct_messages_parameter(developer_prompt, "give the next statement", context[len(context) - 5:])
        ChatCompletionObject = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
        )
        
        return ChatCompletionObject.choices[0].message.content
    except Exception as e:
        print("Error calling OpenAI: ", str(e))
        return "Error"

def construct_messages_parameter(developer_prompt:str = None,
                                user_prompt: str = None,
                                context: List[str] = None):
    messages = []
    if developer_prompt:
        messages.append({"role": "developer", "content": developer_prompt})
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})
    for message in context:
        messages.append({"role": "assistant", "content": [{ "type": "text", "text": message }]})
    return messages

def generate_text_openai(prompt: str) -> str:
    try:
        ChatCompletionObject = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"{prompt}"},
        ]
        )
        return ChatCompletionObject.choices[0].message.content
    except Exception as e:
        print("Error calling OpenAI: ", str(e))
        return "Error"

def generate_text_ollama(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "prompt": prompt,
        "model": "llama3.2",
        "temperature": 0.7,
        "max_tokens": 256
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    result_text = ""
    for line in response.iter_lines(decode_unicode=True):
        if line.strip():
            try:
                json_data = json.loads(line)
                if "response" in json_data:
                    result_text += json_data["response"]
            except json.JSONDecodeError:
                pass

    return result_text.strip()

def print_statements(statements: List[str]):
    for i, statement in enumerate(statements):
        print(f"========================Statement{i+1}========================")
        print(statement)
    print("==========================================================")