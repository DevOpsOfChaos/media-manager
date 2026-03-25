import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Button {
    id: control
    property string title: ""
    property string subtitle: ""
    implicitHeight: 88
    background: Rectangle {
        radius: 22
        color: control.down ? "#14233A" : (control.hovered ? "#132339" : "#101C2F")
        border.color: "#243650"
    }
    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 4
        Label {
            text: control.title
            color: "#F7FAFF"
            font.pixelSize: 18
            font.bold: true
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
        Label {
            text: control.subtitle
            color: "#AFC1D9"
            font.pixelSize: 13
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }
    }
}
