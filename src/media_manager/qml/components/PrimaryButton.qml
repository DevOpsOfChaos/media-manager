import QtQuick
import QtQuick.Controls

Button {
    id: control
    implicitHeight: 58
    implicitWidth: 260
    background: Rectangle {
        radius: 18
        color: control.down ? "#275BC2" : (control.hovered ? "#2A63D1" : "#2F6FED")
    }
    contentItem: Text {
        text: control.text
        color: "#F7FAFF"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: 16
        font.bold: true
    }
}
