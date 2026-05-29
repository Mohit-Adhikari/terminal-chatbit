import logging
import os
from typing import AsyncIterator
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, Field
from typing import Optional

logger = logging.getLogger(__name__)
load_dotenv()

# --- Pydantic Schemas ---
class MessageSchema(BaseModel):
    role: str
    content: str

class OllamaStreamChunk(BaseModel):
    model: str
    message: Optional[MessageSchema] = None
    done: bool

# --- Chat Function ---
async def chat(user_input: str, max_retries: int = 5, thinking: bool = False) -> AsyncIterator[str]:
    url = os.getenv("OLLAMA_URL")
    if not url:
        logger.error("OLLAMA_URL environment variable is missing.")
        return

    logger.info("Ollama chat request received thinking=%s", thinking)
    
    conversation = [
        {
            "role": "system",
            "content": "You are a science teacher. Answer student science questions in concise, clear plain text. Do not return JSON or code blocks."
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    payload = {
        "model": "gemma4:31b-cloud",
        "messages": conversation,
        "think": thinking,
        "stream": True
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            async with client.stream("POST", url=url, json=payload) as response:
                response.raise_for_status() # Catch 4xx/5xx errors early
                
                buffer=""
                async for line in response.aiter_lines():
                    if not line or not line.strip():
                        continue
                    
                    try:
                        # Pydantic v2 optimized method: parses and validates string directly
                        chunk = OllamaStreamChunk.model_validate_json(line)
                        
                        if chunk.message and chunk.message.content:
                            # Clean markdown if needed
                            cleaned_content = chunk.message.content.replace("```json", "").replace("```", "")
                            buffer+=cleaned_content
                            yield cleaned_content

                        if chunk.done:
                            logger.info("The chat response was %s",buffer)
                            break

                    except ValidationError as e:
                        logger.warning("Dropped malformed streaming chunk: %s", e)
                        continue # Safely skip bad chunks instead of crashing the stream

        except httpx.HTTPStatusError as e:
            logger.error("HTTP error occurred: %s", e)
            yield "The server encountered an error processing your request."
        except httpx.RequestError as e:
            logger.error("Network error occurred: %s", e)
            yield "Failed to reach the AI server."