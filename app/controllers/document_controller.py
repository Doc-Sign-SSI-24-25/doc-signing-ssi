from controllers.base_controller import BaseController
from models.request_models import SignDocumentRequest
from motor.motor_asyncio import AsyncIOMotorClient


class DocumentController(BaseController):
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def sign_document(self, request: SignDocumentRequest):
        from models.signer import Signer
        from services.signer_services import sign_pdf
        from bson.objectid import ObjectId
        from fastapi import HTTPException

        user = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)},
            {"_id": 0, "name": 1, "email": 1, "certificate": 1},
        )
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if not user.get("certificate"):
            raise HTTPException(status_code=400, detail="Certificado não encontrado")
        signer = Signer(
            name=user["name"],
            email=user["email"],
            private_key=request.private_key,
            cert_pem=user["certificate"],
        )
        try:
            from utils.crypto_utils import create_hash

            signed_document = sign_pdf(
                request.file_content,
                signer,
                request.reason,
                request.location,
                request.positions,
            )
            signed_document_hash = create_hash(signed_document)
            import base64

            file_base_64 = base64.b64encode(signed_document).decode("utf-8")
            return {
                "signed_document": file_base_64,
                "filename": request.filename.replace(".pdf", "-signed.pdf"),
                "hash": signed_document_hash,
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao assinar: {e}")
    
    async def verify_hash(self, file_content: bytes, hash: bytes):
        """
        Verifica se o hash do conteúdo do arquivo é igual ao hash fornecido.
        """
        from utils.crypto_utils import create_hash

        file_hash = create_hash(file_content)

        return file_hash.encode() == hash

    async def verify_document(self, file_content: bytes):
        """
        Essa função busca todos os usuários que possuem certificado e
        verifica se o documento foi assinado por algum deles.
        """
        import services.signer_services as s
        try:
            cursor = self.db.users.find(
                {"certificate": {"$exists": True}},
                {"_id": 0, "certificate": 1, "email": 1},
            )
            trusted_signers = await cursor.to_list(None)
        except Exception as e:
            print("failed to get certificates")
            print(e)
            return {"validated": False, "error": str(e)}

        try:
            res = await s.verify_document(file_content, trusted_signers=trusted_signers)
        except Exception as e:
            print(e)
            res = {"validated": False, "error": str(e)}

        return res
