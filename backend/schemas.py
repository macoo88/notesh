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

class UserView(BaseModel):
    id: int
    username: str
    email: str
    is_verified: bool

    class Config:
        from_attributes = True




class NoteCreate(BaseModel):
    title: str
    content: str
#class NoteCreate(BaseModel):
#    title: str
#    content: str
#    subject: str = "General"  # Giving it a default value
#    #topic: str = None         # This can be optional


# What you send BACK to the user (GET)
class NoteView(NoteCreate):
    id: int # Now the ID is included!

    class Config:
        from_attributes = True

class NoteSchema(BaseModel):
    title: str
    content: str

    class Config:
        from_attributes = True
