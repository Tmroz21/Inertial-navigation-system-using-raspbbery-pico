import serial.tools.list_ports
import serial
import sys
import pandas as pd
import numpy as np
# from PyQt5.QtCore import QTimer
from PySide6.QtCore import QPointF, QObject, QTimer, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication, QGridLayout, QSizePolicy, QPushButton, QHBoxLayout, QWidget,QVBoxLayout, QComboBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis


df1 = pd.read_csv('gui\pomiar3.csv')

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
        self.time = 0.01

        chartLayout = QHBoxLayout()
        portsViewLayout = QHBoxLayout()
        mainLayout = QVBoxLayout()

        # data series
        dataFreqz = 100;  # number of readigns from sensor in time of 1s

        self.seriesAccelX = QLineSeries()
        self.seriesAccelY = QLineSeries()
        self.seriesAccelZ = QLineSeries()
        for x in range(len(ax)):
           # self.seriesAccelX.append(QPointF(x / dataFreqz, ax[x]))
            self.seriesAccelY.append(QPointF(x / dataFreqz, ay[x]))
            self.seriesAccelZ.append(QPointF(x / dataFreqz, az[x]))

        self.chartAccX = QChart()
        self.chartAccX.legend().hide()
        self.chartAccX.addSeries(self.seriesAccelX)  # adding series to chart
        #self.chartAccX.createDefaultAxes()
        self.chartAccX.setPlotArea(QRectF(2.0,0.0,4.0,4.0))


        self.chartAccX.setTitle("odczyt z akcelerometru dla osi X ")
        self.chartAccY = QChart()
        self.chartAccY.legend().hide()
        self.chartAccY.addSeries(self.seriesAccelY) # adding series to chart
        self.chartAccY.createDefaultAxes()
        self.chartAccY.setTitle("odczyt z akcelerometru dla osi Y ")
        self.chartAccZ = QChart()
        self.chartAccZ.legend().hide()
        self.chartAccZ.addSeries(self.seriesAccelZ) # adding series to chart
        self.chartAccZ.createDefaultAxes()
        self.chartAccZ.setTitle("odczyt z akcelerometru dla osi Z")

        self._chart_viewAccX = QChartView(self.chartAccX)
        self._chart_viewAccX.setRenderHint(QPainter.Antialiasing)
        self._chart_viewAccY = QChartView(self.chartAccY)
        self._chart_viewAccY.setRenderHint(QPainter.Antialiasing)
        self._chart_viewAccZ = QChartView(self.chartAccZ)
        self._chart_viewAccZ.setRenderHint(QPainter.Antialiasing)

        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setHorizontalStretch(1)

        self._chart_viewAccX.setSizePolicy(size)
        self._chart_viewAccY.setSizePolicy(size)
        self._chart_viewAccZ.setSizePolicy(size)

        chartLayout.addWidget(self._chart_viewAccX)
        chartLayout.addWidget(self._chart_viewAccY)
        chartLayout.addWidget(self._chart_viewAccZ)

        self.FindAvalibleComports(comList) # finding avalible ports and appending them to comList
        self.AddPortsToCombo(comList,self.comComboBox) # adding ports to list
        
        self.comComboBox.activated.connect(self.SetCurrentPort) # connecting SetCurrentPort function to comComboBox activating when item is chosen from the list


        portsViewLayout.addWidget(self.refreshButton)
        portsViewLayout.addWidget(self.comComboBox)

        mainLayout.addLayout(portsViewLayout)
        mainLayout.addLayout(chartLayout)
        
        self.setLayout(mainLayout)


        self.worker = Worker(self.UpdatePlot,100)
        self.refreshButton.clicked.connect(self.worker.start)

    def UpdatePlot(self):
        self.seriesAccelX.remove
        #self.arr.append(int(getData(self.currentComport)))
        self.time = self.time + 0.01
        dataFreqz = 100
        self.seriesAccelX.append(self.time, getData(self.currentComport))

        #self.seriesAccelX.append(QPointF((len(arr)-1)/dataFreqz, arr[len(arr)-1]))
        self.chartAccX.update()

        self._chart_viewAccX.update()

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

def getData(currentComport):
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
    #print(str(int(new_ax)*accel))
    return int(new_ax)*accel


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Inertial Navigation Controll App")
    window.show()
    window.resize(1200, 500)

    sys.exit(app.exec())
