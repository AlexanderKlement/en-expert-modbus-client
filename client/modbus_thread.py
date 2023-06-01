import json
import threading
import logging
import configuration
import mqtt_helper
import modbus_helper


class ModbusThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        modbus_config, mqtt_config, scan_interval = configuration.import_configuration()

        mqtt_client = mqtt_helper.create_mqtt_client(mqtt_config['broker'], mqtt_config['port'],
                                                     mqtt_config['username'], mqtt_config['password'])

        mqtt_client.connect(mqtt_config['broker'], mqtt_config['port'])

        for modbus_slaves in modbus_config['slaves']:

            try:
                slave_dict = modbus_helper.create_slave_dict(slave_name=modbus_slaves['name'],
                                                             slave_ip=modbus_slaves['host'],
                                                             slave_port=modbus_slaves['port'])
            except Exception as e:
                logging.error('Error creating slave dictionary. Skipping... : {}'.format(e))
                continue

            slave_dict_json = json.dumps(slave_dict)

            mqtt_client.publish(mqtt_config['topic'], payload=slave_dict_json)
            # Log the event
            logging.info('Published data to MQTT broker')
        else:
            # Log the error
            logging.error('Error reading Modbus device')

        mqtt_client.disconnect()
