import httpx
import asyncio
from dotenv import load_dotenv
import os


load_dotenv()


async def chat():
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
    header={
        "x-goog-api-key": os.getenv("GEMINI_API_KEY"),
        "Content-Type":"application/json"
    }
    payload={
        "contents":[{
            "role":"user",
            "parts":[{
                "text": "Explain how AI works in a single paragraph."
            }]
        }]
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response= await client.post(url=url,headers=header,json=payload)
        response_json=response.json()

        print(response_json.get('candidates')[0].get('content').get('parts')[0].get('text'))

def main():
    asyncio.run(chat())
if __name__ == "__main__":
    main()