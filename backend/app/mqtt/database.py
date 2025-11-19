from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# CONFIGURAÇÃO DO BANCO

DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "projeto_gps"
DB_DRIVER = "postgresql+psycopg2"
DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# TABELA LeituraGPS
class LeituraGPS(Base):
    __tablename__ = "leituras_gps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    speed_kmh = Column(Float)
    course_deg = Column(Float)
    num_satellites = Column(Integer)
    hdop = Column(Float)


# Cria as tabelas se não existirem,  importante garantir que a tabela exista antes de inserir.
Base.metadata.create_all(engine)

# FUNÇÃO AUXILIAR PARA SALVAR UMA LEITURA JSON
def salvar_leitura(json_data: dict):
    # Cria uma nova sessão a cada chamada da função para gerenciamento seguro
    session = SessionLocal()
    try:
        device_id = json_data["device"]["id"]

        gps = json_data["gps"]

        # Tratamento do timestamp
        timestamp_str = gps.get("timestamp_utc")
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        location = gps.get("location", {})
        latitude = location.get("lat")
        longitude = location.get("lon") or location.get("lng")

        leitura = LeituraGPS(
            device_id=device_id,
            timestamp_utc=timestamp,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=gps.get("speed_kmh"),
            course_deg=gps.get("course_deg"),
            num_satellites=gps.get("num_satellites"),
            hdop=gps.get("hdop"),
        )

        session.add(leitura)
        session.commit()
        print(f"✔ Leitura salva com sucesso! Device ID: {device_id}")

    except Exception as e:
        session.rollback() # Reverte a transação em caso de erro
        print(f"❌ Erro ao salvar leitura: {e}")
        # Se você quiser re-lançar o erro: raise e
    finally:
        session.close() # Sempre fecha a sessão