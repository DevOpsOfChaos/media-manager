import QtQuick
import QtQuick.Controls

Button {
    id: control
    implicitHeight: 54
    implicitWidth: 220
    hoverEnabled: true

    background: Rectangle {
        radius: 16
        color: control.down ? "#275BC2" : (control.hovered ? "#2A64D5" : "#2F6FED")
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
