
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
                    elide: Text.ElideRight
                }

                Button {
                    text: "✕"
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
                                    text: modelData.size + " • " + modelData.date
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

                PrimaryButton {
                    text: trKey("duplicate_detail_keep_selected")
                    onClicked: appState.keepSelectedDuplicateCandidate()
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

                SidebarButton { text: trKey("nav_home"); active: appState.currentPage === "home"; onClicked: appState.setPage("home") }
                SidebarButton { text: trKey("nav_workflow"); active: appState.currentPage === "workflow"; onClicked: appState.setPage("workflow") }
                SidebarButton { text: trKey("nav_duplicates"); active: appState.currentPage === "duplicates"; onClicked: appState.setPage("duplicates") }
                SidebarButton { text: trKey("nav_organize"); active: appState.currentPage === "organize"; onClicked: appState.setPage("organize") }
                SidebarButton { text: trKey("nav_rename"); active: appState.currentPage === "rename"; onClicked: appState.setPage("rename") }

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

                                Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }
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

                                    PrimaryButton {
                                        text: trKey("stage_sources_action")
                                        onClicked: sourceFolderDialog.open()
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

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }

                                Label {
                                    text: appState.targetPath.length > 0 ? appState.targetPath : trKey("stage_target_empty")
                                    color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"
                                    wrapMode: Text.WrapAnywhere
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                }

                                RowLayout {
                                    Layout.fillWidth: true

                                    PrimaryButton {
                                        text: trKey("stage_target_action")
                                        onClicked: targetFolderDialog.open()
                                    }

                                    Button {
                                        text: trKey("button_clear")
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

                                Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }

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

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }

                                PrimaryButton {
                                    text: trKey("stage_duplicates_action")
                                    enabled: appState.sourceCount > 0
                                    onClicked: appState.startDuplicatePreview()
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

                                Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }
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
                                                    Layout.fillWidth: true
                                                    implicitHeight: 76
                                                    radius: 12
                                                    color: "#091321"
                                                    border.color: modelData.status === "blocked" ? "#D07A63" : "#22324A"

                                                    ColumnLayout {
                                                      anchors.fill: parent
                                                      anchors.margins: 10
                                                        spacing: 4

                                                        Label {
                                                            text: modelData.status_label + " • " + modelData.action_label
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
                                                    Layout.fillWidth: true
                                                    implicitHeight: 76
                                                   radius: 12
                                                    color: "#091321"
                                                    border.color: modelData.status === "blocked" ? "#D07A63" : "#22324A"

                                                    ColumnLayout {
                                                      anchors.fill: parent
                                                      anchors.margins: 10
                                                        spacing: 4

                                                        Label {
                                                            text: modelData.status_label + " • " + modelData.row_type_label
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

                                    PrimaryButton {
                                        text: trKey("stage_summary_action")
                                        enabled: appState.summaryReadyForDryRun
                                        onClicked: appState.workflowNext()
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

                                Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }
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

                                    CardPanel {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 118

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: appState.cycleSortingYearStyle()
                                        }

                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 6
                                            Label { text: trKey("sorting_level_year"); color: "#F7FAFF"; font.pixelSize: 15; font.bold: true }
                                            Label { text: appState.sortingYearStyleLabel; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                            Item { Layout.fillHeight: true }
                                            Label { text: trKey("sorting_cycle_action"); color: "#6F8FB9"; font.pixelSize: 11 }
                                        }
                                    }

                                    CardPanel {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 118

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: appState.cycleSortingMonthStyle()
                                        }

                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 6
                                            Label { text: trKey("sorting_level_month"); color: "#F7FAFF"; font.pixelSize: 15; font.bold: true }
                                            Label { text: appState.sortingMonthStyleLabel; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                            Item { Layout.fillHeight: true }
                                            Label { text: trKey("sorting_cycle_action"); color: "#6F8FB9"; font.pixelSize: 11 }
                                        }
                                    }

                                    CardPanel {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 118

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: appState.cycleSortingDayStyle()
                                        }

                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 6
                                            Label { text: trKey("sorting_level_day"); color: "#F7FAFF"; font.pixelSize: 15; font.bold: true }
                                            Label { text: appState.sortingDayStyleLabel; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                            Item { Layout.fillHeight: true }
                                            Label { text: trKey("sorting_cycle_action"); color: "#6F8FB9"; font.pixelSize: 11 }
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
                                            visible: appState.sortingPreviewRows.length === 0
                                            text: trKey("sorting_preview_empty")
                                            color: "#AFC1D9"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }
                                }

                                Flickable {
                                    contentWidth: width
                                    contentHeight: renameStageColumn.implicitHeight
                                    clip: true

                                    ColumnLayout {
                                        id: renameStageColumn
                                        width: parent.width
                                        spacing: 12

                                        Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }
                                        Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                                        CardPanel {
                                            Layout.fillWidth: true
                                            implicitHeight: renameHeroColumn.implicitHeight + 24

                                            ColumnLayout {
                                                id: renameHeroColumn
                                                anchors.fill: parent
                                                anchors.margins: 12
                                                spacing: 8

                                                Label { text: trKey("rename_template_title"); color: "#AFC1D9"; font.pixelSize: 12; font.bold: true }
                                                Label {
                                                    text: appState.renameLiveTemplateName
                                                    color: "#F7FAFF"
                                                    font.pixelSize: 26
                                                    font.bold: true
                                                    wrapMode: Text.WrapAnywhere
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

                                        Flow {
                                            width: parent.width
                                            spacing: 8

                                            Repeater {
                                                model: appState.renameTemplateOptions

                                                delegate: Button {
                                                    required property var modelData
                                                    visible: modelData.key !== "custom"
                                                    text: modelData.label
                                                    hoverEnabled: true
                                                    onClicked: appState.setRenameTemplate(modelData.key)

                                                    background: Rectangle {
                                                        radius: 12
                                                          color: index === appState.renameSelectedTemplateIndex ? "#132B4A" : (parent.down ? "#102038" : (parent.hovered ? "#132B4A" : "transparent"))
                                                        border.width: 1
                                                        border.color: index === appState.renameSelectedTemplateIndex ? "#4A82D7" : "#30465F"
                                                    }

                                                    contentItem: Text {
                                                        text: parent.text
                                                        color: "#F7FAFF"
                                                        horizontalAlignment: Text.AlignHCenter
                                                        verticalAlignment: Text.AlignVCenter
                                                        font.pixelSize: 11
                                                        font.bold: true
                                                        wrapMode: Text.WordWrap
                                                    }
                                                }
                                            }
                                        }

                                        Flow {
                                            width: parent.width
                                            spacing: 8

                                            Repeater {
                                                model: appState.renameBlocks

                                                delegate: Rectangle {
                                                    width: 220
                                                    height: 104
                                                    radius: 14
                                                    color: "#091321"
                                                    border.color: "#22324A"

                                                    MouseArea {
                                                        anchors.fill: parent
                                                        onClicked: appState.cycleRenameBlock(modelData.index)
                                                    }

                                                    ColumnLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 10
                                                        spacing: 4

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
                                                                text: trKey("rename_remove_block_action")
                                                                  hoverEnabled: true
                                                                  onClicked: appState.removeRenameBlock(modelData.index)
                                                                background: OutlineButtonBackground {}
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
                                                          font.pixelSize: 16
                                                        font.bold: true
                                                        wrapMode: Text.WordWrap
                                                        Layout.fillWidth: true
                                                    }

                                                      Item { Layout.fillHeight: true }

                                                    Label {
                                                        text: modelData.hint
                                                          color: "#6F8FB9"
                                                          font.pixelSize: 11
                                                        wrapMode: Text.WordWrap
                                                        Layout.fillWidth: true
                                                    }
                                                  }
                                                }
                                            }
                                        }

                                    Button {
                                        width: 220
                                        height: 104
                                        text: trKey("rename_add_block_action")
                                        hoverEnabled: true
                                        onClicked: appState.addRenameBlock()
                                        background: OutlineButtonBackground {}

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

                                CardPanel {
                                    Layout.fillWidth: true
                                    implicitHeight: renamePreviewColumn.implicitHeight + 24

                                    ColumnLayout {
                                        id: renamePreviewColumn
                                        id: renamePreviewColumn
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 8

                                        RowLayout {
                                            Layout.fillWidth: true
                                            Label { text: trKey("rename_preview_title"); color: "#F7FAFF"; font.pixelSize: 18; font.bold: true; Layout.fillWidth: true }
                                            Label { text: appState.renamePreviewCountLabel; color: "#8FB0E1"; font.pixelSize: 12; font.bold: true }
                                        }

                                        Label {
                                            text: trKey("rename_preview_body")
                                            color: "#CFE1EF"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }

                                        Repeater {
                                            model: appState.renamePreviewRows

                                                delegate: Rectangle {
                                                width: renamePreviewColumn.width
                                                  implicitHeight: 68
                                                  radius: 12
                                                  color: "#091321"
                                                  border.color: "#22324A"

                                                  ColumnLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 10
                                                    spacing: 4

                                                    Label {
                                                        text: modelData.source_name
                                                        color: "#AFC1D9"
                                                      font.pixelSize: 11
                                                      font.bold: true
                                                        Layout.fillWidth: true
                                                      elide: Text.ElideRight
                                                    }

                                                    Label {
                                                        text: modelData.proposed_name
                                                        color: "#F7FAFF"
                                                      font.pixelSize: 13
                                                      font.bold: true
                                                        wrapMode: Text.WrapAnywhere
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
                                            visible: appState.renamePreviewRows.length === 0
                                            text: trKey("rename_preview_empty")
                                            color: "#AFC1D9"
                                            wrapMode: Text.WordWrap
                                            Layout.fillWidth: true
                                        }
                                    }
                                }
                            }

                        CardPanel {
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 18
                                spacing: 10

                                Label { text: trKey("stage_done_title"); color: "#F7FAFF"; font.pixelSize: 24; font.bold: true }
                                Label { text: trKey("stage_done_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                Item { Layout.fillHeight: true }

                                PrimaryButton {
                                    text: trKey("button_home")
                                    onClicked: appState.backToHome()
                                }
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Button {
                            text: trKey("button_back")
                            hoverEnabled: true
                            onClicked: appState.workflowBack()
                            background: OutlineButtonBackground {}

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

                        Button {
                            visible: appState.canAdvanceWorkflow && appState.workflowStageKey !== "summary" && appState.workflowStageKey !== "done"
                            text: trKey("button_next")
                            onClicked: appState.workflowNext()
                            background: OutlineButtonBackground {}

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

                StackLayout {
                    currentIndex: appState.currentPage === "duplicates" ? 0 : (appState.currentPage === "organize" ? 1 : 2)

                    Flickable {
                        contentWidth: width
                        contentHeight: duplicatesManualColumn.implicitHeight
                        clip: true

                        ColumnLayout {
                            id: duplicatesManualColumn
                            width: parent.width
                            spacing: 12

                            Label { text: "Manual duplicate review"; color: "#F7FAFF"; font.pixelSize: 30; font.bold: true }
                            Label { text: "Direct access to duplicate rows, dry-run rows, and execution rows."; color: "#AFC1D9"; wrapMode: Text.WordWrap; Layout.fillWidth: true }

                            CardPanel {
                                Layout.fillWidth: true
                                implicitHeight: manualRowsColumn.implicitHeight + 24

                                ColumnLayout {
                                    id: manualRowsColumn
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 8

                                    Repeater {
                                        model: appState.duplicateRows
                                        delegate: Label {
                                            text: modelData.name + " • " + modelData.size
                                            color: "#E6EEF8"
                                            font.pixelSize: 12
                                            wrapMode: Text.WordWrap
                                            width: duplicatesManualColumn.width
                                        }
                                    }
                                }
                            }

                            CardPanel {
                                Layout.fillWidth: true
                                implicitHeight: manualDryRunColumn.implicitHeight + 24

                                ColumnLayout {
                                    id: manualDryRunColumn
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 8

                                    Label { text: trKey("dryrun_title"); color: "#F7FAFF"; font.pixelSize: 18; font.bold: true }

                                    Repeater {
                                        model: appState.dryRunRows
                                        delegate: Label {
                                            text: modelData.status_label + " • " + modelData.action_label + " • " + modelData.reason_label
                                            color: "#CFE1EF"
                                            font.pixelSize: 11
                                            wrapMode: Text.WordWrap
                                            width: duplicatesManualColumn.width
                                        }
                                    }
                                }
                            }

                            CardPanel {
                                Layout.fillWidth: true
                                implicitHeight: manualExecColumn.implicitHeight + 24

                                ColumnLayout {
                                    id: manualExecColumn
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 8

                                    Label { text: "Execution preview"; color: "#F7FAFF"; font.pixelSize: 18; font.bold: true }

                                    Repeater {
                                        model: appState.executionRows
                                        delegate: Label {
                                            text: modelData.status_label + " • " + modelData.row_type_label + " • " + modelData.reason_label
                                            color: "#CFE1EF"
                                            font.pixelSize: 11
                                            wrapMode: Text.WordWrap
                                            width: duplicatesManualColumn.width
                                        }
                                    }
                                }
                            }
                        }

                        Flickable {
                            contentWidth: width
                            contentHeight: organizeColumn.implicitHeight
                            clip: true

                            ColumnLayout {
                                id: organizeColumn
                                width: parent.width
                                spacing: 12

                                Label { text: "Manual organize"; color: "#F7FAFF"; font.pixelSize: 30; font.bold: true }

                                Repeater {
                                    model: appState.sortingPreviewRows
                                    delegate: Label {
                                        text: modelData.source_name + " → " + modelData.relative_directory
                                        color: "#CFE1EF"
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                        width: organizeColumn.width
                                    }
                                }
                            }

                        Flickable {
                            contentWidth: width
                            contentHeight: renameColumn.implicitHeight
                            clip: true

                            ColumnLayout {
                                id: renameColumn
                                width: parent.width
                                spacing: 12

                                Label { text: "Manual rename"; color: "#F7FAFF"; font.pixelSize: 30; font.bold: true }

                                Repeater {
                                    model: appState.renamePreviewRows
                                    delegate: Label {
                                        text: modelData.source_name + " → " + modelData.proposed_name
                                        color: "#CFE1EF"
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                        width: renameColumn.width
                                    }
                                }
                            }
                }
            }
    }
}
