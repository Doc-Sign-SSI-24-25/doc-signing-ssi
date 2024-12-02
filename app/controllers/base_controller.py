from abc import abstractmethod
from motor.motor_asyncio import AsyncIOMotorClient

class BaseController():
    """
    A Base controller class that defines the basic methods that a controller should have
    """
    def __init__(self, db: AsyncIOMotorClient):
        pass
    
    def findOne(self, query: dict):
        pass
    
    @abstractmethod
    def findOneById(self, id: str):
        pass
    
    @abstractmethod
    def create(self, data: dict):
        pass
    
    @abstractmethod
    def update(self, id, data: dict):
        pass
    
    @abstractmethod
    def delete(self, id:dict):
        pass
    
    
    
    