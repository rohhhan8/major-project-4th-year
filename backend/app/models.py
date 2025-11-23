# backend/app/models.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    google_id: str

class Token(BaseModel):
    access_token: str
    token_type: str
