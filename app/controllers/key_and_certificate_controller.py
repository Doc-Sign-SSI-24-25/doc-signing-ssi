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
        from app.services.key_and_certificate_services import generate_key_pair

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
        """
        Função para gerar um certificado autoassinado para o usuário que fez a requisição.
        Os dados do Signer são buscados no banco de dados e utilizados para gerar o certificado.
        Se o utilizador não possuir o par de chaves privada e pública, a função lança um erro 400.
        """
        from app.models.signer import Signer
        from app.services.key_and_certificate_services import generate_certificate
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
            # Gera o certificado no formato PEM
            certificate = generate_certificate(signer)
        except Exception as e:
            print(e.with_traceback)
            print(e.__cause__)
            raise HTTPException(
                status_code=500, detail="Erro ao gerar certificado: " + str(e)
            )

        # Se não houver erro, atualiza o usuário no banco de dados com o certificado gerado
        await self.db.users.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$set": {"certificate": certificate}},
        )
        filename = f"{signer.email.replace('.','_').lower()}-cert.pem"

        # Retorna o certificado gerado e o nome do arquivo
        return {
            "certificate": certificate,
            "filename": filename,
        }

    async def create_key_and_certificate(self, request: Request):
        """
        Função que gera um par de chaves privada e pública RSA e um certificado autoassinado
        para o usuário que fez a requisição. As chaves e o certificado são armazenados no banco
        de dados e o nome dos arquivos são retornados na resposta.
        """
        from app.services.key_and_certificate_services import generate_key_and_certificate

        # Busca o usuário no banco de dados e retorna apenas os campos name, email
        user = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"_id": 0, "name": 1, "email": 1}
        )
        if not user:
            # Se o usuário não for encontrado, retorna um erro 404
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        name = user["name"]
        email = user["email"]
        private_key, public_key,certificate = generate_key_and_certificate(user_name=name)
        public_key_filename = f"{email.replace('.','_').lower()}-private-key.pem"
        private_key_filename = f"{email.replace('.','_').lower()}-public-key.pem"
        cert_filename = f"{email.replace('.','_').lower()}-key-cert.pem"

        await self.db.users.update_one(
            {"_id": ObjectId(request.user_id)},
            {
                "$set": {
                    "private_key": private_key,
                    "public_key": public_key,
                    "certificate": certificate,
                }
            },
        )
        return {
            "private_key": private_key,
            "certificate": certificate,
            "public_key_filename": public_key_filename,
            "private_key_filename": private_key_filename,
            "cert_filename": cert_filename,
        }

    async def get_keys(self, request: Request):
        email = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"email": 1, "_id": 0}
        )
        if not email:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        keys = await self.db.users.find_one(
            {"_id": ObjectId(request.user_id)}, {"private_key": 1, "public_key":1,"_id": 0}
        )
        if not keys:
            return {"private_key": None,"public_key":None, "public_key_filename": None,"private_key_filename": None,}
        return {
            "private_key": keys["private_key"],
            "public_key": keys["public_key"],
            "private_key_filename": f"{email['email'].replace('.','_').lower()}-private-key.pem",
            "public_key_filename": f"{email['email'].replace('.','_').lower()}-public-key.pem",
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