import { useEffect, useState } from 'react';
import mqtt from 'mqtt';
import type { BusDataPayload } from '../types';
import { parseBusMessage } from '../utils/validator';

// Configurações do Broker
// Lembre-se: Porta 8000 para WS (WebSockets) inseguro, 8884 para WSS (Seguro)
const BROKER_URL = 'ws://broker.hivemq.com:8000/mqtt';

const ROOT_TOPIC = 'busuff';

export function useMqtt(routeId: string | null) {
  const [data, setData] = useState<BusDataPayload | null>(null);
  const [status, setStatus] = useState<string>('Desconectado');

  useEffect(() => {
    // Se não houver uma rota selecionada (estamos na Home ou Dashboard), não conectamos
    if (!routeId) {
      console.log('Nenhuma rota ativa. MQTT em espera.');
      return;
    }

    setStatus('Conectando...');
    
    const client = mqtt.connect(BROKER_URL);

    client.on('connect', () => {
      console.log('Conectado ao HiveMQ!');
      setStatus('Conectado');

      // Usamos o curinga '+' para escutar qualquer dispositivo dentro desta rota
      // Formato: busuff/{route_id}/+
      const topic = `${ROOT_TOPIC}/${routeId}/+`;
      
      client.subscribe(topic, (err) => {
        if (!err) {
          console.log(`Inscrito no tópico: ${topic}`);
        } else {
          console.error('Erro ao se inscrever:', err);
        }
      });
    });

    client.on('message', (_topic, message) => {
      // O _topic conterá o ID real do dispositivo (ex: busuff/rota_1/device_99)
      // Passamos a mensagem crua para o nosso validador
      const validData = parseBusMessage(message.toString());
      
      if (validData) {
        setData(validData);
      }
    });

    client.on('error', (err) => {
      console.error('Erro na conexão MQTT:', err);
      setStatus('Erro de conexão');
    });

    // Cleanup: Fecha a conexão se o componente desmontar ou se a rota mudar
    return () => {
      if (client.connected) {
        console.log('Fechando conexão MQTT...');
        client.end();
      }
    };
  }, [routeId]); // O Hook recarrega se o routeId mudar

  return { data, status };
}