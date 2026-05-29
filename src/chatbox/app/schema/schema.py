from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal, Optional

class MessageSchema(BaseModel):
    role: str
    content: str

class OllamaStreamChunk(BaseModel):
    model: str
    message: Optional[MessageSchema] = None
    done: bool


class chatschema(BaseModel):

    chat: str = Field(...,description="This is the response from the llm/user. Example: 'Hey how hot is the sun?", min_length=5, max_length=150)
    role: Literal["model","user","assistant"]


