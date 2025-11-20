import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
// O CSS já deve ter sido importado no main.tsx, se não, coloque aqui:
// import 'leaflet/dist/leaflet.css';

function App() {
  // Coordenada inicial (Ex: São Paulo, ou a coordenada do seu exemplo no README)
  const initialPosition = { lat: -23.550520, lng: -46.633308 };

  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      {/* MapContainer precisa ter uma altura definida (height) para aparecer */}
      <MapContainer 
        center={initialPosition} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Usamos um CircleMarker por enquanto para evitar problemas com ícones de imagem */}
        <CircleMarker center={initialPosition} radius={10} color="red">
          <Popup>
            O ônibus está aqui!
          </Popup>
        </CircleMarker>
      </MapContainer>
    </div>
  );
}

export default App;