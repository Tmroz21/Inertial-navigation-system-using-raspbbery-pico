import serial.tools.list_ports
import serial
import sys
import pandas as pd
import numpy as np
# from PyQt5.QtCore import QTimer
from PySide6.QtCore import QPointF, QObject, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication, QGridLayout, QSizePolicy, QPushButton, QHBoxLayout, QWidget,QVBoxLayout, QComboBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis

accel = 8.0/32768.0
gyro = 1000.0/32768.0

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

        self.refreshButton = QPushButton("refresh")
        self.comComboBox = QComboBox()

        self.currentComport = "X"
        self.arr = []
        self.time = 0.0
        self.maximumXValue = 15.0
        self.timeStep = 0.1

        acChartLayout = QHBoxLayout()
        portsViewLayout = QHBoxLayout()
        mainLayout = QVBoxLayout()

        dataFreqz = 100;  # number of readigns from sensor in time of 1s

        self.seriesAccelX = QLineSeries()
        self.seriesAccelY = QLineSeries()
        self.seriesAccelZ = QLineSeries()

        self.chartAccX = QChart()
        self.chartAccY = QChart()
        self.chartAccZ = QChart()

        self.SetChart(self.chartAccX,self.seriesAccelX,acChartLayout)
        self.SetChart(self.chartAccY,self.seriesAccelY,acChartLayout)
        self.SetChart(self.chartAccZ,self.seriesAccelZ,acChartLayout)   

        self.FindAvalibleComports(comList) # finding avalible ports and appending them to comList
        self.AddPortsToCombo(comList,self.comComboBox) # adding ports to list
        
        self.comComboBox.activated.connect(self.SetCurrentPort) # connecting SetCurrentPort function to comComboBox activating when item is chosen from the list

        portsViewLayout.addWidget(self.refreshButton)
        portsViewLayout.addWidget(self.comComboBox)

        mainLayout.addLayout(portsViewLayout)
        mainLayout.addLayout(acChartLayout)
        
        self.setLayout(mainLayout)

        self.worker = Worker(self.UpdatePlot,100)
        self.refreshButton.clicked.connect(self.worker.start)
        

    def SetChart(self,chart,series,chartLayout):

        chart.legend().hide()
        chart.addSeries(series)  # adding series to chart
        # .. axis properties ..
        axisX = QValueAxis()
        axisY = QValueAxis()
        axisY.setRange(-2.0,2.0) # setting the range for y axis
        axisY.setTitleText("Przyśpieszenie[g]") # seting title to y axis
        axisX.setRange(0.0,self.maximumXValue) # setting the range for x axis
        axisX.setTitleText("Czas[s]") # setting title to x axis
        chart.setAxisX(axisX,series) # connecting axis propertis to series 
        chart.setAxisY(axisY,series) # connecting axis properties to series
        # ...
        chart.setTitle("odczyt z akcelerometru dla osi X ")     
        chartView = QChartView(chart) #adding chart to chartView
        chartView.setRenderHint(QPainter.Antialiasing)
        chartLayout.addWidget(chartView) # adding chartView to layout
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        chartView.setSizePolicy(size)

    def UpdatePlot(self):       
        #self.arr.append(int(getData(self.currentComport)))
        self.time = self.time + self.timeStep
        dataFreqz = 100
        self.seriesAccelX.append(self.time, getData(self.currentComport,"ax"))
        self.seriesAccelY.append(self.time, getData(self.currentComport,"ay"))
        self.seriesAccelZ.append(self.time, getData(self.currentComport,"az"))
        
        if self.time >= self.maximumXValue:
            self.time = 0.0
            self.seriesAccelX.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesAccelY.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)
            self.seriesAccelZ.removePoints(0,int(self.maximumXValue/ self.timeStep)+1)

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

def getData(currentComport,dataType):
    ser = serial.Serial(currentComport,timeout=0)
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
    data = data[i+1:]
    i = data.find(',')
    new_ay = data[0:i]
    data = data[i+1:]
    i =data.find(',')
    new_az = data[0:i]
    ax.pop(0)
    ay.pop(0)
    az.pop(0)
    ax.append(int(new_ax) * accel)
    ay.append(int(new_ay))
    az.append(int(new_az))
    match dataType:
        case "ax":
            return int(new_ax)*accel
        case "ay":
            return int(new_ay)*accel
        case "az":
            return int(new_az)*accel

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Inertial Navigation Controll App")
    window.show()
    window.resize(1200, 500)

    sys.exit(app.exec())
