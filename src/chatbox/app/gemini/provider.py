import json
import logging
import os

import httpx
from dotenv import load_dotenv
from schema.schema import chatschema
from pydantic import ValidationError

logger = logging.getLogger(__name__)

load_dotenv()
conversation = [{"role":"model", "parts":[{"text":"You are a science teacher and you will answer the students query about science. IT should be very concise, short and meaningful."}]},
                {"role":"user", "parts":[{"text":"What is the speed of light"}]},
                {"role":"model", "parts":[{"text":"The speed of light is 3 * 10 ^ 8"}]},
                {"role":"user", "parts":[{"text":"Who theorized the theory of Relativity?"}]},
                {"role":"model", "parts":[{"text":"Albert Einstein"}]},
                ]  # 🧠 memory


async def chat(user_input: str, max_retries: int = 5, thinking: bool = False):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    header = {
        "x-goog-api-key": os.getenv("GEMINI_API_KEY"),
        "Content-Type": "application/json"
    }
    logger.info("Gemini chat request received thinking=%s", thinking)
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
            "thinkingBudget": 1024 if thinking else 0
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
    raw_text = None
    async with httpx.AsyncClient(timeout=20) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(url=url, headers=header, json=payload)
                response_json = response.json()
                logger.info("Gemini response received status=%s", response.status_code)
                if response.status_code == 503:
                    logger.warning("Gemini server busy")
                    return chatschema(chat="The server is busy right now", role="model")
                if response.status_code == 429:
                    logger.error("Gemini quota exceeded")
                    return chatschema(chat="Your quota exceded. Try again later", role="model")
                #print(response_json)


                reply = response_json.get('candidates')[0].get('content').get('parts')[0].get('text')
                data_dict = json.loads(reply)
                chat = data_dict.get('chat')
                role = data_dict.get('role')



                #token_count=response_json.get("usageMetadata").get("totalTokenCount")
                
                chat = chatschema(chat=chat, role=role)


                conversation.append({
                    "role": role,
                    "parts": [{"text": reply}]
                })
                raw_text = response_json
                logger.debug("Gemini chat parsed role=%r chat=%s", role, chat.chat)

                return chat
            except (ValidationError, json.JSONDecodeError) as e:
                logger.warning(
                    "Gemini invalid model output on attempt %s/%s: %s",
                    attempt + 1,
                    max_retries,
                    e,
                )
                
                if attempt == max_retries - 1:
                    logger.exception("Gemini max retries reached while recovering malformed output")
                    raise RuntimeError("Max retries reached. Unable to recover malformed LLM output.") from e
                
                logger.error("Gemini recovery prompt will be sent after parsing failure")
                
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
            except httpx.HTTPError as e:
                logger.exception(
                    "Gemini transport error on attempt %s/%s", attempt + 1, max_retries
                )
                if attempt == max_retries - 1:
                    raise RuntimeError("Max retries reached due to Gemini API connectivity issues.") from e
                
    