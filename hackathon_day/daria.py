#!/usr/bin/env python
# coding: utf-8

# In[12]:


import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objects as go


# In[13]:


csv_path = "/Users/majojacome/Documents/Documents - Majo’s MacBook Pro/4. Majo/hackahealth/sensor_data_09_11_2024__17_23_09.csv"
df = pd.read_csv(csv_path)


# In[14]:


df.head()


# In[29]:


# start_date = pd.Timestamp('2024-11-09 18:43:29')
# df['Timestamp'] = start_date + pd.to_timedelta(df['timestamp'], unit='ms')
# df['timestamp'] = df['Timestamp']


# In[30]:


# df = df.drop(columns=['Timestamp'])


# In[31]:


# df.head()


# In[15]:


def plot_data(y_values, title, ylabel):
    plt.figure(figsize=(14, 7))
    for column in y_values.columns:
        plt.plot(df.index, y_values[column], label=column)
    plt.plot(df.index, y_values)
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.grid()
    plt.tight_layout()
    #plt.legend()
    plt.show()

plot_data(df[["x_acc", "y_acc", "z_acc"]], 'Accelerometer Data', 'Accelerometer (m/s²)')


# In[16]:


fig = px.line(df, x=df.index, y=["x_acc", "y_acc", "z_acc"], 
              title='Acelerometer',
              labels={'value': 'Acceleration (m/s²)', 'variable': 'Accelerometer Components'})
fig.show()


# In[34]:


import numpy as np
from scipy.signal import butter,filtfilt
# Filter requirements.
T = 10.0         # Sample Period
fs = 10.0       # sample rate, Hz
cutoff = 1      # desired cutoff frequency of the filter, Hz ,      slightly higher than actual 1.2 Hz
nyq = 0.5 * fs  # Nyquist Frequency
order = 2     # sin wave can be approx represented as quadratic
n = int(T * fs) # total number of samples


# In[35]:


def butter_lowpass_filter(data, cutoff, fs, order):
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients 
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y


# In[36]:


# Filter the data, and plot both the original and filtered signals.
y = butter_lowpass_filter(df['x_acc'], cutoff, fs, order)
fig = go.Figure()
fig.add_trace(go.Scatter(
            y = df['x_acc'],
            line =  dict(shape =  'spline' ),
            name = 'signal with noise'
            ))
fig.add_trace(go.Scatter(
            y = y,
            line =  dict(shape =  'spline' ),
            name = 'filtered signal'
            ))
fig.show()


# In[37]:


xdata = df['timestamp'] - df['timestamp'][0]
dx = np.diff(xdata)
xdata, dx


# In[38]:


print('length of x:', len(xdata))
print('length of dx:', len(dx))


# In[39]:


# y = xdata**2
plt.plot(xdata, y, 'go', fillstyle = 'none');


# In[40]:


dydx = np.diff(y)/np.diff(xdata)
print('dy/dx:', dydx)


# In[41]:


x1 = xdata[1:len(xdata)]
print('length of x1:', len(x1))


# In[42]:


def linearFunc(x, slope, intercept):
    y = slope*x + intercept
    return y
from scipy.optimize import curve_fit
a_fit, cov = curve_fit(linearFunc, x1, dydx)


# In[43]:


plt.plot(x1, dydx, 'o', fillstyle = 'none')
fitFcn = np.poly1d(a_fit)
plt.plot(x1, fitFcn(x1), 'k-');


# In[44]:


max_var = dydx.max()
min_var = dydx.min()
print(min_var, max_var)


# In[57]:


var_extrem = np.array([abs(max_var), abs(min_var)])
print(var_extrem)
perc_100 = var_extrem.min()
print(perc_100)
threshold = 0.6 * perc_100
print(threshold)


# In[21]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

buffer = []
decision = []

def processData(new_value):

    threshold = 0

    buffer.append(new_value)

    if len(buffer) < 11: 
        decision.append(3)  # Buffer is not full

    else:
        buffer.pop(0)
        N = len(buffer)
        mean_kernel = np.ones(N)/N
        buffer_filt = np.convolve(buffer, mean_kernel, mode='same')
        last_value = buffer_filt[-1]
        
        if last_value > threshold:  # arm goes towards mouth
            decision.append(2)  # stop music
        elif last_value < -threshold:  # arm goes away from mouth
            decision.append(1)  # start music
        else:
            decision.append(8000)  # error happened
                
    return decision


# In[38]:


x = 0
data = df['x_acc']
for i in range(len(data)-1): #range(0,100)
    decision = processData(data[i])
    x+=1
    print(i)
    print(data[i])
    
time = np.linspace(0, len(data)-1, len(data))

plt.plot(time, decision)


# In[ ]:




