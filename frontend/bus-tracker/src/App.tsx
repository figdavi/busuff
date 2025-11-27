import { useEffect, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import './App.css';
import type { RouteConfig } from './types';

// Componentes
import { useMqtt } from './hooks/useMQTT';
import { InfoPanel } from './components/InfoPanel';
import { BusMap } from './components/BusMap';
import { BeginScreen } from './components/BeginScreen';
import { DashboardScreen } from './components/DashboardScreen';

function App() {

  const [currentScreen, setCurrentScreen] = useState<'begin' | 'dashboard' | 'map'>('begin');
  const [myRoutes, setMyRoutes] = useState<RouteConfig[]>([]);

  // Lógica do MQTT (por padrão fica próximo da UFF Rio das Ostras)
  const { data, status } = useMqtt();
  const [position, setPosition] = useState<[number, number]>([-22.505253, -41.9206433]);

  useEffect(() => {
    if (data && data.gps.location) {
      setPosition([data.gps.location.lat, data.gps.location.lng]);
    }
  }, [data]);

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

  // 3. Mapa (Onde vemos o ônibus)
  return (
    <div className="app-container">
      {/* Botão flutuante para voltar para a Dashboard */}
      <button 
        className="back-button"
        onClick={() => setCurrentScreen('dashboard')}
        style={{
          position: 'absolute', 
          top: 15, 
          left: 15, 
          zIndex: 1000, // Acima do mapa
          background: 'white',
          border: 'none',
          padding: '8px 12px',
          borderRadius: '4px',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 2px 5px rgba(0,0,0,0.3)'
        }}
      >
        ⬅ Voltar
      </button>

      <InfoPanel status={status} data={data} />
      <BusMap position={position} data={data} />
    </div>
  );
}

export default App;