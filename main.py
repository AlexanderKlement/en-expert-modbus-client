import yaml
import logging
import paho.mqtt.client as mqtt
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import time

# Set up logging
logging.basicConfig(filename='/var/log/en-expert-modbus.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

modbus_config = config['modbus']
mqtt_config = config['mqtt']
scan_interval = config['interval']

# Create a Modbus client
modbus_client = ModbusClient(modbus_config['host'], port=modbus_config['port'])

# Create an MQTT client
mqtt_client = mqtt.Client()
if 'username' in mqtt_config and 'password' in mqtt_config:
    username = mqtt_config['username']
    password = mqtt_config['password']

    mqtt_client.username_pw_set(username=username, password=None)

# Connect the MQTT client to the broker
mqtt_client.connect(mqtt_config['broker'], mqtt_config['port'])

while True:
    if not modbus_client.connect(): #This could maybe lead to errors. Maybe we will have to setup a new connection every interval
        logging.error('Could not connect to Modbus device')
        time.sleep(scan_interval)
        continue

    # Read data from Modbus device
    rr = modbus_client.read_holding_registers(1, 1)
    if not rr.isError():
        # Publish data to MQTT broker
        mqtt_client.publish(mqtt_config['topic'], rr.registers[0])
        # Log the event
        logging.info('Published data to MQTT broker')
    else:
        # Log the error
        logging.error('Error reading Modbus device')

    # Sleep for the specified interval
    time.sleep(scan_interval)