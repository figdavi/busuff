import { useEffect, useState } from 'react';
import '../style/DashboardScreen.css';
import { RouteSelectionModal } from './RouteSelectionModal';
import { RouteCard } from './RouteCard';
import type { RouteConfig } from '../types';
import { ListIcon, PlusIcon } from '@phosphor-icons/react';
import { api } from '../services/api';

interface DashboardScreenProps {
  onSelectRoute: (route: RouteConfig) => void; 
  myRoutes: RouteConfig[];
  onUpdateRoutes: (routes: RouteConfig[]) => void;
}

export function DashboardScreen({ onSelectRoute, myRoutes, onUpdateRoutes }: DashboardScreenProps) {
  
  // Controle do Modal
  const [showModal, setShowModal] = useState(false);
  
  // Rotas disponíveis no BANCO DE DADOS (para escolher no modal)
  const [availableRoutes, setAvailableRoutes] = useState<RouteConfig[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // 1. Busca as rotas do Backend assim que a tela abre
  useEffect(() => {
    setIsLoading(true);
    api.getRoutes()
      .then(routes => {
        setAvailableRoutes(routes);
      })
      .catch(err => console.error("Erro ao carregar rotas:", err))
      .finally(() => setIsLoading(false));
  }, []);

  // 2. Adiciona as rotas selecionadas à lista pessoal
  const handleAddRoutes = (newRoutes: RouteConfig[]) => {
    const uniqueRoutes = [...myRoutes];
    
    newRoutes.forEach(route => {
      // Evita duplicatas pelo ID
      if (!uniqueRoutes.find(r => r.id === route.id)) {
        uniqueRoutes.push(route);
      }
    });
    
    onUpdateRoutes(uniqueRoutes);
    setShowModal(false);
  };

  return (
    <div className="dashboard-container">
      
      {/* Modal de Seleção (Agora recebe as rotas do banco) */}
      {showModal && (
        <RouteSelectionModal 
          onClose={() => setShowModal(false)} 
          onAddRoutes={handleAddRoutes}
          // Passamos as rotas carregadas da API para o modal listar
          availableRoutes={availableRoutes} 
        />
      )}

      {/* --- HEADER --- */}
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

      {/* --- CONTEÚDO --- */}
      <main className="dashboard-content">
        
        {/* Botão Nova Rota */}
        <button className="new-route-btn" onClick={() => setShowModal(true)}>
          <PlusIcon size={20} weight="bold" style={{ marginRight: '5px' }} />
          Nova rota
        </button>

        {/* Lista de Rotas do Usuário */}
        <div className="routes-list" style={{ marginTop: '20px' }}>
          
          {myRoutes.length === 0 ? (
            <div className="empty-state">
              <p style={{ opacity: 0.5, textAlign: 'center', marginTop: '40px' }}>
                {isLoading ? "Carregando sistema..." : "Nenhuma rota adicionada à sua dashboard."}
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              {myRoutes.map(route => (
                <RouteCard 
                  key={route.id}
                  route={route}
                  variant="blue" // Estilo Dashboard
                  actionType="navigate"
                  // Ao clicar, avisamos o App.tsx qual rota foi escolhida
                  onClick={() => onSelectRoute(route)} 
                />
              ))}
            </div>
          )}
        </div>

      </main>
    </div>
  );
}