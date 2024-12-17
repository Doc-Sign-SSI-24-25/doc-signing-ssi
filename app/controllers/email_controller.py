from app.controllers.base_controller import BaseController
from app.models.request_models import EmailRequest
from motor.motor_asyncio import AsyncIOMotorClient

class EmailController(BaseController):
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        
    async def send_email(self, request: EmailRequest):
        pass
        # from app.models.signer import Signer
        
        