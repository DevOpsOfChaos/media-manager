import QtQuick
import QtQuick.Controls

Button {
    id: control
    implicitHeight: 54
    implicitWidth: 220
    hoverEnabled: true

    background: Rectangle {
        radius: 16
        color: control.down ? "#234FAE" : "#2F6FED"
        border.width: 1
        border.color: (control.hovered || control.down) ? "#9BC0FF" : "#7BA7FF"
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
