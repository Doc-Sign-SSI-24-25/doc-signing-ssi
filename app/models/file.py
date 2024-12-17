from enum import Enum
from app.services.signer_services import sign_pdf
from app.models.signer import Signer

FileType = Enum("FileType", [("PDF", "pdf"), ("OFFICE", "office"), ("UNSUPPORTED", "unsupported")])

class File():
    _name:str
    _type:FileType
    _content:bytes    
     
    def __init__(self, name:str, content:bytes):
        file_type = self.get_file_type(content)
        if file_type == FileType.UNSUPPORTED:
            raise ValueError(f"Unsupported file type")
        self.name = name
        self.type = file_type
        self.content = content

    def __str__(self):
        return f"{self.name} ({self.path})"
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, value):
        self._type = value
    
    @property
    def content(self):
        return self._content
    
    @content.setter
    def content(self, value):
        self._content = value
    
    @staticmethod
    def get_file_type(file:bytes):
        if file[:4] == b'%PDF':
            return FileType.PDF
        else:
            return FileType.UNSUPPORTED
        
    def sign(self, signer: Signer, signature_position = (470, 840, 570, 640), reason = '', location = ''):   
        if self.type == FileType.PDF:
            signed_data = sign_pdf(self.content, signer, reason, location, signature_position)
            new_file_name =self.name.split('.')[0] + '-signed.pdf'
            return File(new_file_name, signed_data)        
        else:
            # sign_office(file, signer, reason, location)
            raise NotImplementedError("Office signing not implemented yet")
         