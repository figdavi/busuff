import json
from typing import Any, Literal
import os
from app.crud import create_position
from app.utils import parse_position
from app.core.database import SessionLocal

import paho.mqtt.client as mqttc
import paho.mqtt.reasoncodes as mqttrc
import paho.mqtt.properties as mqttprop
import paho.mqtt.enums as mqttenums

broker = os.getenv("MQTT_BROKER_IP")
port = (
    int(os.getenv("MQTT_BROKER_PORT", 0))
    if os.getenv("MQTT_BROKER_PORT") is not None
    else None
)
topic = "busuff/#"
transport: Literal["tcp", "websockets", "unix"] = "tcp"
protocol = mqttc.MQTTv5


def connect_mqtt(mqtt_broker_ip: str, mqtt_broker_port: int) -> mqttc.Client | None:
    def on_connect(
        client: mqttc.Client,
        userdata: Any,
        flags: mqttc.ConnectFlags,
        reason_code: mqttrc.ReasonCode,
        properties: mqttprop.Properties | None,
    ):
        # https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901031
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {reason_code}\n")
            return

    # If you want to use a specific client id, use
    # mqtt.Client("client-id")
    # but note that the client id must be unique on the broker. Leaving the
    # client id parameter empty will generate a random id for you.

    client = mqttc.Client(
        transport=transport,
        protocol=protocol,
        callback_api_version=mqttenums.CallbackAPIVersion.VERSION2,
    )
    client.on_connect = on_connect

    if not mqtt_broker_ip:
        raise ValueError("Parameter 'mqtt_broker_ip' cannot be empty.")
    if not mqtt_broker_port:
        raise ValueError("Parameter 'mqtt_broker_port' cannot be empty.")

    client.connect(mqtt_broker_ip, mqtt_broker_port)
    return client


def subscribe(client: mqttc.Client):
    def on_message(client: mqttc.Client, userdata: Any, msg: mqttc.MQTTMessage):
        try:
            data = json.loads(msg.payload.decode())
            print(f"From topic: '{msg.topic}', message: ")
            print(json.dumps(data, indent=4))

            position = parse_position(data)

            with SessionLocal.begin() as session:
                create_position(session, position)
                print("Position saved.")

        except Exception as e:
            print(f"Erro no processamento/salvamento da mensagem: {e}")

    # subscribe method of mqtt.Client
    client.subscribe(topic)
    client.on_message = on_message


def run():
    try:
        if broker is None:
            print("Error: broker not defined")
            return
        if port is None:
            print("Error: port not defined")
            return

        client = connect_mqtt(broker, port)

        if not client:
            print("Error: client not defined")
            return

        subscribe(client)
        client.loop_forever()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run()
