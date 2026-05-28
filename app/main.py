from gemini.provider import chat
import asyncio

async def main():
    print("Chatbot started (type 'exit' to stop)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = await chat(user_input)
        print("Bot:", reply.chat)

if __name__ == "__main__":
    asyncio.run(main())


