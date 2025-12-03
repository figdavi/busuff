import json
from typing import Any, Literal
from app.core.database import salvar_leitura

import paho.mqtt.client as mqttc
import paho.mqtt.reasoncodes as mqttrc
import paho.mqtt.properties as mqttprop
import paho.mqtt.enums as mqtte

# https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
# https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file#usage-and-api
# https://www.emqx.com/en/blog/how-to-use-mqtt-in-python

# TODO: Update to MQTTv5 (If possible)
# TODO: Validate data

broker = "broker.hivemq.com"
port = 1883
topic = "mqtt_iot_123321/busuff"
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
        callback_api_version=mqtte.CallbackAPIVersion.VERSION2,
    )
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqttc.Client):
    def on_message(client: mqttc.Client, userdata: Any, msg: mqttc.MQTTMessage):
        print(f"From topic: '{msg.topic}', message: ")
        try:
            data = json.loads(msg.payload.decode())
            print(json.dumps(data, indent=4))

            # Salva os dados no Banco
            salvar_leitura(data)

        except Exception as e:
            # Se houver erro na decodificação JSON OU no salvamento no banco
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
