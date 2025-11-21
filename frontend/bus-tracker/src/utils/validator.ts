import type { BusDataPayload } from '../types';

/**
 * Recebe uma string (mensagem crua do MQTT) e tenta converter para um objeto seguro.
 * Retorna NULL se a mensagem for inválida ou estruturalmente incorreta.
 */
export function parseBusMessage(rawMessage: string): BusDataPayload | null {
  try {
    
    const parsed = JSON.parse(rawMessage);

    // Se não tiver 'gps' ou 'device', nem adianta continuar
    if (!parsed || !parsed.gps || !parsed.device) {
      console.warn('Pacote descartado: Estrutura incompleta');
      return null;
    }

    // Valida se o dados de localização são do tipo number
    const safePayload: BusDataPayload = {
      device: {
        id: String(parsed.device.id)
      },
      gps: {
        timestamp_utc: parsed.gps.timestamp_utc, // Poderíamos validar a data aqui também
        
        // Campos Opcionais: Usamos verificação defensiva
        speed_kmh: typeof parsed.gps.speed_kmh === 'number' ? parsed.gps.speed_kmh : 0,
        num_satellites: typeof parsed.gps.num_satellites === 'number' ? parsed.gps.num_satellites : 0,
        hdop: parsed.gps.hdop,
        
        location: (parsed.gps.location && 
                   typeof parsed.gps.location.lat === 'number' && 
                   typeof parsed.gps.location.lng === 'number') 
                   ? { 
                       lat: parsed.gps.location.lat, 
                       lng: parsed.gps.location.lng
                     }
                   : undefined
      }
    };

    return safePayload;

  } catch (error) {
    console.error('Erro crítico ao processar JSON:', error);
    return null;
  }
}