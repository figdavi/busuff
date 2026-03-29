import { useState, useEffect } from 'react';

export function useUserLocation() {
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [accuracy, setAccuracy] = useState<number>(0); // Margem de erro em metros

  useEffect(() => {
    // Se o navegador não suportar GPS, não faz nada
    if (!navigator.geolocation) {
      console.warn('Geolocalização não suportada neste navegador.');
      return;
    }

    // Função chamada sempre que o usuário se mover
    const handleSuccess = (position: GeolocationPosition) => {
      const { latitude, longitude, accuracy } = position.coords;
      setUserLocation([latitude, longitude]);
      setAccuracy(accuracy);
    };

    const handleError = (error: GeolocationPositionError) => {
      console.error('Erro ao obter localização do usuário:', error);
    };

    // Inicia o rastreamento (watchPosition)
    const watcherId = navigator.geolocation.watchPosition(
      handleSuccess,
      handleError,
      {
        enableHighAccuracy: true, // Pede GPS preciso (gasta mais bateria)
        timeout: 10000,
        maximumAge: 0
      }
    );

    // Limpeza ao fechar o app
    return () => navigator.geolocation.clearWatch(watcherId);
  }, []);

  return { userLocation, accuracy };
}