import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import './App.css';
import  type { RouteConfig } from './types';
import { useMqtt } from './hooks/useMQTT';
import { useUserLocation } from './hooks/useUserLocation';
import { CheckCircleIcon } from '@phosphor-icons/react';

// Imports dos componentes
import { InfoPanel } from './components/InfoPanel';
import { BusMap } from './components/BusMap';
import { BeginScreen } from './components/BeginScreen';
import { DashboardScreen } from './components/DashboardScreen';


function App() {
  const [currentScreen, setCurrentScreen] = useState<'begin' | 'dashboard' | 'map'>('begin');
  const [myRoutes, setMyRoutes] = useState<RouteConfig[]>([]);
  const { data, status } = useMqtt();
  const [position, setPosition] = useState<[number, number]>([-22.505253, -41.9206433]);
  const { userLocation, accuracy } = useUserLocation();

  useEffect(() => {
    if (data && data.gps.location) {
      setPosition([data.gps.location.lat, data.gps.location.lng]);
    }
  }, [data]);

  // --- FUNÇÃO PARA MARCAR PRESENÇA ---
  const handleMarkPresence = () => {
    // Por enquanto usamos um prompt nativo do navegador
    const nome = window.prompt("Digite seu nome para confirmar presença na viagem:");
    
    if (nome) {
      // AQUI ENTRARÁ A LÓGICA DE ENVIAR PARA O MQTT/BACKEND NO FUTURO
      console.log(`Presença marcada para: ${nome}`);
      alert(`✅ Presença confirmada, ${nome}! Boa viagem.`);
    }
  };

  // --- RENDERIZAÇÃO ---
  if (currentScreen === 'begin') {
    return <BeginScreen onStart={() => setCurrentScreen('dashboard')} />;
  }

  if (currentScreen === 'dashboard') {
    return (
      <DashboardScreen 
        onSelectRoute={() => setCurrentScreen('map')}
        myRoutes={myRoutes}
        onUpdateRoutes={setMyRoutes}
      />
    );
  }

  // TELA DO MAPA
  return (
    <div className="app-container">
      
      <InfoPanel 
        status={status} 
        data={data} 
        onBack={() => setCurrentScreen('dashboard')}
      />

      <BusMap 
        position={position} 
        data={data}
        userLocation={userLocation}
        userAccuracy={accuracy} 
      />

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