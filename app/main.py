from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DATABASE_NAME

app = FastAPI()

# Conexão com o MongoDB
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]

@app.get("/")
async def root():
    return {"message": "Ferramenta de Assinatura Digital de Documentos"}