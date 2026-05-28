import json
import logging

import httpx
from pydantic import ValidationError

from schema.schema import chatschema

logging.basicConfig(
    filename='app.log',     # The name of the file
    filemode='w',           # 'a' to append logs, 'w' to overwrite the file every run
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG     # Capture INFO, WARNING, ERROR, and CRITICAL
)

async def chat(user_input:str, max_retries:int=5):
    url="http://localhost:11434/api/chat"
    conversation = [
    {
        "role": "system",
        "content": "You are a science teacher and you will answer the students query about science. IT should be very concise, short and meaningful.Return ONLY valid response matching this schema: chat= str min_length=5, max_length=150), role: Literal between model,user,assistant"
    },

    ]

    conversation.append({
        "role":"user",
        "content":user_input
    })   


    payload = {
        "model": "gemma4:31b-cloud",
        "messages": conversation,
        "think": False,
        "stream": False
    }



    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(max_retries):
            try:
                response= await client.post(url=url,json=payload)
                response_json=response.json()
                if(response.status_code==503):
                    logging.warning("Server Busy")
                    return chatschema(chat="The server is busy right now",role="model")
                if(response.status_code==429):
                    logging.error("Quota Excedded.")
                    return chatschema(chat="Your quota exceded. Try again later",role="model")

                raw=response_json.get('message').get('content')
                raw = raw.replace("```json", "").replace("```", "").strip()
                print(type(raw))
                
                data=json.loads(raw)
                print(data)

                #role=response_json.get('message').get('role')
                
                chat=chatschema(**data)       


                conversation.append({
                    "role": chat.role,
                    "content": chat.chat
                })
                print(conversation)
                raw_text=response_json
                logging.debug("The chat displayed was %s and role was %r", chat.chat, chat.role)

                return chat
            except (ValidationError, json.JSONDecodeError) as e:
                 print(f"Attempt {attempt + 1} failed with error: {e}")
                
                 if attempt == max_retries - 1:
                     raise RuntimeError("Max retries reached. Unable to recover malformed LLM output.") from e
                
                 logging.error("The error was caught, which is %s", e)
                
                 # Recovery step: Feed the error back to the LLM so it can fix its own mistake
                 conversation.append({
                     "role": 'user',
                     "content": f"""
                            Your previous response was invalid.

                                ERROR:
                                 {str(e)}

                                 BAD OUTPUT:
                                 {raw_text if 'raw_text' in locals() else "None"}

                                 TASK:
                                 Fix the output and return ONLY valid response. 
                                 Return ONLY valid response matching this schema: {chatschema.model_json_schema()}                               

                                 user_input:
                                 {user_input}
                                         """})
            