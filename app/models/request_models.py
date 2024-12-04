from pydantic import BaseModel, EmailStr
from fastapi import UploadFile

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
    user_id: str
    reason: str
    location: str
    file: UploadFile
    positions: list | None = None