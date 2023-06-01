#!/bin/sh
# /etc/init.d/en-expert-modbus-client.sh

case "$1" in
  start)
    echo "Starting en-expert modbus service"
    /usr/local/bin/python3 /opt/en-expert/modbus-client/main.py &
    ;;
  stop)
    echo "Stopping en-expert modbus service"
    pkill -f /opt/en-expert/modbus-client/main.py
    ;;
  restart)
    echo "Restarting en-expert modbus service"
    pkill -f /opt/en-expert/modbus-client/main.py
    /usr/local/bin/python3 /opt/en-expert/modbus-client/main.py &
    ;;
  *)
    echo "Usage: /etc/init.d/en-expert-modbus-client {start|stop|restart}"
    exit 1
    ;;
esac

exit 0




