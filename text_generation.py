from typing import List
from openai import OpenAI

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

def print_statements(statements: List[str]):
    for i, statement in enumerate(statements):
        print(f"========================Statement{i+1}========================")
        print(statement)
    print("==========================================================")