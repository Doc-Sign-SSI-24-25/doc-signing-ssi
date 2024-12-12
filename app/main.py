# from typing import Annotated
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URI, DATABASE_NAME

from app.models.request_models import (
    SignDocumentRequest,
    UserRequest,
    RegisterUserRequest,
    Request,
)

# Conexão com o MongoDB
client = AsyncIOMotorClient(MONGODB_URI)

db = client[DATABASE_NAME]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # ["http://localhost:3000", "http://127.0.0.1:3000"],  # Trocar pela URL do frontend
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # utilizar apenas os 2
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


@app.get("/")
async def root():
    return {"message": "Ferramenta de Assinatura Digital de Documentos"}


@app.post("/create_key_and_certificate")
async def create_key_and_certificate(request: Request):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.create_key_and_certificate(request)
        return {
            "message": "Chave e certificado criados com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao criar chave e certificado")


@app.post("/sign_document")
async def sign_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    reason: str = Form(...),
    location: str = Form(...),
    positions: list | None = Form(None),
):
    from app.controllers.document_controller import DocumentController

    controller = DocumentController(db)
    try:
        request = SignDocumentRequest(
            file_content=await file.read(),
            filename=file.filename,
            user_id=user_id,
            reason=reason,
            location=location,
            positions=positions if positions else None,
        )
        result = await controller.sign_document(request)
        return {
            "message": "Documento assinado com sucesso",
            "data": {
                "filename": result["filename"],
                "signed_document": result["signed_document"],
                "hash": result["hash"],
            },
        }
    except Exception as e:
        print(e)
        print(e.with_traceback)
        raise HTTPException(
            status_code=500, detail=f"Erro 500. Erro ao assinar documento: {str(e)}"
        )


@app.get("/verify_document")
async def verify_document():
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/login")
async def login(user: UserRequest):
    from app.controllers.user_controller import UserController

    controller = UserController(db)
    try:
        return {
            "message": "Usuário logado com sucesso",
            "data": await controller.login(user),
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/register")
async def create_user(user: RegisterUserRequest):
    from app.controllers.user_controller import UserController

    controller = UserController(db)
    try:
        result = await controller.register(user)
        return {
            "message": "Usuário criado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao criar usuário")


@app.post("/get_keys")
async def get_keys(request: Request):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.get_keys(request)
        if result.get("private_key") is None:
            return {
                "message": "Chave não encontrada",
                "data": None,
            }
        return {
            "message": "Chave recuperada com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao recuperar chaves")


@app.post("/create_certificate")
async def create_certificate(certificate: Request):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.create_certificate(certificate)
        return {
            "message": "Certificado criado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Erro ao criar certificado: {e}")


@app.post("/get_certificate")
async def get_certificate(request: Request):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.get_certificate(request)
        if result.get("certificate") is None:
            return {
                "message": "Certificado não encontrado",
                "data": None,
            }
        return {
            "message": "Certificado recuperado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao recuperar certificado")


@app.post("/create_key")
async def create_key(request: Request):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.create_key_pair(request)
        return {
            "message": "Chave criada com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao criar chave")


@app.post("/send_email")
async def send_email(request: Request):
    from app.controllers.email_controller import EmailController

    controller = EmailController(db)
    try:
        result = await controller.send_email(request)
        return {
            "message": "Email enviado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao enviar email")


@app.post("/sign_document_and_send")
async def sign_document_and_send(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    reason: str = Form(...),
    location: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    emails: str = Form(...),
    positions: list | None = Form(None),
):
    from app.controllers.document_controller import DocumentController
    from app.models.request_models import EmailRequest
    from app.controllers.email_controller import EmailController

    controller = DocumentController(db)
    try:
        request = SignDocumentRequest(
            file_content=await file.read(),
            filename=file.filename,
            user_id=user_id,
            reason=reason,
            location=location,
            positions=positions if positions else None,
        )
        result = await controller.sign_document(request)
        request = EmailRequest(
            subject=subject,
            message=message,
            emails= emails.split(","),
            filename=result["filename"],
            attachment=result["signed_document"],
        )
        email_controller = EmailController(db)
        await email_controller.send_email(request)
        return {
            "message": "Documento assinado e enviado com sucesso",
            "data": {
                "filename": result["filename"],
                "signed_document": result["signed_document"],
            },
        }
    except Exception as e:
        print(e)
        print(e.with_traceback)
        raise HTTPException(
            status_code=500, detail=f"Erro 500. Erro ao assinar documento: {str(e)}"
        )