# from typing import Annotated
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DATABASE_NAME
import json
from controllers.document_controller import DocumentController
from controllers.email_controller import EmailController
import asyncio
import sys

from models.request_models import (
    CertificateRequest,
    SignDocumentRequest,
    UserRequest,
    RegisterUserRequest,
    Request,
)

# Conexão com o MongoDB
client = AsyncIOMotorClient(MONGODB_URI)

db = client[DATABASE_NAME]

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()
ALLOWED_ORIGINS = ["https://localhost:3000","https://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, # Permitir apenas o endereço do frontend
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # utilizar apenas os 2
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_disconnects(request: Request, call_next):
    import logging
    try:
        response = await call_next(request)
        return response
    except ConnectionResetError:
        logging.warning("A conexão foi fechada abruptamente pelo cliente.")
        return JSONResponse(content={"detail":"Conexão interrompida"}, status_code=499)  # Código 499: Client Closed Request


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
    from controllers.key_and_certificate_controller import KeyCertController

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
    private_key: UploadFile = File(...),
    user_id: str = Form(...),
    reason: str = Form(...),
    location: str = Form(...),
    positions: list | None = Form(None),
):
    from controllers.document_controller import DocumentController

    controller = DocumentController(db)
    try:
        request = SignDocumentRequest(
            file_content=await file.read(),
            private_key = await private_key.read(),
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


@app.post("/validate")
async def verify_document(
    file_content: UploadFile = File(...),
    file_hash: UploadFile = File(...),
):
    from controllers.document_controller import DocumentController

    controller = DocumentController(db)
    try:
        file_content_data = await file_content.read()
        file_hash_data = await file_hash.read()
        print(file_hash)
        print(file_hash_data)
        equal = await controller.verify_hash(file_content_data, file_hash_data)
        if not equal:
            return {
                "message": "Hashes não são iguais",
                "data": {
                    "validated": False,
                }
            }
        
        # file_hash_data = await file_hash.read()
        result = await controller.verify_document(file_content_data)
        if not result or not result.get("validated"):
            return {
                "message": "Não foi possível validar a integridade do documento.",
                "data": result,
            }
        return {
            "message": "Documento validado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Erro ao validar documento: " + str(e)
        )


@app.post("/login")
async def login(user: UserRequest):
    from controllers.user_controller import UserController

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
    from controllers.user_controller import UserController

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


@app.get("/get_keys")
async def get_keys(user_id: str):
    from controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        result = await controller.get_keys(user_id)
        if result.get("public_key") is None:
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
async def create_certificate(
    user_id: str = Form(...),
    private_key: UploadFile = File(...),
):
    from controllers.key_and_certificate_controller import KeyCertController

    controller = KeyCertController(db)
    try:
        private_key_data = await private_key.read()
        if not private_key_data:
            raise HTTPException(status_code=400, detail="Chave privada não encontrada")
        request = CertificateRequest(
            user_id=user_id,
            private_key=private_key_data,
        )
        result = await controller.create_certificate(request)
        return {
            "message": "Certificado criado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Erro ao criar certificado: {e}")


@app.post("/get_certificate")
async def get_certificate(request: Request):
    from controllers.key_and_certificate_controller import KeyCertController

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
    from controllers.key_and_certificate_controller import KeyCertController

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
async def send_email(
    user_id: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    emails: str = Form(...),  # Lista de emails como string separada por vírgulas
    attachment: UploadFile | None = File(None),  # O anexo é opcional
):
    from controllers.email_controller import EmailController

    controller = EmailController(db)
    try:
        # Converte a string de emails para lista
        email_list = emails.split(",")

        # Chama o controlador
        result = await controller.send_email(
            user_id=user_id,
            subject=subject,
            message=message,
            emails=email_list,
            attachment=attachment,  # Passa o objeto UploadFile diretamente
        )
        return {
            "message": "Email enviado com sucesso",
            "data": result,
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Erro ao enviar email")


document_controller = DocumentController(db)
email_controller = EmailController(db)

from tempfile import SpooledTemporaryFile

@app.post("/sign_document_and_send")
async def sign_document_and_send(
    file: UploadFile = File(...),
    private_key: UploadFile = File(...),
    user_id: str = Form(...),
    reason: str = Form(...),
    location: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...),
    emails: str = Form(...),  # Lista de emails como string separada por vírgulas
    positions: Optional[str] = Form(None),
):
    try:
        # Converter `positions` para lista (se aplicável)
        positions_list = json.loads(positions) if positions else None

        # Assinar o documento chamando a função existente
        sign_request = SignDocumentRequest(
            file_content=await file.read(),
            private_key=await private_key.read(),
            filename=file.filename,
            user_id=user_id,
            reason=reason,
            location=location,
            positions=positions_list,
        )
        signed_document = await document_controller.sign_document(sign_request)

        import base64
        # Decodificar o documento assinado em base64
        signed_pdf_data = base64.b64decode(signed_document["signed_document"])

        # Criar um arquivo temporário para o anexo
        temp_file = SpooledTemporaryFile()
        temp_file.write(signed_pdf_data)
        temp_file.seek(0)

        # Recriar o arquivo para o envio de e-mail
        attachment = UploadFile(
            filename=signed_document["filename"],
            file=temp_file,
        )

        # Enviar o e-mail com o documento assinado
        email_list = emails.split(",")
        await email_controller.send_email(
            user_id=user_id,
            subject=subject,
            message=message,
            emails=email_list,
            attachment=attachment,
        )

        return {
            "message": "Documento assinado e enviado com sucesso!",
            "data": {
                "filename": signed_document["filename"],
                "hash": signed_document["hash"],
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")
