import type { RouteConfig } from '../types';

// URL do seu Backend Python (localhost ou AWS)
const API_URL = 'http://ec2-18-221-16-56.us-east-2.compute.amazonaws.com/api/'; 

export const api = {
  // Busca as rotas do banco de dados
  getRoutes: async (): Promise<RouteConfig[]> => {
    try {
      const response = await fetch(`${API_URL}/routes`);
      if (!response.ok) throw new Error('Erro ao buscar rotas');
      const data = await response.json();
      
      // Adaptador: O banco retorna "TimeRange", o front usa "timeRange"
      return data.map((r: any) => ({
        id: r.id,
        origin: r.origin,
        destination: r.destination,
        timeRange: r.TimeRange,
        days: r.days,
        deviceId: r.device_id // Importante para o MQTT saber qual tópico ouvir
      }));
    } catch (error) {
      console.error(error);
      return [];
    }
  },

  // Envia a presença para o banco
  markPresence: async (userName: string, routeId: string, deviceId: string) => {
    await fetch(`${API_URL}/presence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        user_name: userName, 
        route_id: routeId,
        device_id: deviceId 
      })
    });
  }
};