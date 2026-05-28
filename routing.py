import httpx
import asyncio
from dotenv import load_dotenv
import os


load_dotenv()
conversation = [{"role":"system", "parts":[{"text":"you are a science teacher and you will answer the students query about science."}]},
                {"role":"user", "parts":[{"text":"What is the speed of light"}]},
                {"role":"assistant", "parts":[{"text":"The speed of light is 3 * 10 ^ 8"}]}
                ]  # 🧠 memory


async def chat(user_input:str):
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
    header={
        "x-goog-api-key": os.getenv("GEMINI_API_KEY"),
        "Content-Type":"application/json"
    }
    conversation.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    payload = {
        "contents": conversation
    }
    # payload={
    #     "contents":[{
    #         "role":"user",
    #         "parts":[{
    #             "text": "Explain how AI works in a single paragraph."
    #         }]
    #     }]
    # }
    async with httpx.AsyncClient(timeout=20) as client:
        response= await client.post(url=url,headers=header,json=payload)
        response_json=response.json()

        reply=response_json.get('candidates')[0].get('content').get('parts')[0].get('text')

        conversation.append({
            "role": "assistant",
            "parts": [{"text": reply}]
        })
        return reply

async def main():
    print("Chatbot started (type 'exit' to stop)\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        reply = await chat(user_input)
        print("Bot:", reply)

if __name__ == "__main__":
    asyncio.run(main())


