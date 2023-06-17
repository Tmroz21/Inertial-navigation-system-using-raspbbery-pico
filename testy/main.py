import pandas as pd
import matplotlib.pyplot as plt

df1 = pd.read_csv('pomiar3.csv')

accel = 8.0/32768.0
gyro = 1000.0/32768.0

ax = df1['ax'] * accel
ay = df1['ay'] * accel
az = df1['az'] * accel
gx = df1['gx'] * gyro
gy = df1['gy'] * gyro
gz = df1['gz'] * gyro

plt.plot(gx)
plt.plot(gy)
plt.plot(gz)

plt.show()
