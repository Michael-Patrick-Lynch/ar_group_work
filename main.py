import asyncio
from text_generation import generate_next_statement
from prompt import Prompt
from live_chat import LiveChat 

async def main():
    live_chat = LiveChat()
    bot_task = asyncio.create_task(live_chat.start())

    try:

        statements = []
        msgs_already_responded_to = set()
        prompt = Prompt()

        for _ in range(20):
            livechat_messages = [msg for msg in live_chat.messages if msg not in msgs_already_responded_to]
            msgs_already_responded_to.update(livechat_messages)

            generated_text = generate_next_statement(prompt.body, statements, livechat_messages)
            statements.append(generated_text)
            print(f"======================\n{generated_text}\n======================")
            await asyncio.sleep(2)
    finally:
        await live_chat.close()
        await bot_task


if __name__ == "__main__":
    asyncio.run(main())
