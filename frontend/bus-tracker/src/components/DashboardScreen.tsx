import { useState } from 'react';
import '../style/DashboardScreen.css';
import { RouteSelectionModal } from './RouteSelectionModal';
import { RouteCard } from './RouteCard';
import type { RouteConfig } from '../types';
import { ListIcon, PlusIcon } from '@phosphor-icons/react';

interface DashboardScreenProps {
  onSelectRoute: () => void;
  myRoutes: RouteConfig[]; 
  onUpdateRoutes: (routes: RouteConfig[]) => void;
}

export function DashboardScreen({ onSelectRoute, myRoutes, onUpdateRoutes }: DashboardScreenProps) {
  const [showModal, setShowModal] = useState(false);

  const handleAddRoutes = (newRoutes: RouteConfig[]) => {
    const uniqueRoutes = [...myRoutes];
    newRoutes.forEach(route => {
      if (!uniqueRoutes.find(r => r.id === route.id)) {
        uniqueRoutes.push(route);
      }
    });
    
    // Chamamos a função do pai para salvar
    onUpdateRoutes(uniqueRoutes);
    setShowModal(false);
  };

  return (
    <div className="dashboard-container">
      {showModal && (
        <RouteSelectionModal 
          onClose={() => setShowModal(false)} 
          onAddRoutes={handleAddRoutes} 
        />
      )}
      
      <header className="dashboard-header">
        
        <button className="hamburger-btn" aria-label="Menu">
          <ListIcon size={28} color="#fff" weight="bold" />
        </button>

        <div className="header-brand">
          <img src="/logo-uff.png" alt="Logo UFF" className="header-logo-img" />
          <div className="header-text">
            <span>Universidade</span>
            <span>Federal</span>
            <span>Fluminense</span>
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        
        {/* Botão de abrir o modal */}
        <button className="new-route-btn" onClick={() => setShowModal(true)}>
          <PlusIcon size={20} weight="bold" style={{ marginRight: '5px' }} />
          Nova rota
        </button>

        <div className="routes-list" style={{ marginTop: '20px' }}>
          {myRoutes.length === 0 ? (
            <div className="empty-state">
              <p style={{ opacity: 0.5, textAlign: 'center', marginTop: '40px' }}>
                Nenhuma rota adicionada.
              </p>
            </div>
          ) : (
            // Lista de rotas adicionadas (Cartões Azuis)
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {myRoutes.map(route => (
                <RouteCard 
                  key={route.id}
                  route={route}
                  variant="blue" // Aqui usamos o estilo AZUL
                  actionType="navigate"
                  onClick={onSelectRoute} // Vai para o mapa
                />
              ))}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}