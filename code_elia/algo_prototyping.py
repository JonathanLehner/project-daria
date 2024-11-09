import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
plt.switch_backend('TkAgg')  # 'TkAgg' is a GUI backend
plt.ion()  # Enable interactive mode

df = pd.read_csv('data/sensor_data_09_11_2024__17_23_09.csv', sep=',', index_col=0)

# df.index = pd.to_datetime(df.index)
df.index = (df.index - df.index[0])/1000
fig, axs = plt.subplots(1, 2, sharex=True)

axs[0].plot(df.index, df['x_acc'], label='x_acc', color='red', alpha=0.5)
axs[0].plot(df.index, df['y_acc'], label='y_acc', color='green', alpha=0.5)
axs[0].plot(df.index, df['z_acc'], label='z_acc', color='blue', alpha=0.5)
axs[0].legend()

axs[1].plot(df.index, df['x_gyro'], label='x_gyro', color='red', alpha=0.5)
axs[1].plot(df.index, df['y_gyro'], label='y_gyro', color='green', alpha=0.5)
axs[1].plot(df.index, df['z_gyro'], label='z_gyro', color='blue', alpha=0.5)
axs[1].legend()

dt = 10 #seconds
i = 0
# while i+dt < len(df):

plt.show()

pass