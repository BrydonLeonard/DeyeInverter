from inverter.inverter_client import InverterClient
from inverter.config import Config
from inverter.mqtt_client import MqttClient
import logging


def setup_logging():
    if (config.logging_path != None):
        logging.basicConfig(
            filename=config.logging_path, 
            format="%(asctime)s [%(levelname)s] %(message)s",
            level=logging.DEBUG
        )
    else:
        logging.basicConfig(
            format="%(asctime)s [%(levelname)s] %(message)s",
            level=logging.DEBUG
        )

if __name__ == "__main__":
    config = Config("./config.cfg") 
    setup_logging()

    logging.info("Starting up")
    inverter_client = InverterClient(config)
    response = inverter_client.read_realtime_data()

    mqtt_client = MqttClient(config)
    mqtt_client.write_to_mqtt(response)

    logging.info("Done!")

    print(response)