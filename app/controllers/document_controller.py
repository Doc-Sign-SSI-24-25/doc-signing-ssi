from app.controllers.base_controller import BaseController
from app.models.request_models import SignDocumentRequest
from motor.motor_asyncio import AsyncIOMotorClient

class DocumentController(BaseController):
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def sign_document(self, request: SignDocumentRequest):
        from app.models.signer import Signer
        from app.utils.signer_utils import sign_pdf
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
            signed_document = sign_pdf(request.file_content, signer,request.reason, request.location, request.positions)
            import base64
            file_base_64 = base64.b64encode(signed_document).decode('utf-8')
            return {"signed_document": file_base_64, "filename": request.filename.replace(".pdf", "-signed.pdf")}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Erro ao assinar: {e}')
    
    async def verify_document(self):
        from fastapi import HTTPException
        raise HTTPException(status_code=500,detail="This feature is not implemented yet")