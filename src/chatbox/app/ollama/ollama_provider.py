import json
import logging
from dotenv import load_dotenv
import httpx
from pydantic import ValidationError
import os

from schema.schema import chatschema

logger = logging.getLogger()
load_dotenv()


async def chat(user_input: str, max_retries: int = 5, thinking: bool = False):
    url = os.getenv("OLLAMA_URL")
    logger.info("Ollama chat request received thinking=%s", thinking)
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
        "think": thinking,
        "stream": False
    }

    raw_text = None
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url=url, json=payload)
                response_json = response.json()
                logger.info("Ollama response received status=%s", response.status_code)
                if response.status_code == 503:
                    logger.warning("Ollama server busy")
                    return chatschema(chat="The server is busy right now", role="model")
                if response.status_code == 429:
                    logger.error("Ollama quota exceeded")
                    return chatschema(chat="Your quota exceded. Try again later", role="model")

                raw = response_json.get('message').get('content')
                raw = raw.replace("```json", "").replace("```", "").strip()
                
                data = json.loads(raw)

                #role=response_json.get('message').get('role')
                
                chat = chatschema(**data)


                conversation.append({
                    "role": chat.role,
                    "content": chat.chat
                })
                
                raw_text = response_json
                logger.debug("Ollama chat parsed role=%r chat=%s", chat.role, chat.chat)

                return chat
            except (ValidationError, json.JSONDecodeError) as e:
                 logger.warning(
                     "Ollama invalid model output on attempt %s/%s: %s",
                     attempt + 1,
                     max_retries,
                     e,
                 )
                
                 if attempt == max_retries - 1:
                     logger.exception("Ollama max retries reached while recovering malformed output")
                     raise RuntimeError("Max retries reached. Unable to recover malformed LLM output.") from e
                
                 logger.error("Ollama recovery prompt will be sent after parsing failure")
                
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
            except httpx.HTTPError as e:
                logger.exception(
                    "Ollama transport error on attempt %s/%s", attempt + 1, max_retries
                )
                if attempt == max_retries - 1:
                    raise RuntimeError("Max retries reached due to Ollama connectivity issues.") from e
            