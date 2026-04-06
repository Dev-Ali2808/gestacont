from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.connection import get_db
from database.models import Empresa, Funcionario
from backend.security import criptografar_senha, verificar_senha
from backend.auth import criar_token, verificar_token

app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Schemas
class EmpresaSchema(BaseModel):
    nome: str
    email: str
    senha: str
    num_funcionarios: int

class LoginSchema(BaseModel):
    email: str
    senha: str

class FuncionarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    setor: Optional[str] = None

# Função que pega empresa logada
def get_empresa_atual(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    empresa = db.query(Empresa).filter(Empresa.email == payload["sub"]).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    return empresa

# Rotas
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
def painel(empresa: Empresa = Depends(get_empresa_atual)):
    return {"mensagem": f"Bem vindo, {empresa.nome}!"}

@app.post("/funcionario/cadastrar")
def cadastrar_funcionario(
    dados: FuncionarioSchema,
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_empresa_atual)
):
    funcionario = Funcionario(
        empresa_id=empresa.id,
        nome=dados.nome,
        email=dados.email,
        senha=criptografar_senha(dados.senha),
        setor=dados.setor
    )
    db.add(funcionario)
    db.commit()
    return {"mensagem": f"Funcionario {dados.nome} cadastrado com sucesso!"}

@app.get("/funcionarios")
def listar_funcionarios(
    db: Session = Depends(get_db),
    empresa: Empresa = Depends(get_empresa_atual)
):
    funcionarios = db.query(Funcionario).filter(
        Funcionario.empresa_id == empresa.id
    ).all()
    return [{"id": f.id, "nome": f.nome, "email": f.email, "setor": f.setor, "ativo": f.ativo} for f in funcionarios]
