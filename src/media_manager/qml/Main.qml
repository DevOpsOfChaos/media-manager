
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: root
    visible: true
    width: 1360
    height: 860
    minimumWidth: 1180
    minimumHeight: 760
    title: appState.text("app_title")
    color: "#07111F"

    function trKey(key) { return appState.text(key) }

    function pageIndex() {
        if (appState.currentPage === "home")
            return 0
        if (appState.currentPage === "workflow")
            return 1
        return 2
    }

    component OutlineButtonBackground: Rectangle {
        radius: 14
        color: parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent")
        border.width: 1
        border.color: parent.hovered ? "#4A82D7" : "#30465F"
    }

    component CardPanel: Rectangle {
        radius: 18
        color: "#0F1A2C"
        border.color: "#22324A"
        border.width: 1
    }

    component SectionTitle: Label {
        color: "#F7FAFF"
        font.pixelSize: 24
        font.bold: true
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
        width: Math.min(root.width * 0.78, 920)
        height: Math.min(root.height * 0.76, 700)
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        anchors.centerIn: Overlay.overlay
        onClosed: appState.closeDuplicateGroup()

        background: Rectangle {
            radius: 24
            color: "#0C1728"
            border.color: "#27456E"
            border.width: 1
        }

        contentItem: ColumnLayout {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 10

            RowLayout {
                Layout.fillWidth: true

                Label {
                    text: appState.duplicateDetailTitle
                    color: "#F7FAFF"
                    font.pixelSize: 24
                    font.bold: true
                    Layout.fillWidth: true
                    elide: Text.Elidd’ight
                }

                Button {
                    text: "âœ•"
                    hoverEnabled: true
                    onClicked: duplicateDetailPopup.close()
                    background: OutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 16
                        font.bold: true
                    }
                }
            }

            Label {
                text: appState.duplicateDetailSummary
                color: "#AFC1D9"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Flickable {
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentWidth: width
                contentHeight: detailColumn.implicitHeight
                clip: true

                Column {
                    id: detailColumn
                    width: parent.width
                    spacing: 8

                    Repeater {
                        model: appState.duplicateDetailFiles

                        delegate: Rectangle {
                            width: detailColumn.width
                            height: 96
                            radius: 14
                            color: modelData.selected ? "#173056" : "#0F1A2C"
                            border.color: modelData.selected ? "#4A82D7" : "#22324A"
                            border.width: 1

                            MouseArea {
                                anchors.fill: parent
                                onClicked: appState.selectDuplicateCandidate(index)
                            }

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 4

                                Label {
                                    text: modelData.name
                                    color: "#F7FAFF"
                                    font.pixelSize: 15
                                    font.bold: true
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }

                                Label {
                                    text: modelData.path
                                    color: "#8FB0E1"
                                    font.pixelSize: 11
                                    wrapMode: Text.WrapAnywhere
                                    Layout.fillWidth: true
                                }

                                Label {
                                    text: modelData.size + " â€¢ " + modelData.date
                                    color: "#AFC1D9"
                                    font.pixelSize: 12
                                }
                            }
                        }
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    text: trKey("duplicate_detail_keep_selected")
                    hoverEnabled: true
                    onClicked: appState.keepSelectedDuplicateCandidate()
                    background: OutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                }

                Button {
                    text: trKey("duplicate_detail_keep_newest")
                    hoverEnabled: true
                    onClicked: appState.chooseDuplicateKeepNewest()
                    background: OutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                }

                Button {
                    text: trKey("duplicate_detail_keep_oldest")
                    hoverEnabled: true
                    onClicked: appState.chooseDuplicateKeepOldest()
                    background: OutlineButtonBackground {}
                    contentItem: Text {
                        text: parent.text
                        color: "#F7FAFF"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                }

                Item { Layout.fillWidth: true }
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
            radius: 24
            color: "#081322"
            border.color: "#1E2C40"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Label {
                    text: trKey("app_title")
                    color: "#F7FAFF"
                    font.pixelSize: 16
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                    Layout.fillWidth: true
                }

                Label {
                    text: trKey("nav_subtitle")
                    color: "#8FA7C7"
                    font.pixelSize: 11
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                Item { Layout.preferredHeight: 8 }

                Repeater {
                    model: [
                        { "key": "home", "label": trKey("nav_home") },
                        { "key": "workflow", "label": trKey("nav_workflow") },
                        { "key": "duplicates", "label": trKey("nav_duplicates") },
                        { "key": "organize", "label": trKey("nav_organize") },
                        { "key": "rename", "label": trKey("nav_rename") }
                    ]

                    delegate: Button {
                        required property var modelData
                        Layout.fillWidth: true
                        hoverEnabled: true
                        onClicked: appState.setPage(modelData.key)

                        background: Rectangle {
                            radius: 14
                            color: appState.currentPage === modelData.key ? "#132B4A" : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                            border.width: 1
                            border.color: appState.currentPage === modelData.key ? "#4A82D7" : "#30465F"
                        }

                        contentItem: Text {
                            text: modelData.label
                            color: "#F7FAFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }

                Item { Layout.fillHeight: true }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                Item { Layout.fillWidth: true }

                Button {
                    Layout.preferredWidth: 60
                    Layout.preferredHeight: 36
                    hoverEnabled: true
                    onClicked: appState.toggleLanguage()
                    background: OutlineButtonBackground {}

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

                Flickable {
                    contentWidth: width
                    contentHeight: homeColumn.implicitHeight
                    clip: true

                    ColumnLayout {
                        id: homeColumn
                        width: parent.width
                        spacing: 14

                        Item { Layout.preferredHeight: 24 }

                        Label {
                            Layout.alignment: Qt.AlignHCenter
                            text: trKey("home_title")
                            color: "#F7FAFF"
                            font.pixelSize: 58
                            font.bold: true
                        }

                        Label {
                            Layout.alignment: Qt.AlignHCenter
                            text: trKey("home_subtitle")
                            color: "#B7CAE2"
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            Layout.preferredWidth: 720
                        }

                        Repeater {
                            model: ["full_cleanup", "ready_for_sorting", "ready_for_rename", "exact_duplicates_only"]

                            delegate: Button {
                                required property string modelData
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: 560
                                Layout.preferredHeight: 58
                                hoverEnabled: true
                                onClicked: appState.selectProblemAndStart(modelData)
                                background: OutlineButtonBackground {}

                                contentItem: Text {
                                    text: appState.problemLabel(modelData)
                                    color: "#F7FAFF"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    wrapMode: Text.WordWrap
                                    font.pixelSize: 15
                                    font.bold: true
                                }
                            }
                        }
                    }
                }

                ColumnLayout {
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: trKey("workflow_title"); color: "#F7FAFF"; font.pixelSize: 28; font.bold: true }
                        Item { Layout.fillWidth: true }
                        Label { text: (appState.workflowStageIndex + 1) + " / " + appState.workflowTotalSteps; color: "#B8D3FF"; font.pixelSize: 13; font.bold: true }
                    }

                    ProgressBar {
                        Layout.fillWidth: true
                        from: 0
                        to: appState.workflowTotalSteps
                        value: appState.workflowStageIndex + 1
                    }

                    StackLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        currentIndex: appState.workflowStageIndex

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                SectionTitle { text: appState.workflowStageTitle }
                                Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    model: appState.sourceFolders
                                    delegate: Label {
                                        text: modelData
                                        color: "#E6EEF8"
                                        font.pixelSize: 13
                                        width: ListView.view.width
                                        elide: Text.ElideMiddle
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true

                                    Button {
                                        text: trKey("stage_sources_action")
                                        hoverEnabled: true
                                        onClicked: sourceFolderDialog.open()
                                        background: OutlineButtonBackground {}
                                        contentItem: Text {
                                            text: parent.text
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }

                                    Button {
                                        text: trKey("button_clear")
                                        hoverEnabled: true
                                        enabled: appState.sourceCount > 0
                                        onClicked: appState.clearSourceFolders()
                                        background: OutlineButtonBackground {}
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

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                SectionTitle { text: appState.workflowStageTitle }

                                Label {
                                    text: appState.targetPath.length > 0 ? appState.targetPath : trKey("stage_target_empty")
                                    color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"
                                    wrapMode: Text.WrapAnywhere
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                }

                                RowLayout {
                                    Layout.fillWidth: true

                                    Button {
                                        text: trKey("stage_target_action")
                                        hoverEnabled: true
                                        onClicked: targetFolderDialog.open()
                                        background: OutlineButtonBackground {}
                                        contentItem: Text {
                                            text: parent.text
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }

                                    Button {
                                        text: trKey"("button_clear")
                                        hoverEnabled: true
                                        enabled: appState.targetPath.length > 0
                                        onClicked: appState.clearTargetFolder()
                                        background: OutlineButtonBackground {}
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

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                SectionTitle { text: appState.workflowStageTitle }

                                Repeater {
                                    model: ["copy", "move", "delete"]

                                    delegate: Button {
                                        required property string modelData
                                        Layout.preferredHeight: 52
                                        hoverEnabled: true
                                        onClicked: appState.setOperationMode(modelData)

                                        background: Rectangle {
                                            radius: 16
                                            color: appState.operationMode === modelData ? "#132B4A" : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                                            border.width: 1
                                            border.color: appState.operationMode === modelData ? "#4A82D7" : "#30465F"
                                        }

                                        contentItem: Text {
                                            text: trKey("mode_" + modelData)
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

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                SectionTitle { text: appState.workflowStageTitle }

                                Button {
                                    text: trKey("stage_duplicates_action")
                                    hoverEnabled: true
                                    enabled: appState.sourceCount > 0
                                    onClicked: appState.startDuplicatePreview()
                                    background: OutlineButtonBackground {}
                                    contentItem: Text {
                                        text: parent.text
                                        color: "#F7FAFF"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                        font.pixelSize: 12
                                        font.bold: true
                                    }
                                }

                                ProgressBar {
                                    Layout.fillWidth: true
                                    from: 0
                                    to: 100
                                    value: appState.duplicateProgress
                                }

                                Label {
                                    text: appState.statusText
                                    color: "#CFE1EF"
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }

                                ListView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    model: appState.duplicateRows
                                    spacing: 8

                                    delegate: Rectangle {
                                        width: ListView.view.width
                                        height: 58
                                        radius: 12
                                        color: "#091321"
                                        border.color: "#22324A"
                                        border.width: 1

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 8

                                            Label { Layout.fillWidth: true; text: modelData.name; color: "#E6EEF8"; font.pixelSize: 13 }
                                            Label { Layout.fillWidth: true; text: modelData.size; color: "#E6EEF8"; font.pixelSize: 13 }
                                            Label { Layout.fillWidth: true; text: modelData.matches; color: "#E6EEF8"; font.pixelSize: 13 }

                                            Button {
                                                text: trKey("table_show")
                                                hoverEnabled: true
                                                onClicked: {
                                                    appState.openDuplicateGroup(Number(modelData.index))
                                                    duplicateDetailPopup.open()
                                                }
                                                background: OutlineButtonBackground {}
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

                        Flickable {
                            contentWidth: width
                            contentHeight: summaryColumn.implicitHeight
                            clip: true

                            ColumnLayout {
                                id: summaryColumn
                                width: parent.width
                                spacing: 12

                                SectionTitle { text: appState.workflowStageTitle }
                                Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                CardPanel {
                                    Layout.fillWidth: true
                                    implicitHeight: 92
                                    border.color: appState.summaryReadyForDryRun ? "#47B36A" : "#D07A63"
                                    color: appState.summaryReadyForDryRun ? "#123926" : "#40241F"

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 14
                                        spacing: 4

                                        Label { text: appState.summaryDecisionStatus; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                        Label {
                                            text: appState.summaryReadyForDryRun ? trKey("summary_ready_body") : trKey("summary_unresolved_body")
                                            color: "#F7FAFF"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Repeater {
                                        model: [
                                            [trKey("summary_groups"), appState.summaryExactGroupCount.toString()],
                                            [trKey("summary_duplicate_files"), appState.summaryExactDuplicateFiles.toString()],
                                            [trKey("summary_extra_duplicates"), appState.summaryExtraDuplicates.toString()],
                                            [trKey("summary_mode"), appState.summaryOperationModeLabel]
                                        ]

                                        delegate: CardPanel {
                                            required property var modelData
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 80

                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 10
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
                                                    font.pixelSize: 18
                                                    font.bold: true
                                                  }
                                            }
                                        }
                                    }
                                }

                                CardPanel {
                                    Layout.fillWidth: true
                                    implicitHeight: dryRunColumn.implicitHeight + 24

                                    ColumnLayout {
                                        id: dryRunColumn
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8

                                        RowLayout {
                                            Layout.fillWidth: true
                                            Label { text: trKey("dryrun_title"); color: "#F7FAFF"; font.pixelSize: 18; font.bold: true; Layout.fillWidth: true }
                                            Label { text: appState.dryRunStatusLabel; color: appState.dryRunReady ? "#8CE99A" : "#FFD18C"; font.pixelSize: 12; font.bold: true }
                                        }

                                        Label {
                                            text: trKey("dryrun_subtitle")
                                            color: "#CFE1EF"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }

                                        Flow {
                                            width: parent.width
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
                                                          color: appState.dryRunFilterKey === modelData.key ? "#132B4A" : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                                                          border.width: 1
                                                        border.color: appState.dryRunFilterKey === modelData.key ? "#4A82D7" : "#30465F"
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
                                        }

                                        Label {
                                            text: appState.dryRunRowsCountLabel
                                            color: "#8FB0E1"
                                            font.pixelSize: 12
                                            font.bold: true
                                            Layout.fillWidth: true
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 6
                                            visible: appState.dryRunRows.length > 0

                                            Repeater {
                                                model: appState.dryRunRows

                                                delegate: Rectangle {
                                                    required property var modelData
                                                    width: dryRunColumn.width
                                                    implicitHeight: 76
                                                    radius: 12
                                                    color: "#091321"
                                                    border.color: modelData.status === "blocked" ? "#D07A63" : "#22324A"
                                                    border.width: 1

                                                    ColumnLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 10
                                                        spacing: 4

                                                        Label {
                                                            text: modelData.status_label + " â€¢ " + modelData.action_label
                                                          color: "#F7FAFF"
                                                          font.pixelSize: 12
                                                          font.bold: true
                                                            Layout.fillWidth: true
                                                          wrapMode: Text.WordWrap
                                                        }

                                                        Label {
                                                            text: modelData.reason_label
                                                            color: "#CFE1EF"
                                                            font.pixelSize: 11
                                                            Layout.fillWidth: true
                                                            wrapMode: Text.WordWrap
                                                          }

                                                        Label {
                                                            text: modelData.source_path
                                                            color: "#8FB0E1"
                                                            font.pixelSize: 10
                                                            Layout.fillWidth: true
                                                            wrapMode: Text.WrapAnywhere
                                                          }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }

                                CardPanel {
                                    Layout.fillWidth: true
                                    implicitHeight: executionColumn.implicitHeight + 24

                                    ColumnLayout {
                                        id: executionColumn
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8

                                        RowLayout {
                                            Layout.fillWidth: true
                                            Label { text: "Execution preview"; color: "#F7FAFF"; font.pixelSize: 18; font.bold: true; Layout.fillWidth: true }
                                            Label { text: appState.executionStatusLabel; color: appState.executionReady ? "#8CE99A" : "#FFD18C"; font.pixelSize: 12; font.bold: true }
                                        }

                                        Label {
                                            text: appState.executionRowsCountLabel
                                            color: "#8FB0E1"
                                            font.pixelSize: 12
                                            font.bold: true
                                            Layout.fillWidth: true
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 6
                                            visible: appState.executionRows.length > 0

                                            Repeater {
                                                model: appState.executionRows

                                                delegate: Rectangle {
                                                    required property var modelData
                                                    width: executionColumn.width
                                                    implicitHeight: 76
                                                   radius: 12
                                                    color: "#091321"
                                                    border.color: modelData.status === "blocked" ? "#D07A63" : "#22324A"
                                                    border.width: 1

                                                    ColumnLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 10
                                                        spacing: 4

                                                        Label {
                                                            text: modelData.status_label + " â€¢ " + modelData.row_type_label
                                                            color: "#F7FAFF"
                                                            font.pixelSize: 12
                                                            font.bold: true
                                                          Layout.fillWidth: true
                                                          wrapMode: Text.WordWrap
                                                        }

                                                        Label {
                                                            text: modelData.reason_label
                                                            color: "#CFE1EF"
                                                            font.pixelSize: 11
                                                            Layout.fillWidth: true
                                                            wrapMode: Text.WordWrap
                                                          }

                                                        Label {
                                                            text: modelData.source_path
                                                            color: "#8FB0E1"
                                                            font.pixelSize: 10
                                                            Layout.fillWidth: true
                                                            wrapMode: Text.WrapAnywhere
                                                          }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    Item { Layout.fillWidth: true }

                                    Button {
                                        text: trKey("stage_summary_action")
                                        hoverEnabled: true
                                        enabled: appState.summaryReadyForDryRun
                                        onClicked: appState.workflowNext()
                                        background: OutlineButtonBackground {}
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

                        Flickable {
                            contentWidth: width
                            contentHeight: sortingStageColumn.implicitHeight
                            clip: true

                            ColumnLayout {
                                id: sortingStageColumn
                                width: parent.width
                                spacing: 12

                                SectionTitle { text: appState.workflowStageTitle }
                                Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                CardPanel {
                                    Layout.fillWidth: true
                                    implicitHeight: sortingHeroColumn.implicitHeight + 24

                                    ColumnLayout {
                                        id: sortingHeroColumn
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8

                                        Label { text: trKey("sorting_template_title"); color: "#AFC1D9"; font.pixelSize: 12; font.bold: true }
                                        Label {
                                            text: appState.sortingTemplatePathLabel.length > 0 ? appState.sortingTemplatePathLabel : "2025 / 07 / 14"
                                            color: "#F7FAFF"
                                            font.pixelSize: 28
                                            font.bold: true
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                        Label {
                                            text: appState.sortingTemplateHintLabel
                                            color: "#8FB0E1"
                                            font.pixelSize: 12
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 8

                                    Repeater {
                                        model: [
                                            { "title": trKey("sorting_level_year"), "value": appState.sortingYearStyleLabel, "action": "year" },
                                            { "title": trKey("sorting_level_month"), "value": appState.sortingMonthStyleLabel, "action": "month" },
                                            { "title": trKey("sorting_level_day"), "value": appState.sortingDayStyleLabel, "action": "day" }
                                        ]

                                        delegate: CardPanel {
                                            required property var modelData
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 118

                                            MouseArea {
                                                anchors.fill: parent
                                                onClicked: {
                                                    if (modelData.action === "year")
                                                        appState.cycleSortingYearStyle()
                                                    else if (modelData.action === "month")
                                                        appState.cycleSortingMonthStyle()
                                                      else
                                                      appState.cycleSortingDayStyle()
                                                }
                                            }

                                            ColumnLayout {
                                                anchors.fill: parent
                                                anchors.margins: 10
                                                spacing: 6

                                                Label { text: modelData.title; color: "#F7FAFF"; font.pixelSize: 15; font.bold: true }
                                                Label { text: modelData.value; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                                Item { Layout.fillHeight: true }
                                                Label { text: trKey("sorting_cycle_action"); color: "#6F8FB9"; font.pixelSize: 11 }
                                            }
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true

                                    Button {
                                        text: trKey("sorting_reset_action")
                                        hoverEnabled: true
                                        onClicked: appState.resetSortingDefaults()
                                        background: OutlineButtonBackground {}
                                        contentItem: Text {
                                            text: parent.text
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }

                                    Item { Layout.fillWidth: true }
                                }

                                CardPanel {
                                    Layout.fillWidth: true
                                    implicitHeight: sortingPreviewColumn.implicitHeight + 24

                                    ColumnLayout {
                                        id: sortingPreviewColumn
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8

                                        RowLayout {
                                            Layout.fillWidth: true
                                            Label { text: trKey("sorting_preview_title"); color: "#F7FAFF"; font.pixelSize: 18; font.bold: true; Layout.fillWidth: true }
                                            Label { text: appState.sortingPreviewCountLabel; color: "#8FB0E1"; font.pixelSize: 12; font.bold: true }
                                        }

                                        Label {
                                            text: trKey("sorting_preview_body")
                                            color: "#CFE1EF"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }

                                        Repeater {
                                            model: appState.sortingPreviewRows

                                            delegate: Rectangle {
                                                width: sortingPreviewColumn.width
                                                implicitHeight: 68
                                                radius: 12
                                                color: "#091321"
                                                border.color: "#22324A"
                                                border.width: 1

                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 10
                                                    spacing: 4

                                                    Label {
                                                        text: modelData.source_name
                                                        color: "#F7FAFF"
                                                      font.pixelSize: 12
                                                      font.bold: true
                                                        Layout.fillWidth: true
                                                      elide: Text.ElideRight
                                                    }

                                                    Label {
                                                        text: modelData.relative_directory
                                                          color: "#8FB0E1"
                                                            font.pixelSize: 11
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }

                                                    Label {
                                                        text: modelData.source_path
                                                        color: "#6F8FB9"
                                                            font.pixelSize: 10
                                                            Layout.fillWidth: true
                                                            elide: Text.ElideMiddle
                                                        }
                                                    }
                                            }
                                        }

                                        Label {
                                            visible: appState.sortingPreviewRows.length === 0(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰Í½ÉÑ¥¹}ÁÉ•Ù¥•Ý}•µÁÑäˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅäˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€±¥­…‰±”ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ]¥‘Ñ èÝ¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ!•¥¡ÐèÉ•¹…µ•MÑ…•½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€±¥ÀèÑÉÕ”((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èÉ•¹…µ•MÑ…•½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÁ…É•¹Ð¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€ÄÈ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€M•Ñ¥½¹Q¥Ñ±”ìÑ•áÐè…ÁÁMÑ…Ñ”¹Ý½É­™±½ÝMÑ…•Q¥Ñ±”ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè…ÁÁMÑ…Ñ”¹Ý½É­™±½ÝMÑ…•MÕ‰Ñ¥Ñ±”ì½±½Èè€ˆÅäˆìÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…Àì1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…É‘A…¹•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥µÁ±¥¥Ñ!•¥¡ÐèÉ•¹…µ•!•É½½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð€¬€ÈÐ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èÉ•¹…µ•!•É½½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐèÑÉ-•ä ‰É•¹…µ•}Ñ•µÁ±…Ñ•}Ñ¥Ñ±”ˆ¤ì½±½Èè€ˆÅäˆì™½¹Ð¹Á¥á•±M¥é”è€ÄÈì™½¹Ð¹‰½±èÑÉÕ”ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐè…ÁÁMÑ…Ñ”¹É•¹…µ•1¥Ù•Q•µÁ±…Ñ•9…µ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÈØ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]É…Á¹åÝ¡•É”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐè…ÁÁMÑ…Ñ”¹É•¹…µ•1¥Ù•Q•µÁ±…Ñ•!¥¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆŒáÁÄˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€±½Üì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÁ…É•¹Ð¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹É•¹…µ•Q•µÁ±…Ñ•=ÁÑ¥½¹Ì((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”è	ÕÑÑ½¸ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€É•ÅÕ¥É•ÁÉ½Á•ÉÑäÙ…Èµ½‘•±…Ñ„(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù¥Í¥‰±”èµ½‘•±…Ñ„¹­•ä€„ôô€‰ÕÍÑ½´ˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹±…‰•°(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½Ù•É¹…‰±•èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹Í•ÑI•¹…µ•Q•µÁ±…Ñ”¡µ½‘•±…Ñ„¹­•ä¤((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰…­É½Õ¹èI•Ñ…¹±”ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€É…‘¥ÕÌè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè¥¹‘•à€ôôô…ÁÁMÑ…Ñ”¹É•¹…µ•M•±•Ñ•‘Q•µÁ±…Ñ•%¹‘•à€ü€ˆŒÄÌÉÑˆ€è€¡Á…É•¹Ð¹‘½Ý¸€ü€ˆŒÄÀÈÀÌàˆ€è€¡Á…É•¹Ð¹¡½Ù•É•€ü€ˆŒÄÌÉÑˆ€è€‰ÑÉ…¹ÍÁ…É•¹Ðˆ¤¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰½É‘•È¹Ý¥‘Ñ è€Ä(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰½É‘•È¹½±½Èè¥¹‘•à€ôôô…ÁÁMÑ…Ñ”¹É•¹…µ•M•±•Ñ•‘Q•µÁ±…Ñ•%¹‘•à€ü€ˆŒÑàÉÜˆ€è€ˆŒÌÀÐØÕˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ%Ñ•´èQ•áÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÁ…É•¹Ð¹Ñ•áÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½É¥é½¹Ñ…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹!•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù•ÉÑ¥…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹Y•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÄ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€±½Üì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÁ…É•¹Ð¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹É•¹…µ•	±½­Ì((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”èI•Ñ…¹±”ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ è€ÈÈÀ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡•¥¡Ðè€ÄÀÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€É…‘¥ÕÌè€ÄÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆŒÀäÄÌÈÄˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰½É‘•È¹½±½Èè€ˆŒÈÈÌÈÑˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰½É‘•È¹Ý¥‘Ñ è€Ä((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€5½ÕÍ•É•„ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹å±•I•¹…µ•	±½¬¡µ½‘•±…Ñ„¹¥¹‘•à¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÀ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€Ð((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I½Ý1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹Í±½Ñ}±…‰•°(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆŒáÁÄˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÄ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€	ÕÑÑ½¸ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù¥Í¥‰±”èµ½‘•±…Ñ„¹É•µ½Ù…‰±”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰É•¹…µ•}É•µ½Ù•}‰±½­}…Ñ¥½¸ˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½Ù•É¹…‰±•èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹É•µ½Ù•I•¹…µ•	±½¬¡µ½‘•±…Ñ„¹¥¹‘•à¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰…­É½Õ¹è=ÕÑ±¥¹•	ÕÑÑ½¹	…­É½Õ¹íô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ%Ñ•´èQ•áÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÁ…É•¹Ð¹Ñ•áÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½É¥é½¹Ñ…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹!•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù•ÉÑ¥…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹Y•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÀ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹±…‰•°(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄØ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€%Ñ•´ì1…å½ÕÐ¹™¥±±!•¥¡ÐèÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹¡¥¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆŒÙáäˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÄ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€	ÕÑÑ½¸ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ è€ÈÈÀ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡•¥¡Ðè€ÄÀÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰É•¹…µ•}…‘‘}‰±½­}…Ñ¥½¸ˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½Ù•É¹…‰±•èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹…‘‘I•¹…µ•	±½¬ ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰…­É½Õ¹è=ÕÑ±¥¹•	ÕÑÑ½¹	…­É½Õ¹íô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ%Ñ•´èQ•áÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÁ…É•¹Ð¹Ñ•áÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½É¥é½¹Ñ…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹!•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù•ÉÑ¥…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹Y•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…É‘A…¹•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥µÁ±¥¥Ñ!•¥¡ÐèÉ•¹…µ•AÉ•Ù¥•Ý½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð€¬€ÈÐ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èÉ•¹…µ•AÉ•Ù¥•Ý½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I½Ý1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐèÑÉ-•ä ‰É•¹…µ•}ÁÉ•Ù¥•Ý}Ñ¥Ñ±”ˆ¤ì½±½Èè€ˆÝˆì™½¹Ð¹Á¥á•±M¥é”è€Äàì™½¹Ð¹‰½±èÑÉÕ”ì1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè…ÁÁMÑ…Ñ”¹É•¹…µ•AÉ•Ù¥•Ý½Õ¹Ñ1…‰•°ì½±½Èè€ˆŒáÁÄˆì™½¹Ð¹Á¥á•±M¥é”è€ÄÈì™½¹Ð¹‰½±èÑÉÕ”ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰É•¹…µ•}ÁÉ•Ù¥•Ý}‰½‘äˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹É•¹…µ•AÉ•Ù¥•ÝI½ÝÌ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”èI•Ñ…¹±”ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÉ•¹…µ•AÉ•Ù¥•Ý½±Õµ¸¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥µÁ±¥¥Ñ!•¥¡Ðè€Øà(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€É…‘¥ÕÌè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆŒÀäÄÌÈÄˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰½É‘•È¹½±½Èè€ˆŒÈÈÌÈÑˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰½É‘•È¹Ý¥‘Ñ è€Ä((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÀ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€Ð((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹Í½ÕÉ•}¹…µ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅäˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÄ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€•±¥‘”èQ•áÐ¹±¥‘•I¥¡Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹ÁÉ½Á½Í•‘}¹…µ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]É…Á¹åÝ¡•É”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹Í½ÕÉ•}Á…Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆŒÙáäˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÀ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€•±¥‘”èQ•áÐ¹±¥‘•5¥‘‘±”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù¥Í¥‰±”è…ÁÁMÑ…Ñ”¹É•¹…µ•AÉ•Ù¥•ÝI½ÝÌ¹±•¹Ñ €ôôô€À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰É•¹…µ•}ÁÉ•Ù¥•Ý}•µÁÑäˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅäˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€…É‘A…¹•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€Äà(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€ÄÀ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€M•Ñ¥½¹Q¥Ñ±”ìÑ•áÐèÑÉ-•ä ‰ÍÑ…•}‘½¹•}Ñ¥Ñ±”ˆ¤ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐèÑÉ-•ä ‰ÍÑ…•}‘½¹•}ÍÕ‰Ñ¥Ñ±”ˆ¤ì½±½Èè€ˆÅäˆìÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…Àì1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€%Ñ•´ì1…å½ÕÐ¹™¥±±!•¥¡ÐèÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€	ÕÑÑ½¸ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰‰ÕÑÑ½¹}¡½µ”ˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½Ù•É¹…‰±•èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹‰…­Q½!½µ” ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‰…­É½Õ¹è=ÕÑ±¥¹•	ÕÑÑ½¹	…­É½Õ¹íô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ%Ñ•´èQ•áÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÁ…É•¹Ð¹Ñ•áÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½É¥é½¹Ñ…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹!•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù•ÉÑ¥…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹Y•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€I½Ý1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”((€€€€€€€€€€€€€€€€€€€€€€€	ÕÑÑ½¸ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰‰ÕÑÑ½¹}‰…¬ˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½Ù•É¹…‰±•èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹Ý½É­™±½Ý	…¬ ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€‰…­É½Õ¹è=ÕÑ±¥¹•	ÕÑÑ½¹	…­É½Õ¹íô(€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ%Ñ•´èQ•áÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÁ…É•¹Ð¹Ñ•áÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½É¥é½¹Ñ…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹!•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù•ÉÑ¥…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹Y•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€%Ñ•´ì1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€	ÕÑÑ½¸ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù¥Í¥‰±”è…ÁÁMÑ…Ñ”¹…¹‘Ù…¹•]½É­™±½Ü€˜˜…ÁÁMÑ…Ñ”¹Ý½É­™±½ÝMÑ…•-•ä€„ôô€‰ÍÕµµ…Éäˆ€˜˜…ÁÁMÑ…Ñ”¹Ý½É­™±½ÝMÑ…•-•ä€„ôô€‰‘½¹”ˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÑÉ-•ä ‰‰ÕÑÑ½¹}¹•áÐˆ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½Ù•É¹…‰±•èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹±¥­•è…ÁÁMÑ…Ñ”¹Ý½É­™±½Ý9•áÐ ¤(€€€€€€€€€€€€€€€€€€€€€€€€€€€‰…­É½Õ¹è=ÕÑ±¥¹•	ÕÑÑ½¹	…­É½Õ¹íô(€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ%Ñ•´èQ•áÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèÁ…É•¹Ð¹Ñ•áÐ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÝˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¡½É¥é½¹Ñ…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹!•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ù•ÉÑ¥…±±¥¹µ•¹ÐèQ•áÐ¹±¥¹Y•¹Ñ•È(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹‰½±èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€MÑ…­1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€ÕÉÉ•¹Ñ%¹‘•àè…ÁÁMÑ…Ñ”¹ÕÉÉ•¹ÑA…”€ôôô€‰‘ÕÁ±¥…Ñ•Ìˆ€ü€À€è€¡…ÁÁMÑ…Ñ”¹ÕÉÉ•¹ÑA…”€ôôô€‰½É…¹¥é”ˆ€ü€Ä€è€È¤((€€€€€€€€€€€€€€€€€€€±¥­…‰±”ì(€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ]¥‘Ñ èÝ¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ!•¥¡Ðè‘ÕÁ±¥…Ñ•Í5…¹Õ…±½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð(€€€€€€€€€€€€€€€€€€€€€€€±¥ÀèÑÉÕ”((€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€¥è‘ÕÁ±¥…Ñ•Í5…¹Õ…±½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÁ…É•¹Ð¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€ÄÈ((€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè€‰5…¹Õ…°‘ÕÁ±¥…Ñ”É•Ù¥•Üˆì½±½Èè€ˆÝˆì™½¹Ð¹Á¥á•±M¥é”è€ÌÀì™½¹Ð¹‰½±èÑÉÕ”ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè€‰¥É•Ð…•ÍÌÑ¼‘ÕÁ±¥…Ñ”É½ÝÌ°‘ÉäµÉÕ¸É½ÝÌ°…¹•á•ÕÑ¥½¸É½ÝÌ¸ˆì½±½Èè€ˆÅäˆìÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…Àì1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€…É‘A…¹•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥µÁ±¥¥Ñ!•¥¡Ðèµ…¹Õ…±I½ÝÍ½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð€¬€ÈÐ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èµ…¹Õ…±I½ÝÍ½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹‘ÕÁ±¥…Ñ•I½ÝÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”è1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹¹…µ”€¬€ˆƒŠˆ€ˆ€¬µ½‘•±…Ñ„¹Í¥é”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÙàˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ è‘ÕÁ±¥…Ñ•Í5…¹Õ…±½±Õµ¸¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€…É‘A…¹•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥µÁ±¥¥Ñ!•¥¡Ðèµ…¹Õ…±ÉåIÕ¹½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð€¬€ÈÐ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èµ…¹Õ…±ÉåIÕ¹½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐèÑÉ-•ä ‰‘ÉåÉÕ¹}Ñ¥Ñ±”ˆ¤ì½±½Èè€ˆÝˆì™½¹Ð¹Á¥á•±M¥é”è€Äàì™½¹Ð¹‰½±èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹‘ÉåIÕ¹I½ÝÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”è1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹ÍÑ…ÑÕÍ}±…‰•°€¬€ˆƒŠˆ€ˆ€¬µ½‘•±…Ñ„¹…Ñ¥½¹}±…‰•°€¬€ˆƒŠˆ€ˆ€¬µ½‘•±…Ñ„¹É•…Í½¹}±…‰•°(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÄ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ è‘ÕÁ±¥…Ñ•Í5…¹Õ…±½±Õµ¸¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€…É‘A…¹•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…å½ÕÐ¹™¥±±]¥‘Ñ èÑÉÕ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥µÁ±¥¥Ñ!•¥¡Ðèµ…¹Õ…±á•½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð€¬€ÈÐ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èµ…¹Õ…±á•½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹™¥±°èÁ…É•¹Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€…¹¡½ÉÌ¹µ…É¥¹Ìè€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€à((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè€‰á•ÕÑ¥½¸ÁÉ•Ù¥•Üˆì½±½Èè€ˆÝˆì™½¹Ð¹Á¥á•±M¥é”è€Äàì™½¹Ð¹‰½±èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹•á•ÕÑ¥½¹I½ÝÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”è1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹ÍÑ…ÑÕÍ}±…‰•°€¬€ˆƒŠˆ€ˆ€¬µ½‘•±…Ñ„¹É½Ý}ÑåÁ•}±…‰•°€¬€ˆƒŠˆ€ˆ€¬µ½‘•±…Ñ„¹É•…Í½¹}±…‰•°(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÄ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ è‘ÕÁ±¥…Ñ•Í5…¹Õ…±½±Õµ¸¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€±¥­…‰±”ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ]¥‘Ñ èÝ¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ!•¥¡Ðè½É…¹¥é•½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€±¥ÀèÑÉÕ”((€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥è½É…¹¥é•½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÁ…É•¹Ð¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€ÄÈ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè€‰5…¹Õ…°½É…¹¥é”ˆì½±½Èè€ˆÝˆì™½¹Ð¹Á¥á•±M¥é”è€ÌÀì™½¹Ð¹‰½±èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹Í½ÉÑ¥¹AÉ•Ù¥•ÝI½ÝÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”è1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹Í½ÕÉ•}¹…µ”€¬€ˆƒŠH€ˆ€¬µ½‘•±…Ñ„¹É•±…Ñ¥Ù•}‘¥É•Ñ½Éä(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ è½É…¹¥é•½±Õµ¸¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô((€€€€€€€€€€€€€€€€€€€€€€€±¥­…‰±”ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ]¥‘Ñ èÝ¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€½¹Ñ•¹Ñ!•¥¡ÐèÉ•¹…µ•½±Õµ¸¹¥µÁ±¥¥Ñ!•¥¡Ð(€€€€€€€€€€€€€€€€€€€€€€€€€€€±¥ÀèÑÉÕ”((€€€€€€€€€€€€€€€€€€€€€€€€€€€½±Õµ¹1…å½ÕÐì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€¥èÉ•¹…µ•½±Õµ¸(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÁ…É•¹Ð¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÍÁ…¥¹œè€ÄÈ((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€1…‰•°ìÑ•áÐè€‰5…¹Õ…°É•¹…µ”ˆì½±½Èè€ˆÝˆì™½¹Ð¹Á¥á•±M¥é”è€ÌÀì™½¹Ð¹‰½±èÑÉÕ”ô((€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€I•Á•…Ñ•Èì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€µ½‘•°è…ÁÁMÑ…Ñ”¹É•¹…µ•AÉ•Ù¥•ÝI½ÝÌ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€‘•±•…Ñ”è1…‰•°ì(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ñ•áÐèµ½‘•±…Ñ„¹Í½ÕÉ•}¹…µ”€¬€ˆƒŠH€ˆ€¬µ½‘•±…Ñ„¹ÁÉ½Á½Í•‘}¹…µ”(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€½±½Èè€ˆÅˆ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€™½¹Ð¹Á¥á•±M¥é”è€ÄÈ(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ÝÉ…Á5½‘”èQ•áÐ¹]½É‘]É…À(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€Ý¥‘Ñ èÉ•¹…µ•½±Õµ¸¹Ý¥‘Ñ (€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€€€€€€€€€€€€€ô(€€€€€€€€€€€€€€€ô(€€€€€€€€€€€ô(€€€ô)ô(