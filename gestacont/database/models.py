from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    num_funcionarios = Column(Integer)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Funcionario(Base):
    __tablename__ = "funcionarios"
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    setor = Column(String)
    ativo = Column(Boolean, default=True)

class Tarefa(Base):
    __tablename__ = "tarefas"
    id = Column(Integer, primary_key=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    funcionario_id = Column(Integer, ForeignKey("funcionarios.id"))
    titulo = Column(String, nullable=False)
    descricao = Column(String)
    setor = Column(String)
    prazo = Column(DateTime)
    concluida = Column(Boolean, default=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
