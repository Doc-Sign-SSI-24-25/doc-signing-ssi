from app.models.file import File

def import_file(path:str) -> File:
    with open(path, 'rb') as f:
        file = File(f.name, f.read())
    return file

def import_key(path:str) -> bytes:
    with open(path, 'rb') as f:
        key = f.read()
    return key

def import_cert(path:str) -> bytes:
    with open(path, 'rb') as f:
        cert = f.read()
    return cert

def export_file(file:File, path:str):
    with open(path, 'wb') as f:
        f.write(file.content)

def export_key(key:bytes, path:str):
    with open(path, 'wb') as f:
        f.write(key)

def export_cert(cert:bytes, path:str):
    with open(path, 'wb') as f:
        f.write(cert)
