import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property string title: ""
    property string subtitle: ""
    implicitHeight: 104

    background: Rectangle {
        radius: 24
        color: control.down ? "#15263F" : (control.hovered ? "#14253D" : "#101C2F")
        border.color: control.hovered ? "#3A5F8A" : "#243650"

        Rectangle {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 5
            radius: 3
            color: "#2F6FED"
            opacity: control.hovered ? 1.0 : 0.75
        }
    }

    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        anchors.leftMargin: 24
        spacing: 6

        Label {
            text: control.title
            color: "#F7FAFF"
            font.pixelSize: 20
            font.bold: true
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        Label {
            text: control.subtitle
            color: "#AFC1D9"
            font.pixelSize: 14
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }
}
