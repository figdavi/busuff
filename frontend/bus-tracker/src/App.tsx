import { useEffect, useState } from 'react'; 
import { useMqtt } from './hooks/useMQTT';
import { InfoPanel } from './components/InfoPanel';
import { BusMap } from './components/BusMap';
import 'leaflet/dist/leaflet.css';
import './App.css';

function App() {
  const { data, status } = useMqtt();
  
  // (Posição inicial: UFF Rio das Ostras)
  const [position, setPosition] = useState<[number, number]>([-22.505253, -41.9206433]);

  useEffect(() => {
    if (data && data.gps.location) {
      setPosition([data.gps.location.lat, data.gps.location.lng]);
    }
  }, [data]);

  return (
    <div className="app-container">
      <InfoPanel status={status} data={data} />
      <BusMap position={position} data={data} />
    </div>
  );
}

export default App;