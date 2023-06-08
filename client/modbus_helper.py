import logging

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.framer.rtu_framer import ModbusRtuFramer
from pymodbus.payload import BinaryPayloadDecoder

from modbus_data_format_enum import ModbusDataFormat


def create_modbus_client(host: str, port: int) -> ModbusTcpClient:
    return ModbusTcpClient(host=host, port=port, framer=ModbusRtuFramer)


def read_modbus_data_point(client: ModbusTcpClient, address: int, data_format: ModbusDataFormat):
    slave = 0x00

    if data_format in [ModbusDataFormat.U_WORD, ModbusDataFormat.S_WORD]:
        count = 1
    elif data_format in [ModbusDataFormat.UD_WORD, ModbusDataFormat.SD_WORD]:
        count = 2
    else:
        raise NotImplementedError("Data format {} not implemented".format(data_format))

    request = client.read_holding_registers(address=address, count=count, slave=slave)

    value = None

    try:
        decoder = BinaryPayloadDecoder.fromRegisters(request.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        if data_format == ModbusDataFormat.U_WORD:
            value = decoder.decode_16bit_uint()
        elif data_format == ModbusDataFormat.S_WORD:
            value = decoder.decode_16bit_int()
        elif data_format == ModbusDataFormat.UD_WORD:
            value = decoder.decode_32bit_uint()
        elif data_format == ModbusDataFormat.SD_WORD:
            value = decoder.decode_32bit_int()
        else:
            raise NotImplementedError("Data format {} not implemented".format(data_format))
    except Exception as e:
        logging.error("Could not decode modbus data point: {}".format(e))
    return value


def create_slave_dict(slave_name: str, slave_ip: str, slave_port: int) -> dict:
    client = create_modbus_client(host=slave_ip, port=slave_port)

    current_transformer_ration = read_modbus_data_point(client=client, address=0x100,
                                                        data_format=ModbusDataFormat.U_WORD)
    voltage_transformer_ration = read_modbus_data_point(client=client, address=0x102,
                                                        data_format=ModbusDataFormat.U_WORD)
    kta_times_ktv = current_transformer_ration * voltage_transformer_ration

    phase_voltage_mV = read_modbus_data_point(client=client, address=0x301, data_format=ModbusDataFormat.UD_WORD)

    active_power_W = read_modbus_data_point(client=client, address=0x319, data_format=ModbusDataFormat.UD_WORD)
    active_power_W = convert_power(value=active_power_W, kta_times_ktv=kta_times_ktv)

    apparent_power_W = read_modbus_data_point(client=client, address=0x321, data_format=ModbusDataFormat.UD_WORD)
    apparent_power_W = convert_power(value=apparent_power_W, kta_times_ktv=kta_times_ktv)

    positive_active_energy_W = read_modbus_data_point(client=client, address=0x325,
                                                      data_format=ModbusDataFormat.UD_WORD)
    positive_active_energy_W = convert_energy(value=positive_active_energy_W, kta_times_ktv=kta_times_ktv)

    negative_active_energy_W = read_modbus_data_point(client=client, address=0x335,
                                                      data_format=ModbusDataFormat.UD_WORD)
    negative_active_energy_W = convert_energy(value=negative_active_energy_W, kta_times_ktv=kta_times_ktv)

    frequency_Hz = read_modbus_data_point(client=client, address=0x339, data_format=ModbusDataFormat.U_WORD) / 10

    thd_v1_percent = read_modbus_data_point(client=client, address=0x390, data_format=ModbusDataFormat.U_WORD)
    phase_voltage_max_mV = read_modbus_data_point(client=client, address=0x3c4, data_format=ModbusDataFormat.UD_WORD)

    slave_dict = {
        "name": slave_name,
        "ip": slave_ip,
        "port": slave_port,
        "phase_voltage_mV": phase_voltage_mV,
        "active_power_W": active_power_W,
        "apparent_power_W": apparent_power_W,
        "positive_active_energy_W": positive_active_energy_W,
        "negative_active_energy_W": negative_active_energy_W,
        "frequency_Hz": frequency_Hz,
        "thd_v1_percent": thd_v1_percent,
        "phase_voltage_max_mV": phase_voltage_max_mV,
    }

    client.close()

    return slave_dict


def convert_power(value: int, kta_times_ktv: int) -> int:
    if kta_times_ktv < 5000:
        return int(value / 100)
    return value


def convert_energy(value: int, kta_times_ktv: int) -> int:
    if kta_times_ktv < 10:
        return int(value / 10)
    if kta_times_ktv < 100:
        return int(value / 100)
    if kta_times_ktv < 1000:
        return int(value / 1000)
    if kta_times_ktv < 10000:
        return int(value / 10000)
    if kta_times_ktv < 100000:
        return int(value / 100000)
    return value
