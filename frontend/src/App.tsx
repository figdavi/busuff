import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import './App.css';

// Hooks
import { useMqtt } from './hooks/useMQTT';
import { useUserLocation } from './hooks/useUserLocation';

// Componentes de Tela
import { BeginScreen } from './components/BeginScreen';
import { DashboardScreen } from './components/DashboardScreen';
import { BusMap } from './components/BusMap';
import { InfoPanel } from './components/InfoPanel';

// Tipos e Serviços
import  type { RouteConfig } from './types';
import { api } from './services/api';
import { CheckCircleIcon } from '@phosphor-icons/react';

// Define quais telas o app possui
type ScreenType = 'begin' | 'dashboard' | 'map';

function App() {
  // --- ESTADOS GLOBAIS ---
  const [currentScreen, setCurrentScreen] = useState<ScreenType>('begin');
  
  // Rotas que o usuário adicionou à dashboard ("Meus Favoritos")
  const [myRoutes, setMyRoutes] = useState<RouteConfig[]>([]);
  
  // A rota que está sendo visualizada no momento (Clica na dashboard -> Seta aqui)
  const [activeRoute, setActiveRoute] = useState<RouteConfig | null>(null);

  // --- LÓGICA DE DADOS ---
  
  const { data, status } = useMqtt(activeRoute ? activeRoute.id : null);
  const { userLocation, accuracy } = useUserLocation();

  // Posição do Ônibus
  const [busPosition, setBusPosition] = useState<[number, number]>([-22.505253, -41.9206433]); // Default: UFF

  // Efeito: Toda vez que chegar dado novo do MQTT, atualiza o mapa
  useEffect(() => {
    if (data && data.gps.location) {
      const newPos: [number, number] = [data.gps.location.lat, data.gps.location.lng];
      
      setBusPosition(newPos);
    }
  }, [data]);

  // --- HANDLERS (Ações do Usuário) ---

  // Quando o usuário clica em um card na Dashboard
  const handleSelectRoute = (route: RouteConfig) => {
    setActiveRoute(route);        // Define qual rota vamos escutar
    setBusPosition([-22.505253, -41.9206433]); // Reseta posição (ou poderia ser a origem da rota)
    setCurrentScreen('map');      // Muda a tela
  };

  // Quando o usuário clica em "Voltar" no mapa
  const handleBackToDashboard = () => {
    setActiveRoute(null); // Desconecta o MQTT (para economizar dados/bateria)
    setCurrentScreen('dashboard');
  };

  // Quando o usuário clica em "Marcar Presença"
  const handleMarkPresence = async () => {
    const nome = window.prompt("Digite seu nome para confirmar presença:");
    
    if (nome && activeRoute) {
      try {
        // Envia para o Backend Python via API REST
        // O activeRoute.deviceId aqui é o padrão da rota, mas o backend vai registrar
        await api.markPresence(nome, activeRoute.id, activeRoute.deviceId || "unknown_device");
        alert(`✅ Presença confirmada para ${nome}!`);
      } catch (error) {
        alert("❌ Erro ao marcar presença. Tente novamente.");
        console.error(error);
      }
    }
  };

  // --- RENDERIZAÇÃO CONDICIONAL ---

  // 1. Tela Inicial (Splash)
  if (currentScreen === 'begin') {
    return <BeginScreen onStart={() => setCurrentScreen('dashboard')} />;
  }

  // 2. Dashboard (Lista de Rotas)
  if (currentScreen === 'dashboard') {
    return (
      <DashboardScreen 
        onSelectRoute={handleSelectRoute}
        myRoutes={myRoutes}
        onUpdateRoutes={setMyRoutes}
      />
    );
  }

  // 3. Mapa (Monitoramento)
  return (
    <div className="app-container">
      
      {/* Header com botão de voltar */}
      <InfoPanel 
        status={status} 
        data={data} 
        onBack={handleBackToDashboard} 
      />

      {/* O Mapa Interativo */}
      <BusMap 
        position={busPosition} 
        data={data} 
        userLocation={userLocation}
        userAccuracy={accuracy}
      />

      {/* Botão Flutuante de Presença */}
      <div className="presence-container">
        <button className="presence-btn" onClick={handleMarkPresence}>
          <CheckCircleIcon size={24} weight="fill" />
          Marcar presença
        </button>
      </div>

    </div>
  );
}

export default App;