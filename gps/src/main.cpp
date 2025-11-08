/* References:
 * https://randomnerdtutorials.com/esp8266-nodemcu-neo-6m-gps-module-arduino/
 * https://arduinojson.org/
 * https://www.emqx.com/en/blog/esp8266-connects-to-the-public-mqtt-broker
 * https://tttapa.github.io/ESP8266/Chap07%20-%20Wi-Fi%20Connections.html
 * http://www.pequenosprojetos.com.br/rastreador-gps-sim800l-e-esp8266-node-mcu/
 */

// TODO: Test SIM800L
// TODO: Micro SIM card free trial
// TODO: Introduce auth and encryption to MQTT comm
// TODO: Resolve RX pin issue (change gps baud rate to 9600)
// TODO: Decide internet data x historical data (send invalid data? send outdated data? If yes, Use queue to buffer unsent messages.)
// TODO: Remove ArduinoJson
// TODO: OTA uploads

#include <Arduino.h>
#include "secrets.h"

#include <TinyGPS++.h>
TinyGPSPlus gps;

#include <ArduinoJson.h>
JsonDocument jsonData;

#include <ESP8266WiFi.h>
WiFiClient wifiClient;

#include <PubSubClient.h>
PubSubClient mqttClient;

// https://github.com/mqtt/mqtt.org/wiki/public_brokers
static const char MQTT_BROKER[] = "broker.hivemq.com";
static const char MQTT_TOPIC[] = "mqtt_iot_123321/busuff";
static const int MQTT_PORT = 1883;
static const unsigned long MQTT_PUB_INTERVAL_MS = 5000;

// #include <SoftwareSerial.h>
// static const int RX_PIN = D7;
// SoftwareSerial gpsSerial(RX_PIN, -1);
static const int GPS_BAUD = 115200; // Do NOT use 9600 baud rate, only 115200 works.

char DEVICE_ID[32];

#define DEBUG 0

#if DEBUG
#define DEBUG_PRINT(x) Serial.print(x)
#define DEBUG_PRINTLN(x) Serial.println(x)
#else
#define DEBUG_PRINT(x)
#define DEBUG_PRINTLN(x)
#endif

// Function declarations
void checkMQTT();
void checkWiFi();
bool buildPayload(char *output, size_t outputSize);
static inline double roundN(double value, int places);

void setup()
{
    sprintf(DEVICE_ID, "bus_%u", ESP.getChipId());

    // gpsSerial.begin(GPS_BAUD);
    Serial.begin(GPS_BAUD);

    WiFi.begin(WIFI_SSID, WIFI_PASS);

    DEBUG_PRINT("IP address: ");
    DEBUG_PRINTLN(WiFi.localIP());

    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setClient(wifiClient);
}

void loop()
{
    // NOTE: Keep all network tasks non-blocking (for OTA, MQTT, and WiFi reconnect to work reliably)
    checkWiFi();
    checkMQTT();

    while (Serial.available())
    {
        char c = Serial.read();
        gps.encode(c);
        // DEBUG_PRINT(c); // raw output
    }

    // static, initialization happens only once and variable persists values between iterations
    static unsigned long lastSend = 0;
    bool intervalHasPassed = (millis() - lastSend) > MQTT_PUB_INTERVAL_MS;

    // With valid timestamp we can study where gps failed.
    bool timestampIsValid = gps.date.isValid() && gps.time.isValid();

    if (intervalHasPassed && timestampIsValid)
    {
        lastSend = millis();
        char message[256];

        if (!buildPayload(message, sizeof(message)))
        {
            DEBUG_PRINTLN("Failed to build payload.");
            return;
        }
        DEBUG_PRINTLN(message);

        if (!mqttClient.connected())
        {
            DEBUG_PRINTLN("MQTT not connected, skipping publish");
            return;
        }
        mqttClient.publish(MQTT_TOPIC, message);
    }
}

void checkWiFi()
{
    static unsigned long lastAttempt = 0;
    static bool wasConnected = false;

    if (WiFi.status() != WL_CONNECTED)
    {
        if (millis() - lastAttempt > 5000)
        {
            lastAttempt = millis();

            DEBUG_PRINT("Attempt to connect to WiFi. SSID: ");
            DEBUG_PRINTLN(WiFi.SSID());

            WiFi.reconnect();
        }
        wasConnected = false;
    }
    else if (!wasConnected)
    {
        DEBUG_PRINTLN("WiFi connected!");
        DEBUG_PRINT("IP: ");
        DEBUG_PRINTLN(WiFi.localIP());
        wasConnected = true;
    }
}

void checkMQTT()
{
    static unsigned long lastAttempt = 0;
    static bool wasConnected = false;
    if (!mqttClient.connected())
    {
        // Try only if we have WiFi
        if (WiFi.status() == WL_CONNECTED && millis() - lastAttempt > 3000)
        {
            lastAttempt = millis();
            DEBUG_PRINT("Attempt to connect to MQTT broker. URL: ");
            DEBUG_PRINTLN(MQTT_BROKER);
            mqttClient.connect(DEVICE_ID);
        }
        wasConnected = false;
    }
    else
    {
        if (!wasConnected)
        {
            DEBUG_PRINTLN("MQTT connected!");
            wasConnected = true;
        }
        // Keep connection alive
        mqttClient.loop();
    }
}

bool buildPayload(char *output, size_t outputSize)
{
    jsonData.clear();

    char timestampStr[32];
    sprintf(timestampStr, "%04d-%02d-%02dT%02d:%02d:%02dZ",
            gps.date.year(),
            gps.date.month(),
            gps.date.day(),
            gps.time.hour(),
            gps.time.minute(),
            gps.time.second());

    jsonData["device"]["id"] = DEVICE_ID;
    jsonData["gps"]["timestamp_utc"] = timestampStr;

    // Optional fields:
    if (gps.location.isValid())
    {
        jsonData["gps"]["location"]["lat"] = roundN(gps.location.lat(), 6);
        jsonData["gps"]["location"]["lng"] = roundN(gps.location.lng(), 6);
    }
    if (gps.speed.isValid())
        jsonData["gps"]["speed_kmh"] = roundN(gps.speed.kmph(), 1);
    if (gps.course.isValid())
        jsonData["gps"]["course_deg"] = roundN(gps.course.deg(), 1);
    if (gps.satellites.isValid())
        jsonData["gps"]["num_satellites"] = gps.satellites.value();
    if (gps.hdop.isValid())
        jsonData["gps"]["hdop"] = roundN(gps.hdop.hdop(), 2);

    return serializeJson(jsonData, output, outputSize) > 0;
}

// Ref: https://arduinojson.org/v6/how-to/configure-the-serialization-of-floats/
static inline double roundN(double value, int places)
{
    // Up to 6 places (1.0 -> no decimal, 10.0 -> 1 place,...)
    static const double factors[] = {1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0};
    return (value >= 0.0)
               ? (int)(value * factors[places] + 0.5) / factors[places]
               : (int)(value * factors[places] - 0.5) / factors[places];
}