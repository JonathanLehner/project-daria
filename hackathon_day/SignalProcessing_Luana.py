#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
import pandas as pd

# Read file, split data by comma, and store in DataFrame
def read_and_publish(file_path):
    # Create an empty list to store parsed data rows
    data_rows = []

    # Initialize line counter
    line_count = 0

    # Read the file line by line
    with open(file_path, 'r') as file:
        for line in file:
            # Only process every 10th line (i.e., if line_count is divisible by 10)
            if line_count % 10 != 0:
                line_count += 1
                continue  # Skip lines that aren't the 10th
            
            # Split line by " - " to remove the timestamp and keep only the data
            data = line.split(" - ", 1)[-1].strip()
            
            # Split the data by comma to get individual values
            data_values = data.split(',')
            
            # Append the list of values to data_rows
            data_rows.append(data_values)

            # Optional: Print the data for verification
            #print(data_values)
            
            # Increment the line counter
            line_count += 1
            
            # Delay for MQTT testing (optional)
            time.sleep(0.1)

    # Create DataFrame from data_rows
    df = pd.DataFrame(data_rows)
    
    # Optional: Show the first few rows of the DataFrame for verification
    print(df.head())

    # Print total lines processed
    print(f"Processed {line_count} lines")

    return df  # Return the DataFrame if further processing is needed

# Example usage
file_path = 'logs.txt'
df = read_and_publish(file_path)


# In[2]:


import numpy as np
rows, columns = df.shape
print(f"Number of rows: {rows}")
print(f"Number of columns: {columns}")
# Example: Renaming specific columns
# Example: Changing column names to "Sensor1", "Sensor2", "Sensor3", etc.
df.columns = ["AccX", "AccY", "AccZ", "GyroX", "GyroY", "GyroZ"]  # Make sure the list length matches the number of columns


# In[3]:


import matplotlib.pyplot as plt

def plot_data(y_values, title, ylabel):
    plt.figure(figsize=(14, 7))

    # Plot each column in y_values
    for column in y_values.columns:
        plt.plot(y_values.index, y_values[column], label=column)  # Plot each column with label
    
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.grid()
    plt.tight_layout()
    plt.legend()  # Show legend to distinguish each line
    plt.show()

# Example usage with the df DataFrame
plot_data(df[["AccX", "AccY", "AccZ"]], 'Accelerometer Data', 'Accelerometer (m/s²)')
plot_data(df[["GyroX", "GyroY", "GyroZ"]], 'Gyro Data', 'Gyrometer (rad?)')


# In[20]:


import numpy as np
import pandas as pd
from vqf import VQF
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
# Assume `df` has accelerometer and gyroscope data
# dt should be the sampling time interval (in seconds) between each measurement
dt = 0.01  # For example, 100 Hz sampling frequency, adjust according to your data rate

# Initialize the VQF filter
vqf = VQF(dt)  # or another argument that matches your sensor settings

quaternions=[]

# Sample function to compute orientation quaternions with VQF
def compute_quaternion_with_vqf(acc_data, gyro_data, dt):
    quaternions = []
    
    for acc, gyro in zip(acc_data, gyro_data):
        # Make sure the accelerometer and gyroscope data are C-contiguous
        acc = np.ascontiguousarray(np.array(acc, dtype=np.float64))
        gyro = np.ascontiguousarray(np.array(gyro, dtype=np.float64))
        
        # Update VQF filter with accelerometer, gyroscope, and dummy magnetometer data
        vqf.update(gyro, acc)
        
        
        # Retrieve the 3D quaternion directly from the VQF filter
        quaternion = vqf.getQuat3D()  # Get the quaternion directly (no argument passed)
        
        # Append the quaternion to the list
        quaternions.append(quaternion)
        
    return np.array(quaternions)



# Extract accelerometer and gyroscope data as numpy arrays
acc_data = df[["AccX", "AccY", "AccZ"]].values
gyro_data = df[["GyroX", "GyroY", "GyroZ"]].values

# Step 1: Calculate orientation quaternions
quaternions = compute_quaternion_with_vqf(acc_data, gyro_data, dt)

# Step 2: Rotate accelerometer data to global frame
def rotate_to_global(quaternions, local_vectors):
    global_vectors = []
    
    for q, vector in zip(quaternions, local_vectors):
        # Ensure the quaternion is a numpy array
        q = np.array(q, dtype=np.float64)
        
        # Ensure the local vector is a numpy array and has the shape (3,)
        vector = np.array(vector, dtype=np.float64)
        
        # Convert quaternion to a rotation object
        rotation = R.from_quat(q)
        
        # Rotate the local vector to the global frame using the rotation
        global_vector = rotation.apply(vector)  # Apply rotation to the vector
        
        # Append the rotated vector to the list
        global_vectors.append(global_vector)
    
    return np.array(global_vectors)

# Convert accelerometer data to global frame
global_acc_data = rotate_to_global(quaternions, acc_data)
global_acc_data[:, 2]=global_acc_data[:, 2]+14


# Step 3: Plot global acceleration data
plt.figure(figsize=(14, 7))
plt.plot(global_acc_data[:, 0], label='Global AccX')
plt.plot(global_acc_data[:, 1], label='Global AccY')
plt.plot(global_acc_data[:, 2], label='Global AccZ')
plt.xlabel("Time (samples)")
plt.ylabel("Acceleration (m/s²)")
plt.title("Global Acceleration Data")
plt.legend()
plt.grid()
plt.show()


# In[ ]:




