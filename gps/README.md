# gps

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
			"lon": float (*OPTIONAL*, 6 decimal places)
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
	"device":{
		"id":"14757629"
	},
	"gps": {
		"timestamp_utc":"2025-11-02T22:21:04Z",
		"location":{
			"lat":60.424116,
			"lng":-22.814005
		},
		"speed_kmh":0,
		"course_deg":163.1,
		"num_satellites":8,
		"hdop":1.12
	}
}
```
- Nota: Se o gps não obter uma boa leitura de um (ou mais) campo opcional (marcado por "*OPTIONAL*"), por exemplo, localização e velocidade, o campo "location" e "speed_kmh" não existirão no envio. Segue um exemplo:
```json
{
	"device":{
		"id":"14757629"
	},
	"gps": {
		"timestamp_utc":"2025-11-02T22:21:04Z",
		"course_deg":163.1,
		"num_satellites":8,
		"hdop":1.12
	}
}
```


## How to build PlatformIO based project

1. Install PlatformIO Core
2. Download development platform with examples
3. Extract ZIP archive
4. Run these commands:

```bash
# Change directory to example
$ cd platform-espressif8266/examples/arduino-wifiscan

# Build project
$ pio run

# Upload firmware
$ pio run --target upload

# Clean build files
$ pio run --target clean
```