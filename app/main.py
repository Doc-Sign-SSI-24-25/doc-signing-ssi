from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URI, DATABASE_NAME
from app.models.request_models import (
    CertificateRequest,
    KeyRequest,
    SignDocumentRequest,
    UserRequest,
    RegisterUserRequest
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

@app.get("/")
async def root():
    return {"message": "Ferramenta de Assinatura Digital de Documentos"}


@app.post("/create_certificate")
async def create_certificate(certificate: CertificateRequest):
    from app.controllers.key_and_certificate_controller import KeyCertController
    KeyCertController(db)
    return await KeyCertController.create_certificate(certificate)


@app.post("/create_key_and_certificate")
async def create_key_and_certificate(request: KeyRequest):
    from app.controllers.key_and_certificate_controller import KeyCertController
    KeyCertController(db)
    try:
        key = await KeyCertController.create_key(request)["private_key"]
        certificate = await KeyCertController.create_certificate(request)["certificate"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "message": "Chave e certificado criados com sucesso",
        "private_key": key,
        "certificate": certificate,
    }

@app.post("/sign_document")
async def sign_document(document: SignDocumentRequest):
    from app.controllers.document_controller import DocumentController
    DocumentController(db)
    return await DocumentController.sign_document(document)


@app.get("/verify_document")
async def verify_document():
    return {"message": "Documento verificado com sucesso"}


@app.post("/login")
async def login(user: UserRequest):
    from app.controllers.user_controller import UserController
    controller = UserController(db)
    try:
        id = await controller.login(user)
    except Exception as e:
        print(e)        
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "message": "Usuário logado com sucesso",
        "id": str(id),
    }

@app.post("/register")
async def create_user(user: RegisterUserRequest):
    from app.controllers.user_controller import UserController
    uc = UserController(db)
    user_id = await uc.register(user)
    
    return {"message": "Usuário criado com sucesso", "uid": str(user_id)}

@app.post("/create_key")
async def create_key(request: KeyRequest):
    from app.models.signer import Signer
    from app.utils.key_cert_utils import generate_key

    user = await db.users.find_one({"_id": ObjectId(request.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    signer = Signer(user["name"], user["email"])
    private_key = generate_key()
    signer.private_key = private_key
    filename = f"{signer.email.replace('.','_').lower()}-key.pem"
    await db.users.update_one(
        {"_id": ObjectId(request.user_id)}, {"$set": {"private_key": private_key}}
    )
    return {
        "message": "Chave criada com sucesso",
        "private_key": private_key,
        "filename": filename,
    }
