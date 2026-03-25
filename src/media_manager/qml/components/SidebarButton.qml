import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool active: false
    implicitHeight: 48
    background: Rectangle {
        radius: 16
        color: control.active ? "#18345B" : (control.hovered ? "#122033" : "transparent")
        border.color: control.active ? "#2F6FED" : "transparent"
    }
    contentItem: Text {
        text: control.text
        color: "#F7FAFF"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 14
        font.pixelSize: 15
        font.bold: control.active
    }
}
