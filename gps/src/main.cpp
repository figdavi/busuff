// Libraries
#include <Arduino.h>
#include "secrets.h" // WiFi and Hotspot credentials
#include <TinyGPS++.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SoftwareSerial.h>

// Pin Definitions
static const int GPS_RX_PIN = D7;
static const int WIFI_LED = D1;
static const int MQTT_LED = D2;

// Constants
static const int GPS_BAUD = 9600;
static const int SERIAL_BAUD = 115200;
static const char MQTT_BROKER[] = "broker.hivemq.com";
static const char MQTT_TOPIC[] = "mqtt_iot_123321/busuff";
static const int MQTT_PORT = 1883;
static const unsigned long MQTT_PUB_INTERVAL_MS = 5000;
static const unsigned long WIFI_RECONNECT_INTERVAL_MS = 5000;
static const unsigned long MQTT_RECONNECT_INTERVAL_MS = 3000;

// Global Objects
SoftwareSerial gpsSerial(GPS_RX_PIN);
TinyGPSPlus gps;
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
JsonDocument jsonData;

// Device ID (unique per ESP8266)
char DEVICE_ID[32];

// Helper Macros for Debugging (defined in platformio.ini)
#if LOG_LEVEL >= 1
#define DEBUG_PRINT(x) Serial.print(x)
#define DEBUG_PRINTLN(x) Serial.println(x)
#else
#define DEBUG_PRINT(x)
#define DEBUG_PRINTLN(x)
#endif

// Function declarations
void checkMQTT();
void checkWiFi();
static inline void readGPS();
bool buildPayload(char *output, size_t outputSize);
bool buildTimestamp(char *output, size_t outputSize);
static inline double roundN(double value, int places);

// Setup
void setup()
{
    gpsSerial.begin(GPS_BAUD);
    Serial.begin(SERIAL_BAUD);

    // Led on HIGH == Disconnected
    pinMode(WIFI_LED, OUTPUT);
    pinMode(MQTT_LED, OUTPUT);
    digitalWrite(WIFI_LED, HIGH);
    digitalWrite(MQTT_LED, HIGH);

    snprintf(DEVICE_ID, sizeof(DEVICE_ID), "bus_%u", ESP.getChipId());

    WiFi.begin(WIFI_SSID, WIFI_PASS);
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
}

// Main Loop
void loop()
{
    /* NOTE: Keep all tasks non-blocking, since watchdog needs constant feed.
     * It gets it through the end of each loop() iteration
     */

    checkWiFi();
    checkMQTT();
    readGPS();

    // Check if interval has passed
    static unsigned long lastSend = 0;
    if (millis() - lastSend < MQTT_PUB_INTERVAL_MS)
    {
        return;
    }
    lastSend = millis();

    // Try to build the json payload
    char message[256];
    if (!buildPayload(message, sizeof(message)))
    {
        DEBUG_PRINTLN("Failed to build payload.");
        return;
    }
    DEBUG_PRINTLN(message);

    // Try to publish the json payload to broker
    if (!mqttClient.connected())
    {
        DEBUG_PRINTLN("MQTT not connected, skipping publish");
        return;
    }
    mqttClient.publish(MQTT_TOPIC, message);
}

void checkWiFi()
{
    static unsigned long lastAttempt = 0;
    static bool wasConnected = false;

    if (WiFi.status() != WL_CONNECTED)
    {
        if (millis() - lastAttempt > WIFI_RECONNECT_INTERVAL_MS)
        {
            lastAttempt = millis();

            DEBUG_PRINT("Trying to connect to WiFi: ");
            DEBUG_PRINTLN(WiFi.SSID());
            WiFi.reconnect();
        }
        wasConnected = false;
        digitalWrite(WIFI_LED, HIGH);
    }
    else if (!wasConnected)
    {
        DEBUG_PRINTLN("WiFi connected!");
        wasConnected = true;
        digitalWrite(WIFI_LED, LOW);
    }
}

void checkMQTT()
{
    static unsigned long lastAttempt = 0;
    static bool wasConnected = false;
    if (!mqttClient.connected())
    {
        // Try only if we have WiFi
        if (WiFi.status() == WL_CONNECTED && millis() - lastAttempt > MQTT_RECONNECT_INTERVAL_MS)
        {
            lastAttempt = millis();
            DEBUG_PRINT("Trying to connect to MQTT broker: ");
            DEBUG_PRINTLN(MQTT_BROKER);
            mqttClient.connect(DEVICE_ID);
        }
        wasConnected = false;
        digitalWrite(MQTT_LED, HIGH);
    }
    else
    {
        if (!wasConnected)
        {
            DEBUG_PRINTLN("MQTT connected!");
            wasConnected = true;
            digitalWrite(MQTT_LED, LOW);
        }
        // Keep connection alive
        mqttClient.loop();
    }
}

static inline void readGPS()
{
    while (gpsSerial.available() > 0)
    {
        gps.encode(gpsSerial.read());
    }
}

bool buildPayload(char *output, size_t outputSize)
{
    /* Two important notes for checking data:
     * 1. https://github.com/mikalhart/TinyGPSPlus/issues/107: isValid() does not really mean valid data.
     * 2. https://forum.arduino.cc/t/tinygpsplus-isupdated-qustion/1233296: isUpdated() indicates whether the object’s value has been read (not necessarily changed) since the last time you queried it.
     */
    jsonData.clear();

    jsonData["device"]["id"] = DEVICE_ID;

    char timestampStr[32];
    if (!buildTimestamp(timestampStr, sizeof(timestampStr)))
    {
        DEBUG_PRINTLN("Invalid timestamp, skipping payload build.");
        return false;
    }
    jsonData["gps"]["timestamp_utc"] = timestampStr;

    // Optional fields:
    if (gps.location.isValid() && gps.location.isUpdated())
    {
        jsonData["gps"]["location"]["lat"] = roundN(gps.location.lat(), 6);
        jsonData["gps"]["location"]["lng"] = roundN(gps.location.lng(), 6);
    }
    if (gps.speed.isValid() && gps.speed.isUpdated())
        jsonData["gps"]["speed_kmh"] = roundN(gps.speed.kmph(), 1);
    if (gps.course.isValid() && gps.course.isUpdated())
        jsonData["gps"]["course_deg"] = roundN(gps.course.deg(), 1);
    if (gps.satellites.isValid() && gps.satellites.isUpdated())
        jsonData["gps"]["num_satellites"] = gps.satellites.value();
    if (gps.hdop.isValid() && gps.hdop.isUpdated())
        jsonData["gps"]["hdop"] = roundN(gps.hdop.hdop(), 2);

    return serializeJson(jsonData, output, outputSize) > 0;
}

bool buildTimestamp(char *output, size_t outputSize)
{
    /* NOTE: TinyGPS does internal timestamp prediction when no gps readings are available (we'll use those predictions).
     * Those predictions do not pass isValid()
     */

    // 1. Check if date and time have values inside basic ranges
    if (!(gps.date.year() >= 2025 &&
          gps.date.month() >= 1 && gps.date.month() <= 12 &&
          gps.date.day() >= 1 && gps.date.day() <= 31 &&
          gps.time.hour() < 24 &&
          gps.time.minute() < 60 &&
          gps.time.second() < 60))
        return false;

    static char lastTimestamp[32] = "";
    // Create currentTimestamp
    snprintf(output, outputSize, "%04u-%02u-%02uT%02u:%02u:%02uZ",
             gps.date.year(),
             gps.date.month(),
             gps.date.day(),
             gps.time.hour(),
             gps.time.minute(),
             gps.time.second());

    // 2. Check if timestamp has changed
    // isUpdated() does not check if value has changed and only works for non-predicted values
    if (strcmp(lastTimestamp, output) == 0)
        return false;

    strcpy(lastTimestamp, output);
    return true;
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