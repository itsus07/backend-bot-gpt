from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CreateConversationRequest(BaseModel):
    message: str
    type: str = "text"

class MessageRequest(BaseModel):
    message: str

class ConversationResponse(BaseModel):
    conversation_id: str
    reply: str

class MessageResponse(BaseModel):
    reply: str

class ConversationDetail(BaseModel):
    conversation_id: str
    title: str
    update_date: datetime

    class Config:
        from_attributes = True

class FullConversationDetail(BaseModel):
    conversation_id: str
    title: str
    messages: List[dict]