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
                                                            spacing: 8

                                                            Label {
                                                                text: root.trKey("summary_dry_run_title")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 18
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Label {
                                                                text: root.trKey("summary_dry_run_body")
                                                                color: "#CFE1FF"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }

                                                            RowLayout {
                                                                Layout.fillWidth: true
                                                                spacing: 10

                                                                Rectangle {
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
                                                                            text: root.trKey("summary_resolved_groups")
                                                                            color: "#AFC1D9"
                                                                            font.pixelSize: 12
                                                                        }

                                                                        Label {
                                                                            text: appState.summaryResolvedDuplicateGroups.toString()
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 20
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }

                                                                Rectangle {
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
                                                                            text: root.trKey("summary_unresolved_groups")
                                                                            color: "#AFC1D9"
                                                                            font.pixelSize: 12
                                                                        }

                                                                        Label {
                                                                            text: appState.summaryUnresolvedDuplicateGroups.toString()
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 20
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }

                                                                Rectangle {
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
                                                                            text: root.trKey("summary_remove_candidate_label")
                                                                            color: "#AFC1D9"
                                                                            font.pixelSize: 12
                                                                        }

                                                                        Label {
                                                                            text: appState.summaryPlannedRemovalCount.toString()
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 20
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }

                                                                Rectangle {
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
                                                                            text: root.trKey("summary_estimated_reclaimable_label")
                                                                            color: "#AFC1D9"
                                                                            font.pixelSize: 12
                                                                        }

                                                                        Label {
                                                                            text: appState.summaryEstimatedReclaimableSizeLabel
                                                                            color: "#F7FAFF"
                                                                            font.pixelSize: 20
                                                                            font.bold: true
                                                                        }
                                                                    }
                                                                }
                                                            }

                                                            Label {
                                                                text: root.trKey("summary_plan_intro")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 15
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Label { text: "• " + root.trKey("summary_plan_line_1"); color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                            Label { text: "• " + root.trKey("summary_plan_line_2"); color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                            Label { text: "• " + root.trKey("summary_plan_line_3"); color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
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

                                                        Rectangle {
                                                            Layout.fillWidth: true
                                                            Layout.preferredHeight: 132
                                                            radius: 18
                                                            color: "#0F1A2C"
                                                            border.color: "#27456E"

                                                            ColumnLayout {
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
                                                                    font.pixelSize: 26
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

                                                        RowLayout {
                                                            Layout.fillWidth: true
                                                            spacing: 10

                                                            Label {
                                                                text: root.trKey("rename_template_selector")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 14
                                                                font.bold: true
                                                            }

                                                            ComboBox {
                                                                Layout.preferredWidth: 340
                                                                model: appState.renameTemplateOptions
                                                                textRole: "label"
                                                                currentIndex: appState.renameSelectedTemplateIndex
                                                                onActivated: function(activatedIndex) { appState.setRenameTemplate(appState.renameTemplateKeyAt(activatedIndex)) }

                                                                background: Rectangle {
                                                                    radius: 12
                                                                    color: "#0F1A2C"
                                                                    border.color: "#30465F"
                                                                }

                                                                contentItem: Text {
                                                                    leftPadding: 12
                                                                    rightPadding: 28
                                                                    text: parent.displayText
                                                                    color: "#F7FAFF"
                                                                    verticalAlignment: Text.AlignVCenter
                                                                    font.pixelSize: 13
                                                                    elide: Text.ElideRight
                                                                }
                                                            }

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

                                                            Item { Layout.fillWidth: true }

                                                            Rectangle {
                                                                radius: 12
                                                                color: "transparent"
                                                                border.color: "#30465F"
                                                                Layout.preferredWidth: 170
                                                                Layout.preferredHeight: 32

                                                                Label {
                                                                    anchors.centerIn: parent
                                                                    text: appState.renamePreviewCountLabel
                                                                    color: "#B8D3FF"
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

                                                        Flow {
                                                            Layout.fillWidth: true
                                                            spacing: 8

                                                            Repeater {
                                                                model: appState.renameBlockLabels
                                                                delegate: Rectangle {
                                                                    radius: 12
                                                                    color: "#132B4A"
                                                                    border.color: "#4A82D7"
                                                                    height: 34
                                                                    width: Math.max(120, label.implicitWidth + 24)

                                                                    Label {
                                                                        id: label
                                                                        anchors.centerIn: parent
                                                                        text: modelData
                                                                        color: "#F7FAFF"
                                                                        font.pixelSize: 12
                                                                        font.bold: true
                                                                    }
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: root.trKey("rename_preview_title")
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 20
                                                            font.bold: true
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

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 14

                        Label {
                            text: root.trKey("manual_placeholder_title")
                            color: "#F7FAFF"
                            font.pixelSize: 30
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            Layout.fillWidth: true
                        }

                        Label {
                            text: root.trKey("manual_placeholder_body")
                            color: "#C8D9EE"
                            wrapMode: Text.WordWrap
                            horizontalAlignment: Text.AlignHCenter
                            Layout.preferredWidth: 660
                        }

                        Label {
                            text: root.trKey("manual_hint")
                            color: "#CFE1FF"
                            wrapMode: Text.WordWrap
                            horizontalAlignment: Text.AlignHCenter
                            Layout.preferredWidth: 620
                        }

                        PrimaryButton {
                            text: root.trKey("nav_workflow")
                            onClicked: appState.setPage("workflow")
                        }
                    }
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

