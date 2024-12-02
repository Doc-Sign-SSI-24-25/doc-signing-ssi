class User():
    _id: str
    name: str
    email: str
    password: str
    
    def __init__(self, name:str, email:str, password:str):
        self.name = name
        self.email = email
        self.password = password
    
    def get_id(self):
        return self._id
    