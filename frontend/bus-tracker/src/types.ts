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