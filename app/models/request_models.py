from pydantic import BaseModel, EmailStr

class UserRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class KeyRequest(BaseModel):
    user_id: str

class CertificateRequest(BaseModel):
    user_id: str

class SignDocumentRequest(BaseModel):
    user_id: str
    reason: str
    location: str
    document: str
    filename: str
    position: list | None = None