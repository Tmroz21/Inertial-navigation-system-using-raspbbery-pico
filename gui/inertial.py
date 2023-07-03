import serial
import numpy as np

import serial
import numpy as np
import time

accelRate = 2.0 / 32768.0
gyroRate = 250.0 / 32768.0
currGyro = [0, 0, 0]
currAccel = [0, 0, 0]

sampleTime = 0.01
radToDeg = 180 / np.pi
degToRad = np.pi / 180
currSpeed = [0, 0]
pos = [0, 0]
accelOffset = [0, 0]
def getData():
    ser = serial.Serial("COM6", timeout=0)
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

def setInitAng():
    getData()
    R = np.sqrt(currAccel[0] * currAccel[0] + currAccel[1] * currAccel[1] + currAccel[2] * currAccel[2])
    global currAng
    # currAng = [np.arccos(currVec[0]), np.arccos(currVec[1]), np.arccos(currVec[2])]
    currAng = [np.arctan2(currAccel[1], currAccel[2]), np.arctan2(currAccel[2], currAccel[0]), np.arctan2(currAccel[0], currAccel[1])]

def nextPos():
    trust = 10 # im większy tym bardziej ufamy dla żyroskopu
    pastAccel = currAccel
    pastGyro = currGyro
    getData()
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
    #print(pos)
    return(pos)
    # print(currSpeed)
