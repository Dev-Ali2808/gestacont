from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.connection import get_db
from database.models import Empresa, Funcionario, Tarefa
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

class FuncionarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    setor: Optional[str] = None

class TarefaSchema(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    setor: Optional[str] = None
    prazo: Optional[datetime] = None
    funcionario_id: int

def get_empresa_atual(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    payload = verificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    empresa = db.query(Empresa).filter(Empresa.email == payload["sub"]).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")
    return empresa

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
def cadastrar_funcionario(dados: FuncionarioSchema, db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    funcionario = Funcionario(
        empresa_id=empresa.id,
        nome=dados.nome,
        email=dados.email,
        senha=criptografar_senha(dados.senha),
        setor=dados.setor
    )
    db.add(funcionario)
    db.commit()
    return {"mensagem": f"Funcionario {dados.nome} cadastrado!"}

@app.get("/funcionarios")
def listar_funcionarios(db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    funcionarios = db.query(Funcionario).filter(Funcionario.empresa_id == empresa.id).all()
    return [{"id": f.id, "nome": f.nome, "email": f.email, "setor": f.setor, "ativo": f.ativo} for f in funcionarios]

@app.post("/tarefa/criar")
def criar_tarefa(dados: TarefaSchema, db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    tarefa = Tarefa(
        empresa_id=empresa.id,
        funcionario_id=dados.funcionario_id,
        titulo=dados.titulo,
        descricao=dados.descricao,
        setor=dados.setor,
        prazo=dados.prazo
    )
    db.add(tarefa)
    db.commit()
    return {"mensagem": f"Tarefa '{dados.titulo}' criada com sucesso!"}

@app.get("/tarefas")
def listar_tarefas(db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    tarefas = db.query(Tarefa).filter(Tarefa.empresa_id == empresa.id).all()
    return [{"id": t.id, "titulo": t.titulo, "setor": t.setor, "prazo": t.prazo, "concluida": t.concluida, "funcionario_id": t.funcionario_id} for t in tarefas]

@app.patch("/tarefa/{tarefa_id}/concluir")
def concluir_tarefa(tarefa_id: int, db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id, Tarefa.empresa_id == empresa.id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa nao encontrada")
    tarefa.concluida = True
    db.commit()
    return {"mensagem": f"Tarefa '{tarefa.titulo}' concluida!"}
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    funcionarios = db.query(Funcionario).filter(Funcionario.empresa_id == empresa.id).all()
    
    relatorio = []
    for f in funcionarios:
        total = db.query(Tarefa).filter(Tarefa.funcionario_id == f.id).count()
        concluidas = db.query(Tarefa).filter(Tarefa.funcionario_id == f.id, Tarefa.concluida == True).count()
        pendentes = total - concluidas
        desempenho = round((concluidas / total * 100), 1) if total > 0 else 0
        
        relatorio.append({
            "funcionario": f.nome,
            "setor": f.setor,
            "total_tarefas": total,
            "concluidas": concluidas,
            "pendentes": pendentes,
            "desempenho": f"{desempenho}%"
        })
    
    return {
        "empresa": empresa.nome,
        "total_funcionarios": len(funcionarios),
        "relatorio": relatorio
    }

@app.get("/tarefas/atrasadas")
def tarefas_atrasadas(db: Session = Depends(get_db), empresa: Empresa = Depends(get_empresa_atual)):
    agora = datetime.utcnow()
    atrasadas = db.query(Tarefa).filter(
        Tarefa.empresa_id == empresa.id,
        Tarefa.concluida == False,
        Tarefa.prazo < agora
    ).all()
    
    return {
        "total_atrasadas": len(atrasadas),
        "tarefas": [{"id": t.id, "titulo": t.titulo, "prazo": t.prazo, "funcionario_id": t.funcionario_id} for t in atrasadas]
    }
