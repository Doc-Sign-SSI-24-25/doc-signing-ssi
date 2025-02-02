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

class CertificateRequest(BaseModel):
    user_id: str
    private_key: bytes

class SignDocumentRequest(BaseModel):
    file_content: bytes
    private_key: bytes
    filename: str
    user_id: str 
    reason: str 
    location: str
    positions: list | None = None

class EmailRequest(BaseModel):
    user_id: str
    recipient_email: str
    subject: str
    message: str
    attachment_filename: str | None = None
    attachment_content: bytes | None = None