import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    property string label: ""
    property string value: "-"
    radius: 18
    color: "#0F1A2C"
    border.color: "#22324A"
    Layout.preferredWidth: 140
    Layout.fillHeight: true

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 4
        Label {
            text: root.label
            color: "#93A8C6"
            font.pixelSize: 12
            Layout.fillWidth: true
        }
        Label {
            text: root.value
            color: "#F7FAFF"
            font.pixelSize: 16
            font.bold: true
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
    }
}
