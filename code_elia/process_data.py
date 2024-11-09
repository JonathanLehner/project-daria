import serial
import csv
import time

# Configure the serial connection (update 'COM3' to your Arduino's serial port)
SERIAL_PORT = 'COM5'  # For Windows, replace with your port name
BAUD_RATE = 115200

# Open the serial port
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)


time0 = None
start_time = time.time()
print(start_time)
try:
    while True:
        # Read a line from the serial port and decode it to a string
        line = ser.readline().decode('utf-8').strip()
        # Split the line by commas
        data = line.split(',')
        

        # Check if we have the correct data format 
        if len(data) == 7:
            for i in range(1, len(data)):
                data[i] = float(data[i])
            t, x_acc, y_acc, z_acc, x_gyro, y_gyro, z_gyro = data
            t = int(t)
            if time0 is None:
                time0 = t
                print(time0)
            t = t - time0
            # Get the current timestamp
            timestamp = start_time + t
            
            
            
            # Print data for real-time monitoring
            print(f"{timestamp:.2f}, {x_acc}, {y_acc}, {z_acc}, {x_gyro}, {y_gyro}, {z_gyro}")

except KeyboardInterrupt:
    print("Data collection stopped.")

finally:
    # Close the serial connection
    ser.close()