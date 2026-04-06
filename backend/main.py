from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.connection import get_db
from database.models import Empresa
from backend.security import criptografar_senha, verificar_senha
from backend.auth import criar_token, verificar_token

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

class EmpresaSchema(BaseModel):
    nome: str
    email: str
    senha: str
    num_funcionarios: int

class LoginSchema(BaseModel):
    email: str
    senha: str

@app.get("/")
def home():
    return {"mensagem": "GestaCont online!"}

@app.post("/empresa/cadastrar")
def cadastrar_empresa(dados: EmpresaSchema, db: Session = Depends(get_db)):
    empresa = Empresa(
        nome=dados.nome,
        email=dados.email,
        senha=criptografar_senha(dados.senha),
        num_funcionarios=dados.num_funcionarios
    )
    db.add(empresa)
    db.commit()
    return {"mensagem": "Empresa cadastrada com sucesso!"}

@app.post("/login")
def login(dados: LoginSchema, db: Session = Depends(get_db)):
    empresa = db.query(Empresa).filter(Empresa.email == dados.email).first()
    if not empresa or not verificar_senha(dados.senha, empresa.senha):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    token = criar_token({"sub": empresa.email, "id": empresa.id})
    return {"token": token, "tipo": "bearer"}

@app.get("/painel")
def painel(token: str = Depends(oauth2)):
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    return {"mensagem": f"Bem vindo ao painel!", "email": payload["sub"]}
