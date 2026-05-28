import json

import httpx
from dotenv import load_dotenv
import os
from schema.schema import chatschema
from pydantic import ValidationError
import logging

logging.basicConfig(
    filename='app.log',     # The name of the file
    filemode='w',           # 'a' to append logs, 'w' to overwrite the file every run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG     # Capture INFO, WARNING, ERROR, and CRITICAL
)

load_dotenv()
conversation = [{"role":"model", "parts":[{"text":"You are a science teacher and you will answer the students query about science. IT should be very concise, short and meaningful."}]},
                {"role":"user", "parts":[{"text":"What is the speed of light"}]},
                {"role":"model", "parts":[{"text":"The speed of light is 3 * 10 ^ 8"}]},
                {"role":"user", "parts":[{"text":"Who theorized the theory of Relativity?"}]},
                {"role":"model", "parts":[{"text":"Albert Einstein"}]},
                ]  # 🧠 memory


async def chat(user_input:str, max_retries:int=5):
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    header={
        "x-goog-api-key": os.getenv("GEMINI_API_KEY"),
        "Content-Type":"application/json"
    }
    conversation.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    payload = {
        "contents": conversation,
        
        "generationConfig": {
            "maxOutputTokens": 1000,
            "temperature": 0.7,
            "topP": 0.9,
            "responseMimeType": "application/json",
            "responseSchema": chatschema.model_json_schema(),
            "thinkingConfig": {
                "thinkingBudget": 0
        }

        }
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
        for attempt in range(max_retries):
            try:
                response= await client.post(url=url,headers=header,json=payload)
                response_json=response.json()
                if(response.status_code==503):
                    logging.warning("Server Busy")
                    return chatschema(chat="The server is busy right now",role="model")
                if(response.status_code==429):
                    logging.error("Quota Excedded.")
                    return chatschema(chat="Your quota exceded. Try again later",role="model")
                #print(response_json)


                reply=response_json.get('candidates')[0].get('content').get('parts')[0].get('text')
                data_dict = json.loads(reply)
                chat=data_dict.get('chat')
                role=data_dict.get('role')



                #token_count=response_json.get("usageMetadata").get("totalTokenCount")
                
                chat=chatschema(chat=chat,role=role)       


                conversation.append({
                    "role": role,
                    "parts": [{"text": reply}]
                })
                raw_text=response_json
                logging.debug("The chat displayed was %s and role was %r", chat, role)

                return chat
            except (ValidationError, json.JSONDecodeError) as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                
                if attempt == max_retries - 1:
                    raise RuntimeError("Max retries reached. Unable to recover malformed LLM output.") from e
                
                logging.error("The error was caught, which is %s", e)
                
                # Recovery step: Feed the error back to the LLM so it can fix its own mistake
                conversation.append({
                    "role": 'model',
                    "parts": [{"text": f"""
                            Your previous response was invalid.

                                ERROR:
                                {str(e)}

                                BAD OUTPUT:
                                {raw_text if 'raw_text' in locals() else "None"}

                                TASK:
                                Fix the output and return ONLY valid response. 
                                Return ONLY valid JSON matching this schema: {chatschema.model_json_schema()}                               

                                user_input:
                                {user_input}
                                        """}]
                })
                
    