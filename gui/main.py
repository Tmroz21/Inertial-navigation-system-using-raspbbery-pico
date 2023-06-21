import serial.tools.list_ports
import sys
import pandas as pd
import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication, QGridLayout, QSizePolicy, QPushButton, QHBoxLayout, QWidget,QVBoxLayout, QComboBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries

df1 = pd.read_csv('gui\pomiar3.csv')

accel = 8.0/32768.0
gyro = 1000.0/32768.0

ax = df1['ax'] * accel
ay = df1['ay'] * accel
az = df1['az'] * accel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.refreshButton = QPushButton("refresh")
        self.comComboBox = QComboBox()

        comList = []

        chartLayout = QHBoxLayout()
        portsViewLayout = QHBoxLayout()
        mainLayout = QVBoxLayout()

        self.AddDataToChart(ax,chartLayout,"X")  
        self.AddDataToChart(ay,chartLayout,"Y")
        self.AddDataToChart(az,chartLayout,"Z")

        self.FindAvalibleComports(comList) # finding avalible ports and appending them to comList
        self.AddPortsToCombo(comList,self.comComboBox) # adding ports to list
        
        self.comComboBox.activated.connect(self.SetCurrentPort) # connecting SetCurrentPort function to comComboBox activating when item is chosen from the list

        portsViewLayout.addWidget(self.refreshButton)
        portsViewLayout.addWidget(self.comComboBox)

        mainLayout.addLayout(portsViewLayout)
        mainLayout.addLayout(chartLayout)
        
        self.setLayout(mainLayout)

    def FindAvalibleComports(self,comList):
        ports = serial.tools.list_ports.comports()

        for port, desc, hwid in sorted(ports):
            comList.append("{}: {}".format(port, desc))
        print(comList)

    def AddDataToChart(self,data,layout,axisTitle):
                
        dataFreqz = 100; # number of readigns from sensor in time of 1s

        self.series = QLineSeries()
        for x in range(len(data)):
             self.series.append(QPointF(x/dataFreqz, data[x]))
        #..creating chart..
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series) # adding series to chart
        self.chart.createDefaultAxes()
        self.chart.setTitle("odczyt z akcelerometru dla osi " + axisTitle)
        #..creating chartView from chart
        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        #..adding chartView to layout
        size = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        size.setHorizontalStretch(1)
        self._chart_view.setSizePolicy(size)
        layout.addWidget(self._chart_view)

    def SetCurrentPort(self):
        print("clicked")
        value = self.comComboBox.currentIndex
        print(value)
        
    def AddPortsToCombo(self,comList,combo):
        for port in sorted(comList):
            combo.addItem(port)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Inertial Navigation Controll App")
    window.show()
    window.resize(1200, 500)
    sys.exit(app.exec())
