import type { RouteConfig } from "../types";

const API_URL = import.meta.env.VITE_API_URL;

export const api = {
  // Busca as rotas do banco de dados
  getRoutes: async (): Promise<RouteConfig[]> => {
    try {
      const response = await fetch(`${API_URL}/routes`);
      if (!response.ok) throw new Error("Erro ao buscar rotas");
      const jsonData = await response.json();

      return jsonData.data.map((r: any) => ({
        id: r.id,
        origin: r.origin,
        destination: r.destination,
        timeRange: r.time_range,
        days: r.days,
        deviceId: r.device_id, // Importante para o MQTT saber qual tópico ouvir
      }));
    } catch (error) {
      console.error(error);
      return [];
    }
  },

  // Envia a presença para o banco
  markPresence: async (userName: string, routeId: string, deviceId: string) => {
    await fetch(`${API_URL}/presence`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_name: userName,
        route_id: routeId,
        device_id: deviceId,
      }),
    });
  },
};
