from sqlalchemy import create_engine
from models import Base

engine = create_engine("sqlite:///gestacont.db")
Base.metadata.create_all(engine)
print("Banco de dados criado com sucesso!")
