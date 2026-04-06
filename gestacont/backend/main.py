from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import sys
sys.path.append("../database")
from connection import get_db
from models import Empresa

app = FastAPI()

class EmpresaSchema(BaseModel):
    nome: str
    email: str
    senha: str
    num_funcionarios: int

@app.post("/empresa/cadastrar")
def cadastrar_empresa(dados: EmpresaSchema, db: Session = Depends(get_db)):
    empresa = Empresa(
        nome=dados.nome,
        email=dados.email,
        senha=dados.senha,
        num_funcionarios=dados.num_funcionarios
    )
    db.add(empresa)
    db.commit()
    return {"mensagem": "Empresa cadastrada com sucesso!"}

@app.get("/")
def home():
    return {"mensagem": "GestaCont online!"}
