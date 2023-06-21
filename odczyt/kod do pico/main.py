import machine
from machine import Pin, I2C
import math
import time
import sys
import uio

Gyro  = [0,0,0]
Accel = [0,0,0]
gyroOffset=[0,0,0]
znacz = '|'

## MPU9250 Default I2C slave address
SLAVE_ADDRESS        = 0x68
## AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
## Device id
DEVICE_ID            = 0x71

''' MPU-9250 Register Addresses '''
## sample rate driver
SMPLRT_DIV     = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR   = 0x1E
WOM_THR        = 0x1F
FIFO_EN        = 0x23
I2C_MST_CTRL   = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG    = 0x37
INT_ENABLE     = 0x38
INT_STATUS     = 0x3A
ACCEL_OUT      = 0x3B
TEMP_OUT       = 0x41
GYRO_OUT       = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL    = 0x69
USER_CTRL          = 0x6A
PWR_MGMT_1         = 0x6B
PWR_MGMT_2         = 0x6C
FIFO_R_W           = 0x74
WHO_AM_I           = 0x75

## Gyro Full Scale Select 250dps
GFS_250  = 0x00
## Gyro Full Scale Select 500dps
GFS_500  = 0x01
## Gyro Full Scale Select 1000dps
GFS_1000 = 0x02
## Gyro Full Scale Select 2000dps
GFS_2000 = 0x03
## Accel Full Scale Select 2G
AFS_2G   = 0x00
## Accel Full Scale Select 4G
AFS_4G   = 0x01
## Accel Full Scale Select 8G
AFS_8G   = 0x02
## Accel Full Scale Select 16G
AFS_16G  = 0x03

# AK8963 Register Addresses
AK8963_ST1        = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1      = 0x0A
AK8963_CNTL2      = 0x0B
AK8963_ASAX       = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN   = 0x00
## One shot data output
AK8963_MODE_ONE    = 0x01

## Continous data output 8Hz
AK8963_MODE_C8HZ   = 0x02
## Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
## 14bit output
AK8963_BIT_14 = 0x00
## 16bit output
AK8963_BIT_16 = 0x01

## smbus
bus = I2C(1,scl=Pin(7),sda=Pin(6),freq=400_000)

## MPU9250 I2C Controll class
class MPU9250:

    ## Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(self, address=SLAVE_ADDRESS):
        self.address = address
        self.configMPU9250(GFS_1000, AFS_8G)
        self.readGyroOffset()
        

    ## Search Device
    #  @param [in] self The object pointer.
    #  @retval true device connected
    #  @retval false device error
    def searchDevice(self):
        who_am_i = bus.readfrom_mem(int(self.address), int(WHO_AM_I),1)
        if(who_am_i == DEVICE_ID):
            return true
        else:
            return false

    ## Configure MPU-9250
    #  @param [in] self The object pointer.
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def configMPU9250(self, gfs, afs):
        if gfs == GFS_250:
            self.gres = 250.0/32768.0
        elif gfs == GFS_500:
            self.gres = 500.0/32768.0
        elif gfs == GFS_1000:
            self.gres = 1000.0/32768.0
        else:  # gfs == GFS_2000
            self.gres = 2000.0/32768.0

        if afs == AFS_2G:
            self.ares = 2.0/32768.0
        elif afs == AFS_4G:
            self.ares = 4.0/32768.0
        elif afs == AFS_8G:
            self.ares = 8.0/32768.0
        else: # afs == AFS_16G:
            self.ares = 16.0/32768.0

        # sleep off
        bus.writeto_mem(int(self.address), int(PWR_MGMT_1), b'\x00')
        time.sleep(0.1)
        # auto select clock source
        bus.writeto_mem(int(self.address), int(PWR_MGMT_1), b'\x01')
        time.sleep(0.1)
        # DLPF_CFG
        bus.writeto_mem(int(self.address), int(CONFIG), b'\x03')
        # sample rate divider
        bus.writeto_mem(int(self.address), int(SMPLRT_DIV), b'\x04')
        # gyro full scale select
        bus.writeto_mem(int(self.address), int(GYRO_CONFIG), bytes([gfs << 
3]) )
        # accel full scale select
        bus.writeto_mem(int(self.address), int(ACCEL_CONFIG), bytes([afs 
<< 3]) )
        # A_DLPFCFG
        bus.writeto_mem(int(self.address), int(ACCEL_CONFIG_2), b'\x03')
        # BYPASS_EN
        bus.writeto_mem(int(self.address), int(INT_PIN_CFG), b'\x02')
        time.sleep(0.1)

 

    ## brief Check data ready
    #  @param [in] self The object pointer.
    #  @retval true data is ready
    #  @retval false data is not ready
    def checkDataReady(self):
        drdy = bus.readfrom_mem( int(self.address), int(INT_STATUS), 1 )
        if drdy[0] & 0x01:
            return True
        else:
            return False

    ## Read accelerometer
    #  @param [in] self The object pointer.
    #  @retval x : x-axis data
    #  @retval y : y-axis data
    #  @retval z : z-axis data
    def readAccel(self):
        data = bus.readfrom_mem( int(self.address), int(ACCEL_OUT), 6)
        Accel[0] = self.dataConv(data[1], data[0])
        Accel[1] = self.dataConv(data[3], data[2])
        Accel[2] = self.dataConv(data[5], data[4])

    ## Read gyro
    #  @param [in] self The object pointer.
    #  @retval x : x-gyro data
    #  @retval y : y-gyro data
    #  @retval z : z-gyro data
    
    def readGyro(self):
        data = bus.readfrom_mem(int(self.address), int(GYRO_OUT), 6)
        Gyro[0] = self.dataConv(data[1], data[0]) - gyroOffset[0]
        Gyro[1] = self.dataConv(data[3], data[2]) - gyroOffset[1]
        Gyro[2] = self.dataConv(data[5], data[4]) - gyroOffset[2]
                
    def readGyroOffset(self):
        s32TempGx = 0
        s32TempGy = 0
        s32TempGz = 0
        for i in range(0,32):
            self.readGyro()
            s32TempGx += Gyro[0]
            s32TempGy += Gyro[1]
            s32TempGz += Gyro[2]
            time.sleep(0.01)
        gyroOffset[0] = s32TempGx >> 5
        gyroOffset[1] = s32TempGy >> 5
        gyroOffset[2] = s32TempGz >> 5



    ## Data Convert
    # @param [in] self The object pointer.
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def dataConv(self, data1, data2):
        value = data1 | (data2 << 8)
        if(value & (1 << 16 - 1)):
            value -= (1<<16)
        return value
    
mpu9250 = MPU9250()

try:
    while True:
        mpu9250.readAccel()
        mpu9250.readGyro()
        
        print('%d,%d,%d,%d,%d,%d|'%(Accel[0],Accel[1],Accel[2],Gyro[0],Gyro[1],Gyro[2]))
        #data = Accel[0],Accel[1],Accel[2],Gyro[0],Gyro[1],Gyro[2]
        time.sleep(0.01)
        #print(data)

except KeyboardInterrupt:
    sys.exit()




