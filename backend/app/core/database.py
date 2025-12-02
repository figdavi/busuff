from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    select,
    ForeignKey,
    ARRAY,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from datetime import datetime
from typing import Generator, Optional, List
import json
import os

# Types
jsonData = dict[str, dict[str, str | int]]

# CONFIGURAÇÃO DO BANCO
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = "postgresql+psycopg2"

DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# DEFINIÇÃO DA TABELA LeituraGPS
class LeituraGPS(Base):
    __tablename__ = "leituras_gps"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # CHAVE ESTRANGEIRA: Referencia a coluna 'id' na tabela 'devices'
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False)

    timestamp_utc = Column(DateTime, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    speed_kmh = Column(Float)
    course_deg = Column(Float)
    num_satellites = Column(Integer)
    hdop = Column(Float)
    # Permite acessar o objeto Device(leitura.device)
    device = relationship("Device")


class Route(Base):
    __tablename__ = "routes"
    bd_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(50), nullable=False, unique=True)

    # CHAVE ESTRANGEIRA: Referencia a coluna 'id' na tabela 'devices'
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=False)

    origin = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)

    # timeRange é uma string formatada (Ex: "07:00 - 09:00 / 16:00 - 18:00")
    timeRange = Column(String(150), nullable=False)

    # days é um array de strings (Ex: ["SEG", "TER"])
    days = Column(ARRAY(String(150)), nullable=False)

    # Permite acessar o objeto Device(leitura.device)
    device = relationship("Device")

    # metodo que converte o objeto ORM em um dicionário e retorna uma representação em dicionário do objeto Route, pronta para ser convertida em JSON.
    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "origin": self.origin,
            "destination": self.destination,
            "TimeRange": self.timeRange,
            "days": self.days,
        }


# DEFINIÇÃO DA TABELA Device
class Device(Base):
    __tablename__ = "devices"

    # O device_id será a chave primária (PK)
    id = Column(String(50), primary_key=True, unique=True, nullable=False)
    name = Column(String(100))
    # Espaço para adicionar mais colunas


# Cria as tabelas se não existirem, importante para garantir que a tabela exista antes de inserir.
def init_db():
    Base.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Cria uma nova sessão de banco de dados (SessionLocal),
    a entrega para o código chamador (yield) e garante que ela
    será fechada (db.close()) no bloco finally, mesmo em caso de erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FUNÇÃO AUXILIAR PARA SALVAR UMA LEITURA JSON
def salvar_leitura(json_data: jsonData) -> None:
    # Cria uma nova sessão a cada chamada da função para gerenciamento seguro
    session = SessionLocal()
    try:
        device_id = json_data["device"]["id"]

        gps = json_data["gps"]

        # GARANTE A EXISTÊNCIA DO DEVICE antes de salvar a leitura
        get_or_create_device(
            session, device_id
        )  # device_name pode ser passado aqui se estiver no json

        # Tratamento do timestamp
        timestamp_str = gps.get("timestamp_utc")
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        location = gps.get("location", {})
        latitude = location.get("lat")
        longitude = location.get("lng")

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
        session.rollback()  # Reverte a transação em caso de erro
        print(f"Erro ao salvar leitura: {e}")
        # Se você quiser re-lançar o erro: raise e
    finally:
        session.close()  # Sempre fecha a sessão


# Busca uma configuração de rota pelo ID e retorna um JSON (string). Retorna None se a rota não for encontrada.
def obter_rota_json(route_id: str) -> Optional[str]:
    # Gerencia a sessão do banco de dados (usando o padrão get_db)
    for db in get_db():
        try:
            # Busca um único registro onde Route.id é igual ao route_id fornecido
            stmt = select(Route).where(Route.id == route_id)

            #  Executa a consulta e pega o primeiro resultado
            rota_obj = db.execute(stmt).scalars().first()

            if rota_obj:
                # Converte o objeto ORM para um dicionário
                rota_dict = rota_obj.to_dict()

                # Serializa o dicionário para uma string JSON
                rota_json = json.dumps(rota_dict, indent=4, ensure_ascii=False)

                print(f"✅ Rota '{route_id}' encontrada e serializada.")
                return rota_json
            else:
                print(f"❌ Rota '{route_id}' não encontrada no banco de dados.")
                return None

        except Exception as e:
            # É bom ter o bloco try/except para capturar erros de conexão/SQL.
            print(f"Erro ao consultar o banco de dados: {e}")
            return None


# Cria uma nova configuração de rota, gerencia sua própria sessão, faz o commit e a fecha.
def salvar_rota(
    route_id: str,
    device_id: str,
    origin: str,
    destination: str,
    days: List[str],
    time_range: Optional[str] = None,
) -> None:
    session = SessionLocal()
    try:
        # Cria o objeto ORM (Route)
        nova_config = Route(
            id=route_id,
            device_id=device_id,
            origin=origin,
            destination=destination,
            timeRange=time_range,
            days=days,
        )

        # Adiciona e confirma
        session.add(nova_config)
        session.commit()

        print(f"✅ Rota '{route_id}' salva com sucesso!")

    except Exception as e:
        # Reverte em caso de erro
        session.rollback()
        print(f"❌ Erro ao salvar a rota '{route_id}'. Transação revertida: {e}")

    finally:
        # Sempre fecha a sessão, independentemente do sucesso ou falha
        session.close()


# Busca o device pelo ID. Se não existir, o cria e o adiciona à sessão.
def get_or_create_device(
    session: Session, device_id: str, device_name: str = None
) -> Device:
    # Tenta buscar o device
    device = session.get(Device, device_id)

    if device is None:
        # Se não encontrar, cria um novo objeto
        device = Device(id=device_id, name=device_name or f"Device {device_id}")
        session.add(device)
        print(f"Dispositivo '{device_id}' criado e adicionado à sessão.")

    return device


init_db()
