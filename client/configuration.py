import yaml


def import_configuration():
    # Load configuration
    with open('/opt/en-expoert/modbus-client/config.yml', 'r', encoding='utf8') as f:
        config = yaml.safe_load(f)

    modbus_config = config['modbus']
    mqtt_config = config['mqtt']
    scan_interval = config['interval']

    return modbus_config, mqtt_config, scan_interval
