import { useEffect, useMemo, useState } from "react";
import {
    MapContainer,
    TileLayer,
    Marker,
    Popup,
    useMap,
    Polyline,
    Circle,
    CircleMarker,
    useMapEvents,
} from "react-leaflet";
import { CrosshairIcon } from "@phosphor-icons/react";
import L from "leaflet";
import type { BusDataPayload } from "../types";

interface BusMapProps {
    position: [number, number];
    data: BusDataPayload | null;
    history?: [number, number][];
    userLocation?: [number, number] | null;
    userAccuracy?: number;
}

// Sub-componente para controlar o movimento suave
function MapController({
    center,
    isFollowing,
    onUserInteraction,
}: {
    center: [number, number];
    isFollowing: boolean;
    onUserInteraction: () => void;
}) {
    const map = useMap();

    useMapEvents({
        dragstart: () => {
            onUserInteraction();
        },
        zoomstart: () => {
            onUserInteraction();
        },
    });

    useEffect(() => {
        if (isFollowing) {
            map.flyTo(center, map.getZoom(), { animate: true, duration: 1.5 });
        }
    }, [center, map, isFollowing]);

    return null;
}

export function BusMap({
    position,
    data,
    history = [],
    userLocation,
    userAccuracy = 0,
}: BusMapProps) {
    const [isFollowingBus, setIsFollowingBus] = useState(true);

    const rotation = data?.gps.course_deg ?? 0;

    const bus3dIcon = useMemo(() => {
        return L.divIcon({
            className: "custom-bus-icon",
            iconSize: [60, 60],
            iconAnchor: [30, 30],
            popupAnchor: [0, -30],
            html: `
        <div style="
          transform: rotate(${rotation}deg); 
          transition: transform 0.5s linear;
          width: 100%; 
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
        ">
          <img 
            src="/bus-3d.png" 
            style="width: 100%; height: auto; filter: drop-shadow(4px 6px 4px rgba(0,0,0,0.5));" 
          />
        </div>
      `,
        });
    }, [rotation]);

    const limeOptions = { color: "#0091ea", weight: 5, opacity: 0.7 };

    return (
        <div className="busmap-relative-container">
            <MapContainer
                center={position}
                zoom={16}
                className="map-wrapper"
                zoomControl={false}
            >
                <TileLayer
                    attribution="&copy; OpenStreetMap"
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                <MapController
                    center={position}
                    isFollowing={isFollowingBus}
                    onUserInteraction={() => setIsFollowingBus(false)}
                />

                {history.length > 0 && (
                    <Polyline pathOptions={limeOptions} positions={history} />
                )}

                {/* Marcador do usuário */}
                {userLocation && (
                    <>
                        <Circle
                            center={userLocation}
                            radius={userAccuracy}
                            pathOptions={{
                                color: "transparent",
                                fillColor: "#4285F4",
                                fillOpacity: 0.15,
                            }}
                        />

                        <CircleMarker
                            center={userLocation}
                            radius={8}
                            pathOptions={{
                                color: "white",
                                weight: 2,
                                fillColor: "#4285F4",
                                fillOpacity: 1,
                            }}
                        >
                            <Popup>Você está aqui</Popup>
                        </CircleMarker>
                    </>
                )}

                {/* Marcador do onibus */}
                <Marker position={position} icon={bus3dIcon}>
                    <Popup>
                        <div style={{ textAlign: "center" }}>
                            <strong>🚌 Linha UFF</strong>
                            <br />
                            {data ? (
                                <>
                                    Data: {data.gps.timestamp_utc}
                                    <br />
                                    Velocidade: {data.gps.speed_kmh} km/h
                                    <br />
                                    Direção: {data.gps.course_deg}°
                                </>
                            ) : (
                                "Aguardando dados..."
                            )}
                        </div>
                    </Popup>
                </Marker>
            </MapContainer>

            {!isFollowingBus && (
                <button
                    className="recenter-btn"
                    onClick={() => setIsFollowingBus(true)}
                    aria-label="Centralizar no Ônibus"
                >
                    <CrosshairIcon size={32} weight="bold" />
                </button>
            )}
        </div>
    );
}
