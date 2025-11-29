from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, LeituraGPS
import asyncio
import json

router = APIRouter()

# Função auxiliar para pegar a última leitura do banco
def get_latest_position(db: Session):
    return db.query(LeituraGPS).order_by(LeituraGPS.timestamp_utc.desc()).first()

@router.websocket("/ws/rotas")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Frontend conectado ao WebSocket!")
    
    db = SessionLocal()
    last_id = 0
    
    try:
        while True:
            # Busca a última leitura salva pelo MQTT
            leitura = get_latest_position(db)
            
            if leitura:
                # Só envia se for uma leitura nova ou para garantir atualização
                # Aqui convertemos o objeto do banco para JSON
                data = {
                    "device_id": leitura.device_id,
                    "lat": leitura.latitude,
                    "lng": leitura.longitude,
                    "speed": leitura.speed_kmh,
                    "timestamp": leitura.timestamp_utc.isoformat()
                }
                
                # Envia para o Frontend
                await websocket.send_json(data)
                
            else:
                await websocket.send_text("Aguardando dados...")

            # Espera 1 segundo antes de checar o banco de novo
            # Isso simula o "Tempo Real" sem travar o servidor
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("❌ Frontend desconectou.")
    except Exception as e:
        print(f"Erro no WebSocket: {e}")
    finally:
        db.close()
