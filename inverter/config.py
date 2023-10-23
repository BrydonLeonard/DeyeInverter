import configparser
import paho.mqtt.client as paho

class Config:
    def __init__(self, config_path = './config.cfg'):
        config_parser = configparser.RawConfigParser()
        config_parser.read(config_path)

        self.inverter_ip = config_parser.get('inverter', 'inverter_ip')
        self.inverter_port = config_parser.getint('inverter', 'inverter_port')
        self.inverter_sn = config_parser.getint('inverter', 'inverter_sn')
        self.inverter_installed_power = config_parser.getint('inverter', 'installed_power')

        self.mqtt_enabled = config_parser.getboolean('mqtt', 'enabled', fallback=False)
        self.mqtt_server = config_parser.get('mqtt', 'server', fallback='')
        self.mqtt_port = config_parser.getint('mqtt', 'port', fallback=1883)
        self.mqtt_topic = config_parser.get('mqtt', 'topic', fallback='')
        self.mqtt_username = config_parser.get('mqtt', 'username', fallback='')
        self.mqtt_password = config_parser.get('mqtt', 'password', fallback='')

        self.influxdb_enabled = config_parser.getboolean('influxdb', 'enabled', fallback=False)
        self.influxdb_token = config_parser.get('influxdb', 'token', fallback='')
        self.influxdb_org = config_parser.get('influxdb', 'org', fallback='')
        self.influxdb_url = config_parser.get('influxdb', 'url', fallback='')
        self.influxdb_bucket = config_parser.get('influxdb', 'bucket', fallback='')

        self.logging_path = config_parser.get('logging', 'path', fallback=None)