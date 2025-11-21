import type { BusDataPayload } from '../types';

interface InfoPanelProps {
  status: string;
  data: BusDataPayload | null;
}

export function InfoPanel({ status, data }: InfoPanelProps) {
  
  const isMqttConnected = status === 'Conectado';
  const hasGpsSignal = data?.gps.location !== undefined;

  let statusClass = '';

  if (!isMqttConnected) {
    statusClass = 'disconnected';
  } else if (!hasGpsSignal && data) {
    statusClass = 'no-signal';
  } else {
    statusClass = 'connected';
  }

  return (
    <div className={`status-bar ${statusClass}`}>
      <div>
        <strong>Status:</strong> {status}
        
        {isMqttConnected && !hasGpsSignal && data && (
           <span className="alert-text">
             Sem sinal do dispositivo ⚠️
           </span>
        )}
      </div>

      {data && (
        <div className="data-group">
           <span> Sat: <strong>{data.gps.num_satellites ?? 0}</strong></span>
           <span> Vel: <strong>{data.gps.speed_kmh ?? 0} km/h</strong></span>
        </div>
      )}
    </div>
  );
}