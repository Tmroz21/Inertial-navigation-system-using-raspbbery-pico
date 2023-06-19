
import sys
import pandas as pd
import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QMainWindow, QApplication, QGridLayout, QSizePolicy, QPushButton, QHBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries

df1 = pd.read_csv('pomiar3.csv')

accel = 8.0/32768.0
gyro = 1000.0/32768.0

ax = df1['ax'] * accel
ay = df1['ay'] * accel
az = df1['az'] * accel

class TestChart(QMainWindow):
    def __init__(self):
        super().__init__()

        self.series = QLineSeries()
        for x in range(len(ax)):
             self.series.append(QPointF(x/100, ax[x]))
             

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setTitle("odczyt osi x akcelerometr")

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)

        self.testButton = QPushButton()

        self.layout = QHBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)

        size.setHorizontalStretch(1)
        self.testButton.setSizePolicy(size)
        self.layout.addWidget(self.testButton)

        #size.setHorizontalStretch(4)
        #self._chart_view.setSizePolicy(size)
        #self.layout.addWidget(self._chart_view)


        self.setLayout(self.layout)
        #self.setCentralWidget(self._chart_view)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TestChart()
    window.show()
    window.resize(440, 300)
    sys.exit(app.exec())