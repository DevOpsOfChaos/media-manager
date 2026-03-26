import QtQuick
import QtQuick.Controls

Button {
    id: control
    implicitHeight: 60
    implicitWidth: 280

    background: Rectangle {
        radius: 18
        color: control.down ? "#275BC2" : (control.hovered ? "#2A63D1" : "#2F6FED")
        border.color: control.hovered ? "#7BA7FF" : "transparent"
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
