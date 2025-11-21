import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { BusDataPayload } from '../types';

const busIcon = new L.Icon({
  iconUrl: '/icone_onibus.png', 
  iconSize: [45, 45],
  iconAnchor: [17, 35],
  popupAnchor: [0, -35]
});

interface BusMapProps {
  position: [number, number];
  data: BusDataPayload | null;
}

function MapController({ center }: { center: [number, number] }) {
  const map = useMap();
  
  useEffect(() => {
    map.flyTo(center, map.getZoom());
  }, [center, map]);

  return null;
}

export function BusMap({ position, data }: BusMapProps) {
  return (
    <MapContainer center={position} zoom={15} className="map-wrapper">
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      <MapController center={position} />

      <Marker position={position} icon={busIcon}>
        <Popup>
          <div style={{ textAlign: 'center' }}>
            <strong> BusUFF</strong><br/>
            Velocidade: {data?.gps.speed_kmh} km/h<br/>
            <small>{data?.gps.timestamp_utc}</small>
          </div>
        </Popup>
      </Marker>
    </MapContainer>
  );
}