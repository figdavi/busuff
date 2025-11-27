import '../style/RouteCard.css';
import type { RouteConfig } from '../types';

interface RouteCardProps {
  route: RouteConfig;
  variant: 'light' | 'blue';
  actionType?: 'add' | 'navigate';
  isSelected?: boolean;
  onAction?: () => void;
  onClick?: () => void;
}

export function RouteCard({ 
  route, 
  variant, 
  actionType, 
  isSelected, 
  onAction, 
  onClick 
}: RouteCardProps) {
  
  const allDays = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SAB'];

  return (
    <div 
      className={`route-card ${variant}`} 
      onClick={onClick}
    >
      <div className="days-row">
        {allDays.map(day => {
          const isActive = route.days.includes(day);
          return (
            <div key={day} className={`day-bubble ${isActive ? 'active' : ''}`}>
              {day}
            </div>
          );
        })}
      </div>

      <div className="timeline-container">
        
        {/* Ponto A: Origem */}
        <div className="timeline-item">
          <div className="timeline-icon origin"></div>
          <div className="timeline-text">
            <span className="label">Saindo de:</span>
            <span className="value">{route.origin}</span>
          </div>
        </div>

        <div className="timeline-line"></div>

        {/* Ponto B: Destino */}
        <div className="timeline-item">
          <div className="timeline-icon destination"></div>
          <div className="timeline-text">
            <span className="label">Indo para:</span>
            <span className="value">{route.destination}</span>
          </div>
        </div>
      </div>

      {/* Rodapé: Horário e Botão de Ação */}
      <div className="card-footer">
        <span className="time-range">{route.timeRange}</span>
        
        {actionType === 'add' && (
          <button 
            className={`add-btn ${isSelected ? 'selected' : ''}`} 
            onClick={(e) => {
              e.stopPropagation();
              onAction && onAction();
            }}
          >
            {isSelected ? '✓' : '+'}
          </button>
        )}
      </div>
    </div>
  );
}