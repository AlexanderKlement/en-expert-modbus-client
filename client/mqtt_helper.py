import paho.mqtt.client as mqtt

def create_mqtt_client(host: str, port: int, username: str = None, password: str = None) -> mqtt.Client:
    client = mqtt.Client()
    if username is not None and password is not None:
        client.username_pw_set(username=username, password=password)
    return client

