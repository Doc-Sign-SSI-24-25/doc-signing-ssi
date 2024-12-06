from pydantic import BaseModel, EmailStr
from fastapi import UploadFile, Form, File

class Request(BaseModel):
    """
    A base request model that contains the user_id field.
    """
    user_id: str

class UserRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class SignDocumentRequest(BaseModel):
    file_content: bytes
    filename: str
    user_id: str 
    reason: str 
    location: str
    positions: list | None = None