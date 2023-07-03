import serial.tools.list_ports
import serial
import sys
# import pandas as pd
import numpy as np
import inertial
from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QSizePolicy, QPushButton, QHBoxLayout, QWidget,QVBoxLayout, QComboBox, QLabel
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

accel = 2.0/32768.0
gyro = 250.0/32768.0

ax = []
ay = []
az = []

for i in range(0,100):
    ax.append(0)
    ay.append(0)
    az.append(0)

comList = []

class Worker(QObject):
    def __init__(self, function, interval):
        super(Worker, self).__init__()
        self._funcion = function
        self._timer = QTimer(self, interval=interval, timeout=self.execute)

    @property
    def running(self):
        return self._timer.isActive()

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def execute(self):
        self._funcion()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.i = 1
        self.refreshButton = QPushButton("refresh")
        self.comComboBox = QComboBox()
        self.angleXlabel = QLabel()
        self.angleYlabel = QLabel()

        self.currentComport = "X"
        self.arr = []
        self.time = 0.0
        self.maximumXValue = 15.0
        self.timeStep = 0.1

        acChartLayout = QHBoxLayout()
        gyChartLayout = QHBoxLayout()
        labelLayout = QHBoxLayout()
        portsViewLayout = QHBoxLayout()
        mainLayout = QVBoxLayout()

        dataFreqz = 100;  # number of readigns from sensor in time of 1s

        self.seriesAccelX = QLineSeries()
        self.seriesAccelY = QLineSeries()
        self.seriesAccelZ = QLineSeries()
        self.seriesGyroX = QLineSeries()
        self.seriesGyroY = QLineSeries()
        self.seriesGyroZ = QLineSeries()
        self.seriesXY = QLineSeries()

        self.chartAccX = QChart()
        self.chartAccY = QChart()
        self.chartAccZ = QChart()
        self.chartGyX = QChart()
        self.chartGyY = QChart()
        self.chartGyZ = QChart()
        self.chartXY = QChart()

        self.SetChart(self.chartAccX,self.seriesAccelX,acChartLayout,2.0,"acc","x")
        self.SetChart(self.chartAccY,self.seriesAccelY,acChartLayout,2.0,"acc","y")
        self.SetChart(self.chartAccZ,self.seriesAccelZ,acChartLayout,2.0,"acc","z")
        
        self.SetChart(self.chartGyX,self.seriesGyroX,gyChartLayout,360.0,"gyro","x")
        self.SetChart(self.chartGyY,self.seriesGyroY,gyChartLayout,360.0,"gyro","y")
        self.SetChart(self.chartGyZ,self.seriesGyroZ,gyChartLayout,360.0,"gyro","z")
        
        
        ####
        self.chartXY.legend().hide()
        self.chartXY.addSeries(self.seriesXY)  # adding series to chart
        # .. axis properties ..
        axisX = QValueAxis()
        axisY = QValueAxis()
        axisY.setRange(-20,20) # setting the range for y axis
        axisY.setTitleText("Y") 
        axisX.setRange(-20,20) # setting the range for x axis
        axisX.setTitleText("X") # setting title to x axis
        self.chartXY.setAxisX(axisX,self.seriesXY) # connecting axis propertis to series 
        self.chartXY.setAxisY(axisY,self.seriesXY) # connecting axis properties to series
        self.chartViewXY = QChartView(self.chartXY) #adding chart to chartView
        self.chartViewXY.setRenderHint(QPainter.Antialiasing)
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        self.chartViewXY.setSizePolicy(size)
        ####

        self.FindAvalibleComports(comList) # finding avalible ports and appending them to comList
        self.AddPortsToCombo(comList,self.comComboBox) # adding ports to list
        
        self.comComboBox.activated.connect(self.SetCurrentPort) # connecting SetCurrentPort function to comComboBox activating when item is chosen from the list


        portsViewLayout.addWidget(self.refreshButton)
        portsViewLayout.addWidget(self.comComboBox)
        labelLayout.addWidget(self.angleXlabel)
        labelLayout.addWidget(self.angleYlabel)
        self.angleXlabel.setText("X angle:")
        self.angleYlabel.setText("Y angle:")
        mainLayout.addLayout(portsViewLayout)
        mainLayout.addWidget(self.chartViewXY)
        mainLayout.addLayout(labelLayout) 
        mainLayout.addLayout(acChartLayout)
        mainLayout.addLayout(gyChartLayout)
        mainLayout.setStretch(0,1)
        mainLayout.setStretch(1,12)
        mainLayout.setStretch(2,1)
        mainLayout.setStretch(3,10)
        mainLayout.setStretch(4,10)
        
        self.setLayout(mainLayout)

        self.worker = Worker(self.UpdatePlot,100)
        self.refreshButton.clicked.connect(self.worker.start)
        

    def SetChart(self,chart,series,chartLayout,xAxisRange,chartType,title):

        chart.legend().hide()
        chart.addSeries(series)  # adding series to chart
        # .. axis properties ..
        axisX = QValueAxis()
        axisY = QValueAxis()
        axisY.setRange(-xAxisRange,xAxisRange) # setting the range for y axis
        match chartType: # seting title to y axis
            case "acc":
                axisY.setTitleText("Przyśpieszenie[g]") 
            case "gyro":
                axisY.setTitleText("Przyśpieszenie[deg/s^2]")

        axisX.setRange(0.0,self.maximumXValue) # setting the range for x axis
        axisX.setTitleText("Czas[s]") # setting title to x axis
        chart.setAxisX(axisX,series) # connecting axis propertis to series 
        chart.setAxisY(axisY,series) # connecting axis properties to series
        # ...
        match chartType: # seting title to y axis
            case "acc":
                      chart.setTitle("odczyt z akcelerometru dla osi " + title)  
            case "gyro":
                      chart.setTitle("odczyt z żyroskopu dla osi " + title)  
      
        chartView = QChartView(chart) #adding chart to chartView
        chartView.setRenderHint(QPainter.Antialiasing)
        chartLayout.addWidget(chartView) # adding chartView to layout
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        chartView.setSizePolicy(size)

    def UpdatePlot(self):       
        #self.arr.append(int(getData(self.currentComport)))
        if self.i == 1:
            inertial.setInitAng(self.currentComport)
            self.i = self.i +1
        self.time = self.time + self.timeStep
        dataFreqz = 100
        inertial.nextPos(self.currentComport)
        self.seriesAccelX.append(self.time, inertial.currAccel[0] )
        self.seriesAccelY.append(self.time, inertial.currAccel[1])
        self.seriesAccelZ.append(self.time, inertial.currAccel[2])
        self.seriesGyroX.append(self.time, inertial.currGyro[0])
        self.seriesGyroY.append(self.time, inertial.currGyro[1])
        self.seriesGyroZ.append(self.time, inertial.currGyro[2])
        # dataIner = []
        # dataIner = getData(self.currentComport,"pos")
        # pos = dataIner[0]
        # angle = dataIner[1]
        self.seriesXY.append(inertial.pos[0],inertial.pos[1])
        self.angleXlabel.setText("X angle: " + str(round(inertial.currAng[0]*180/np.pi, 4)))
        self.angleYlabel.setText("Y angle: " + str(round(inertial.currAng[1]*180/np.pi-90, 4)))
        # print(dataIner)
        
        if self.time >= self.maximumXValue:
            self.time = 0.0
            self.seriesAccelX.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesAccelY.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesAccelZ.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesGyroX.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesGyroY.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesGyroZ.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
    def FindAvalibleComports(self,comList):

        ports = serial.tools.list_ports.comports()

        for port, desc, hwid in sorted(ports):
            comList.append("{}".format(port))
        print(comList)

    def SetCurrentPort(self,index):
        self.currentComport = self.comComboBox.itemText(index)
        print(self.currentComport)
      
    def AddPortsToCombo(self,comList,combo):
        for port in sorted(comList):
            combo.addItem(port)

# def getData(currentComport,dataType):
#     ser = serial.Serial(currentComport,timeout=0)
#     data = ''
#     while 1:
#         x = ser.read()
#         x = x.decode('utf-8')
#         data = data + x
#         if x == '|':
#             ser.close()
#             break
#     i = data.find(',')
#     new_ax = data[0:i]
#     data = data[i+1:]
#     i = data.find(',')
#     new_ay = data[0:i]
#     data = data[i+1:]
#     i =data.find(',')
#     new_az = data[0:i]
#     data = data[i+1:]
#     i =data.find(',')
#     new_gx = data[0:i]
#     data = data[i+1:]
#     i =data.find(',')
#     new_gy = data[0:i]
#     data = data[i+1:]
#     i =data.find(',')
#     new_gz = data[0:i]
#     match dataType:
#         case "pos":
#             return inertial.nextPos()
#         case "ax":
#             return int(new_ax)*accel
#         case "ay":
#             return int(new_ay)*accel
#         case "az":
#             return int(new_az)*accel
#         case "gx":
#             return int(new_gx)*gyro
#         case "gz":
#             return int(new_gy)*gyro
#         case "gy":
#             return int(new_gz)*gyro

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Inertial Navigation Controll App")
    window.show()
    window.resize(1200, 900)
    # inertial.setInitAng()
    #window.showFullScreen()
    sys.exit(app.exec())
