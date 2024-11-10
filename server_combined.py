import paho.mqtt.client as mqtt
import time
import os
import random
import pygame
import numpy as np
from datetime import datetime

# Initialize pygame mixer
pygame.mixer.init()

# Path to the music folder
MUSIC_FOLDER = "music"

# Load all music files from the folder
music_files = [file for file in os.listdir(MUSIC_FOLDER) if file.endswith(('.mp3', '.wav', '.ogg'))]

if not music_files:
    print("No music files found in the 'music' folder.")
    exit()
    
def play_random_song():
    """Load and play a random song from the music folder."""
    song = random.choice(music_files)
    pygame.mixer.music.load(os.path.join(MUSIC_FOLDER, song))
    pygame.mixer.music.play()
    print(f"Playing: {song}")
    
playing = False
def on_connect(client, userdata, flags, rc):
   global flag_connected
   flag_connected = 1
   client_subscriptions(client)
   print("Connected to MQTT server")
   
   play_random_song()
   global playing
   playing = True  # Keep track of whether music is currently playing

def on_disconnect(client, userdata, rc):
   global flag_connected
   flag_connected = 0
   print("Disconnected from MQTT server")
   
buffer = []
decision = []

def processData(new_value):

    decision = -1
    threshold = 10

    buffer.append(new_value)

    if len(buffer) < 11: 
        decision = 3  # Buffer is not full

    else:
        buffer.pop(0)
        N = len(buffer)
        mean_kernel = np.ones(N)/N
        buffer_filt = np.convolve(buffer, mean_kernel, mode='same')
        last_value = buffer_filt[-1] - 14
        
        if last_value > threshold:  # arm goes towards mouth
            decision = 2  # stop music
        elif last_value < -threshold:  # arm goes away from mouth
            decision = 1  # start music
        else:
            decision = 8000  # error happened
                
    return decision

# a callback functions 
def callback_esp32_sensor1(client, userdata, msg):
    print('ESP sensor1 data: ', msg.payload.decode('utf-8'))
    global playing
    
    new_data = msg.payload.decode('utf-8')
    
    file_path = "logs.txt"
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Open the file in append mode
    with open(file_path, 'a') as file:
        # Write the timestamp and data
        file.write(f"{timestamp} - {new_data}\n")

    new_data_list = new_data.split(",")
    new_data_x = float(new_data_list[0])
    new_data_y = float(new_data_list[1])
    new_data_z = float(new_data_list[2])

    action = processData(new_data_z)
    # action = random.randint(0, 2)  # Randomly pick 0, 1, or 2
    if action == 0:
        print("Action: Do nothing")
        #continue  # Do nothing and continue to the next iteration

    elif action == 1:
        if not playing:
            pygame.mixer.music.unpause()
            playing = True
            print("Action: Unpause music")

    elif action == 2:
        if playing:
            pygame.mixer.music.pause()
            playing = False
            print("Action: Pause music")

    # If the music has stopped naturally, load and play another random song
    if not pygame.mixer.music.get_busy() and playing:
        play_random_song()

def callback_esp32_sensor2(client, userdata, msg):
    print('ESP sensor2 data: ', str(msg.payload.decode('utf-8')))

def callback_rpi_broadcast(client, userdata, msg):
    print('RPi Broadcast message:  ', str(msg.payload.decode('utf-8')))

def client_subscriptions(client):
    client.subscribe("esp32/#")
    client.subscribe("rpi/broadcast")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "rpi_client1") #this should be a unique name
flag_connected = 0

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.message_callback_add('esp32/sensor1', callback_esp32_sensor1)
client.message_callback_add('esp32/sensor2', callback_esp32_sensor2)
client.message_callback_add('rpi/broadcast', callback_rpi_broadcast)
client.connect('127.0.0.1',1883)
# start a new thread
client.loop_start()
client_subscriptions(client)
print("......client setup complete............")


while True:
    time.sleep(4)
    if (flag_connected != 1):
        print("trying to connect MQTT server..")
