import { useState } from 'react';
import { ArrowLeftIcon, FadersIcon } from '@phosphor-icons/react';
import type { RouteConfig } from '../types';
import { RouteCard } from './RouteCard';
import '../style/RouteSelectionModal.css';

// DADOS travados (A única rota disponível)
const AVAILABLE_ROUTES: RouteConfig[] = [
  {
    id: '1',
    origin: 'Macaé',
    destination: 'UFF - Rio das Ostras',
    timeRange: '07:00 - 09:00 / 16:00 - 18:00',
    days: ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
  }
];

interface Props {
  onClose: () => void;
  onAddRoutes: (routes: RouteConfig[]) => void;
}

export function RouteSelectionModal({ onClose, onAddRoutes }: Props) {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const toggleRoute = (id: string) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(itemId => itemId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleConfirm = () => {
    // Filtra as rotas completas baseadas nos IDs selecionados
    const routesToAdd = AVAILABLE_ROUTES.filter(r => selectedIds.includes(r.id));
    onAddRoutes(routesToAdd);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-header">
        <button onClick={onClose} className="back-btn" aria-label="Voltar">
          <ArrowLeftIcon size={28} color="#fff" weight="bold" />
        </button>

        <button className="filter-btn">
           {/* 3. ÍCONE DE FILTRO */}
           <FadersIcon size={20} color="#0091ea" weight="bold" style={{ marginRight: '8px' }} />
           Filtros
        </button>
      </div>

      <div className="modal-content">
        {AVAILABLE_ROUTES.map(route => (
          <RouteCard 
            key={route.id}
            route={route}
            variant="light"
            actionType="add"
            isSelected={selectedIds.includes(route.id)}
            onAction={() => toggleRoute(route.id)}
          />
        ))}
      </div>

      <div className="modal-footer">
        {selectedIds.length > 0 && (
          <button className="confirm-fab" onClick={handleConfirm}>
             + Adicionar rotas
          </button>
        )}
      </div>
    </div>
  );
}