from inverter.config import Config
import paho.mqtt.client as paho
import socket

class MqttClient:
    def __init__(self, config: Config):
        self.client = paho.Client("inverter_monitor")
        self.client.username_pw_set(username = config.mqtt_username, password = config.mqtt_password)
        self.client.connect(config.mqtt_server, config.mqtt_port)
        self.topic = config.mqtt_topic

    def write_to_mqtt(self, output):
        self.client.publish(self.topic, output)