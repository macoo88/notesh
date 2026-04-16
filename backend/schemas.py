from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    again_password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserVerify(BaseModel):
    username: str
    code: str

# What the user sends TO you (POST)
class NoteCreate(BaseModel):
    title: str
    content: str

# What you send BACK to the user (GET)
class NoteView(NoteCreate):
    id: int # Now the ID is included!

    class Config:
        from_attributes = True

