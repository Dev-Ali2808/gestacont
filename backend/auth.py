from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = "gestacont2026chaveultrasecretary"
ALGORITHM = "HS256"
EXPIRACAO = 30

def criar_token(dados: dict):
    payload = dados.copy()
    expira = datetime.utcnow() + timedelta(minutes=EXPIRACAO)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
