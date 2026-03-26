import QtQuick
import QtQuick.Controls

Button {
    id: control
    implicitHeight: 54
    implicitWidth: 220
    hoverEnabled: true

    background: Rectangle {
        radius: 16
        color: "#2F6FED"
        border.width: 1
        border.color: (control.hovered || control.visualFocus) ? "#A7C7FF" : "#4A82D7"
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
