import paho.mqtt.client as mqtt
import time

# MQTT setup
broker = '127.0.0.1'  # Replace with your broker address if different
port = 1883  # Default MQTT port for most brokers
topic = 'esp32/sensor1'

# Read file and send data
def read_and_publish(file_path):
    # Create MQTT client and connect
    client = mqtt.Client()
    client.connect(broker, port, 60)
    
    # Read the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Split line by " - " to remove the timestamp and keep only the data
            data = line.split(" - ", 1)[-1].strip()
            # Send each data as a message to the MQTT topic
            client.publish(topic, data)
            print(f"Published: {data} to topic {topic}")
            time.sleep(0.1)  # Optional delay between messages for testing

    # Disconnect after publishing
    client.disconnect()

# Example usage
file_path = 'logs.txt'
read_and_publish(file_path)
