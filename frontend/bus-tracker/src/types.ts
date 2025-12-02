export interface GpsLocation {
    lat : number;
    lng : number;
}

export interface GpsInfo {
    timestamp_utc : string;
    //Campos opcionais marcados com ?
    location?: GpsLocation; 
    speed_kmh?: number;
    course_deg?: number;
    num_satellites?: number;
    hdop?: number;
}

export interface BusDataPayload {
  device: {
    id: string;
  };
  gps: GpsInfo;
}

export interface RouteConfig {
  id: string;
  origin: string;
  destination: string;
  timeRange: string; // Ex: "07:00 - 09:00 / 16:00 - 18:00"
  days: string[]; // Ex: ["SEG", "TER"]
  deviceId: string;
}