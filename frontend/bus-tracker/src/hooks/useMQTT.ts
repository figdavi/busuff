import { useEffect, useState } from 'react';
import type { BusDataPayload } from '../types';
import { parseBusMessage } from '../utils/validator';
import mqtt from 'mqtt';

// Configurações do Broker (WebSockets)
const BROKER_URL = 'ws://broker.hivemq.com:8000/mqtt';
const TOPIC = 'mqtt_iot_123321/busuff';

export function useMqtt() {
  // Estado para guardar o último pacote de dados recebido
  const [data, setData] = useState<BusDataPayload | null>(null);
  const [status, setStatus] = useState<string>('Desconectado');

  useEffect(() => {
    setStatus('Conectando...');
    
    const client = mqtt.connect(BROKER_URL);

    client.on('connect', () => {
      console.log('Conectado ao MQTT Broker via WS!');
      setStatus('Conectado');
      client.subscribe(TOPIC);
    });

    client.on('message', (_topic, message) => {
      const validData = parseBusMessage(message.toString());

      if (validData) {
        setData(validData);
      } else {
        // Se retornou null, ignoramos silenciosamente
      }
    });

    client.on('error', (err) => {
      console.error('Erro de conexão:', err);
      setStatus('Erro de conexão');
    });

    // Cleanup: Fecha a conexão quando o componente for desmontado (fechar aba/mudar página)
    return () => {
      if (client.connected) {
        client.end();
      }
    };
  }, []);

  return { data, status };
}