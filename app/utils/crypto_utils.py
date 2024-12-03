import bcrypt

def hashPassword(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def checkPassword(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())