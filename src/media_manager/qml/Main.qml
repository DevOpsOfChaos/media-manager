import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import "components"

ApplicationWindow {
    id: root
    visible: true
    width: 1360
    height: 860
    minimumWidth: 1180
    minimumHeight: 760
    title: root.trKey("app_title")
    color: "#07111F"

    property string langTick: appState.language

    function trKey(key) {
        const _ = appState.language
        return appState.text(key)
    }

    function problemLabelText(key) {
        const _ = appState.language
        return appState.problemLabel(key)
    }

    function problemDescriptionText(key) {
        const _ = appState.language
        return appState.problemDescription(key)
    }

    function pageIndex() {
        if (appState.currentPage === "home")
            return 0
        if (appState.currentPage === "workflow")
            return 1
        return 2
    }

        component SubtleOutlineButtonBackground : Rectangle {
        radius: 16
        color: parent.down ? "#102038" : ((parent.hovered || (typeof parent.active !== "undefined" && parent.active)) ? "#132B4A" : "transparent")
        border.width: 1
        border.color: (parent.hovered || (typeof parent.active !== "undefined" && parent.active)) ? "#4A82D7" : "#30465F"
    }

    FolderDialog {
        id: sourceFolderDialog
        onAccepted: appState.addSourceFolder(selectedFolder.toString())
    }

    FolderDialog {
        id: targetFolderDialog
        onAccepted: appState.setTargetFolder(selectedFolder.toString())
    }

    Popup {
        id: duplicateDetailPopup
        width: Math.min(root.width * 0.78, 980)
        height: Math.min(root.height * 0.78, 720)
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        anchors.centerIn: Overlay.overlay
        onClosed: appState.closeDuplicateGroup()

        background: Rectangle {
            radius: 28
            color: "#0C1728"
            border.color: "#27456E"
        }

        contentItem: ColumnLayout {
            anchors.fill: parent
            anchors.margins: 22
            spacing: 14

            RowLayout {
                Layout.fillWidth: true

                Label {
                    text: appState.duplicateDetailTitle
                    color: "#F7FAFF"
                    font.pixelSize: 28
                    font.bold: true
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Button {
                    text: "✕"
                    onClicked: duplicateDetailPopup.close()

                    background: Rectangle {
                        radius: 12
                        color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                        border.width: 1
                        border.color: parent.hovered ? "#4A82D7" : "#30465F"
                    }

                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 18
                        font.bold: true
                    }
                }
            }

            Label {
                text: appState.duplicateDetailSummary
                color: "#AFC1D9"
                font.pixelSize: 15
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Label {
                text: root.trKey("duplicate_detail_hint")
                color: "#8FB0E1"
                font.pixelSize: 14
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 20
                color: "#091321"
                border.color: "#22324A"

                Flickable {
                    anchors.fill: parent
                    anchors.margins: 14
                    contentWidth: width
                    contentHeight: detailRows.implicitHeight
                    clip: true

                    Column {
                        id: detailRows
                        width: parent.width
                        spacing: 10

                        Repeater {
                            model: appState.duplicateDetailFiles

                            delegate: Rectangle {
                                width: detailRows.width
                                height: 104
                                radius: 16
                                color: modelData.selected ? "#173056" : "#0F1A2C"
                                border.color: modelData.selected ? "#4A82D7" : "#22324A"

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: appState.selectDuplicateCandidate(index)
                                }

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 14
                                    spacing: 6

                                    RowLayout {
                                        Layout.fillWidth: true

                                        Label {
                                            text: modelData.name
                                            color: "#F7FAFF"
                                            font.pixelSize: 16
                                            font.bold: true
                                            Layout.fillWidth: true
                                            elide: Text.ElideRight
                                        }

                                        Rectangle {
                                            radius: 10
                                            color: modelData.selected ? "#132B4A" : "transparent"
                                            border.width: 1
                                            border.color: modelData.selected ? "#4A82D7" : "#30465F"
                                            Layout.preferredWidth: 170
                                            Layout.preferredHeight: 30

                                            Label {
                                                anchors.centerIn: parent
                                                text: modelData.selected ? root.trKey("duplicate_detail_selected") : ""
                                                color: "#F7FAFF"
                                                font.pixelSize: 12
                                                font.bold: true
                                            }
                                        }
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 12

                                        Label {
                                            text: modelData.size
                                            color: "#AFC1D9"
                                            font.pixelSize: 13
                                        }

                                        Label {
                                            text: modelData.date
                                            color: "#AFC1D9"
                                            font.pixelSize: 13
                                        }
                                    }

                                    Label {
                                        text: root.trKey("duplicate_detail_path") + ": " + modelData.path
                                        color: "#93A8C6"
                                        font.pixelSize: 12
                                        wrapMode: Text.WrapAnywhere
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Button {
                    text: root.trKey("duplicate_detail_keep_selected")
                    onClicked: appState.keepSelectedDuplicateCandidate()
                    background: Rectangle {
                        radius: 14
                        color: parent.down ? "#234FAE" : "#2F6FED"
                        border.width: 1
                        border.color: "#7BA7FF"
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }

                Button {
                    text: root.trKey("duplicate_detail_keep_newest")
                    onClicked: appState.chooseDuplicateKeepNewest()
                    background: Rectangle {
                        radius: 14
                        color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                        border.width: 1
                        border.color: parent.hovered ? "#4A82D7" : "#30465F"
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }

                Button {
                    text: root.trKey("duplicate_detail_keep_oldest")
                    onClicked: appState.chooseDuplicateKeepOldest()
                    background: Rectangle {
                        radius: 14
                        color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                        border.width: 1
                        border.color: parent.hovered ? "#4A82D7" : "#30465F"
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }

                Item { Layout.fillWidth: true }

                Button {
                    text: root.trKey("duplicate_detail_close")
                    onClicked: duplicateDetailPopup.close()
                    background: Rectangle {
                        radius: 14
                        color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                        border.width: 1
                        border.color: parent.hovered ? "#4A82D7" : "#30465F"
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#091321" }
            GradientStop { position: 0.45; color: "#07111F" }
            GradientStop { position: 1.0; color: "#050D19" }
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 18

        Rectangle {
            Layout.preferredWidth: 188
            Layout.fillHeight: true
            radius: 26
            color: "#081322"
            border.color: "#1E2C40"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Label {
                    text: root.trKey("app_title")
                    color: "#F7FAFF"
                    font.pixelSize: 16
                    font.bold: true
                    font.family: "SF Pro Display, Segoe UI Variable, Segoe UI, Arial"
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    text: root.trKey("nav_subtitle")
                    color: "#8FA7C7"
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                Item { Layout.preferredHeight: 6 }

                SidebarButton { text: root.trKey("nav_home"); active: appState.currentPage === "home"; onClicked: appState.setPage("home") }
                SidebarButton { text: root.trKey("nav_workflow"); active: appState.currentPage === "workflow"; onClicked: appState.setPage("workflow") }
                SidebarButton { text: root.trKey("nav_duplicates"); active: appState.currentPage === "duplicates"; onClicked: appState.setPage("duplicates") }
                SidebarButton { text: root.trKey("nav_organize"); active: appState.currentPage === "organize"; onClicked: appState.setPage("organize") }
                SidebarButton { text: root.trKey("nav_rename"); active: appState.currentPage === "rename"; onClicked: appState.setPage("rename") }

                Item { Layout.fillHeight: true }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                Item { Layout.fillWidth: true }

                Button {
                    Layout.preferredWidth: 60
                    Layout.preferredHeight: 36
                    ToolTip.visible: hovered
                    ToolTip.text: root.trKey("language_tooltip")
                    onClicked: appState.toggleLanguage()

                    background: Rectangle {
                        radius: 12
                        color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                        border.width: 1
                        border.color: (parent.hovered || parent.down) ? "#4A82D7" : "#30465F"
                    }

                    contentItem: Image {
                        source: appState.flagPath
                        fillMode: Image.PreserveAspectFit
                        anchors.fill: parent
                        anchors.margins: 6
                    }
                }
            }

            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: pageIndex()

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Flickable {
                        anchors.fill: parent
                        contentWidth: width
                        contentHeight: homeColumn.implicitHeight
                        clip: true

                        ColumnLayout {
                            id: homeColumn
                            width: parent.width
                            spacing: 14

                            Item { Layout.preferredHeight: 12 }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: root.trKey("home_title")
                                color: "#F7FAFF"
                                font.pixelSize: 58
                                font.bold: true
                                font.family: "SF Pro Display, Segoe UI Variable, Segoe UI, Arial"
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: root.trKey("home_subtitle")
                                color: "#B7CAE2"
                                font.pixelSize: 16
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.WordWrap
                                Layout.preferredWidth: 720
                            }

                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: 150
                                Layout.preferredHeight: 2
                                color: "#355988"
                                opacity: 0.75
                            }

                            ColumnLayout {
                                Layout.alignment: Qt.AlignHCenter
                                spacing: 10
                                visible: appState.wizardVisible

                                Repeater {
                                    model: ["full_cleanup", "ready_for_sorting", "ready_for_rename", "exact_duplicates_only"]

                                    delegate: Button {
                                        required property string modelData
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 560
                                        Layout.preferredHeight: 62
                                        hoverEnabled: true
                                        onClicked: appState.selectProblemAndStart(modelData)

                                        background: Rectangle {
                                            radius: 18
                                            color: parent.down ? "#102038" : ((parent.hovered || parent.visualFocus) ? "#132B4A" : "transparent")
                                            border.width: 1
                                            border.color: (parent.hovered || parent.visualFocus) ? "#4A82D7" : "#263A57"
                                        }

                                        contentItem: Text {
                                            text: root.problemLabelText(modelData)
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            wrapMode: Text.WordWrap
                                            font.pixelSize: 16
                                            font.bold: true
                                        }
                                    }
                                }
                            }

                            Button {
                                visible: appState.wizardVisible
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: 230
                                Layout.preferredHeight: 52
                                text: root.trKey("home_dismiss")
                                onClicked: appState.dismissWizard()
                                hoverEnabled: true

                                background: Rectangle {
                                    radius: 16
                                    color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                                    border.color: parent.hovered ? "#4A82D7" : "#30465F"
                                    border.width: 1
                                }

                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 15
                                    font.bold: true
                                }
                            }

                            Button {
                                visible: !appState.wizardVisible
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: 260
                                Layout.preferredHeight: 54
                                text: root.trKey("home_restart")
                                onClicked: appState.restartWizard()

                                background: Rectangle {
                                    radius: 18
                                    color: parent.down ? "#234FAE" : "#2F6FED"
                                    border.width: 1
                                    border.color: "#7BA7FF"
                                }

                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 16
                                    font.bold: true
                                }
                            }

                            Item { Layout.preferredHeight: 2 }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: root.trKey("home_info_title")
                                color: "#F7FAFF"
                                font.pixelSize: 28
                                font.bold: true
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: root.trKey("home_info_body")
                                color: "#C9D9EE"
                                font.pixelSize: 16
                                horizontalAlignment: Text.AlignHCenter
                                wrapMode: Text.WordWrap
                                Layout.preferredWidth: 720
                            }

                            Item { Layout.preferredHeight: 18 }
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 12

                        RowLayout {
                            Layout.fillWidth: true

                            ColumnLayout {
                                spacing: 4

                                Label {
                                    text: root.trKey("workflow_title")
                                    color: "#F7FAFF"
                                    font.pixelSize: 30
                                    font.bold: true
                                }

                                Label {
                                    text: root.trKey("workflow_subtitle")
                                    color: "#AFC1D9"
                                    font.pixelSize: 14
                                }
                            }

                            Item { Layout.fillWidth: true }

                            Rectangle {
                                radius: 12
                                color: "transparent"
                                border.color: "#27456E"
                                Layout.preferredWidth: 96
                                Layout.preferredHeight: 34

                                Label {
                                    anchors.centerIn: parent
                                    text: (appState.workflowStageIndex + 1) + " / " + appState.workflowTotalSteps
                                    color: "#B8D3FF"
                                    font.pixelSize: 13
                                    font.bold: true
                                }
                            }
                        }

                        ProgressBar {
                            Layout.fillWidth: true
                            from: 0
                            to: appState.workflowTotalSteps
                            value: appState.workflowStageIndex + 1

                            background: Rectangle {
                                radius: 8
                                color: "#101B2D"
                            }

                            contentItem: Item {
                                Rectangle {
                                    width: parent.width * ((appState.workflowStageIndex + 1) / appState.workflowTotalSteps)
                                    height: parent.height
                                    radius: 8
                                    color: "#2F6FED"
                                }
                            }
                        }

                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: 820
                            Layout.fillHeight: true
                            radius: 26
                            color: "transparent"
                            border.color: "#243650"

                            Item {
                                anchors.fill: parent
                                anchors.margins: 24

                                StackLayout {
                                    anchors.fill: parent
                                    currentIndex: appState.workflowStageIndex

                                    // sources
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12

                                            Label {
                                                text: appState.workflowStageTitle
                                                color: "#F7FAFF"
                                                font.pixelSize: 26
                                                font.bold: true
                                            }

                                            Label {
                                                text: appState.workflowStageSubtitle
                                                color: "#AFC1D9"
                                                font.pixelSize: 15
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                radius: 18
                                                color: "#091321"
                                                border.color: "#22324A"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 22
                                                    spacing: 16

                                                    Label {
                                                        visible: appState.sourceCount === 0
                                                        Layout.alignment: Qt.AlignHCenter
                                                        text: root.trKey("stage_sources_empty")
                                                        color: "#8FB0E1"
                                                        font.pixelSize: 18
                                                        horizontalAlignment: Text.AlignHCenter
                                                    }

                                                    Rectangle {
                                                        visible: appState.sourceCount > 0
                                                        Layout.alignment: Qt.AlignHCenter
                                                        radius: 14
                                                        color: "#102038"
                                                        border.color: "#4A82D7"
                                                        implicitWidth: sourceCountChip.implicitWidth + 28
                                                        implicitHeight: sourceCountChip.implicitHeight + 16

                                                        Label {
                                                            id: sourceCountChip
                                                            anchors.centerIn: parent
                                                            text: appState.sourceCount + " " + (appState.sourceCount === 1 ? "folder selected" : "folders selected")
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 14
                                                            font.bold: true
                                                        }
                                                    }

                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        Layout.fillHeight: true
                                                        radius: 18
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        Loader {
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            active: appState.sourceCount > 0
                                                            sourceComponent: sourceListComponent
                                                        }

                                                        ColumnLayout {
                                                            visible: appState.sourceCount === 0
                                                            anchors.centerIn: parent
                                                            spacing: 10

                                                            Label {
                                                                text: "1"
                                                                color: "#4A82D7"
                                                                font.pixelSize: 22
                                                                font.bold: true
                                                                horizontalAlignment: Text.AlignHCenter
                                                                Layout.alignment: Qt.AlignHCenter
                                                            }

                                                            Label {
                                                                text: "Choose one or more source folders to begin the guided cleanup."
                                                                color: "#CFE1FF"
                                                                font.pixelSize: 15
                                                                horizontalAlignment: Text.AlignHCenter
                                                                wrapMode: Text.WordWrap
                                                                Layout.preferredWidth: 520
                                                                Layout.alignment: Qt.AlignHCenter
                                                            }
                                                        }
                                                    }

                                                    RowLayout {
                                                        Layout.fillWidth: true
                                                        spacing: 10

                                                        PrimaryButton {
                                                            text: root.trKey("stage_sources_action")
                                                            onClicked: sourceFolderDialog.open()
                                                        }

                                                        Button {
                                                            text: root.trKey("button_clear")
                                                            enabled: appState.sourceCount > 0
                                                            onClicked: appState.clearSourceFolders()
                                                            hoverEnabled: true
                                                            background: SubtleOutlineButtonBackground {}
                                                            contentItem: Text {
                                                                text: parent.text
                                                                color: "#F7FAFF"
                                                                horizontalAlignment: Text.AlignHCenter
                                                                verticalAlignment: Text.AlignVCenter
                                                                font.pixelSize: 14
                                                                font.bold: true
                                                            }
                                                        }

                                                        Item { Layout.fillWidth: true }
                                                    }
                                                }
                                            }
                                        }
                                    }

// target
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12

                                            Label {
                                                text: appState.workflowStageTitle
                                                color: "#F7FAFF"
                                                font.pixelSize: 26
                                                font.bold: true
                                            }

                                            Label {
                                                text: appState.workflowStageSubtitle
                                                color: "#AFC1D9"
                                                font.pixelSize: 15
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                radius: 18
                                                color: "#091321"
                                                border.color: "#22324A"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 22
                                                    spacing: 16

                                                    Rectangle {
                                                        visible: appState.targetPath.length > 0
                                                        Layout.alignment: Qt.AlignHCenter
                                                        radius: 14
                                                        color: "#102038"
                                                        border.color: "#4A82D7"
                                                        implicitWidth: targetChipLabel.implicitWidth + 28
                                                        implicitHeight: targetChipLabel.implicitHeight + 16

                                                        Label {
                                                            id: targetChipLabel
                                                            anchors.centerIn: parent
                                                            text: "Target selected"
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 14
                                                            font.bold: true
                                                        }
                                                    }

                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        Layout.fillHeight: true
                                                        radius: 18
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 18
                                                            spacing: 12

                                                            Label {
                                                                text: appState.targetPath.length > 0 ? "Chosen target folder" : "No target folder selected yet"
                                                                color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"
                                                                font.pixelSize: 18
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Rectangle {
                                                                Layout.fillWidth: true
                                                                Layout.fillHeight: true
                                                                radius: 14
                                                                color: "#091321"
                                                                border.color: "#22324A"

                                                                Label {
                                                                    anchors.fill: parent
                                                                    anchors.margins: 16
                                                                    text: appState.targetPath.length > 0 ? appState.targetPath : root.trKey("stage_target_empty")
                                                                    color: appState.targetPath.length > 0 ? "#E6EEF8" : "#8FB0E1"
                                                                    wrapMode: Text.WrapAnywhere
                                                                    verticalAlignment: Text.AlignVCenter
                                                                    font.pixelSize: 15
                                                                }
                                                            }

                                                            Label {
                                                                text: "The action mode can still be changed later before real execution."
                                                                color: "#AFC1D9"
                                                                font.pixelSize: 13
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }

                                                    RowLayout {
                                                        Layout.fillWidth: true
                                                        spacing: 10

                                                        PrimaryButton {
                                                            text: root.trKey("stage_target_action")
                                                            onClicked: targetFolderDialog.open()
                                                        }

                                                        Button {
                                                            text: root.trKey("button_clear")
                                                            enabled: appState.targetPath.length > 0
                                                            onClicked: appState.clearTargetFolder()
                                                            hoverEnabled: true
                                                            background: SubtleOutlineButtonBackground {}
                                                            contentItem: Text {
                                                                text: parent.text
                                                                color: "#F7FAFF"
                                                                horizontalAlignment: Text.AlignHCenter
                                                                verticalAlignment: Text.AlignVCenter
                                                                font.pixelSize: 14
                                                                font.bold: true
                                                            }
                                                        }

                                                        Item { Layout.fillWidth: true }
                                                    }
                                                }
                                            }
                                        }
                                    }

// mode
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12
                                            Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 26; font.bold: true }
                                            Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            ColumnLayout {
                                                Layout.alignment: Qt.AlignHCenter
                                                spacing: 12

                                                Repeater {
                                                    model: ["copy", "move", "delete"]

                                                    delegate: Button {
                                                        required property string modelData
                                                        Layout.alignment: Qt.AlignHCenter
                                                        Layout.preferredWidth: 440
                                                        Layout.preferredHeight: 60
                                                        hoverEnabled: true
                                                        onClicked: appState.setOperationMode(modelData)

                                                        background: Rectangle {
                                                            radius: 18
                                                            color: appState.operationMode === modelData ? "#132B4A" : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                                                            border.color: (appState.operationMode === modelData || parent.hovered) ? "#4A82D7" : "#263A57"
                                                            border.width: (appState.operationMode === modelData || parent.hovered) ? 2 : 1
                                                        }

                                                        contentItem: Text {
                                                            text: root.trKey("mode_" + modelData)
                                                            color: "#F7FAFF"
                                                            horizontalAlignment: Text.AlignHCenter
                                                            verticalAlignment: Text.AlignVCenter
                                                            font.pixelSize: 16
                                                            font.bold: true
                                                        }
                                                    }
                                                }
                                            }

                                            Item { Layout.fillHeight: true }
                                        }
                                    }

                                    // duplicates
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12
                                            Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 26; font.bold: true }
                                            Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            PrimaryButton { text: root.trKey("stage_duplicates_action"); enabled: appState.sourceCount > 0; onClicked: appState.startDuplicatePreview() }

                                            ProgressBar {
                                                Layout.fillWidth: true
                                                from: 0
                                                to: 100
                                                value: appState.duplicateProgress
                                                background: Rectangle { radius: 8; color: "#101B2D" }
                                                contentItem: Item { Rectangle { width: parent.width * (appState.duplicateProgress / 100.0); height: parent.height; radius: 8; color: "#2F6FED" } }
                                            }

                                            Label { text: appState.statusText; color: "#CFE1FF"; wrapMode: Text.WordWrap; font.pixelSize: 14; Layout.fillWidth: true }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                radius: 18
                                                color: "#091321"
                                                border.color: "#22324A"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 14
                                                    spacing: 8

                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        Layout.preferredHeight: 42
                                                        radius: 12
                                                        color: "#0F1A2C"

                                                        RowLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 10
                                                            spacing: 8
                                                            Repeater {
                                                                model: [root.trKey("table_name"), root.trKey("table_size"), root.trKey("table_date"), root.trKey("table_matches"), root.trKey("table_score"), root.trKey("table_action")]
                                                                delegate: Label {
                                                                    Layout.fillWidth: true
                                                                    text: modelData
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 13
                                                                    font.bold: true
                                                                }
                                                            }
                                                        }
                                                    }

                                                    Flickable {
                                                        Layout.fillWidth: true
                                                        Layout.fillHeight: true
                                                        contentWidth: width
                                                        contentHeight: rowsColumn.implicitHeight
                                                        clip: true

                                                        Column {
                                                            id: rowsColumn
                                                            width: parent.width
                                                            spacing: 8

                                                            Repeater {
                                                                model: appState.duplicateRows
                                                                delegate: Rectangle {
                                                                    width: rowsColumn.width
                                                                    height: 52
                                                                    radius: 12
                                                                    color: "#0F1A2C"
                                                                    border.color: "#22324A"

                                                                    RowLayout {
                                                                        anchors.fill: parent
                                                                        anchors.margins: 10
                                                                        spacing: 8
                                                                        Label { Layout.fillWidth: true; text: modelData.name; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                        Label { Layout.fillWidth: true; text: modelData.size; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                        Label { Layout.fillWidth: true; text: modelData.date; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                        Label { Layout.fillWidth: true; text: modelData.matches; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                        Label { Layout.fillWidth: true; text: modelData.score; color: modelData.score === "100%" ? "#8CE99A" : "#FFD18C"; font.pixelSize: 13; font.bold: true }
                                                                        Button {
                                                                            Layout.fillWidth: true
                                                                            text: root.trKey("table_show")
                                                                            hoverEnabled: true
                                                                            onClicked: {
                                                                                appState.openDuplicateGroup(Number(modelData.index))
                                                                                duplicateDetailPopup.open()
                                                                            }
                                                                            background: SubtleOutlineButtonBackground {}
                                                                            contentItem: Text {
                                                                                text: parent.text
                                                                                color: "#F7FAFF"
                                                                                horizontalAlignment: Text.AlignHCenter
                                                                                verticalAlignment: Text.AlignVCenter
                                                                                font.pixelSize: 12
                                                                                font.bold: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // summary
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12

                                            Label {
                                                text: appState.workflowStageTitle
                                                color: "#F7FAFF"
                                                font.pixelSize: 26
                                                font.bold: true
                                            }

                                            Label {
                                                text: appState.workflowStageSubtitle
                                                color: "#AFC1D9"
                                                font.pixelSize: 15
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }

                                            Flickable {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                contentWidth: width
                                                contentHeight: summaryScrollColumn.implicitHeight
                                                clip: true

                                                ColumnLayout {
                                                    id: summaryScrollColumn
                                                    width: parent.width
                                                    spacing: 14

                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        implicitHeight: summaryHeroColumn.implicitHeight + 32
                                                        radius: 18
                                                        color: appState.summaryReadyForDryRun ? "#123926" : "#40241F"
                                                        border.color: appState.summaryReadyForDryRun ? "#47B36A" : "#D07A63"

                                                        ColumnLayout {
                                                            id: summaryHeroColumn
                                                            anchors.fill: parent
                                                            anchors.margins: 16
                                                            spacing: 8

                                                            Label {
                                                                text: appState.summaryDecisionStatus
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 22
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Label {
                                                                text: appState.summaryReadyForDryRun ? root.trKey("summary_ready_body") : root.trKey("summary_unresolved_body")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 14
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }

                                                    GridLayout {
                                                        Layout.fillWidth: true
                                                        columns: 4
                                                        columnSpacing: 10
                                                        rowSpacing: 10

                                                        Repeater {
                                                            model: [
                                                                [root.trKey("summary_groups"), appState.summaryExactGroupCount.toString()],
                                                                [root.trKey("summary_duplicate_files"), appState.summaryExactDuplicateFiles.toString()],
                                                                [root.trKey("summary_extra_duplicates"), appState.summaryExtraDuplicates.toString()],
                                                                [root.trKey("summary_mode"), appState.summaryOperationModeLabel]
                                                            ]

                                                            delegate: Rectangle {
                                                                required property var modelData
                                                                Layout.fillWidth: true
                                                                Layout.preferredHeight: 86
                                                                radius: 16
                                                                color: "#0F1A2C"
                                                                border.color: "#22324A"

                                                                ColumnLayout {
                                                                    anchors.fill: parent
                                                                    anchors.margins: 14
                                                                    spacing: 6

                                                                    Label {
                                                                        text: modelData[0]
                                                                        color: "#AFC1D9"
                                                                        font.pixelSize: 12
                                                                        wrapMode: Text.WordWrap
                                                                        Layout.fillWidth: true
                                                                    }

                                                                    Label {
                                                                        text: modelData[1]
                                                                        color: "#F7FAFF"
                                                                        font.pixelSize: 22
                                                                        font.bold: true
                                                                        Layout.fillWidth: true
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }

                                                                                                        Rectangle {
                                                        Layout.fillWidth: true
                                                        implicitHeight: dryRunColumn.implicitHeight + 28
                                                        radius: 18
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            id: dryRunColumn
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            spacing: 10

                                                            RowLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 10

                                                                Label {
                                                                    text: root.trKey("dryrun_title")
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 18
                                                                    font.bold: true
                                                                    Layout.fillWidth: true
                                                                }

                                                                Rectangle {
                                                                    radius: 12
                                                                    color: appState.dryRunReady ? "#123926" : "#40241F"
                                                                    border.color: appState.dryRunReady ? "#47B36A" : "#D07A63"
                                                                    implicitWidth: dryRunStatusChip.implicitWidth + 22
                                                                    implicitHeight: dryRunStatusChip.implicitHeight + 12

                                                                    Label {
                                                                        id: dryRunStatusChip
                                                                        anchors.centerIn: parent
                                                                        text: appState.dryRunStatusLabel
                                                                        color: "#F7FAFF"
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                    }
                                                                }

                                                                Rectangle {
                                                                    radius: 12
                                                                    color: "transparent"
                                                                    border.color: "#355988"
                                                                    implicitWidth: dryRunCountChip.implicitWidth + 22
                                                                    implicitHeight: dryRunCountChip.implicitHeight + 12

                                                                    Label {
                                                                        id: dryRunCountChip
                                                                        anchors.centerIn: parent
                                                                        text: appState.dryRunRowsCountLabel
                                                                        color: "#B8D3FF"
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                text: root.trKey("dryrun_subtitle")
                                                                color: "#CFE1FF"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }

                                                            GridLayout {
                                                                Layout.fillWidth: true
                                                                columns: 5
                                                                columnSpacing: 10
                                                                rowSpacing: 10

                                                                Repeater {
                                                                    model: [
                                                                        [root.trKey("dryrun_filter_planned"), appState.dryRunPlannedCount.toString()],
                                                                        [root.trKey("dryrun_filter_blocked"), appState.dryRunBlockedCount.toString()],
                                                                        [root.trKey("dryrun_filter_delete"), appState.dryRunDeleteCount.toString()],
                                                                        [root.trKey("dryrun_filter_exclude_from_copy"), appState.dryRunExcludeFromCopyCount.toString()],
                                                                        [root.trKey("dryrun_filter_exclude_from_move"), appState.dryRunExcludeFromMoveCount.toString()]
                                                                    ]

                                                                    delegate: Rectangle {
                                                                        required property var modelData
                                                                        Layout.fillWidth: true
                                                                        Layout.preferredHeight: 78
                                                                        radius: 14
                                                                        color: "#091321"
                                                                        border.color: "#22324A"

                                                                        ColumnLayout {
                                                                            anchors.fill: parent
                                                                            anchors.margins: 12
                                                                            spacing: 4

                                                                            Label {
                                                                                text: modelData[0]
                                                                                color: "#AFC1D9"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: modelData[1]
                                                                                color: "#F7FAFF"
                                                                                font.pixelSize: 20
                                                                                font.bold: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Flow {
                                                                Layout.fillWidth: true
                                                                spacing: 8

                                                                Repeater {
                                                                    model: appState.dryRunFilterOptions

                                                                    delegate: Button {
                                                                        required property var modelData
                                                                        text: modelData.label
                                                                        hoverEnabled: true
                                                                        onClicked: appState.setDryRunFilter(modelData.key)

                                                                        background: Rectangle {
                                                                            radius: 12
                                                                            color: appState.dryRunFilterKey === modelData.key
                                                                                ? "#132B4A"
                                                                                : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                                                                            border.width: 1
                                                                            border.color: appState.dryRunFilterKey === modelData.key
                                                                                ? "#4A82D7"
                                                                                : (parent.hovered ? "#4A82D7" : "#30465F")
                                                                        }

                                                                        contentItem: Text {
                                                                            text: parent.text
                                                                            color: "#F7FAFF"
                                                                            horizontalAlignment: Text.AlignHCenter
                                                                            verticalAlignment: Text.AlignVCenter
                                                                            font.pixelSize: 12
                                                                            font.bold: true
                                                                            wrapMode: Text.WordWrap
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            ColumnLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 8
                                                                visible: appState.dryRunRows.length > 0

                                                                Repeater {
                                                                    model: appState.dryRunRows

                                                                    delegate: Rectangle {
                                                                        required property var modelData
                                                                        Layout.fillWidth: true
                                                                        implicitHeight: dryRunRowColumn.implicitHeight + 24
                                                                        radius: 14
                                                                        color: "#091321"
                                                                        border.color: modelData.status === "blocked" ? "#D07A63" : "#22324A"

                                                                        ColumnLayout {
                                                                            id: dryRunRowColumn
                                                                            anchors.fill: parent
                                                                            anchors.margins: 12
                                                                            spacing: 5

                                                                            RowLayout {
                                                                                Layout.fillWidth: true
                                                                                spacing: 8

                                                                                Label {
                                                                                    text: modelData.source_name
                                                                                    color: "#F7FAFF"
                                                                                    font.pixelSize: 13
                                                                                    font.bold: true
                                                                                    Layout.fillWidth: true
                                                                                    elide: Text.ElideRight
                                                                                }

                                                                                Rectangle {
                                                                                    radius: 10
                                                                                    color: modelData.status === "blocked" ? "#40241F" : "#132B4A"
                                                                                    border.color: modelData.status === "blocked" ? "#D07A63" : "#4A82D7"
                                                                                    implicitWidth: dryRunRowStatus.implicitWidth + 16
                                                                                    implicitHeight: dryRunRowStatus.implicitHeight + 8

                                                                                    Label {
                                                                                        id: dryRunRowStatus
                                                                                        anchors.centerIn: parent
                                                                                        text: modelData.status_label
                                                                                        color: "#F7FAFF"
                                                                                        font.pixelSize: 11
                                                                                        font.bold: true
                                                                                    }
                                                                                }

                                                                                Rectangle {
                                                                                    radius: 10
                                                                                    color: "transparent"
                                                                                    border.color: "#30465F"
                                                                                    implicitWidth: dryRunRowAction.implicitWidth + 16
                                                                                    implicitHeight: dryRunRowAction.implicitHeight + 8

                                                                                    Label {
                                                                                        id: dryRunRowAction
                                                                                        anchors.centerIn: parent
                                                                                        text: modelData.action_label
                                                                                        color: "#B8D3FF"
                                                                                        font.pixelSize: 11
                                                                                        font.bold: true
                                                                                    }
                                                                                }
                                                                            }

                                                                            Label {
                                                                                text: modelData.reason_label + "  â€¢  " + modelData.size + "  â€¢  " + modelData.operation_mode_label
                                                                                color: "#AFC1D9"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: modelData.source_path
                                                                                color: "#8FB0E1"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WrapAnywhere
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                visible: modelData.survivor_path.length > 0
                                                                                text: "Survivor: " + modelData.survivor_name
                                                                                color: "#CFE1FF"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                visible: modelData.target_path.length > 0
                                                                                text: "Target: " + modelData.target_path
                                                                                color: "#6F8FB9"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WrapAnywhere
                                                                                Layout.fillWidth: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                visible: appState.dryRunRows.length === 0
                                                                text: appState.language === "de"
                                                                      ? "Noch keine Dry-Run-Zeilen sichtbar."
                                                                      : "No dry-run rows visible yet."
                                                                color: "#AFC1D9"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }

                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        implicitHeight: executionColumn.implicitHeight + 28
                                                        radius: 18
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            id: executionColumn
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            spacing: 10

                                                            RowLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 10

                                                                Label {
                                                                    text: appState.language === "de" ? "AusfÃ¼hrungsvorschau" : "Execution preview"
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 18
                                                                    font.bold: true
                                                                    Layout.fillWidth: true
                                                                }

                                                                Rectangle {
                                                                    radius: 12
                                                                    color: appState.executionReady ? "#123926" : "#40241F"
                                                                    border.color: appState.executionReady ? "#47B36A" : "#D07A63"
                                                                    implicitWidth: executionStatusChip.implicitWidth + 22
                                                                    implicitHeight: executionStatusChip.implicitHeight + 12

                                                                    Label {
                                                                        id: executionStatusChip
                                                                        anchors.centerIn: parent
                                                                        text: appState.executionStatusLabel
                                                                        color: "#F7FAFF"
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                    }
                                                                }

                                                                Rectangle {
                                                                    radius: 12
                                                                    color: "transparent"
                                                                    border.color: "#355988"
                                                                    implicitWidth: executionCountChip.implicitWidth + 22
                                                                    implicitHeight: executionCountChip.implicitHeight + 12

                                                                    Label {
                                                                        id: executionCountChip
                                                                        anchors.centerIn: parent
                                                                        text: appState.executionRowsCountLabel
                                                                        color: "#B8D3FF"
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                text: appState.language === "de"
                                                                      ? "Diese Vorschau zeigt, welche Schritte aus dem aktuellen exakten Duplikat-Dry-Run ausfÃ¼hrbar, zurÃ¼ckgestellt oder blockiert wÃ¤ren."
                                                                      : "This preview shows which steps from the current exact-duplicate dry run would be executable, deferred, or blocked."
                                                                color: "#CFE1FF"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }

                                                            GridLayout {
                                                                Layout.fillWidth: true
                                                                columns: 4
                                                                columnSpacing: 10
                                                                rowSpacing: 10

                                                                Repeater {
                                                                    model: [
                                                                        [appState.language === "de" ? "AusfÃ¼hrbar" : "Executable", appState.executionExecutableCount.toString()],
                                                                        [appState.language === "de" ? "ZurÃ¼ckgestellt" : "Deferred", appState.executionDeferredCount.toString()],
                                                                        [appState.language === "de" ? "Blockiert" : "Blocked", appState.executionBlockedCount.toString()],
                                                                        [appState.language === "de" ? "LÃ¶schzeilen" : "Delete rows", appState.executionDeleteCount.toString()]
                                                                    ]

                                                                    delegate: Rectangle {
                                                                        required property var modelData
                                                                        Layout.fillWidth: true
                                                                        Layout.preferredHeight: 78
                                                                        radius: 14
                                                                        color: "#091321"
                                                                        border.color: "#22324A"

                                                                        ColumnLayout {
                                                                            anchors.fill: parent
                                                                            anchors.margins: 12
                                                                            spacing: 4

                                                                            Label {
                                                                                text: modelData[0]
                                                                                color: "#AFC1D9"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: modelData[1]
                                                                                color: "#F7FAFF"
                                                                                font.pixelSize: 20
                                                                                font.bold: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                text: appState.language === "de"
                                                                      ? "Modus: " + appState.executionModeLabel
                                                                      : "Mode: " + appState.executionModeLabel
                                                                color: "#AFC1D9"
                                                                font.pixelSize: 12
                                                                Layout.fillWidth: true
                                                            }

                                                            ColumnLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 8
                                                                visible: appState.executionRows.length > 0

                                                                Repeater {
                                                                    model: appState.executionRows

                                                                    delegate: Rectangle {
                                                                        required property var modelData
                                                                        Layout.fillWidth: true
                                                                        implicitHeight: executionRowColumn.implicitHeight + 24
                                                                        radius: 14
                                                                        color: "#091321"
                                                                        border.color: modelData.status === "blocked" ? "#D07A63" : "#22324A"

                                                                        ColumnLayout {
                                                                            id: executionRowColumn
                                                                            anchors.fill: parent
                                                                            anchors.margins: 12
                                                                            spacing: 5

                                                                            RowLayout {
                                                                                Layout.fillWidth: true
                                                                                spacing: 8

                                                                                Label {
                                                                                    text: modelData.source_name
                                                                                    color: "#F7FAFF"
                                                                                    font.pixelSize: 13
                                                                                    font.bold: true
                                                                                    Layout.fillWidth: true
                                                                                    elide: Text.ElideRight
                                                                                }

                                                                                Rectangle {
                                                                                    radius: 10
                                                                                    color: modelData.status === "blocked"
                                                                                        ? "#40241F"
                                                                                        : (modelData.status === "deferred" ? "#4A3818" : "#123926")
                                                                                    border.color: modelData.status === "blocked"
                                                                                        ? "#D07A63"
                                                                                        : (modelData.status === "deferred" ? "#D6A14A" : "#47B36A")
                                                                                    implicitWidth: executionRowStatus.implicitWidth + 16
                                                                                    implicitHeight: executionRowStatus.implicitHeight + 8

                                                                                    Label {
                                                                                        id: executionRowStatus
                                                                                        anchors.centerIn: parent
                                                                                        text: modelData.status_label
                                                                                        color: "#F7FAFF"
                                                                                        font.pixelSize: 11
                                                                                        font.bold: true
                                                                                    }
                                                                                }

                                                                                Rectangle {
                                                                                    radius: 10
                                                                                    color: "transparent"
                                                                                    border.color: "#30465F"
                                                                                    implicitWidth: executionRowType.implicitWidth + 16
                                                                                    implicitHeight: executionRowType.implicitHeight + 8

                                                                                    Label {
                                                                                        id: executionRowType
                                                                                        anchors.centerIn: parent
                                                                                        text: modelData.row_type_label
                                                                                        color: "#B8D3FF"
                                                                                        font.pixelSize: 11
                                                                                        font.bold: true
                                                                                    }
                                                                                }
                                                                            }

                                                                            Label {
                                                                                text: modelData.reason_label + "  â€¢  " + modelData.size + "  â€¢  " + modelData.operation_mode_label
                                                                                color: "#AFC1D9"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: modelData.source_path
                                                                                color: "#8FB0E1"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WrapAnywhere
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                visible: modelData.survivor_path.length > 0
                                                                                text: "Survivor: " + modelData.survivor_name
                                                                                color: "#CFE1FF"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                visible: modelData.target_path.length > 0
                                                                                text: "Target: " + modelData.target_path
                                                                                color: "#6F8FB9"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WrapAnywhere
                                                                                Layout.fillWidth: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                visible: appState.executionRows.length === 0
                                                                text: appState.language === "de"
                                                                      ? "Noch keine AusfÃ¼hrungszeilen sichtbar."
                                                                      : "No execution rows visible yet."
                                                                color: "#AFC1D9"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }
                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        implicitHeight: plannedColumn.implicitHeight + 28
                                                        radius: 18
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            id: plannedColumn
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            spacing: 8

                                                            Label {
                                                                text: root.trKey("summary_planned_removals_title")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 18
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            ColumnLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 8
                                                                visible: appState.summaryPlannedRemovalsPreview.length > 0

                                                                Repeater {
                                                                    model: appState.summaryPlannedRemovalsPreview

                                                                    delegate: Rectangle {
                                                                        required property var modelData
                                                                        Layout.fillWidth: true
                                                                        implicitHeight: plannedItemColumn.implicitHeight + 24
                                                                        radius: 14
                                                                        color: "#091321"
                                                                        border.color: "#22324A"

                                                                        ColumnLayout {
                                                                            id: plannedItemColumn
                                                                            anchors.fill: parent
                                                                            anchors.margins: 12
                                                                            spacing: 4

                                                                            Label {
                                                                                text: root.trKey("summary_remove_candidate_label") + ": " + modelData.remove_name + "  •  " + modelData.size
                                                                                color: "#F7FAFF"
                                                                                font.pixelSize: 13
                                                                                font.bold: true
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: root.trKey("summary_keep_survivor_label") + ": " + modelData.keep_name
                                                                                color: "#AFC1D9"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: modelData.remove_path
                                                                                color: "#8FB0E1"
                                                                                font.pixelSize: 11
                                                                                wrapMode: Text.WrapAnywhere
                                                                                Layout.fillWidth: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                visible: appState.summaryPlannedRemovalsPreview.length === 0
                                                                text: root.trKey("summary_planned_removals_empty")
                                                                color: "#AFC1D9"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }

                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        implicitHeight: unresolvedColumn.implicitHeight + 28
                                                        radius: 18
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            id: unresolvedColumn
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            spacing: 8

                                                            Label {
                                                                text: root.trKey("summary_unresolved_list_title")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 18
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            ColumnLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 8
                                                                visible: appState.summaryUnresolvedGroupsPreview.length > 0

                                                                Repeater {
                                                                    model: appState.summaryUnresolvedGroupsPreview

                                                                    delegate: Rectangle {
                                                                        required property var modelData
                                                                        Layout.fillWidth: true
                                                                        implicitHeight: unresolvedItemColumn.implicitHeight + 24
                                                                        radius: 14
                                                                        color: "#091321"
                                                                        border.color: "#22324A"

                                                                        ColumnLayout {
                                                                            id: unresolvedItemColumn
                                                                            anchors.fill: parent
                                                                            anchors.margins: 12
                                                                            spacing: 4

                                                                            Label {
                                                                                text: root.trKey("summary_candidates_label") + ": " + modelData.candidate_count + "  •  " + modelData.size
                                                                                color: "#F7FAFF"
                                                                                font.pixelSize: 13
                                                                                font.bold: true
                                                                                Layout.fillWidth: true
                                                                            }

                                                                            Label {
                                                                                text: modelData.preview_names
                                                                                color: "#AFC1D9"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                visible: appState.summaryUnresolvedGroupsPreview.length === 0
                                                                text: root.trKey("summary_unresolved_empty")
                                                                color: "#AFC1D9"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }

                                                    RowLayout {
                                                        Layout.fillWidth: true
                                                        Item { Layout.fillWidth: true }

                                                        PrimaryButton {
                                                            text: root.trKey("stage_summary_action")
                                                            enabled: appState.summaryReadyForDryRun
                                                            onClicked: appState.workflowNext()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }


                                    // sorting
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12

                                            Label {
                                                text: appState.workflowStageTitle
                                                color: "#F7FAFF"
                                                font.pixelSize: 26
                                                font.bold: true
                                            }

                                            Label {
                                                text: appState.workflowStageSubtitle
                                                color: "#AFC1D9"
                                                font.pixelSize: 15
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                radius: 18
                                                color: "#091321"
                                                border.color: "#22324A"

                                                Flickable {
                                                    anchors.fill: parent
                                                    anchors.margins: 18
                                                    contentWidth: width
                                                    contentHeight: sortingColumn.implicitHeight
                                                    clip: true

                                                    ColumnLayout {
                                                        id: sortingColumn
                                                        width: parent.width
                                                        spacing: 16

                                                        Rectangle {
                                                            Layout.fillWidth: true
                                                            implicitHeight: sortingTemplateColumn.implicitHeight + 34
                                                            radius: 18
                                                            color: "#0F1A2C"
                                                            border.color: "#2D4A72"

                                                            ColumnLayout {
                                                                id: sortingTemplateColumn
                                                                anchors.fill: parent
                                                                anchors.margins: 16
                                                                spacing: 8

                                                                Label {
                                                                    text: root.trKey("sorting_template_title")
                                                                    color: "#AFC1D9"
                                                                    font.pixelSize: 14
                                                                    font.bold: true
                                                                    Layout.fillWidth: true
                                                                }

                                                                Label {
                                                                    text: appState.sortingTemplatePathLabel.length > 0 ? appState.sortingTemplatePathLabel : "2025 / 07 / 14"
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 34
                                                                    font.bold: true
                                                                    wrapMode: Text.WordWrap
                                                                    Layout.fillWidth: true
                                                                }

                                                                Label {
                                                                    text: appState.sortingTemplateHintLabel
                                                                    color: "#8FB0E1"
                                                                    font.pixelSize: 13
                                                                    wrapMode: Text.WordWrap
                                                                    Layout.fillWidth: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: root.trKey("sorting_config_title")
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 18
                                                            font.bold: true
                                                        }

                                                        Label {
                                                            text: root.trKey("sorting_config_body")
                                                            color: "#CFE1FF"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                        RowLayout {
                                                            Layout.fillWidth: true
                                                            spacing: 10

                                                            Rectangle {
                                                                Layout.fillWidth: true
                                                                Layout.preferredHeight: 132
                                                                radius: 16
                                                                color: "#0F1A2C"
                                                                border.color: "#22324A"

                                                                ColumnLayout {
                                                                    anchors.fill: parent
                                                                    anchors.margins: 14
                                                                    spacing: 8
                                                                    Label { text: root.trKey("sorting_level_year"); color: "#F7FAFF"; font.pixelSize: 16; font.bold: true }
                                                                    Label { text: appState.sortingYearStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                                    Item { Layout.fillHeight: true }
                                                                    Button {
                                                                        text: root.trKey("sorting_cycle_action")
                                                                        onClicked: appState.cycleSortingYearStyle()
                                                                        hoverEnabled: true
                                                                        background: SubtleOutlineButtonBackground {}
                                                                        contentItem: Text {
                                                                            text: parent.text
                                                                            color: "#F7FAFF"
                                                                            horizontalAlignment: Text.AlignHCenter
                                                                            verticalAlignment: Text.AlignVCenter
                                                                            font.pixelSize: 13
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Rectangle {
                                                                Layout.fillWidth: true
                                                                Layout.preferredHeight: 132
                                                                radius: 16
                                                                color: "#0F1A2C"
                                                                border.color: "#22324A"

                                                                ColumnLayout {
                                                                    anchors.fill: parent
                                                                    anchors.margins: 14
                                                                    spacing: 8
                                                                    Label { text: root.trKey("sorting_level_month"); color: "#F7FAFF"; font.pixelSize: 16; font.bold: true }
                                                                    Label { text: appState.sortingMonthStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                                    Item { Layout.fillHeight: true }
                                                                    Button {
                                                                        text: root.trKey("sorting_cycle_action")
                                                                        onClicked: appState.cycleSortingMonthStyle()
                                                                        hoverEnabled: true
                                                                        background: SubtleOutlineButtonBackground {}
                                                                        contentItem: Text {
                                                                            text: parent.text
                                                                            color: "#F7FAFF"
                                                                            horizontalAlignment: Text.AlignHCenter
                                                                            verticalAlignment: Text.AlignVCenter
                                                                            font.pixelSize: 13
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Rectangle {
                                                                Layout.fillWidth: true
                                                                Layout.preferredHeight: 132
                                                                radius: 16
                                                                color: "#0F1A2C"
                                                                border.color: "#22324A"

                                                                ColumnLayout {
                                                                    anchors.fill: parent
                                                                    anchors.margins: 14
                                                                    spacing: 8
                                                                    Label { text: root.trKey("sorting_level_day"); color: "#F7FAFF"; font.pixelSize: 16; font.bold: true }
                                                                    Label { text: appState.sortingDayStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                                    Item { Layout.fillHeight: true }
                                                                    Button {
                                                                        text: root.trKey("sorting_cycle_action")
                                                                        onClicked: appState.cycleSortingDayStyle()
                                                                        hoverEnabled: true
                                                                        background: SubtleOutlineButtonBackground {}
                                                                        contentItem: Text {
                                                                            text: parent.text
                                                                            color: "#F7FAFF"
                                                                            horizontalAlignment: Text.AlignHCenter
                                                                            verticalAlignment: Text.AlignVCenter
                                                                            font.pixelSize: 13
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }

                                                        RowLayout {
                                                            Layout.fillWidth: true
                                                            spacing: 10

                                                            Button {
                                                                text: root.trKey("sorting_reset_action")
                                                                onClicked: appState.resetSortingDefaults()
                                                                hoverEnabled: true
                                                                background: SubtleOutlineButtonBackground {}
                                                                contentItem: Text {
                                                                    text: parent.text
                                                                    color: "#F7FAFF"
                                                                    horizontalAlignment: Text.AlignHCenter
                                                                    verticalAlignment: Text.AlignVCenter
                                                                    font.pixelSize: 13
                                                                    font.bold: true
                                                                }
                                                            }

                                                            Item { Layout.fillWidth: true }

                                                            PrimaryButton {
                                                                text: root.trKey("stage_sorting_action")
                                                                enabled: appState.canAdvanceWorkflow
                                                                onClicked: appState.workflowNext()
                                                            }
                                                        }

                                                        RowLayout {
                                                            Layout.fillWidth: true

                                                            Label {
                                                                text: root.trKey("sorting_preview_title")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 20
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Rectangle {
                                                                radius: 12
                                                                color: "transparent"
                                                                border.color: "#355988"
                                                                implicitWidth: sortingCountLabel.implicitWidth + 28
                                                                implicitHeight: sortingCountLabel.implicitHeight + 14

                                                                Label {
                                                                    id: sortingCountLabel
                                                                    anchors.centerIn: parent
                                                                    text: appState.sortingPreviewCountLabel
                                                                    color: "#B8D3FF"
                                                                    font.pixelSize: 12
                                                                    font.bold: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: root.trKey("sorting_preview_body")
                                                            color: "#CFE1FF"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                        ColumnLayout {
                                                            Layout.fillWidth: true
                                                            spacing: 10
                                                            visible: appState.sortingPreviewRows.length > 0

                                                            Repeater {
                                                                model: appState.sortingPreviewRows

                                                                delegate: Rectangle {
                                                                    required property var modelData
                                                                    Layout.fillWidth: true
                                                                    implicitHeight: 96
                                                                    radius: 14
                                                                    color: "#0F1A2C"
                                                                    border.color: "#22324A"

                                                                    ColumnLayout {
                                                                        anchors.fill: parent
                                                                        anchors.margins: 12
                                                                        spacing: 6

                                                                        Label {
                                                                            text: modelData.source_name
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 14
                                                                            font.bold: true
                                                                            elide: Text.ElideRight
                                                                            Layout.fillWidth: true
                                                                        }

                                                                        RowLayout {
                                                                            Layout.fillWidth: true
                                                                            spacing: 10

                                                                            Label {
                                                                                text: modelData.captured_at
                                                                                color: "#CFE1FF"
                                                                                font.pixelSize: 12
                                                                                Layout.preferredWidth: 150
                                                                            }

                                                                            Label {
                                                                                text: modelData.relative_directory
                                                                                color: "#8FB0E1"
                                                                                font.pixelSize: 12
                                                                                wrapMode: Text.WordWrap
                                                                                Layout.fillWidth: true
                                                                            }
                                                                        }

                                                                        Label {
                                                                            text: modelData.source_path
                                                                            color: "#6F8FB9"
                                                                            font.pixelSize: 11
                                                                            elide: Text.ElideMiddle
                                                                            Layout.fillWidth: true
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            visible: appState.sortingPreviewRows.length === 0
                                                            text: root.trKey("sorting_preview_empty")
                                                            color: "#AFC1D9"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

// rename
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12

                                            Label {
                                                text: appState.workflowStageTitle
                                                color: "#F7FAFF"
                                                font.pixelSize: 26
                                                font.bold: true
                                            }

                                            Label {
                                                text: appState.workflowStageSubtitle
                                                color: "#AFC1D9"
                                                font.pixelSize: 15
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                radius: 18
                                                color: "#091321"
                                                border.color: "#22324A"

                                                Flickable {
                                                    anchors.fill: parent
                                                    anchors.margins: 18
                                                    contentWidth: width
                                                    contentHeight: renameColumn.implicitHeight
                                                    clip: true

                                                    ColumnLayout {
                                                        id: renameColumn
                                                        width: parent.width
                                                        spacing: 16

                                                        Rectangle {
                                                            Layout.fillWidth: true
                                                            implicitHeight: renameTemplateColumn.implicitHeight + 34
                                                            radius: 18
                                                            color: "#0F1A2C"
                                                            border.color: "#27456E"

                                                            ColumnLayout {
                                                                id: renameTemplateColumn
                                                                anchors.fill: parent
                                                                anchors.margins: 16
                                                                spacing: 8

                                                                Label {
                                                                    text: root.trKey("rename_template_title")
                                                                    color: "#AFC1D9"
                                                                    font.pixelSize: 13
                                                                    font.bold: true
                                                                    Layout.fillWidth: true
                                                                }

                                                                Label {
                                                                    text: appState.renameLiveTemplateName
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 28
                                                                    font.bold: true
                                                                    wrapMode: Text.WrapAnywhere
                                                                    maximumLineCount: 2
                                                                    elide: Text.ElideRight
                                                                    Layout.fillWidth: true
                                                                }

                                                                Label {
                                                                    text: appState.renameLiveTemplateHint
                                                                    color: "#8FB0E1"
                                                                    font.pixelSize: 12
                                                                    wrapMode: Text.WordWrap
                                                                    Layout.fillWidth: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: root.trKey("rename_config_title")
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 20
                                                            font.bold: true
                                                        }

                                                        Label {
                                                            text: root.trKey("rename_config_body")
                                                            color: "#CFE1FF"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                        Flow {
                                                            Layout.fillWidth: true
                                                            spacing: 8

                                                            Repeater {
                                                                model: [
                                                                    { key: "readable_datetime_original", label: root.trKey("rename_template_readable_datetime_original") },
                                                                    { key: "year_month_day_time_original", label: root.trKey("rename_template_year_month_day_time_original") },
                                                                    { key: "date_original", label: root.trKey("rename_template_date_original") }
                                                                ]

                                                                delegate: Button {
                                                                    required property var modelData
                                                                    text: modelData.label
                                                                    hoverEnabled: true
                                                                    onClicked: appState.setRenameTemplate(modelData.key)

                                                                    background: SubtleOutlineButtonBackground {}

                                                                    contentItem: Text {
                                                                        text: parent.text
                                                                        color: "#F7FAFF"
                                                                        horizontalAlignment: Text.AlignHCenter
                                                                        verticalAlignment: Text.AlignVCenter
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                        wrapMode: Text.WordWrap
                                                                    }
                                                                }
                                                            }

                                                            Button {
                                                                text: root.trKey("rename_template_reset_action")
                                                                hoverEnabled: true
                                                                onClicked: appState.resetRenameTemplate()

                                                                background: SubtleOutlineButtonBackground {}

                                                                contentItem: Text {
                                                                    text: parent.text
                                                                    color: "#F7FAFF"
                                                                    horizontalAlignment: Text.AlignHCenter
                                                                    verticalAlignment: Text.AlignVCenter
                                                                    font.pixelSize: 12
                                                                    font.bold: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: root.trKey("rename_blocks_title")
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 18
                                                            font.bold: true
                                                        }

                                                        Label {
                                                            text: root.trKey("rename_blocks_body")
                                                            color: "#CFE1FF"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                        Flow {
                                                            Layout.fillWidth: true
                                                            spacing: 10

                                                            Repeater {
                                                                model: appState.renameBlocks

                                                                delegate: Rectangle {
                                                                    required property var modelData
                                                                    width: 220
                                                                    height: 118
                                                                    radius: 16
                                                                    color: "#0F1A2C"
                                                                    border.color: "#22324A"

                                                                    MouseArea {
                                                                        anchors.fill: parent
                                                                        onClicked: appState.cycleRenameBlock(modelData.index)
                                                                    }

                                                                    ColumnLayout {
                                                                        anchors.fill: parent
                                                                        anchors.margins: 14
                                                                        spacing: 6

                                                                        RowLayout {
                                                                            Layout.fillWidth: true

                                                                            Rectangle {
                                                                                radius: 10
                                                                                color: "#132B4A"
                                                                                border.color: "#4A82D7"
                                                                                implicitWidth: slotChip.implicitWidth + 16
                                                                                implicitHeight: slotChip.implicitHeight + 8

                                                                                Label {
                                                                                    id: slotChip
                                                                                    anchors.centerIn: parent
                                                                                    text: modelData.slot_label
                                                                                    color: "#F7FAFF"
                                                                                    font.pixelSize: 11
                                                                                    font.bold: true
                                                                                }
                                                                            }

                                                                            Item { Layout.fillWidth: true }

                                                                            Button {
                                                                                visible: modelData.removable
                                                                                text: root.trKey("rename_remove_block_action")
                                                                                hoverEnabled: true
                                                                                onClicked: function() { appState.removeRenameBlock(modelData.index) }

                                                                                background: Rectangle {
                                                                                    radius: 10
                                                                                    color: parent.down ? "#40241F" : (parent.hovered ? "#4A1F1F" : "transparent")
                                                                                    border.width: 1
                                                                                    border.color: parent.hovered ? "#D07A63" : "#30465F"
                                                                                }

                                                                                contentItem: Text {
                                                                                    text: parent.text
                                                                                    color: "#F7FAFF"
                                                                                    horizontalAlignment: Text.AlignHCenter
                                                                                    verticalAlignment: Text.AlignVCenter
                                                                                    font.pixelSize: 11
                                                                                    font.bold: true
                                                                                }
                                                                            }
                                                                        }

                                                                        Item { Layout.fillHeight: true }

                                                                        Label {
                                                                            text: modelData.label
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 18
                                                                            font.bold: true
                                                                            wrapMode: Text.WordWrap
                                                                            Layout.fillWidth: true
                                                                        }

                                                                        Label {
                                                                            text: modelData.hint
                                                                            color: "#8FB0E1"
                                                                            font.pixelSize: 12
                                                                            wrapMode: Text.WordWrap
                                                                            Layout.fillWidth: true
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Button {
                                                                width: 220
                                                                height: 118
                                                                text: root.trKey("rename_add_block_action")
                                                                hoverEnabled: true
                                                                onClicked: appState.addRenameBlock()

                                                                background: Rectangle {
                                                                    radius: 16
                                                                    color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                                                                    border.width: 1
                                                                    border.color: parent.hovered ? "#4A82D7" : "#30465F"
                                                                }

                                                                contentItem: Column {
                                                                    spacing: 6
                                                                    anchors.centerIn: parent

                                                                    Text {
                                                                        text: "+"
                                                                        color: "#F7FAFF"
                                                                        horizontalAlignment: Text.AlignHCenter
                                                                        font.pixelSize: 26
                                                                        font.bold: true
                                                                        width: parent.width
                                                                    }

                                                                    Text {
                                                                        text: parent.parent.text
                                                                        color: "#F7FAFF"
                                                                        horizontalAlignment: Text.AlignHCenter
                                                                        verticalAlignment: Text.AlignVCenter
                                                                        font.pixelSize: 14
                                                                        font.bold: true
                                                                        width: parent.width
                                                                    }
                                                                }
                                                            }
                                                        }

                                                        RowLayout {
                                                            Layout.fillWidth: true

                                                            Label {
                                                                text: root.trKey("rename_preview_title")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 20
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Rectangle {
                                                                radius: 12
                                                                color: "transparent"
                                                                border.color: "#355988"
                                                                implicitWidth: renameCountLabel.implicitWidth + 28
                                                                implicitHeight: renameCountLabel.implicitHeight + 14

                                                                Label {
                                                                    id: renameCountLabel
                                                                    anchors.centerIn: parent
                                                                    text: appState.renamePreviewCountLabel
                                                                    color: "#B8D3FF"
                                                                    font.pixelSize: 12
                                                                    font.bold: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: root.trKey("rename_preview_body")
                                                            color: "#CFE1FF"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                        Column {
                                                            width: parent.width
                                                            spacing: 10
                                                            visible: appState.renamePreviewRows.length > 0

                                                            Repeater {
                                                                model: appState.renamePreviewRows

                                                                delegate: Rectangle {
                                                                    required property var modelData
                                                                    width: renameColumn.width
                                                                    height: 92
                                                                    radius: 14
                                                                    color: "#0F1A2C"
                                                                    border.color: "#22324A"

                                                                    ColumnLayout {
                                                                        anchors.fill: parent
                                                                        anchors.margins: 12
                                                                        spacing: 4

                                                                        Label {
                                                                            text: modelData.source_name
                                                                            color: "#AFC1D9"
                                                                            font.pixelSize: 12
                                                                            font.bold: true
                                                                            Layout.fillWidth: true
                                                                            elide: Text.ElideRight
                                                                        }

                                                                        Label {
                                                                            text: modelData.proposed_name
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 17
                                                                            font.bold: true
                                                                            wrapMode: Text.WrapAnywhere
                                                                            Layout.fillWidth: true
                                                                        }

                                                                        Label {
                                                                            text: modelData.source_path
                                                                            color: "#8FB0E1"
                                                                            font.pixelSize: 11
                                                                            Layout.fillWidth: true
                                                                            elide: Text.ElideMiddle
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            visible: appState.renamePreviewRows.length === 0
                                                            text: root.trKey("rename_preview_empty")
                                                            color: "#AFC1D9"
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                        RowLayout {
                                                            Layout.fillWidth: true
                                                            Item { Layout.fillWidth: true }

                                                            PrimaryButton {
                                                                text: root.trKey("stage_rename_action")
                                                                enabled: appState.canAdvanceWorkflow
                                                                onClicked: appState.workflowNext()
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // done
                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 12
                                            Label { text: root.trKey("stage_done_title"); color: "#F7FAFF"; font.pixelSize: 28; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            Label { text: root.trKey("stage_done_subtitle"); color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            Item { Layout.fillHeight: true }
                                            PrimaryButton { text: root.trKey("button_home"); onClicked: appState.backToHome() }
                                        }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.preferredWidth: 460
                            Layout.preferredHeight: 54
                            radius: 16
                            color: "#0A1626"
                            border.color: "#22324A"
                            opacity: 0.88

                            Label {
                                anchors.fill: parent
                                anchors.margins: 12
                                text: appState.currentTip
                                color: "#AFC1D9"
                                wrapMode: Text.WordWrap
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 11
                                font.bold: false
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true

                            Button {
                                text: root.trKey("button_back")
                                onClicked: appState.workflowBack()
                                hoverEnabled: true

                                background: SubtleOutlineButtonBackground {}

                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 15
                                    font.bold: true
                                }
                            }

                            Item { Layout.fillWidth: true }

                            Button {
                                visible: appState.canAdvanceWorkflow
                                         && appState.workflowStageKey !== "summary"
                                         && appState.workflowStageKey !== "sorting"
                                         && appState.workflowStageKey !== "rename"
                                         && appState.workflowStageKey !== "done"
                                enabled: appState.canAdvanceWorkflow
                                text: root.trKey("button_next")
                                onClicked: appState.workflowNext()
                                Layout.preferredWidth: 176
                                Layout.preferredHeight: 54

                                background: Rectangle {
                                    radius: 16
                                    color: parent.down ? "#234FAE" : "#2F6FED"
                                    border.width: 1
                                    border.color: "#7BA7FF"
                                }

                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 17
                                    font.bold: true
                                }
                            }
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    property int manualPageIndex: appState.currentPage === "duplicates" ? 0 : (appState.currentPage === "organize" ? 1 : 2)

                    StackLayout {
                        anchors.fill: parent
                        currentIndex: manualPageIndex

                        // Manual duplicates
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            Flickable {
                                anchors.fill: parent
                                contentWidth: width
                                contentHeight: manualDuplicatesColumn.implicitHeight
                                clip: true

                                ColumnLayout {
                                    id: manualDuplicatesColumn
                                    width: parent.width
                                    spacing: 16

                                    Label {
                                        text: appState.language === "de" ? "Manuelle Duplikat-Prüfung" : "Manual duplicate review"
                                        color: "#F7FAFF"
                                        font.pixelSize: 34
                                        font.bold: true
                                    }

                                    Label {
                                        text: appState.language === "de"
                                              ? "Hier darf die Seite bewusst größer und direkter sein als im Workflow. Du wählst Quellen, Ziel und arbeitest direkt auf der exakten Duplikat-Prüfung."
                                              : "This page is intentionally larger and more direct than the workflow. Select sources, target, and work directly with exact duplicate review."
                                        color: "#AFC1D9"
                                        font.pixelSize: 15
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 14

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 260
                                            radius: 18
                                            color: "#0F1A2C"
                                            border.color: "#22324A"

                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 16
                                                spacing: 10

                                                Label {
                                                    text: appState.language === "de" ? "Quellordner" : "Source folders"
                                                    color: "#F7FAFF"
                                                    font.pixelSize: 20
                                                    font.bold: true
                                                }

                                                Label {
                                                    text: appState.sourceCount === 0
                                                          ? (appState.language === "de" ? "Noch keine Quellordner gewählt." : "No source folders selected yet.")
                                                          : (appState.sourceCount + (appState.language === "de" ? " Ordner aktiv" : " folder(s) active"))
                                                    color: "#AFC1D9"
                                                    font.pixelSize: 14
                                                    wrapMode: Text.WordWrap
                                                    Layout.fillWidth: true
                                                }

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.fillHeight: true
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"

                                                    Flickable {
                                                        anchors.fill: parent
                                                        anchors.margins: 10
                                                        contentWidth: width
                                                        contentHeight: manualDuplicateSources.implicitHeight
                                                        clip: true

                                                        Column {
                                                            id: manualDuplicateSources
                                                            width: parent.width
                                                            spacing: 8

                                                            Repeater {
                                                                model: appState.sourceFolders
                                                                delegate: Rectangle {
                                                                    width: manualDuplicateSources.width
                                                                    height: 42
                                                                    radius: 12
                                                                    color: "#102038"
                                                                    border.color: "#30465F"

                                                                    RowLayout {
                                                                        anchors.fill: parent
                                                                        anchors.margins: 8
                                                                        spacing: 8

                                                                        Label {
                                                                            Layout.fillWidth: true
                                                                            text: modelData
                                                                            color: "#E6EEF8"
                                                                            elide: Text.ElideMiddle
                                                                            font.pixelSize: 12
                                                                        }

                                                                        Button {
                                                                            text: root.trKey("button_remove")
                                                                            onClicked: appState.removeSourceFolder(index)
                                                                            hoverEnabled: true
                                                                            background: SubtleOutlineButtonBackground {}
                                                                            contentItem: Text {
                                                                                text: parent.text
                                                                                color: "#F7FAFF"
                                                                                horizontalAlignment: Text.AlignHCenter
                                                                                verticalAlignment: Text.AlignVCenter
                                                                                font.pixelSize: 11
                                                                                font.bold: true
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                visible: appState.sourceCount === 0
                                                                width: manualDuplicateSources.width
                                                                text: appState.language === "de" ? "Wähle hier einen oder mehrere Quellordner aus." : "Choose one or more source folders here."
                                                                color: "#8FB0E1"
                                                                wrapMode: Text.WordWrap
                                                                font.pixelSize: 13
                                                            }
                                                        }
                                                    }
                                                }

                                                RowLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 10

                                                    PrimaryButton {
                                                        text: root.trKey("stage_sources_action")
                                                        onClicked: sourceFolderDialog.open()
                                                    }

                                                    Button {
                                                        text: root.trKey("button_clear")
                                                        enabled: appState.sourceCount > 0
                                                        onClicked: appState.clearSourceFolders()
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text {
                                                            text: parent.text
                                                            color: "#F7FAFF"
                                                            horizontalAlignment: Text.AlignHCenter
                                                            verticalAlignment: Text.AlignVCenter
                                                            font.pixelSize: 13
                                                            font.bold: true
                                                        }
                                                    }
                                                }
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 260
                                            radius: 18
                                            color: "#0F1A2C"
                                            border.color: "#22324A"

                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 16
                                                spacing: 10

                                                Label {
                                                    text: appState.language === "de" ? "Zielordner" : "Target folder"
                                                    color: "#F7FAFF"
                                                    font.pixelSize: 20
                                                    font.bold: true
                                                }

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.fillHeight: true
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"

                                                    Label {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        text: appState.targetPath.length > 0
                                                              ? appState.targetPath
                                                              : (appState.language === "de" ? "Noch kein Zielordner ausgewählt." : "No target folder selected yet.")
                                                        color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"
                                                        wrapMode: Text.WrapAnywhere
                                                        verticalAlignment: Text.AlignVCenter
                                                        font.pixelSize: 14
                                                    }
                                                }

                                                Label {
                                                    text: (appState.sourceCount > 0 && appState.targetPath === appState.sourceFolders[0])
                                                          ? (appState.language === "de" ? "Quelle und Ziel sind aktuell identisch." : "Source and target are currently identical.")
                                                          : (appState.language === "de" ? "Du kannst das Ziel separat setzen oder bewusst mit der ersten Quelle gleichsetzen." : "You can set a separate target or intentionally match it to the first source.")
                                                    color: "#AFC1D9"
                                                    wrapMode: Text.WordWrap
                                                    font.pixelSize: 13
                                                    Layout.fillWidth: true
                                                }

                                                Flow {
                                                    Layout.fillWidth: true
                                                    spacing: 10

                                                    PrimaryButton {
                                                        text: root.trKey("stage_target_action")
                                                        onClicked: targetFolderDialog.open()
                                                    }

                                                    Button {
                                                        text: appState.language === "de" ? "Quelle = Ziel" : "Source = target"
                                                        enabled: appState.sourceCount > 0
                                                        onClicked: appState.setTargetFolder(appState.sourceFolders[0])
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text {
                                                            text: parent.text
                                                            color: "#F7FAFF"
                                                            horizontalAlignment: Text.AlignHCenter
                                                            verticalAlignment: Text.AlignVCenter
                                                            font.pixelSize: 13
                                                            font.bold: true
                                                        }
                                                    }

                                                    Button {
                                                        text: root.trKey("button_clear")
                                                        enabled: appState.targetPath.length > 0
                                                        onClicked: appState.clearTargetFolder()
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text {
                                                            text: parent.text
                                                            color: "#F7FAFF"
                                                            horizontalAlignment: Text.AlignHCenter
                                                            verticalAlignment: Text.AlignVCenter
                                                            font.pixelSize: 13
                                                            font.bold: true
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        implicitHeight: duplicatesToolColumn.implicitHeight + 34
                                        radius: 20
                                        color: "#091321"
                                        border.color: "#22324A"

                                        ColumnLayout {
                                            id: duplicatesToolColumn
                                            anchors.fill: parent
                                            anchors.margins: 18
                                            spacing: 12

                                            RowLayout {
                                                Layout.fillWidth: true

                                                ColumnLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 4

                                                    Label {
                                                        text: appState.language === "de" ? "Exakte Duplikate" : "Exact duplicates"
                                                        color: "#F7FAFF"
                                                        font.pixelSize: 24
                                                        font.bold: true
                                                    }

                                                    Label {
                                                        text: appState.language === "de"
                                                              ? "Direkter Zugriff auf dieselbe Prüflogik, aber mit mehr Platz und weniger Workflow-Rahmen."
                                                              : "Direct access to the same review logic, but with more space and less workflow framing."
                                                        color: "#AFC1D9"
                                                        font.pixelSize: 14
                                                        wrapMode: Text.WordWrap
                                                        Layout.fillWidth: true
                                                    }
                                                }

                                                Button {
                                                    text: appState.language === "de" ? "Geführten Workflow öffnen" : "Open guided workflow"
                                                    onClicked: appState.setPage("workflow")
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text {
                                                        text: parent.text
                                                        color: "#F7FAFF"
                                                        horizontalAlignment: Text.AlignHCenter
                                                        verticalAlignment: Text.AlignVCenter
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                    }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 10

                                                PrimaryButton {
                                                    text: root.trKey("stage_duplicates_action")
                                                    enabled: appState.sourceCount > 0
                                                    onClicked: appState.startDuplicatePreview()
                                                }

                                                Rectangle {
                                                    radius: 12
                                                    color: "transparent"
                                                    border.color: "#30465F"
                                                    implicitWidth: duplicateManualHint.implicitWidth + 24
                                                    implicitHeight: duplicateManualHint.implicitHeight + 14

                                                    Label {
                                                        id: duplicateManualHint
                                                        anchors.centerIn: parent
                                                        text: appState.sourceCount > 0
                                                              ? (appState.language === "de" ? "Bereit für direkte Prüfung" : "Ready for direct review")
                                                              : (appState.language === "de" ? "Bitte zuerst Quellen setzen" : "Select sources first")
                                                        color: "#B8D3FF"
                                                        font.pixelSize: 12
                                                        font.bold: true
                                                    }
                                                }

                                                Item { Layout.fillWidth: true }
                                            }

                                            ProgressBar {
                                                Layout.fillWidth: true
                                                from: 0
                                                to: 100
                                                value: appState.duplicateProgress
                                                background: Rectangle { radius: 8; color: "#101B2D" }
                                                contentItem: Item { Rectangle { width: parent.width * (appState.duplicateProgress / 100.0); height: parent.height; radius: 8; color: "#2F6FED" } }
                                            }

                                            Label {
                                                text: appState.statusText
                                                color: "#CFE1FF"
                                                wrapMode: Text.WordWrap
                                                font.pixelSize: 14
                                                Layout.fillWidth: true
                                            }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.preferredHeight: 46
                                                radius: 12
                                                color: "#0F1A2C"

                                                RowLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 10
                                                    spacing: 8
                                                    Repeater {
                                                        model: [root.trKey("table_name"), root.trKey("table_size"), root.trKey("table_date"), root.trKey("table_matches"), root.trKey("table_score"), root.trKey("table_action")]
                                                        delegate: Label {
                                                            Layout.fillWidth: true
                                                            text: modelData
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 13
                                                            font.bold: true
                                                        }
                                                    }
                                                }
                                            }

                                            Rectangle {
                                                Layout.fillWidth: true
                                                implicitHeight: manualDuplicateRows.implicitHeight + 20
                                                radius: 16
                                                color: "#0F1A2C"
                                                border.color: "#22324A"

                                                Column {
                                                    id: manualDuplicateRows
                                                    width: parent.width - 20
                                                    anchors.margins: 10
                                                    anchors.left: parent.left
                                                    anchors.top: parent.top
                                                    spacing: 8

                                                    Repeater {
                                                        model: appState.duplicateRows
                                                        delegate: Rectangle {
                                                            width: manualDuplicateRows.width
                                                            height: 60
                                                            radius: 12
                                                            color: "#102038"
                                                            border.color: "#30465F"

                                                            RowLayout {
                                                                anchors.fill: parent
                                                                anchors.margins: 10
                                                                spacing: 8
                                                                Label { Layout.fillWidth: true; text: modelData.name; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                Label { Layout.fillWidth: true; text: modelData.size; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                Label { Layout.fillWidth: true; text: modelData.date; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                Label { Layout.fillWidth: true; text: modelData.matches; color: "#E6EEF8"; font.pixelSize: 13 }
                                                                Label { Layout.fillWidth: true; text: modelData.score; color: modelData.score === "100%" ? "#8CE99A" : "#FFD18C"; font.pixelSize: 13; font.bold: true }
                                                                Button {
                                                                    Layout.fillWidth: true
                                                                    text: root.trKey("table_show")
                                                                    hoverEnabled: true
                                                                    onClicked: {
                                                                        appState.openDuplicateGroup(Number(modelData.index))
                                                                        duplicateDetailPopup.open()
                                                                    }
                                                                    background: SubtleOutlineButtonBackground {}
                                                                    contentItem: Text {
                                                                        text: parent.text
                                                                        color: "#F7FAFF"
                                                                        horizontalAlignment: Text.AlignHCenter
                                                                        verticalAlignment: Text.AlignVCenter
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }

                                                    Label {
                                                        visible: appState.duplicateRows.length === 0
                                                        width: manualDuplicateRows.width
                                                        text: appState.sourceCount === 0
                                                              ? (appState.language === "de" ? "Wähle zuerst Quellordner aus. Danach kannst du die direkte Duplikat-Prüfung starten." : "Select source folders first. Then you can start direct duplicate review.")
                                                              : (appState.language === "de" ? "Noch keine sichtbaren Duplikat-Ergebnisse. Starte die Prüfung oder warte auf den laufenden Scan." : "No visible duplicate results yet. Start the review or wait for the current scan.")
                                                        color: "#AFC1D9"
                                                        wrapMode: Text.WordWrap
                                                        font.pixelSize: 14
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Manual organize
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            Flickable {
                                anchors.fill: parent
                                contentWidth: width
                                contentHeight: manualOrganizeColumn.implicitHeight
                                clip: true

                                ColumnLayout {
                                    id: manualOrganizeColumn
                                    width: parent.width
                                    spacing: 16

                                    Label {
                                        text: appState.language === "de" ? "Manuelles Sortieren" : "Manual organize"
                                        color: "#F7FAFF"
                                        font.pixelSize: 34
                                        font.bold: true
                                    }

                                    Label {
                                        text: appState.language === "de"
                                              ? "Hier darf die Sortierseite ausführlicher sein als im Workflow. Quellen und Ziel setzt du direkt hier, die Strukturvorschau bleibt permanent sichtbar."
                                              : "This organize page is intentionally more detailed than the workflow. Set sources and target directly here while keeping the structure preview always visible."
                                        color: "#AFC1D9"
                                        font.pixelSize: 15
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 14

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 240
                                            radius: 18
                                            color: "#0F1A2C"
                                            border.color: "#22324A"

                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 16
                                                spacing: 10

                                                Label { text: appState.language === "de" ? "Quellen" : "Sources"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                                Label {
                                                    text: appState.sourceCount === 0
                                                          ? (appState.language === "de" ? "Noch keine Quellordner gewählt." : "No source folders selected yet.")
                                                          : (appState.sourceCount + (appState.language === "de" ? " Ordner aktiv" : " folder(s) active"))
                                                    color: "#AFC1D9"
                                                    wrapMode: Text.WordWrap
                                                    Layout.fillWidth: true
                                                }
                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.fillHeight: true
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"
                                                    Label {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        text: appState.sourceCount > 0 ? appState.sourceFolders.join("
") : (appState.language === "de" ? "Wähle hier die Quellordner für das manuelle Sortieren." : "Choose source folders here for manual organize.")
                                                        color: appState.sourceCount > 0 ? "#F7FAFF" : "#8FB0E1"
                                                        wrapMode: Text.WrapAnywhere
                                                        verticalAlignment: Text.AlignTop
                                                        font.pixelSize: 13
                                                    }
                                                }
                                                Flow {
                                                    Layout.fillWidth: true
                                                    spacing: 10
                                                    PrimaryButton { text: root.trKey("stage_sources_action"); onClicked: sourceFolderDialog.open() }
                                                    Button {
                                                        text: root.trKey("button_clear")
                                                        enabled: appState.sourceCount > 0
                                                        onClicked: appState.clearSourceFolders()
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                    }
                                                }
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 240
                                            radius: 18
                                            color: "#0F1A2C"
                                            border.color: "#22324A"

                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 16
                                                spacing: 10

                                                Label { text: appState.language === "de" ? "Ziel" : "Target"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.fillHeight: true
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"
                                                    Label {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        text: appState.targetPath.length > 0 ? appState.targetPath : (appState.language === "de" ? "Noch kein Ziel gesetzt." : "No target selected yet.")
                                                        color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"
                                                        wrapMode: Text.WrapAnywhere
                                                        verticalAlignment: Text.AlignVCenter
                                                        font.pixelSize: 14
                                                    }
                                                }
                                                Label {
                                                    text: appState.language === "de" ? "Für manuelles Sortieren kannst du Ziel und Quelle bewusst gleichsetzen." : "For manual organize, you can intentionally make source and target identical."
                                                    color: "#AFC1D9"
                                                    wrapMode: Text.WordWrap
                                                    Layout.fillWidth: true
                                                    font.pixelSize: 13
                                                }
                                                Flow {
                                                    Layout.fillWidth: true
                                                    spacing: 10
                                                    PrimaryButton { text: root.trKey("stage_target_action"); onClicked: targetFolderDialog.open() }
                                                    Button {
                                                        text: appState.language === "de" ? "Quelle = Ziel" : "Source = target"
                                                        enabled: appState.sourceCount > 0
                                                        onClicked: appState.setTargetFolder(appState.sourceFolders[0])
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                    }
                                                    Button {
                                                        text: root.trKey("button_clear")
                                                        enabled: appState.targetPath.length > 0
                                                        onClicked: appState.clearTargetFolder()
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        implicitHeight: manualOrganizeToolColumn.implicitHeight + 34
                                        radius: 20
                                        color: "#091321"
                                        border.color: "#22324A"

                                        ColumnLayout {
                                            id: manualOrganizeToolColumn
                                            anchors.fill: parent
                                            anchors.margins: 18
                                            spacing: 14

                                            Rectangle {
                                                Layout.fillWidth: true
                                                implicitHeight: 132
                                                radius: 18
                                                color: "#0F1A2C"
                                                border.color: "#2D4A72"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 16
                                                    spacing: 8
                                                    Label { text: appState.language === "de" ? "Aktuelle Zielstruktur" : "Current target structure"; color: "#AFC1D9"; font.pixelSize: 14; font.bold: true }
                                                    Label { text: appState.sortingTemplatePathLabel.length > 0 ? appState.sortingTemplatePathLabel : "2025 / 07 / 14"; color: "#F7FAFF"; font.pixelSize: 34; font.bold: true; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                    Label { text: appState.sortingTemplateHintLabel; color: "#8FB0E1"; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                }
                                            }

                                            Label { text: appState.language === "de" ? "Sortierblöcke" : "Sorting blocks"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                            Label { text: appState.language === "de" ? "Aktuell sind Jahr, Monat und Tag die festen Ebenen. Die Seite ist größer, damit Vorschau und Entscheidungen besser lesbar sind." : "Year, month, and day are still the fixed levels for now. This page is larger so preview and decisions are easier to read."; color: "#CFE1FF"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 12

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.preferredHeight: 152
                                                    radius: 16
                                                    color: "#0F1A2C"
                                                    border.color: "#22324A"
                                                    MouseArea { anchors.fill: parent; onClicked: appState.cycleSortingYearStyle() }
                                                    ColumnLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        spacing: 8
                                                        Label { text: root.trKey("sorting_level_year"); color: "#F7FAFF"; font.pixelSize: 17; font.bold: true }
                                                        Label { text: appState.sortingYearStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                        Item { Layout.fillHeight: true }
                                                        Label { text: appState.language === "de" ? "Klicken zum Ändern" : "Press to change"; color: "#6F8FB9"; font.pixelSize: 12 }
                                                    }
                                                }

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.preferredHeight: 152
                                                    radius: 16
                                                    color: "#0F1A2C"
                                                    border.color: "#22324A"
                                                    MouseArea { anchors.fill: parent; onClicked: appState.cycleSortingMonthStyle() }
                                                    ColumnLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        spacing: 8
                                                        Label { text: root.trKey("sorting_level_month"); color: "#F7FAFF"; font.pixelSize: 17; font.bold: true }
                                                        Label { text: appState.sortingMonthStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                        Item { Layout.fillHeight: true }
                                                        Label { text: appState.language === "de" ? "Klicken zum Ändern" : "Press to change"; color: "#6F8FB9"; font.pixelSize: 12 }
                                                    }
                                                }

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.preferredHeight: 152
                                                    radius: 16
                                                    color: "#0F1A2C"
                                                    border.color: "#22324A"
                                                    MouseArea { anchors.fill: parent; onClicked: appState.cycleSortingDayStyle() }
                                                    ColumnLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        spacing: 8
                                                        Label { text: root.trKey("sorting_level_day"); color: "#F7FAFF"; font.pixelSize: 17; font.bold: true }
                                                        Label { text: appState.sortingDayStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                        Item { Layout.fillHeight: true }
                                                        Label { text: appState.language === "de" ? "Klicken zum Ändern" : "Press to change"; color: "#6F8FB9"; font.pixelSize: 12 }
                                                    }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 10
                                                Button {
                                                    text: root.trKey("sorting_reset_action")
                                                    onClicked: appState.resetSortingDefaults()
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                }
                                                Item { Layout.fillWidth: true }
                                                Button {
                                                    text: appState.language === "de" ? "Geführten Workflow öffnen" : "Open guided workflow"
                                                    onClicked: appState.setPage("workflow")
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                Label { text: appState.language === "de" ? "Vorschau" : "Preview"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true; Layout.fillWidth: true }
                                                Rectangle {
                                                    radius: 12
                                                    color: "transparent"
                                                    border.color: "#355988"
                                                    implicitWidth: manualSortingCount.implicitWidth + 28
                                                    implicitHeight: manualSortingCount.implicitHeight + 14
                                                    Label { id: manualSortingCount; anchors.centerIn: parent; text: appState.sortingPreviewCountLabel; color: "#B8D3FF"; font.pixelSize: 12; font.bold: true }
                                                }
                                            }

                                            Label { text: appState.language === "de" ? "Einige echte Quelldateien werden hier auf ihre Zielordner abgebildet." : "A few real source files are mapped to their future target folders here."; color: "#CFE1FF"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 10
                                                visible: appState.sortingPreviewRows.length > 0

                                                Repeater {
                                                    model: appState.sortingPreviewRows
                                                    delegate: Rectangle {
                                                        required property var modelData
                                                        Layout.fillWidth: true
                                                        implicitHeight: 110
                                                        radius: 14
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 12
                                                            spacing: 6
                                                            Label { text: modelData.source_name; color: "#F7FAFF"; font.pixelSize: 15; font.bold: true; elide: Text.ElideRight; Layout.fillWidth: true }
                                                            RowLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 10
                                                                Label { text: modelData.captured_at; color: "#CFE1FF"; font.pixelSize: 12; Layout.preferredWidth: 150 }
                                                                Label { text: modelData.relative_directory; color: "#8FB0E1"; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                            }
                                                            Label { text: modelData.source_path; color: "#6F8FB9"; font.pixelSize: 11; elide: Text.ElideMiddle; Layout.fillWidth: true }
                                                        }
                                                    }
                                                }
                                            }

                                            Label {
                                                visible: appState.sortingPreviewRows.length === 0
                                                text: appState.language === "de" ? "Noch keine Vorschau verfügbar. Wähle Quellordner mit Mediendateien aus." : "No preview available yet. Choose source folders containing media files."
                                                color: "#AFC1D9"
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // Manual rename
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true

                            Flickable {
                                anchors.fill: parent
                                contentWidth: width
                                contentHeight: manualRenameColumn.implicitHeight
                                clip: true

                                ColumnLayout {
                                    id: manualRenameColumn
                                    width: parent.width
                                    spacing: 16

                                    Label {
                                        text: appState.language === "de" ? "Manuelles Umbenennen" : "Manual rename"
                                        color: "#F7FAFF"
                                        font.pixelSize: 34
                                        font.bold: true
                                    }

                                    Label {
                                        text: appState.language === "de"
                                              ? "Hier ist Rename bewusst größer und detaillierter als im Workflow. Quellen und Ziel setzt du direkt hier, danach arbeitest du sofort mit den aktiven Namensblöcken."
                                              : "Rename is intentionally larger and more detailed here than in the workflow. Set sources and target directly here, then work immediately with the active naming blocks."
                                        color: "#AFC1D9"
                                        font.pixelSize: 15
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }

                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 14

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 230
                                            radius: 18
                                            color: "#0F1A2C"
                                            border.color: "#22324A"
                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 16
                                                spacing: 10
                                                Label { text: appState.language === "de" ? "Quellen" : "Sources"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.fillHeight: true
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"
                                                    Label {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        text: appState.sourceCount > 0 ? appState.sourceFolders.join("
") : (appState.language === "de" ? "Wähle Quellordner für das manuelle Umbenennen." : "Choose source folders for manual rename.")
                                                        color: appState.sourceCount > 0 ? "#F7FAFF" : "#8FB0E1"
                                                        wrapMode: Text.WrapAnywhere
                                                        verticalAlignment: Text.AlignTop
                                                        font.pixelSize: 13
                                                    }
                                                }
                                                Flow {
                                                    Layout.fillWidth: true
                                                    spacing: 10
                                                    PrimaryButton { text: root.trKey("stage_sources_action"); onClicked: sourceFolderDialog.open() }
                                                    Button {
                                                        text: root.trKey("button_clear")
                                                        enabled: appState.sourceCount > 0
                                                        onClicked: appState.clearSourceFolders()
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                    }
                                                }
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 230
                                            radius: 18
                                            color: "#0F1A2C"
                                            border.color: "#22324A"
                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 16
                                                spacing: 10
                                                Label { text: appState.language === "de" ? "Ziel" : "Target"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    Layout.fillHeight: true
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"
                                                    Label {
                                                        anchors.fill: parent
                                                        anchors.margins: 14
                                                        text: appState.targetPath.length > 0 ? appState.targetPath : (appState.language === "de" ? "Noch kein Ziel gesetzt." : "No target selected yet.")
                                                        color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"
                                                        wrapMode: Text.WrapAnywhere
                                                        verticalAlignment: Text.AlignVCenter
                                                        font.pixelSize: 14
                                                    }
                                                }
                                                Label {
                                                    text: appState.language === "de" ? "Auch beim Umbenennen kannst du Quelle und Ziel absichtlich identisch setzen." : "You can intentionally make source and target identical for rename too."
                                                    color: "#AFC1D9"
                                                    wrapMode: Text.WordWrap
                                                    Layout.fillWidth: true
                                                    font.pixelSize: 13
                                                }
                                                Flow {
                                                    Layout.fillWidth: true
                                                    spacing: 10
                                                    PrimaryButton { text: root.trKey("stage_target_action"); onClicked: targetFolderDialog.open() }
                                                    Button {
                                                        text: appState.language === "de" ? "Quelle = Ziel" : "Source = target"
                                                        enabled: appState.sourceCount > 0
                                                        onClicked: appState.setTargetFolder(appState.sourceFolders[0])
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                    }
                                                    Button {
                                                        text: root.trKey("button_clear")
                                                        enabled: appState.targetPath.length > 0
                                                        onClicked: appState.clearTargetFolder()
                                                        hoverEnabled: true
                                                        background: SubtleOutlineButtonBackground {}
                                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    Rectangle {
                                        Layout.fillWidth: true
                                        implicitHeight: manualRenameToolColumn.implicitHeight + 34
                                        radius: 20
                                        color: "#091321"
                                        border.color: "#22324A"

                                        ColumnLayout {
                                            id: manualRenameToolColumn
                                            anchors.fill: parent
                                            anchors.margins: 18
                                            spacing: 14

                                            Rectangle {
                                                Layout.fillWidth: true
                                                implicitHeight: 138
                                                radius: 18
                                                color: "#0F1A2C"
                                                border.color: "#27456E"

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 16
                                                    spacing: 8
                                                    Label { text: root.trKey("rename_template_title"); color: "#AFC1D9"; font.pixelSize: 13; font.bold: true; Layout.fillWidth: true }
                                                    Label { text: appState.renameLiveTemplateName; color: "#F7FAFF"; font.pixelSize: 28; font.bold: true; wrapMode: Text.WrapAnywhere; maximumLineCount: 2; elide: Text.ElideRight; Layout.fillWidth: true }
                                                    Label { text: appState.renameLiveTemplateHint; color: "#8FB0E1"; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                }
                                            }

                                            Label { text: appState.language === "de" ? "Presets" : "Presets"; color: "#F7FAFF"; font.pixelSize: 19; font.bold: true }
                                            Label { text: appState.language === "de" ? "Die Presets setzen nur die Blockliste. Die eigentliche Dateinamenvorschau entsteht immer aus den aktiven Blöcken darunter." : "Presets only set the block list. The real filename preview is always built from the active blocks below."; color: "#CFE1FF"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            Flow {
                                                Layout.fillWidth: true
                                                spacing: 10

                                                Button {
                                                    text: appState.text("rename_template_readable_datetime_original")
                                                    onClicked: appState.setRenameTemplate("readable_datetime_original")
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                                                }

                                                Button {
                                                    text: appState.text("rename_template_year_month_day_time_original")
                                                    onClicked: appState.setRenameTemplate("year_month_day_time_original")
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                                                }

                                                Button {
                                                    text: appState.text("rename_template_date_original")
                                                    onClicked: appState.setRenameTemplate("date_original")
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                                                }

                                                Button {
                                                    text: root.trKey("rename_template_reset_action")
                                                    onClicked: appState.resetRenameTemplate()
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                Label { text: root.trKey("rename_blocks_title"); color: "#F7FAFF"; font.pixelSize: 20; font.bold: true; Layout.fillWidth: true }
                                                Rectangle {
                                                    radius: 12
                                                    color: "transparent"
                                                    border.color: "#30465F"
                                                    implicitWidth: manualRenameCount.implicitWidth + 24
                                                    implicitHeight: manualRenameCount.implicitHeight + 14
                                                    Label { id: manualRenameCount; anchors.centerIn: parent; text: appState.renamePreviewCountLabel; color: "#B8D3FF"; font.pixelSize: 12; font.bold: true }
                                                }
                                            }

                                            Label { text: appState.text("rename_blocks_body"); color: "#CFE1FF"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            Flow {
                                                Layout.fillWidth: true
                                                spacing: 10

                                                Repeater {
                                                    model: appState.renameBlocks
                                                    delegate: Rectangle {
                                                        required property var modelData
                                                        width: 230
                                                        height: 136
                                                        radius: 16
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        MouseArea {
                                                            anchors.fill: parent
                                                            onClicked: appState.cycleRenameBlock(modelData.index)
                                                        }

                                                        ColumnLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            spacing: 8

                                                            RowLayout {
                                                                Layout.fillWidth: true
                                                                Label {
                                                                    text: modelData.slot_label
                                                                    color: "#8FB0E1"
                                                                    font.pixelSize: 12
                                                                    font.bold: true
                                                                    Layout.fillWidth: true
                                                                }

                                                                Button {
                                                                    visible: modelData.removable
                                                                    text: root.trKey("rename_remove_block_action")
                                                                    onClicked: appState.removeRenameBlock(modelData.index)
                                                                    hoverEnabled: true
                                                                    background: SubtleOutlineButtonBackground {}
                                                                    contentItem: Text {
                                                                        text: parent.text
                                                                        color: "#F7FAFF"
                                                                        horizontalAlignment: Text.AlignHCenter
                                                                        verticalAlignment: Text.AlignVCenter
                                                                        font.pixelSize: 10
                                                                        font.bold: true
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                text: modelData.label
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 18
                                                                font.bold: true
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }

                                                            Item { Layout.fillHeight: true }

                                                            Label {
                                                                text: modelData.hint
                                                                color: "#6F8FB9"
                                                                font.pixelSize: 12
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 10
                                                Button {
                                                    text: root.trKey("rename_add_block_action")
                                                    onClicked: appState.addRenameBlock()
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 13; font.bold: true }
                                                }
                                                Item { Layout.fillWidth: true }
                                                Button {
                                                    text: appState.language === "de" ? "Geführten Workflow öffnen" : "Open guided workflow"
                                                    onClicked: appState.setPage("workflow")
                                                    hoverEnabled: true
                                                    background: SubtleOutlineButtonBackground {}
                                                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                                                }
                                            }

                                            Label { text: root.trKey("rename_preview_title"); color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                            Label { text: root.trKey("rename_preview_body"); color: "#CFE1FF"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 10
                                                visible: appState.renamePreviewRows.length > 0

                                                Repeater {
                                                    model: appState.renamePreviewRows
                                                    delegate: Rectangle {
                                                        required property var modelData
                                                        Layout.fillWidth: true
                                                        implicitHeight: 104
                                                        radius: 14
                                                        color: "#0F1A2C"
                                                        border.color: "#22324A"

                                                        ColumnLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 12
                                                            spacing: 4
                                                            Label { text: modelData.source_name; color: "#AFC1D9"; font.pixelSize: 12; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
                                                            Label { text: modelData.proposed_name; color: "#F7FAFF"; font.pixelSize: 18; font.bold: true; wrapMode: Text.WrapAnywhere; Layout.fillWidth: true }
                                                            Label { text: modelData.source_path; color: "#8FB0E1"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideMiddle }
                                                        }
                                                    }
                                                }
                                            }

                                            Label {
                                                visible: appState.renamePreviewRows.length === 0
                                                text: appState.language === "de" ? "Noch keine Rename-Vorschau verfügbar. Wähle Quellordner mit Mediendateien aus." : "No rename preview available yet. Choose source folders containing media files."
                                                color: "#AFC1D9"
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component {
        id: manualEmptyStateDuplicates

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 12

            Label {
                text: appState.language === "de" ? "Wähle zuerst Quellordner aus." : "Select source folders first."
                color: "#F7FAFF"
                font.pixelSize: 24
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: appState.language === "de"
                      ? "Ohne Quellordner kann die manuelle Duplikat-Prüfung nichts anzeigen."
                      : "Without source folders, manual duplicate review cannot show anything yet."
                color: "#CFE1FF"
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                Layout.preferredWidth: 560
                Layout.alignment: Qt.AlignHCenter
            }

            RowLayout {
                spacing: 10
                Layout.alignment: Qt.AlignHCenter

                PrimaryButton {
                    text: root.trKey("stage_sources_action")
                    onClicked: sourceFolderDialog.open()
                }

                Button {
                    text: root.trKey("nav_workflow")
                    onClicked: appState.setPage("workflow")
                    hoverEnabled: true
                    background: SubtleOutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }
            }
        }
    }

    Component {
        id: manualEmptyStateOrganize

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 12

            Label {
                text: appState.language === "de" ? "Wähle zuerst Quellordner aus." : "Select source folders first."
                color: "#F7FAFF"
                font.pixelSize: 24
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: appState.language === "de"
                      ? "Ohne Quellordner gibt es keine echte Sortier-Vorschau."
                      : "Without source folders, there is no real sorting preview yet."
                color: "#CFE1FF"
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                Layout.preferredWidth: 560
                Layout.alignment: Qt.AlignHCenter
            }

            RowLayout {
                spacing: 10
                Layout.alignment: Qt.AlignHCenter

                PrimaryButton {
                    text: root.trKey("stage_sources_action")
                    onClicked: sourceFolderDialog.open()
                }

                Button {
                    text: root.trKey("nav_workflow")
                    onClicked: appState.setPage("workflow")
                    hoverEnabled: true
                    background: SubtleOutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }
            }
        }
    }

    Component {
        id: manualEmptyStateRename

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 12

            Label {
                text: appState.language === "de" ? "Wähle zuerst Quellordner aus." : "Select source folders first."
                color: "#F7FAFF"
                font.pixelSize: 24
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: appState.language === "de"
                      ? "Ohne Quellordner gibt es keine echte Rename-Vorschau."
                      : "Without source folders, there is no real rename preview yet."
                color: "#CFE1FF"
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                Layout.preferredWidth: 560
                Layout.alignment: Qt.AlignHCenter
            }

            RowLayout {
                spacing: 10
                Layout.alignment: Qt.AlignHCenter

                PrimaryButton {
                    text: root.trKey("stage_sources_action")
                    onClicked: sourceFolderDialog.open()
                }

                Button {
                    text: root.trKey("nav_workflow")
                    onClicked: appState.setPage("workflow")
                    hoverEnabled: true
                    background: SubtleOutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 14
                        font.bold: true
                    }
                }
            }
        }
    }

    Component {
        id: manualDuplicatesContent

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                PrimaryButton {
                    text: root.trKey("stage_duplicates_action")
                    enabled: appState.sourceCount > 0
                    onClicked: appState.startDuplicatePreview()
                }

                Button {
                    text: root.trKey("stage_sources_action")
                    onClicked: sourceFolderDialog.open()
                    hoverEnabled: true
                    background: SubtleOutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 13
                        font.bold: true
                    }
                }

                Item { Layout.fillWidth: true }
            }

            ProgressBar {
                Layout.fillWidth: true
                from: 0
                to: 100
                value: appState.duplicateProgress
                background: Rectangle { radius: 8; color: "#101B2D" }
                contentItem: Item { Rectangle { width: parent.width * (appState.duplicateProgress / 100.0); height: parent.height; radius: 8; color: "#2F6FED" } }
            }

            Label {
                text: appState.statusText
                color: "#CFE1FF"
                wrapMode: Text.WordWrap
                font.pixelSize: 14
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: 18
                color: "#0F1A2C"
                border.color: "#22324A"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 42
                        radius: 12
                        color: "#091321"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            spacing: 8
                            Repeater {
                                model: [root.trKey("table_name"), root.trKey("table_size"), root.trKey("table_date"), root.trKey("table_matches"), root.trKey("table_score"), root.trKey("table_action")]
                                delegate: Label {
                                    Layout.fillWidth: true
                                    text: modelData
                                    color: "#F7FAFF"
                                    font.pixelSize: 13
                                    font.bold: true
                                }
                            }
                        }
                    }

                    Flickable {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        contentWidth: width
                        contentHeight: manualDuplicateRowsColumn.implicitHeight
                        clip: true

                        Column {
                            id: manualDuplicateRowsColumn
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: appState.duplicateRows
                                delegate: Rectangle {
                                    width: manualDuplicateRowsColumn.width
                                    height: 52
                                    radius: 12
                                    color: "#091321"
                                    border.color: "#22324A"

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 8
                                        Label { Layout.fillWidth: true; text: modelData.name; color: "#E6EEF8"; font.pixelSize: 13 }
                                        Label { Layout.fillWidth: true; text: modelData.size; color: "#E6EEF8"; font.pixelSize: 13 }
                                        Label { Layout.fillWidth: true; text: modelData.date; color: "#E6EEF8"; font.pixelSize: 13 }
                                        Label { Layout.fillWidth: true; text: modelData.matches; color: "#E6EEF8"; font.pixelSize: 13 }
                                        Label { Layout.fillWidth: true; text: modelData.score; color: modelData.score === "100%" ? "#8CE99A" : "#FFD18C"; font.pixelSize: 13; font.bold: true }
                                        Button {
                                            Layout.fillWidth: true
                                            text: root.trKey("table_show")
                                            hoverEnabled: true
                                            onClicked: {
                                                appState.openDuplicateGroup(Number(modelData.index))
                                                duplicateDetailPopup.open()
                                            }
                                            background: SubtleOutlineButtonBackground {}
                                            contentItem: Text {
                                                text: parent.text
                                                color: "#F7FAFF"
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                                font.pixelSize: 12
                                                font.bold: true
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component {
        id: manualOrganizeContent

        Flickable {
            anchors.fill: parent
            anchors.margins: 18
            contentWidth: width
            contentHeight: manualSortingColumn.implicitHeight
            clip: true

            ColumnLayout {
                id: manualSortingColumn
                width: parent.width
                spacing: 16

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: manualSortingTemplateColumn.implicitHeight + 34
                    radius: 18
                    color: "#0F1A2C"
                    border.color: "#2D4A72"

                    ColumnLayout {
                        id: manualSortingTemplateColumn
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8

                        Label {
                            text: root.trKey("sorting_template_title")
                            color: "#AFC1D9"
                            font.pixelSize: 14
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        Label {
                            text: appState.sortingTemplatePathLabel.length > 0 ? appState.sortingTemplatePathLabel : "2025 / 07 / 14"
                            color: "#F7FAFF"
                            font.pixelSize: 34
                            font.bold: true
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }

                        Label {
                            text: appState.sortingTemplateHintLabel
                            color: "#8FB0E1"
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 132
                        radius: 16
                        color: "#0F1A2C"
                        border.color: "#22324A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 8
                            Label { text: root.trKey("sorting_level_year"); color: "#F7FAFF"; font.pixelSize: 16; font.bold: true }
                            Label { text: appState.sortingYearStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            Item { Layout.fillHeight: true }
                            Button {
                                text: root.trKey("sorting_cycle_action")
                                onClicked: appState.cycleSortingYearStyle()
                                hoverEnabled: true
                                background: SubtleOutlineButtonBackground {}
                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 13
                                    font.bold: true
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 132
                        radius: 16
                        color: "#0F1A2C"
                        border.color: "#22324A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 8
                            Label { text: root.trKey("sorting_level_month"); color: "#F7FAFF"; font.pixelSize: 16; font.bold: true }
                            Label { text: appState.sortingMonthStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            Item { Layout.fillHeight: true }
                            Button {
                                text: root.trKey("sorting_cycle_action")
                                onClicked: appState.cycleSortingMonthStyle()
                                hoverEnabled: true
                                background: SubtleOutlineButtonBackground {}
                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 13
                                    font.bold: true
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 132
                        radius: 16
                        color: "#0F1A2C"
                        border.color: "#22324A"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 8
                            Label { text: root.trKey("sorting_level_day"); color: "#F7FAFF"; font.pixelSize: 16; font.bold: true }
                            Label { text: appState.sortingDayStyleLabel; color: "#AFC1D9"; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                            Item { Layout.fillHeight: true }
                            Button {
                                text: root.trKey("sorting_cycle_action")
                                onClicked: appState.cycleSortingDayStyle()
                                hoverEnabled: true
                                background: SubtleOutlineButtonBackground {}
                                contentItem: Text {
                                    text: parent.text
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    font.pixelSize: 13
                                    font.bold: true
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Button {
                        text: root.trKey("sorting_reset_action")
                        onClicked: appState.resetSortingDefaults()
                        hoverEnabled: true
                        background: SubtleOutlineButtonBackground {}
                        contentItem: Text {
                            text: parent.text
                            color: "#F7FAFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }

                    Button {
                        text: root.trKey("stage_sources_action")
                        onClicked: sourceFolderDialog.open()
                        hoverEnabled: true
                        background: SubtleOutlineButtonBackground {}
                        contentItem: Text {
                            text: parent.text
                            color: "#F7FAFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }

                    Item { Layout.fillWidth: true }
                }

                RowLayout {
                    Layout.fillWidth: true

                    Label {
                        text: root.trKey("sorting_preview_title")
                        color: "#F7FAFF"
                        font.pixelSize: 20
                        font.bold: true
                        Layout.fillWidth: true
                    }

                    Rectangle {
                        radius: 12
                        color: "transparent"
                        border.color: "#355988"
                        implicitWidth: manualSortingCountLabel.implicitWidth + 28
                        implicitHeight: manualSortingCountLabel.implicitHeight + 14

                        Label {
                            id: manualSortingCountLabel
                            anchors.centerIn: parent
                            text: appState.sortingPreviewCountLabel
                            color: "#B8D3FF"
                            font.pixelSize: 12
                            font.bold: true
                        }
                    }
                }

                Label {
                    text: root.trKey("sorting_preview_body")
                    color: "#CFE1FF"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    visible: appState.sortingPreviewRows.length > 0

                    Repeater {
                        model: appState.sortingPreviewRows

                        delegate: Rectangle {
                            required property var modelData
                            Layout.fillWidth: true
                            implicitHeight: 96
                            radius: 14
                            color: "#0F1A2C"
                            border.color: "#22324A"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 6

                                Label {
                                    text: modelData.source_name
                                    color: "#F7FAFF"
                                    font.pixelSize: 14
                                    font.bold: true
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    Label {
                                        text: modelData.captured_at
                                        color: "#CFE1FF"
                                        font.pixelSize: 12
                                        Layout.preferredWidth: 150
                                    }

                                    Label {
                                        text: modelData.relative_directory
                                        color: "#8FB0E1"
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }

                                Label {
                                    text: modelData.source_path
                                    color: "#6F8FB9"
                                    font.pixelSize: 11
                                    elide: Text.ElideMiddle
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }

                Label {
                    visible: appState.sortingPreviewRows.length === 0
                    text: root.trKey("sorting_preview_empty")
                    color: "#AFC1D9"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
    }

    Component {
        id: manualRenameContent

        Flickable {
            anchors.fill: parent
            anchors.margins: 18
            contentWidth: width
            contentHeight: manualRenameColumn.implicitHeight
            clip: true

            ColumnLayout {
                id: manualRenameColumn
                width: parent.width
                spacing: 16

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: manualRenameTemplateColumn.implicitHeight + 34
                    radius: 18
                    color: "#0F1A2C"
                    border.color: "#27456E"

                    ColumnLayout {
                        id: manualRenameTemplateColumn
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8

                        Label {
                            text: root.trKey("rename_template_title")
                            color: "#AFC1D9"
                            font.pixelSize: 13
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        Label {
                            text: appState.renameLiveTemplateName
                            color: "#F7FAFF"
                            font.pixelSize: 28
                            font.bold: true
                            wrapMode: Text.WrapAnywhere
                            maximumLineCount: 2
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        Label {
                            text: appState.renameLiveTemplateHint
                            color: "#8FB0E1"
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }
                }

                Label {
                    text: root.trKey("rename_blocks_body")
                    color: "#CFE1FF"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Repeater {
                        model: appState.renameTemplateOptions

                        delegate: Button {
                            required property var modelData
                            visible: modelData.key !== "custom"
                            text: modelData.label
                            hoverEnabled: true
                            onClicked: appState.setRenameTemplate(modelData.key)
                            background: Rectangle {
                                radius: 14
                                color: index === appState.renameSelectedTemplateIndex ? "#132B4A" : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                                border.width: 1
                                border.color: index === appState.renameSelectedTemplateIndex ? "#4A82D7" : (parent.hovered ? "#4A82D7" : "#30465F")
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#F7FAFF"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: root.trKey("rename_template_reset_action")
                        onClicked: appState.resetRenameTemplate()
                        hoverEnabled: true
                        background: SubtleOutlineButtonBackground {}
                        contentItem: Text {
                            text: parent.text
                            color: "#F7FAFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: root.trKey("rename_blocks_title")
                        color: "#F7FAFF"
                        font.pixelSize: 18
                        font.bold: true
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: root.trKey("rename_add_block_action")
                        onClicked: appState.addRenameBlock()
                        hoverEnabled: true
                        background: SubtleOutlineButtonBackground {}
                        contentItem: Text {
                            text: parent.text
                            color: "#F7FAFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }

                Flow {
                    Layout.fillWidth: true
                    spacing: 10

                    Repeater {
                        model: appState.renameBlocks

                        delegate: Rectangle {
                            required property var modelData
                            width: 220
                            height: 112
                            radius: 16
                            color: "#0F1A2C"
                            border.color: "#22324A"

                            MouseArea {
                                anchors.fill: parent
                                onClicked: appState.cycleRenameBlock(modelData.index)
                            }

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 6

                                RowLayout {
                                    Layout.fillWidth: true

                                    Label {
                                        text: modelData.slot_label
                                        color: "#8FB0E1"
                                        font.pixelSize: 11
                                        font.bold: true
                                        Layout.fillWidth: true
                                    }

                                    Button {
                                        visible: modelData.removable
                                        text: "✕"
                                        onClicked: appState.removeRenameBlock(modelData.index)
                                        hoverEnabled: true
                                        background: Rectangle {
                                            radius: 10
                                            color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
                                            border.width: 1
                                            border.color: parent.hovered ? "#4A82D7" : "#30465F"
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }
                                }

                                Item { Layout.fillHeight: true }

                                Label {
                                    text: modelData.label
                                    color: "#F7FAFF"
                                    font.pixelSize: 18
                                    font.bold: true
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }

                                Label {
                                    text: modelData.hint
                                    color: "#AFC1D9"
                                    font.pixelSize: 12
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true

                    Label {
                        text: root.trKey("rename_preview_title")
                        color: "#F7FAFF"
                        font.pixelSize: 20
                        font.bold: true
                        Layout.fillWidth: true
                    }

                    Rectangle {
                        radius: 12
                        color: "transparent"
                        border.color: "#30465F"
                        implicitWidth: manualRenameCountLabel.implicitWidth + 28
                        implicitHeight: manualRenameCountLabel.implicitHeight + 14

                        Label {
                            id: manualRenameCountLabel
                            anchors.centerIn: parent
                            text: appState.renamePreviewCountLabel
                            color: "#B8D3FF"
                            font.pixelSize: 12
                            font.bold: true
                        }
                    }
                }

                Label {
                    text: root.trKey("rename_preview_body")
                    color: "#CFE1FF"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                Column {
                    width: parent.width
                    spacing: 10
                    visible: appState.renamePreviewRows.length > 0

                    Repeater {
                        model: appState.renamePreviewRows

                        delegate: Rectangle {
                            required property var modelData
                            width: manualRenameColumn.width
                            height: 92
                            radius: 14
                            color: "#0F1A2C"
                            border.color: "#22324A"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 4

                                Label {
                                    text: modelData.source_name
                                    color: "#AFC1D9"
                                    font.pixelSize: 12
                                    font.bold: true
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Label {
                                    text: modelData.proposed_name
                                    color: "#F7FAFF"
                                    font.pixelSize: 17
                                    font.bold: true
                                    wrapMode: Text.WrapAnywhere
                                    Layout.fillWidth: true
                                }

                                Label {
                                    text: modelData.source_path
                                    color: "#8FB0E1"
                                    font.pixelSize: 11
                                    Layout.fillWidth: true
                                    elide: Text.ElideMiddle
                                }
                            }
                        }
                    }
                }

                Label {
                    visible: appState.renamePreviewRows.length === 0
                    text: root.trKey("rename_preview_empty")
                    color: "#AFC1D9"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }
    }


    Component {
        id: sourceListComponent

        ListView {
            clip: true
            model: appState.sourceFolders
            spacing: 10

            delegate: Rectangle {
                width: ListView.view.width
                height: 58
                radius: 14
                color: "#0F1A2C"
                border.color: "#22324A"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12

                    Label {
                        Layout.fillWidth: true
                        text: modelData
                        color: "#E6EEF8"
                        font.pixelSize: 14
                        elide: Text.ElideMiddle
                    }

                    Button {
                        text: root.trKey("button_remove")
                        onClicked: appState.removeSourceFolder(index)
                        hoverEnabled: true

                        background: SubtleOutlineButtonBackground {}

                        contentItem: Text {
                            text: parent.text
                            color: "#F7FAFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 12
                            font.bold: true
                        }
                    }
                }
            }
        }
    }
}



