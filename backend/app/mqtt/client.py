import json
from typing import Any, Literal
from app.crud import save_position
from app.core.database import SessionLocal

import paho.mqtt.client as mqttc
import paho.mqtt.reasoncodes as mqttrc
import paho.mqtt.properties as mqttprop
import paho.mqtt.enums as mqttenums


broker = "broker.hivemq.com"
port = 1883
topic = "busuff/#"
transport: Literal["tcp", "websockets", "unix"] = "tcp"
protocol = mqttc.MQTTv5


def connect_mqtt() -> mqttc.Client:
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
    client.connect(broker, port)
    return client


def subscribe(client: mqttc.Client):
    def on_message(client: mqttc.Client, userdata: Any, msg: mqttc.MQTTMessage):
        try:
            data = json.loads(msg.payload.decode())
            print(f"From topic: '{msg.topic}', message: ")
            print(json.dumps(data, indent=4))

            with SessionLocal.begin() as session:
                save_position(session, data)
                print("Position saved.")

        except Exception as e:
            print(f"Erro no processamento/salvamento da mensagem: {e}")

    # subscribe method of mqtt.Client
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
