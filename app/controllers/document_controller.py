from base_controller import BaseController
from app.models.request_models import CertificateRequest, KeyRequest, SignDocumentRequest, UserRequest

class DocumentController(BaseController):
    def __init__(self, db):
        super().__init__(db)
        
    async def sign_document(self, document: SignDocumentRequest):
        from app.models.signer import Signer
        from app.utils.signer_utils import sign_pdf
        from bson.objectid import ObjectId
        from fastapi import HTTPException

        user = await self.db.users.find_one({"_id": ObjectId(document.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if not user.get("private_key"):
            raise HTTPException(status_code=400, detail="Chave privada não encontrada")
        signer = Signer(user["name"], user["email"], user["private_key"])
        try:
            doc = await document.file.read()
            signed_document = sign_pdf(doc, signer,document.reason, document.location, document.positions)
            return {"signed_document": signed_document, "filename": document.file.filename.replace(".pdf", "-signed.pdf")}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f'Erro ao assinar: {e}')
    
    async def verify_document(self):
        from fastapi import HTTPException
        raise HTTPException(status_code=500,detail="This feature is not implemented yet")