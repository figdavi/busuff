# Busuff Tracker

Busuff Tracker is a real-time bus localization system.It tracks buses using IoT GPS devices and display their positions live on a web map.

## Demo

<figure align="center">
    <img src="./images/map_print_max_zoom.png" alt="Mobile live map with maximum zoom screenshot" height="600px">
    <img src="./images/map_print_medium_zoom.png" alt="Mobile live map with medium zoom screenshot" height="600px">
</figure>

<figure align="center">
    <img src="./images/map_print_desktop.png" alt="Desktop live map screenshot" width="700px">
</figure>

## How it works (simplified logic)

<figure align="center">
    <img src="./images/basic_logic_diagram.png" alt="Desktop live map screenshot" width="500px">
</figure>

## How to run

1. Write corresponding credentials in `.env.example`

2. Rename `.env.example` to `.env`

3. Having Docker installed, run:

```bash
docker compose up --build -d
```

## GPS data format (JSON)

```json
{
	"device": {
		"id": string,
	},
	"gps": {
		"timestamp_utc": string (ISO 8601 UTC time),
		"location" {
			"lat": float (*OPTIONAL*, 6 decimal places),
			"lng": float (*OPTIONAL*, 6 decimal places)
		},
		"speed_kmh": float (*OPTIONAL*, 1 decimal),
		"course_deg": float (*OPTIONAL*, 1 decimal, 0–360°, degrees from North),
		"num_satellites": int (*OPTIONAL*),
		"hdop": float (*OPTIONAL*, 2 decimal)
	}
}
```

### Exemplos

```json
{
    "device": {
        "id": "14757629"
    },
    "gps": {
        "timestamp_utc": "2025-11-02T22:21:04Z",
        "location": {
            "lat": 60.424116,
            "lng": -22.814005
        },
        "speed_kmh": 0,
        "course_deg": 163.1,
        "num_satellites": 8,
        "hdop": 1.12
    }
}
```

- Note: Se o gps não obter uma boa leitura de um (ou mais) campo opcional (marcado por "_OPTIONAL_"), por exemplo, localização e velocidade, o campo "location" e "speed_kmh" não existirão no envio. Segue um exemplo:

```json
{
    "device": {
        "id": "14757629"
    },
    "gps": {
        "timestamp_utc": "2025-11-02T22:21:04Z",
        "course_deg": 163.1,
        "num_satellites": 8,
        "hdop": 1.12
    }
}
```
