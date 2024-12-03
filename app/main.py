# from typing import Annotated
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
# from fastapi.exceptions import RequestValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URI, DATABASE_NAME

from app.models.request_models import (
    CertificateRequest,
    KeyRequest,
    SignDocumentRequest,
    UserRequest,
    RegisterUserRequest,
    Request
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


@app.post("/create_certificate")
async def create_certificate(certificate:CertificateRequest):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    return {
        "message": "Certificado criado com sucesso",
        "data": await controller.create_certificate(certificate),
    }


@app.post("/create_key_and_certificate")
async def create_key_and_certificate(request:KeyRequest):
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
async def sign_document(document: SignDocumentRequest):
    from app.controllers.document_controller import DocumentController

    controller = DocumentController(db)
    try:
        return {
            "message": "Documento assinado com sucesso",
            "data": await controller.sign_document(document),
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao assinar documento")


@app.get("/verify_document")
async def verify_document():
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/login")
async def login(user:UserRequest):
    from app.controllers.user_controller import UserController

    controller = UserController(db)
    try:
        return {
        "message": "Usuário logado com sucesso",
        "data" : await controller.login(user)
    }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail=str(e))
    

@app.post("/register")
async def create_user(user:RegisterUserRequest):
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

@app.post("/get_key")
async def get_key(request: Request):
    from app.controllers.key_and_certificate_controller import KeyCertController
    controller = KeyCertController(db)
    try:
        result = await controller.get_key(request)
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
        raise HTTPException(status_code=500, detail="Erro ao recuperar chave")

@app.post("/create_key")
async def create_key(request: KeyRequest):
    from app.controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.create_key(request)
        return {
            "message": "Chave criada com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao criar chave")
