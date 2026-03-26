import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool active: false
    implicitHeight: 42
    implicitWidth: 148
    hoverEnabled: true

    background: Rectangle {
        radius: 14
        color: (control.active || control.hovered) ? "#132B4A" : "transparent"
        border.width: 1
        border.color: (control.active || control.hovered) ? "#4A82D7" : "transparent"
    }

    contentItem: Text {
        text: control.text
        color: "#F7FAFF"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: 14
        font.bold: control.active || control.hovered
    }
}
