import paho.mqtt.client as mqtt
import time
import os
import random
import pygame
import numpy as np
from datetime import datetime
from vqf import VQF

log_to_file = False

# Initialize the VQF filter
vqf = VQF(0.01)


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

# Initialize variables for tracking gravity and state
gravity_z = 0.0  # Estimate of gravity component
alpha = 0.9  # Smoothing factor for EMA, closer to 1 for a slower response to change
velocity_z = 0.0
hand_position = None  # Can be "up" or "down"
up_velocity_threshold = 0.5  # Threshold indicating "up" position
down_velocity_threshold = -0.5  # Threshold indicating "down" position
stabilization_threshold = 0.1  # Small threshold for detecting velocity stabilization

def processRawData(accel_data, gyro_data, dt=0.01):
    """
    Process accelerometer and gyroscope data using VQF to determine the "up" acceleration.

    Parameters:
    - accel_data: Tuple (ax, ay, az) in m/s^2 representing accelerometer data.
    - gyro_data: Tuple (gx, gy, gz) in rad/s representing gyroscope data.
    - dt: Time interval between readings (in seconds).

    Returns:
    - up_acceleration: The "up" component of acceleration after gravity is removed.
    """
    # Update VQF with new data
    vqf.update(gyro_data, accel_data)

    # Get orientation as a quaternion
    q = vqf.getQuat3D()

    # Convert quaternion to rotation matrix
    R = quaternion_to_rotation_matrix(q)

    # Rotate accelerometer data to align with Earth frame
    accel_earth_frame = R @ np.array(accel_data)

    # The "up" acceleration is the Z-component in the Earth frame minus gravity (9.81 m/s^2)
    up_acceleration = accel_earth_frame[2] - 9.81

    return up_acceleration

def quaternion_to_rotation_matrix(q):
    """
    Convert a quaternion to a rotation matrix.

    Parameters:
    - q: Quaternion [w, x, y, z]

    Returns:
    - 3x3 rotation matrix
    """
    w, x, y, z = q
    return np.array([
        [1 - 2*y**2 - 2*z**2, 2*x*y - 2*z*w, 2*x*z + 2*y*w],
        [2*x*y + 2*z*w, 1 - 2*x**2 - 2*z**2, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w, 2*y*z + 2*x*w, 1 - 2*x**2 - 2*y**2]
    ])

def processData(new_value, dt=0.1):
    global gravity_z, velocity_z, hand_position

    # Update gravity estimate using EMA
    gravity_z = alpha * gravity_z + (1 - alpha) * new_value

    # Calculate dynamic acceleration by removing gravity component
    dynamic_z_accel = new_value - gravity_z

    # Integrate the dynamic acceleration to estimate velocity
    velocity_z += dynamic_z_accel * dt
    print("velocity is", velocity_z)

    # Check if velocity stabilizes within thresholds for "up" or "down"
    if abs(velocity_z) < stabilization_threshold:
        # If velocity is close to zero, assume hand is stable in previous position
        return 2 if hand_position == "up" else 1 if hand_position == "down" else 0

    elif velocity_z >= up_velocity_threshold and hand_position != "up":
        # Hand moves to "up" position
        hand_position = "up"
        return 2

    elif velocity_z <= down_velocity_threshold and hand_position != "down":
        # Hand moves to "down" position
        hand_position = "down"
        return 1

    return 0  # No significant change



# a callback functions 
def callback_esp32_sensor1(client, userdata, msg):
    print('ESP sensor1 data: ', msg.payload.decode('utf-8'))
    global playing
    
    new_data = msg.payload.decode('utf-8')
    
    if log_to_file:
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
    gyro_x = float(new_data_list[3])
    gyro_y = float(new_data_list[4])
    gyro_z = float(new_data_list[5])
    
    accel_up = processRawData(np.array([new_data_x, new_data_y, new_data_z]), np.array([gyro_x, gyro_y, gyro_z]), 0.01)
    action = processData(accel_up, 0.01)
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
