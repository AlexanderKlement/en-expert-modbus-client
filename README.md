# EnExpert Modbus Service (for ResIOT Gateway x2)

This script is reading data from a modbus device and sends it to a backend via MQTT

## Install Notes

1. Copy the files on the device (Suggestion: /opt/en-expert/modbus/)
2. Rename the config.example.yml file to config.yml and edit it to match your setup.
3. Make sure python version 3.5.3 is installed
    ```bash
    curl -s update.resiot.io/extra/python3/resiot_gw_x2_x4_x7_update_python_to_353.sh | bash
4. Install the requirements with pip3 install -r requirements.txt
5. Run the script with
   ```bash
   python3 main.py
   ```
   and let it run a few minutes to see if it works.
6. If it works, you can copy the service file to /etc/init.d/en-expert-modbus make it executable
   ```bash
   chmod +x /etc/init.d/en-expert-modbus
   ```
   and enable it with
   ```bash
   update-rc.d /etc/init.d/en-expert-modbus defaults
   ```
   The defaults option sets the script to start up in runlevels 2, 3, 4, and 5 (which are the usual multi-user
   runlevels), and to shut down in runlevels 0, 1, and 6 (halt, single-user mode, and reboot, respectively).)
7. Start the service and check if it works (maybe also perform a power cut) <br>
   Remember: Since we have no `service`, `systemctl` or other System V wrapper , we have to use the init.d script
   directly
   ```bash
   service /etc/init.d/en-expert-modbus start
   ```
   ```bash
   service /etc/init.d/en-expert-modbus status
   ```
   ```bash
   service /etc/init.d/en-expert-modbus stop
   ```

NOTE: Log files are located in /var/log/en-expert-modbus.log

## OpenVPN Guide

OpenVPN has caused a lot of problems, because first it wouldn't connect (We had an DNS issue there, which would
recommend to
use the public IPv6 address to connect to the VPN server. OpenVPN does only support IPv4, so keep that in mind when
playing
with configuration) <br>
There was also a problem with the nslookup, because the dns server that the lte provider was serving, did not allow to
use external
connections. Therefor we allowed DNS bleeding and did a separate routing for the DNS server, but the DNS server
responses were
strange. <br>
Using another DNS server for the ppp0 device is not possible either, because we maybe need the DNS server for the
initial P2P connection.
The solution I would suggest is updating the resolv.conf when the VPN connection is established, and reverting it if the
VPN connection goes down: <br>

1. Create two files in /etc/openvpn/ with the following content:
    - update-resolv-conf-down.sh
    ```bash
   #!/bin/bash
   echo "nameserver 194.151.228.34" > /etc/resolv.conf
   echo "nameserver 194.151.228.18" >> /etc/resolv.conf
   ```
    - update-resolv-conf-up.sh
    ```bash
   #!/bin/bash
   echo "nameserver 8.8.8.8" > /etc/resolv.conf
   echo "nameserver 8.8.4.4" >> /etc/resolv.conf
   ```
2. Make the both executable:
    ```bash
    chmod +x /etc/openvpn/update-resolv-conf-down.sh
    chmod +x /etc/openvpn/update-resolv-conf-up.sh
    ```
3. Add this lines to the .conf file in the same folder (above the &lt;ca> Tag is fine):
    ```bash
    script-security 2
    up /etc/openvpn/update-resolv-conf-up.sh
    down /etc/openvpn/update-resolv-conf-down.sh
    ```

