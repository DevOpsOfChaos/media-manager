import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property string title: ""
    property string subtitle: ""
    property bool selected: false

    implicitHeight: 96
    implicitWidth: 560
    hoverEnabled: true

    background: Rectangle {
        radius: 24
        color: control.down
            ? "#101D2E"
            : (control.hovered ? "#0C1727" : "transparent")
        border.width: control.selected ? 2 : 1
        border.color: control.selected
            ? "#4A82D7"
            : (control.hovered ? "#365D92" : "#243650")

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: 23
            color: control.selected ? "#0E1E34" : "transparent"
            opacity: 0.95
        }
    }

    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 6

        Label {
            text: control.title
            color: "#F7FAFF"
            font.pixelSize: 20
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Label {
            text: control.subtitle
            color: control.selected ? "#D8E7FF" : "#AFC1D9"
            font.pixelSize: 14
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
            visible: text.length > 0
        }
    }
}
