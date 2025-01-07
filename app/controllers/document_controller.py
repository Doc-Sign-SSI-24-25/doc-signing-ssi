from app.controllers.base_controller import BaseController
from app.models.request_models import SignDocumentRequest
from motor.motor_asyncio import AsyncIOMotorClient

class DocumentController(BaseController):
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def sign_document(self, request: SignDocumentRequest):
        from app.models.signer import Signer
        from app.services.signer_services import sign_pdf
        from bson.objectid import ObjectId
        from fastapi import HTTPException
        user = await self.db.users.find_one({"_id": ObjectId(request.user_id)}, {"_id":0,"private_key": 1, "name": 1, "email": 1,"certificate": 1})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if not user.get("private_key"):
            raise HTTPException(status_code=400, detail="Chave privada não encontrada")
        if not user.get("certificate"):
            raise HTTPException(status_code=400, detail="Certificado não encontrado")
        signer = Signer(name=user["name"], email=user["email"], private_key=user["private_key"], cert_pem=user["certificate"])
        try:
            from app.utils.crypto_utils import create_hash
            signed_document = sign_pdf(request.file_content, signer,request.reason, request.location, request.positions)
            signed_document_hash = create_hash(signed_document)
            import base64
            file_base_64 = base64.b64encode(signed_document).decode('utf-8')
            return {"signed_document": file_base_64, "filename": request.filename.replace(".pdf", "-signed.pdf"), "hash": signed_document_hash}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Erro ao assinar: {e}')
    
    async def verify_document(self, file_content:bytes,file_hash:bytes):
        from app.utils.crypto_utils import verify_hash
        file_ok = verify_hash(file_content, file_hash.decode())
        return file_ok
        