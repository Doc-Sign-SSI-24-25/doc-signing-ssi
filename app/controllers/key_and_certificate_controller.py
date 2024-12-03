from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.controllers.base_controller import BaseController
from app.models.request_models import CertificateRequest, KeyRequest, Request


class KeyCertController(BaseController):
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def create_certificate(self, certificate: CertificateRequest):
        from app.models.signer import Signer
        from app.utils.key_cert_utils import generate_cert

        user = await self.db.users.find_one({"_id": ObjectId(certificate.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if not user.get("private_key"):
            raise HTTPException(status_code=400, detail="Chave pública não encontrada")
        signer = Signer(user["name"], certificate["email"], certificate["private_key"])
        try:
            cert = generate_cert(signer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        await self.db.users.update_one(
            {"_id": ObjectId(certificate.user_id)}, {"$set": {"certificate": cert}}
        )
        filename = f"{signer.email.replace('.','_').lower()}-cert.pem"
        return {
            "certificate": cert,
            "filename": filename,
        }

    async def create_key_and_certificate(self, request: KeyRequest):
        from app.models.signer import Signer
        from app.utils.key_cert_utils import generate_key, generate_cert

        user = await self.db.users.find_one({"_id": ObjectId(request.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        signer = Signer(user["name"], user["email"])
        private_key = generate_key()
        signer.private_key = private_key
        key_filename = f"{signer.email.replace('.','_').lower()}-key.pem"
        cert = generate_cert(signer)
        cert_filename = f"{signer.email.replace('.','_').lower()}-key-cert.pem"
        await self.db.users.update_one(
            {"_id": ObjectId(request.user_id)},
            {"$set": {"private_key": private_key, "certificate": cert}},
        )
        return {
            "private_key": private_key,
            "certificate": cert,
            "key_filename": key_filename,
            "cert_filename": cert_filename,
        }

    async def create_key(self, request: KeyRequest):
        from app.models.signer import Signer
        from app.utils.key_cert_utils import generate_key

        user = await self.db.users.find_one({"_id": ObjectId(request.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        signer = Signer(user["name"], user["email"])
        private_key = generate_key()
        filename = f"{signer.email.replace('.','_').lower()}-key.pem"
        await self.db.users.update_one(
            {"_id": ObjectId(request.user_id)}, {"$set": {"private_key": private_key}}
        )
        return {
            "private_key": private_key,
            "filename": filename,
        }
        
    async def get_key(self, request: Request):
        email = await self.db.users.find_one({"_id": ObjectId(request.user_id)}, {"email": 1,"_id": 0})
        if not email:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        private_key = await self.db.users.find_one({"_id": ObjectId(request.user_id)}, {"private_key": 1,"_id": 0})
        if not private_key:
            return {"private_key": None, "filename": None}
        return {"private_key": private_key["private_key"], "filename": f"{email['email'].replace('.','_').lower()}-key.pem"}
        
        
