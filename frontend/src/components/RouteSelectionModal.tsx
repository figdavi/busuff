import { useState } from 'react';
import { ArrowLeftIcon, FadersIcon } from '@phosphor-icons/react';
import type { RouteConfig } from '../types';
import { RouteCard } from './RouteCard';
import '../style/RouteSelectionModal.css';

interface Props {
  onClose: () => void;
  onAddRoutes: (routes: RouteConfig[]) => void;
  availableRoutes: RouteConfig[];
}

export function RouteSelectionModal({ onClose, onAddRoutes, availableRoutes }: Props) {
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
    const routesToAdd = availableRoutes.filter(r => selectedIds.includes(r.id));
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
        {availableRoutes.map(route => (
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