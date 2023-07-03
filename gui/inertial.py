import serial
import numpy as np

import serial
import numpy as np
import time

accelRate = 2.0 / 32768.0
gyroRate = 250.0 / 32768.0
currGyro = [0, 0, 0]
currAccel = [0, 0, 0]
currAng = [0, 0, 0]

sampleTime = 0.01
radToDeg = 180 / np.pi
degToRad = np.pi / 180
currSpeed = [0, 0]
pos = [0, 0]
accelOffset = [0, 0]


GyroKalman = [0, 0, 0]
AccelKalman = [0, 0, 0]
sigma_y = 1
Q = 0.05  # dla żyroskopu
R = sigma_y * sigma_y
xPostGyro = [0, 0, 0]
pPostGyro = [Q, Q, Q]
Qa = 0.1  # dla akcelerometru
xPostAccel = [0, 0, 0]
pPostAccel = [Qa, Qa, Qa]
def getData(com):
    ser = serial.Serial(com, timeout=0)
    data = ''
    while 1:
        x = ser.read()
        x = x.decode('utf-8')
        data = data + x
        if x == '|':
            ser.close()
            break
    i = data.find(',')
    new_ax = data[0:i]
    data = data[i + 1:]
    i = data.find(',')
    new_ay = data[0:i]
    data = data[i + 1:]
    i = data.find(',')
    new_az = data[0:i]
    data = data[i + 1:]
    i = data.find(',')
    new_gx = data[0:i]
    data = data[i + 1:]
    i = data.find(',')
    new_gy = data[0:i]
    data = data[i + 1:]
    i = data.find(',')
    new_gz = data[0:i]
    global currAccel
    global currGyro
    currAccel = [int(new_ax) * accelRate, int(new_ay) * accelRate, int(new_az) * accelRate]
    currGyro = [int(new_gx) * gyroRate,int(new_gy) * gyroRate, int(new_gz) * gyroRate]
    kalmanAccelUpdate()
    kalmanGyroUpdate()

def setInitAng(com):
    getData(com)
    R = np.sqrt(currAccel[0] * currAccel[0] + currAccel[1] * currAccel[1] + currAccel[2] * currAccel[2])
    global currAng
    # currAng = [np.arccos(currVec[0]), np.arccos(currVec[1]), np.arccos(currVec[2])]
    currAng = [np.arctan2(currAccel[1], currAccel[2]), np.arctan2(currAccel[2], currAccel[0]), np.arctan2(currAccel[0], currAccel[1])]

def nextPos(com):
    trust = 10 # im większy tym bardziej ufamy dla żyroskopu
    pastAccel = currAccel
    pastGyro = currGyro
    getData(com)
    currAng[0] = currAng[0] + (pastGyro[0] + currGyro[0]) * sampleTime * degToRad
    currAng[1] = currAng[1] + (pastGyro[1] + currGyro[1]) * sampleTime * degToRad
    currAng[2] = currAng[2] + (pastGyro[2] + currGyro[2]) * sampleTime * degToRad
    R = np.sqrt(currAccel[0] * currAccel[0] + currAccel[1] * currAccel[1] + currAccel[2] * currAccel[2])
    # estAcc = [np.arccos(currAccel[0]/R), np.arccos(currAccel[1]/R), np.arccos(currAccel[2]/R)]

    estAcc = [np.arctan2(currAccel[1], currAccel[2]), np.arctan2(currAccel[2], currAccel[0]),
     np.arctan2(currAccel[0], currAccel[1])]



    currAng[0] = (currAng[0] * trust + estAcc[0])/(1 + trust)
    currAng[1] = (currAng[1] * trust + estAcc[1])/(1 + trust)
    currAng[2] = (currAng[2] * trust + estAcc[2])/(1 + trust)



    # usuwanie przyśpieszenia ziemskiego
    currAccel[0] = currAccel[0] - np.cos(currAng[1])
    currAccel[1] = currAccel[1] - np.cos(currAng[0] - np.pi/2)

    currAccel[0] = currAccel[0] * np.cos(currAng[1] - np.pi/2)
    currAccel[1] = currAccel[1] * np.cos(currAng[0])


    global currSpeed
    currSpeed[0] = currSpeed[0] + currAccel[0] * sampleTime * 9.81
    currSpeed[1] = currSpeed[1] + currAccel[1] * sampleTime * 9.81

    global pos
    pos = [pos[0] + currSpeed[0] * sampleTime, pos[1] + currSpeed[1] * sampleTime]
    #date = [pos,currAng]
    #print(pos)
    # return [pos,currAng]
    # print(currSpeed)
def kalmanGyroUpdate():

    # predykcja
    global xPostGyro
    global pPostGyro
    for i in range(0, 3):
        xPrio = xPostGyro[i]

        pPrio = pPostGyro[i] + Q
        global R
        # filtracja
        K = pPrio / (pPrio + R)

        xPostGyro[i] = xPrio + K * (currGyro[i] - xPrio)
        pPostGyro[i] = (1 - K) * pPrio
        global GyroKalman
        GyroKalman[i] = xPostGyro[i]

def kalmanAccelUpdate():

    # predykcja
    global xPostAccel
    global pPostAccel
    for i in range(0, 3):
        xPrio = xPostAccel[i]
        pPrio = pPostAccel[i] + Q
        global R
        # filtracja
        K = pPrio / (pPrio + R)

        xPostAccel[i] = xPrio + K * (currAccel[i] - xPrio)
        pPostAccel[i] = (1 - K) * pPrio
        global AccelKalman
        AccelKalman[i] = xPostAccel[i]