import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property string title: ""
    property string subtitle: ""

    implicitHeight: 74
    implicitWidth: 540
    hoverEnabled: true

    background: Rectangle {
        radius: 20
        color: control.down ? "#0B1521" : (control.hovered ? "#0A1420" : "transparent")
        border.width: 1
        border.color: control.hovered ? "#3D68A1" : "#22324A"
    }

    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 2

        Label {
            text: control.title
            color: "#F7FAFF"
            font.pixelSize: 16
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Label {
            text: control.subtitle
            color: "#AFC1D9"
            font.pixelSize: 12
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            visible: text.length > 0
        }
    }
}
