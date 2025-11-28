import type { BusDataPayload } from '../types';
import { ArrowLeftIcon, WifiHighIcon, WifiSlashIcon, MapPinIcon, SpeedometerIcon } from '@phosphor-icons/react';

interface InfoPanelProps {
  status: string;
  data: BusDataPayload | null;
  onBack: () => void;
}

export function InfoPanel({ status, data, onBack }: InfoPanelProps) {
  
  const isConnected = status === 'Conectado';
  const hasGpsSignal = data?.gps.location !== undefined;

  return (
    <div className="map-header">
      <div className="header-left">
        <button onClick={onBack} className="header-back-btn" aria-label="Voltar">
          <ArrowLeftIcon size={24} weight="bold" />
        </button>
        <span className="header-title">Informações (Status)</span>
      </div>

      <div className="header-stats">
        
        <div className="stat-item" title={status}>
          {isConnected ? (
            <WifiHighIcon size={20} weight="bold" color="#fff" />
          ) : (
            <WifiSlashIcon size={20} weight="bold" color="#ff8a80" />
          )}
        </div>

        {/* Indicador de Velocidade (Só mostra se tiver dados) */}
        {data && (
          <div className="stat-item">
            <SpeedometerIcon size={20} weight="bold" />
            <span>{data.gps.speed_kmh ?? 0} km/h</span>
          </div>
        )}

        {/* Alerta de GPS (Se tiver conectado mas sem sinal) */}
        {isConnected && !hasGpsSignal && (
          <div className="stat-badge warning">
             <MapPinIcon size={16} weight="fill" />
             <span>Sem GPS</span>
          </div>
        )}
      </div>
    </div>
  );
}