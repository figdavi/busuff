# Monitoramento busuff

## How to run

1. Write corresponding credentials in `.env.example`

2. Rename `.env.example` to `.env`

3. Having Docker installed, run:

```bash
docker compose up --build
```

## Check data inside postgres container

```
psql -U postgres
# psql (17.7 (Debian 17.7-3.pgdg13+1))
# Type "help" for help.

postgres=# \l
#                                                      List of databases
#     Name     |  Owner   | Encoding | Locale Provider |  Collate   |   Ctype    | Locale | ICU Rules |   Access privileges
# -------------+----------+----------+-----------------+------------+------------+--------+-----------+-----------------------
#  postgres    | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           |
#  projeto_gps | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           |
#  template0   | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
#              |          |          |                 |            |            |        |           | postgres=CTc/postgres
#  template1   | postgres | UTF8     | libc            | en_US.utf8 | en_US.utf8 |        |           | =c/postgres          +
#              |          |          |                 |            |            |        |           | postgres=CTc/postgres
# (4 rows)

postgres=# \c projeto_gps
# You are now connected to database "projeto_gps" as user "postgres".

projeto_gps=# \dt
#             List of relations
#  Schema |     Name     | Type  |  Owner
# --------+--------------+-------+----------
#  public | leituras_gps | table | postgres
# (1 row)

projeto_gps=# SELECT * FROM leituras_gps;
# id |  device_id  |    timestamp_utc    |  latitude  | longitude  | speed_kmh | course_deg | num_satellites | hdop
# ----+-------------+---------------------+------------+------------+-----------+------------+----------------+------
#   1 | bus_9641797 | 2025-11-22 16:32:18 |  -22.50342 | -41.923537 |       1.4 |      295.7 |              4 |  3.8
#   2 | bus_9641797 | 2025-11-22 16:32:23 | -22.503445 | -41.923503 |         0 |      295.7 |              4 |  3.8
#   3 | bus_9641797 | 2025-11-22 16:32:28 | -22.503434 | -41.923485 |         0 |      295.7 |              4 |  3.8
#   4 | bus_9641797 | 2025-11-22 16:32:33 | -22.503444 | -41.923487 |         4 |      197.6 |              4 |  3.9
#   5 | bus_9641797 | 2025-11-22 16:33:13 | -22.503517 |  -41.92364 |         0 |      234.6 |              3 |  3.9
#   6 | bus_9641797 | 2025-11-22 16:33:18 |            |            |           |            |              0 |  3.9
#   7 | bus_9641797 | 2025-11-22 16:33:23 |            |            |           |            |              0 |  3.9
#   8 | bus_9641797 | 2025-11-22 16:33:28 |            |            |           |            |              0 |  3.9
#   9 | bus_9641797 | 2025-11-22 16:33:33 |            |            |           |            |              0 |  3.9
#  10 | bus_9641797 | 2025-11-22 16:33:38 |            |            |           |            |              0 |  3.9

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

- Nota: Se o gps não obter uma boa leitura de um (ou mais) campo opcional (marcado por "_OPTIONAL_"), por exemplo, localização e velocidade, o campo "location" e "speed_kmh" não existirão no envio. Segue um exemplo:

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
