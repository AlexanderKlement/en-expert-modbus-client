from pyModbusTCP.client import ModbusClient
import sys

# Parameter für die Verbindung zum Nemo 96HD
NEMO_IP = "192.168.1.100"  # Ändere dies auf die IP-Adresse des Nemo 96HD
NEMO_PORT = 502
NEMO_ID = 21

# Funktion zum Verbinden und Auslesen der Werte
def read_data(ip, port, device_id):
    try:
        client = ModbusClient(host=ip, port=port, unit_id=device_id)
        client.open()

        # Lesen der Werte für Phasenspannung, Strom, Frequenz und Leistung für alle drei Phasen
        voltage_registers = [0x301, 0x305, 0x309]
        current_registers = [0x30d, 0x311, 0x315]
        power_registers = [0x35d, 0x361, 0x365]
        frequency_register = 0x339

        voltages = []
        currents = []
        powers = []
        for i in range(3):
            voltage_data = client.read_input_registers(voltage_registers[i], 1)
            current_data = client.read_input_registers(current_registers[i], 1)
            power_data = client.read_input_registers(power_registers[i], 2)

            voltages.append(voltage_data[0] / 1000)
            currents.append(current_data[0] / 1000)
            power = int(power_data[0]) << 16 | int(power_data[1])
            power = float.fromhex(hex(power))
            powers.append(power)

        frequency_data = client.read_input_registers(frequency_register, 1)
        frequency = frequency_data[0] / 10.0

        # Ausgabe der Ergebnisse
        for i in range(3):
            print(f"Phase {i + 1}:")
            print(f"  Spannung: {voltages[i]:.2f} V")
            print(f"  Strom: {currents[i]:.2f} A")
            print(f"  Leistung: {powers[i]:.2f} W")
        print(f"Frequenz: {frequency:.2f} Hz")

        client.close()

    except Exception as e:
        print(f"Verbindungsfehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    read_data(NEMO_IP, NEMO_PORT, NEMO_ID)