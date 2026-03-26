import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool active: false
    implicitHeight: 44
    implicitWidth: 156
    hoverEnabled: true

    background: Rectangle {
        radius: 14
        color: control.active ? "#132B4A" : (control.hovered ? "#0E1827" : "transparent")
        border.width: 1
        border.color: control.active ? "#4A82D7" : (control.hovered ? "#314C70" : "transparent")
    }

    contentItem: Text {
        text: control.text
        color: "#F7FAFF"
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.pixelSize: 14
        font.bold: control.active
    }
}
