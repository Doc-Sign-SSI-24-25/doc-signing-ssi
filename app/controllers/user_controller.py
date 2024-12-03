from app.controllers.base_controller import BaseController
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from app.models.request_models import UserRequest

class UserController(BaseController):
    db: AsyncIOMotorClient = None
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
    
    async def register(self, userReq: UserRequest):
        user = await self.db.users.find_one({"email": userReq.email})
        print(user)
        if user:
            raise HTTPException(status_code=400, detail="Usuário já cadastrado")
        user = await self.db.users.insert_one(userReq.model_dump())
        return {"uid": str(user.inserted_id)}
    
    async def login(self, userReq: UserRequest):
        user = await self.db.users.find_one({"email": userReq.email, "password": userReq.password})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"uid": str(user["_id"])}