from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

# Importando do seu arquivo database.py
from .core/database import get_db, Route, LeituraGPS, salvar_leitura

app = FastAPI()

# Configuração de CORS (Para o Frontend acessar o Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, coloque o domínio da AWS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DADOS (Pydantic) ---
class PresenceCreate(BaseModel):
    user_name: str
    route_id: str
    device_id: str

# --- ENDPOINTS ---

@app.get("/routes")
def get_routes(db: Session = Depends(get_db)):
    """
    Retorna todas as rotas cadastradas no banco para preencher a Dashboard
    """
    routes = db.query(Route).all()
    # Converte para o formato que o frontend espera
    return [r.to_dict() for r in routes]

@app.post("/presence")
def mark_presence(data: PresenceCreate, db: Session = Depends(get_db)):
    """
    Salva a presença do aluno. (Aqui você criaria uma tabela 'Presence' no futuro)
    Por enquanto, vamos apenas logar ou salvar simulado.
    """
    print(f"Presença marcada: {data.user_name} na rota {data.route_id}")
    # TODO: Criar tabela de presença no database.py e salvar aqui
    return {"message": "Presença confirmada com sucesso"}

# O endpoint de simulação apenas inicia o script, ou você roda o script separado.