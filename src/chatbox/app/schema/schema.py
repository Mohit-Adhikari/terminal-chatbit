from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal


class chatschema(BaseModel):

    chat: str = Field(...,description="This is the response from the llm/user. Example: 'Hey how hot is the sun?", min_length=5, max_length=150)
    role: Literal["model","user","assistant"]


