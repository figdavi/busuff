import json
import random
from typing import Any, Literal

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties


# https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file#usage-and-api
# https://github.com/eclipse-paho/paho.mqtt.python/blob/master/examples/client_sub.py

# TODO: add broker and topics to .env, share with backend and sensors
# TODO: Update to MQTTv5 (If possible)


broker = "broker.hivemq.com"
port = 1883
topic = "mqtt_iot_123321/busuff"
transport: Literal["tcp", "websockets", "unix"] = "tcp"
protocol = mqtt.MQTTv311


def connect_mqtt() -> mqtt.Client:
    def on_connect(
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: str,
        properties: Properties,
    ):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {reason_code}\n")
            return

    # If you want to use a specific client id, use
    # mqtt.Client("client-id")
    # but note that the client id must be unique on the broker. Leaving the
    # client id parameter empty will generate a random id for you.

    client = mqtt.Client(
        transport=transport,
        protocol=protocol,
        callback_api_version=CallbackAPIVersion.VERSION2,
    )
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt.Client):
    def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage):
        print(f"From topic: '{msg.topic}', message: ")
        try:
            data = json.loads(msg.payload.decode())
            print(json.dumps(data, indent=4))
        except Exception as e:
            print(e)

    # subscribe method of mqtt.Client
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
