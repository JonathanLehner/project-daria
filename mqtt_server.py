import time
from paho.mqtt import client as mqtt

# MQTT configuration
broker_ip = "0.0.0.0"  # Bind to all interfaces
broker_port = 1883
keep_alive = 60

# MQTT Server setup
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Server connected successfully")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_disconnect(client, userdata, rc):
    print("MQTT Server disconnected")

def on_message(client, userdata, msg):
    print(f"Message received: Topic: {msg.topic}, Payload: {msg.payload.decode()}")

# Initialize and configure the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "MQTT_Server")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# Bind the server to the configured IP and port
client.connect(broker_ip, broker_port, keep_alive)

# Subscribe to a topic the ESP32 will publish to
client.subscribe("rpi/broadcast")  # Make sure this matches your ESP32 topic

# Start the loop to listen for connections and messages
print("MQTT server is listening...")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Shutting down MQTT server")
    client.disconnect()
