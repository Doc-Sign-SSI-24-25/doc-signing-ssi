from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.controllers.base_controller import BaseController
from app.models.request_models import  Request


class KeyCertController(BaseController):
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def create_key_pair(self, request: Request):
        from app.models.signer import Signer
        from app.utils.key_cert_utils import generate_key_pair

        user = await self.db.users.find_one({"_id": ObjectId(request.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        signer = Signer(user["name"], user["email"])
        private_key, public_key = generate_key_pair()
        filename_private = f"{signer.email.replace('.','_').lower()}-private-key.pem"
        filename_public = f"{signer.email.replace('.','_').lower()}-public-key.pem"
        await self.db.users.update_one(
            {"_id": ObjectId(request.user_id)},
            {"$set": {"private_key": private_key, "public_key": public_key}},
        )
        return {
            "private_key": private_key,
            "public_key": public_key,
            "filename_public": filename_private,
            "filename_private": filename_public,
        }

    async def create_certificate(self, request: Request):
        from app.models.signer import Signer
        from app.utils.key_cert_utils import generate_cert
        from fastapi import HTTPException
        from bson import ObjectId

        # Busca o usuário no banco de dados e retorna apenas os campos name, email, private_key
        user = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)},
            {"name": 1, "email": 1, "private_key": 1, "public_key": 1},
        )
        if not user:
            # Se o usuário não for encontrado, retorna um erro 404
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if not user.get("private_key"):
            # Se o usuário não tiver chave privada, retorna um erro 400
            raise HTTPException(
                status_code=400, detail="A Chave do utilizador não foi encontrada"
            )

        # Cria um objeto Signer com os dados do usuário
        signer = Signer(
            user["name"], user["email"], user["private_key"], user["public_key"]
        )
        try:
            # Gera o certificado
            cert = generate_cert(signer)
            from cryptography.hazmat.primitives import serialization

            encoded_certificate = cert.public_bytes(serialization.Encoding.PEM)
        except Exception as e:
            print(e.with_traceback)
            print(e.__cause__)
            raise HTTPException(
                status_code=500, detail="Erro ao gerar certificado: " + str(e)
            )

        # Se não houver erro, atualiza o usuário no banco de dados com o certificado gerado
        await self.db.users.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": {"certificate": encoded_certificate}},
        )
        filename = f"{signer.email.replace('.','_').lower()}-cert.pem"

        # Retorna o certificado gerado e o nome do arquivo
        return {
            "certificate": encoded_certificate,
            "filename": filename,
        }

    async def create_key_and_certificate(self, request: Request):
        from app.models.signer import Signer
        from app.utils.key_cert_utils import generate_key_pair, generate_cert

        # Busca o usuário no banco de dados e retorna apenas os campos name, email
        user = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"_id": 0, "name": 1, "email": 1}
        )
        if not user:
            # Se o usuário não for encontrado, retorna um erro 404
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        signer = Signer(user["name"], user["email"])
        private_key, public_key = generate_key_pair()
        signer.private_key = private_key
        signer.public_key = public_key
        public_key_filename = f"{signer.email.replace('.','_').lower()}-private-key.pem"
        private_key_filename = f"{signer.email.replace('.','_').lower()}-public-key.pem"
        cert = generate_cert(signer)
        cert_filename = f"{signer.email.replace('.','_').lower()}-key-cert.pem"
        from cryptography.hazmat.primitives import serialization

        encoded_certificate = cert.public_bytes(serialization.Encoding.PEM)
        await self.db.users.update_one(
            {"_id": ObjectId(request.user_id)},
            {
                "$set": {
                    "private_key": private_key,
                    "public_key": public_key,
                    "certificate": encoded_certificate,
                }
            },
        )
        return {
            "private_key": private_key,
            "certificate": encoded_certificate,
            "public_key_filename": public_key_filename,
            "private_key_filename": private_key_filename,
            "cert_filename": cert_filename,
        }

    async def get_key(self, request: Request):
        email = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"email": 1, "_id": 0}
        )
        if not email:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        private_key = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"private_key": 1, "_id": 0}
        )
        if not private_key:
            return {"private_key": None, "filename": None}
        return {
            "private_key": private_key["private_key"],
            "filename": f"{email['email'].replace('.','_').lower()}-key.pem",
        }

    async def get_certificate(self, request: Request):
        email = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"email": 1, "_id": 0}
        )
        if not email:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        certificate = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"certificate": 1, "_id": 0}
        )
        if not certificate:
            return {"certificate": None, "filename": None}
        return {
            "certificate": certificate["certificate"],
            "filename": f"{email['email'].replace('.','_').lower()}-cert.pem",
        }
        
    async def get_public_key(self, request:Request):
        pass

