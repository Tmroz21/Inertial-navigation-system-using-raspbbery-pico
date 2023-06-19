import QtQuick 2.14
import QtQuick.Window 2.14
import QtQuick.Controls 2.14
import QtCharts 2.14
import QtQml 2.14

ApplicationWindow {
    id: window 
    width: 600
    height: 800
    visible: true 
    title: qsTr("test")

    ChartView{
        width: 500
        height: 300
        anchors.centerIn: parent

        LineSeries{
              XYPoint { x: 0; y: 0 }
              XYPoint { x: 1.1; y: 2.1 }
              XYPoint { x: 1.9; y: 3.3 }
              XYPoint { x: 2.1; y: 2.1 }
              XYPoint { x: 2.9; y: 4.9 }
              XYPoint { x: 3.4; y: 3.0 }
              XYPoint { x: 4.1; y: 3.3 }
        }

        Timer{
            id: refreshTimer
            interval: 1 / 60 * 1000 // 60 Hz
            running: true
            repeat: true
        }
    }
}

