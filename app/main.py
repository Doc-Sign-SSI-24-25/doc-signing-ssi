from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
# from motor.motor_asyncio import AsyncIOMotorClient
# from app.config import MONGODB_URI, DATABASE_NAME

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Adicione isso após a criação do app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Substitua pela URL do seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão com o MongoDB
# client = AsyncIOMotorClient(MONGODB_URI)
# db = client[DATABASE_NAME]

class KeyRequest(BaseModel):
    name: str
    email: EmailStr

@app.get("/")
async def root():
    return {"message": "Ferramenta de Assinatura Digital de Documentos"}


@app.get("/create_key")
async def create_key():
    return {"message": "Chave criada com sucesso"}    


@app.get("/create_certificate")
async def create_certificate():
    return {"message": "Certificado criado com sucesso"}


@app.get("/sign_document")
async def sign_document():
    return {"message": "Documento assinado com sucesso"}


@app.get("/verify_document")
async def verify_document():
    return {"message": "Documento verificado com sucesso"}


@app.get("/login")
async def login():
    return {"message": "Login realizado com sucesso"}


@app.post("/create_key")
async def create_key(request: KeyRequest):
    print(request)
    if not request.name or not request.email:
        raise HTTPException(status_code=400, detail="Nome e email são obrigatórios")
    from app.models.signer import Signer
    from app.utils.key_cert_utils import generate_key

    signer = Signer(request.name, request.email)
    private_key = generate_key()
    signer.private_key = private_key
    filename = f"{signer.email.replace('.','_').lower()}-key.pem"
    return {
        "message": "Chave criada com sucesso",
        "private_key": private_key,
        "filename": filename,
    }
