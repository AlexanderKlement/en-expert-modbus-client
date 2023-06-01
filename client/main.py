import logging
import time
import configuration
import modbus_thread

# Set up logging
logging.basicConfig(filename='/var/log/en-expert-modbus-client.sh.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def run_forever():
    _, _, scan_interval = configuration.import_configuration()

    while True:
        # Connect the MQTT client to the broker
        thread = modbus_thread.ModbusThread()
        thread.start()
        time.sleep(scan_interval)


if __name__ == '__main__':
    run_forever()
