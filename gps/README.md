# GPS

Firmware for the ESP8266 that reads GPS data from a NEO-6M module and publishes JSON messages to an MQTT broker.

Two LEDs indicate connection states:

- Wi-Fi LED: ON = disconnected, OFF = connected
- MQTT LED: ON = disconnected, OFF = connected

![Protoboard photo](images/protoboard_photo.jpeg)

## Getting Started

### Configure credentials

1. Write corresponding credentials in `./src/secrets.h.example`

2. Copy (or rename) `secrets.h.example` to `secrets.h`

### Build and upload

#### Dev

```bash
pio run -e dev --target upload
```

#### Prod

```bash
pio run -e prod --target upload
```

## JSON Payload Specification

All messages follow this schema:

| Field            | Type              | Required | Description                                                                         |
| ---------------- | ----------------- | -------- | ----------------------------------------------------------------------------------- |
| `vehicle_id`     | string            | Yes      | Unique identifier of the vehicle/device sending the telemetry.                      |
| `timestamp_utc`  | string (ISO 8601) | Yes      | UTC timestamp of the GPS reading in ISO 8601 format (e.g., `2026-02-13T15:04:05Z`). |
| `latitude`       | float             | No       | Latitude in decimal degrees (WGS84), up to 6 decimal places.                        |
| `longitude`      | float             | No       | Longitude in decimal degrees (WGS84), up to 6 decimal places.                       |
| `speed_kmh`      | float             | No       | Ground speed in kilometers per hour, 1 decimal place.                               |
| `course_deg`     | float             | No       | Direction of movement in degrees from North (0–360°), 1 decimal place.              |
| `num_satellites` | integer           | No       | Number of satellites used in the GPS fix.                                           |
| `hdop`           | float             | No       | Horizontal Dilution of Precision (signal accuracy indicator), 2 decimal places.     |

### Examples

- **Note**: Fields marked as non-required may be omitted if the GPS signal quality is insufficient.

#### Example 1 (Full GPS Fix)

```json
{
    "vehicle_id": "14757629",
    "timestamp_utc": "2025-11-02T22:21:04Z",
    "latitude": 60.424116,
    "longitude": -22.814005,
    "speed_kmh": 0,
    "course_deg": 163.1,
    "num_satellites": 8,
    "hdop": 1.12
}
```

#### Example 2 (Partial GPS Fix)

```json
{
    "vehicle_id": "14757629",
    "timestamp_utc": "2025-11-02T22:21:04Z",
    "course_deg": 163.1,
    "num_satellites": 8,
    "hdop": 1.12
}
```

## References

- https://randomnerdtutorials.com/esp8266-nodemcu-neo-6m-gps-module-arduino/
- https://arduinojson.org/
- https://www.emqx.com/en/blog/esp8266-connects-to-the-public-mqtt-broker
- https://tttapa.github.io/ESP8266/Chap07%20-%20Wi-Fi%20Connections.html
- http://www.pequenosprojetos.com.br/rastreador-gps-sim800l-e-esp8266-node-mcu/
- https://stuartsprojects.github.io/2024/09/21/How-not-to-read-a-GPS.html
- https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/station-examples.html
