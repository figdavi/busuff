import json
import time
import random
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

# CONFIGURAÇÕES
BROKER = "broker.hivemq.com"
PORT = 1883 # O script Python usa a porta TCP, não WebSockets!
TOPIC = "mqtt_iot_123321/busuff"

# ROTA SIMULADA (Coordenadas em Rio das Ostras - RJ)
# O ônibus vai "andar" por esses pontos
route = [
    {"lat": -22.505253, "lng": -41.920643}, # Ponto Inicial (UFF)
    {"lat": -22.506000, "lng": -41.921000},
    {"lat": -22.507000, "lng": -41.922000},
    {"lat": -22.508000, "lng": -41.923000},
    {"lat": -22.509000, "lng": -41.923500},
    {"lat": -22.510000, "lng": -41.924000},
    {"lat": -22.509000, "lng": -41.925000}, # Fazendo a curva
    {"lat": -22.508000, "lng": -41.924500},
    {"lat": -22.507000, "lng": -41.923500},
    {"lat": -22.506000, "lng": -41.922500},
]

def connect_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Simulador_Python_Bus")
    try:
        client.connect(BROKER, PORT)
        print(f"✅ Simulador conectado ao broker: {BROKER}")
        return client
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        exit(1)

def run_simulation():
    client = connect_mqtt()
    index = 0
    
    print("🚌 Iniciando rota... (Olhe seu navegador!)")
    
    while True:
        # Pega a coordenada atual da lista
        current_point = route[index]
        
        # Gera dados aleatórios para dar "vida" ao dashboard
        velocidade = random.uniform(30.0, 60.0)
        satelites = random.randint(5, 12)
        
        # Monta o JSON exatamente como o README pede
        payload = {
            "device": {
                "id": "simulador-01"
            },
            "gps": {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "location": {
                    "lat": current_point["lat"],
                    "lng": current_point["lng"]  # Nota: usei 'lng' para bater com seu App.tsx
                },
                "speed_kmh": round(velocidade, 1),
                "course_deg": random.randint(0, 360),
                "num_satellites": satelites,
                "hdop": 1.2
            }
        }

        # Envia a mensagem
        client.publish(TOPIC, json.dumps(payload))
        print(f"📡 Enviado: Lat {current_point['lat']}, Lng {current_point['lng']}")

        # Avança para o próximo ponto (loop infinito)
        index = (index + 1) % len(route)
        
        # Espera 2 segundos antes de mover o ônibus de novo
        time.sleep(2)

if __name__ == "__main__":
    run_simulation()