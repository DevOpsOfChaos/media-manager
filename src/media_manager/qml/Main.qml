import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ApplicationWindow {
    id: root
    visible: true
    width: 1480
    height: 940
    minimumWidth: 1280
    minimumHeight: 820
    title: appState.text("app_title")
    color: "#07111F"

    function navText(key) {
        return appState.text(key)
    }

    function pageIndex() {
        if (appState.currentPage === "home") return 0
        if (appState.currentPage === "workflow") return 1
        return 2
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 16

        Rectangle {
            Layout.preferredWidth: 238
            Layout.fillHeight: true
            radius: 26
            color: "#091321"
            border.color: "#1D2A3D"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12

                Label {
                    text: appState.text("app_title")
                    color: "#F7FAFF"
                    font.pixelSize: 28
                    font.bold: true
                    font.family: "SF Pro Display, Segoe UI, Arial"
                }

                Label {
                    text: appState.text("nav_subtitle")
                    color: "#93A8C6"
                    wrapMode: Text.WordWrap
                    font.pixelSize: 13
                }

                Item { Layout.preferredHeight: 8 }

                SidebarButton {
                    text: appState.text("nav_home")
                    active: appState.currentPage === "home"
                    onClicked: appState.setPage("home")
                }
                SidebarButton {
                    text: appState.text("nav_workflow")
                    active: appState.currentPage === "workflow"
                    onClicked: appState.setPage("workflow")
                }
                SidebarButton {
                    text: appState.text("nav_duplicates")
                    active: appState.currentPage === "duplicates"
                    onClicked: appState.setPage("duplicates")
                }
                SidebarButton {
                    text: appState.text("nav_organize")
                    active: appState.currentPage === "organize"
                    onClicked: appState.setPage("organize")
                }
                SidebarButton {
                    text: appState.text("nav_rename")
                    active: appState.currentPage === "rename"
                    onClicked: appState.setPage("rename")
                }

                Item { Layout.fillHeight: true }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 64
                radius: 22
                color: "#0B1628"
                border.color: "#243650"

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8
                    Item { Layout.fillWidth: true }
                    Button {
                        Layout.preferredWidth: 58
                        Layout.preferredHeight: 40
                        background: Rectangle {
                            radius: 12
                            color: "#132033"
                            border.color: "#30465F"
                        }
                        ToolTip.visible: hovered
                        ToolTip.text: appState.text("language_tooltip")
                        onClicked: appState.toggleLanguage()
                        contentItem: Image {
                            source: appState.flagPath
                            fillMode: Image.PreserveAspectFit
                            anchors.fill: parent
                            anchors.margins: 6
                        }
                    }
                }
            }

            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: pageIndex()

                Rectangle {
                    color: "transparent"
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
                            spacing: 18

                            Item { Layout.preferredHeight: 12 }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: appState.text("home_title")
                                color: "#F7FAFF"
                                font.pixelSize: 52
                                font.bold: true
                                font.family: "SF Pro Display, Segoe UI, Arial"
                            }

                            Rectangle {
                                visible: appState.wizardVisible
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: Math.min(parent.width * 0.72, 860)
                                Layout.preferredHeight: 520
                                radius: 28
                                color: "#0C1728"
                                border.color: "#243650"

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 30
                                    spacing: 16

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: appState.text("home_subtitle")
                                        color: "#F7FAFF"
                                        font.pixelSize: 20
                                        font.bold: true
                                    }

                                    Repeater {
                                        model: ["full_cleanup", "ready_for_sorting", "ready_for_rename", "exact_duplicates_only"]
                                        delegate: LargeProblemButton {
                                            Layout.fillWidth: true
                                            title: appState.problemLabel(modelData)
                                            subtitle: appState.problemDescription(modelData)
                                            onClicked: appState.selectProblemAndStart(modelData)
                                        }
                                    }

                                    Item { Layout.fillHeight: true }

                                    Button {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: appState.text("home_dismiss")
                                        background: Rectangle {
                                            radius: 14
                                            color: "#132033"
                                            border.color: "#30465F"
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            font.pixelSize: 15
                                            font.bold: true
                                        }
                                        onClicked: appState.dismissWizard()
                                    }
                                }
                            }

                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: Math.min(parent.width * 0.72, 860)
                                Layout.preferredHeight: appState.wizardVisible ? 200 : 280
                                radius: 28
                                color: "#0C1728"
                                border.color: "#243650"

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 28
                                    spacing: 12

                                    Label {
                                        text: appState.text("home_info_title")
                                        color: "#F7FAFF"
                                        font.pixelSize: 26
                                        font.bold: true
                                    }

                                    Label {
                                        text: appState.text("home_info_body")
                                        color: "#AFC1D9"
                                        wrapMode: Text.WordWrap
                                        font.pixelSize: 16
                                    }

                                    Button {
                                        visible: !appState.wizardVisible
                                        text: appState.text("home_restart")
                                        background: Rectangle {
                                            radius: 16
                                            color: "#2F6FED"
                                        }
                                        contentItem: Text {
                                            text: parent.text
                                            color: "#F7FAFF"
                                            horizontalAlignment: Text.AlignHCenter
                                            verticalAlignment: Text.AlignVCenter
                                            font.pixelSize: 16
                                            font.bold: true
                                        }
                                        onClicked: appState.restartWizard()
                                    }
                                }
                            }

                            Item { Layout.preferredHeight: 16 }
                        }
                    }
                }

                Rectangle {
                    color: "transparent"
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 14

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            radius: 28
                            color: "#0C1728"
                            border.color: "#243650"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 24
                                spacing: 10

                                Label {
                                    text: appState.text("workflow_title")
                                    color: "#F7FAFF"
                                    font.pixelSize: 34
                                    font.bold: true
                                }

                                Label {
                                    text: appState.text("workflow_subtitle")
                                    color: "#AFC1D9"
                                    font.pixelSize: 16
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
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 28
                            color: "#0C1728"
                            border.color: "#243650"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 28
                                spacing: 14

                                Label {
                                    text: appState.workflowStageTitle
                                    color: "#F7FAFF"
                                    font.pixelSize: 28
                                    font.bold: true
                                }

                                Label {
                                    text: appState.workflowStageSubtitle
                                    color: "#AFC1D9"
                                    font.pixelSize: 16
                                    wrapMode: Text.WordWrap
                                }

                                StackLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    currentIndex: appState.workflowStageIndex

                                    Item {
                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            width: Math.min(parent.width * 0.7, 760)
                                            spacing: 16
                                            PrimaryButton {
                                                text: appState.text("stage_sources_action")
                                                onClicked: appState.simulateSourceSelection()
                                            }
                                            Label {
                                                text: appState.statusText
                                                color: "#8FB0E1"
                                                wrapMode: Text.WordWrap
                                                horizontalAlignment: Text.AlignHCenter
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }

                                    Item {
                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            width: Math.min(parent.width * 0.7, 760)
                                            spacing: 16
                                            PrimaryButton {
                                                text: appState.text("stage_target_action")
                                                onClicked: appState.simulateTargetSelection()
                                            }
                                            Label {
                                                text: appState.statusText
                                                color: "#8FB0E1"
                                                wrapMode: Text.WordWrap
                                                horizontalAlignment: Text.AlignHCenter
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }

                                    Item {
                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            width: Math.min(parent.width * 0.72, 820)
                                            spacing: 14
                                            LargeProblemButton {
                                                title: appState.text("mode_copy")
                                                subtitle: appState.operationMode === "copy" ? "Selected" : "Safer while you build trust in the workflow."
                                                onClicked: appState.setOperationMode("copy")
                                            }
                                            LargeProblemButton {
                                                title: appState.text("mode_move")
                                                subtitle: appState.operationMode === "move" ? "Selected" : "Cleaner target result once the review decisions are stable."
                                                onClicked: appState.setOperationMode("move")
                                            }
                                            LargeProblemButton {
                                                title: appState.text("mode_delete")
                                                subtitle: appState.operationMode === "delete" ? "Selected" : "Planned for later execution stages and explicit confirmation."
                                                onClicked: appState.setOperationMode("delete")
                                            }
                                        }
                                    }

                                    Item {
                                        ColumnLayout {
                                            anchors.fill: parent
                                            spacing: 14
                                            Button {
                                                text: appState.text("stage_duplicates_action")
                                                onClicked: appState.startDuplicatePreview()
                                                background: Rectangle { radius: 16; color: "#2F6FED" }
                                                contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 16; font.bold: true }
                                            }
                                            ProgressBar {
                                                Layout.fillWidth: true
                                                from: 0
                                                to: 100
                                                value: appState.duplicateProgress
                                                background: Rectangle { radius: 8; color: "#101B2D" }
                                                contentItem: Item {
                                                    Rectangle {
                                                        width: parent.width * (appState.duplicateProgress / 100.0)
                                                        height: parent.height
                                                        radius: 8
                                                        color: "#2F6FED"
                                                    }
                                                }
                                            }
                                            Label {
                                                text: appState.text("stage_duplicates_hint")
                                                color: "#8FB0E1"
                                                wrapMode: Text.WordWrap
                                                font.pixelSize: 14
                                            }

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
                                                                model: [appState.text("table_name"), appState.text("table_size"), appState.text("table_date"), appState.text("table_matches"), appState.text("table_score"), appState.text("table_action")]
                                                                delegate: Label {
                                                                    Layout.fillWidth: true
                                                                    text: modelData
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 14
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
                                                                            text: appState.text("table_show")
                                                                            background: Rectangle { radius: 10; color: "#132033"; border.color: "#30465F" }
                                                                            contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
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

                                    Item {
                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            width: Math.min(parent.width * 0.7, 760)
                                            spacing: 18
                                            Label { text: "Year / Month / Day"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            Label { text: appState.text("stage_sorting_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            PrimaryButton { text: appState.text("stage_sorting_action"); onClicked: appState.workflowNext() }
                                        }
                                    }

                                    Item {
                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            width: Math.min(parent.width * 0.7, 760)
                                            spacing: 18
                                            Label { text: "Readable date + time + original stem"; color: "#F7FAFF"; font.pixelSize: 20; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            Label { text: appState.text("stage_rename_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            PrimaryButton { text: appState.text("stage_rename_action"); onClicked: appState.workflowNext() }
                                        }
                                    }

                                    Item {
                                        ColumnLayout {
                                            anchors.centerIn: parent
                                            width: Math.min(parent.width * 0.7, 760)
                                            spacing: 18
                                            Label { text: appState.text("stage_done_title"); color: "#F7FAFF"; font.pixelSize: 26; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            Label { text: appState.text("stage_done_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                            PrimaryButton { text: appState.text("button_home"); onClicked: appState.backToHome() }
                                        }
                                    }
                                }

                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 12
                                    Button {
                                        text: appState.text("button_back")
                                        onClicked: appState.workflowBack()
                                        background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }
                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 15; font.bold: true }
                                    }
                                    Item { Layout.fillWidth: true }
                                    Button {
                                        visible: appState.workflowStageKey !== "sorting" && appState.workflowStageKey !== "rename" && appState.workflowStageKey !== "done"
                                        enabled: appState.canAdvanceWorkflow
                                        text: appState.text("button_next")
                                        onClicked: appState.workflowNext()
                                        background: Rectangle { radius: 14; color: parent.enabled ? "#2F6FED" : "#233247" }
                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 15; font.bold: true }
                                    }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 96
                            radius: 24
                            color: "#091321"
                            border.color: "#22324A"

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 14

                                StatChip { label: appState.text("bottom_sources"); value: appState.sourceCount.toString() }
                                StatChip { label: appState.text("bottom_target"); value: appState.targetLabel }
                                StatChip { label: appState.text("bottom_mode"); value: appState.operationMode }
                                StatChip { label: appState.text("bottom_step"); value: (appState.workflowStageIndex + 1) + " / " + appState.workflowTotalSteps }
                                StatChip { label: appState.text("bottom_files"); value: appState.discoveredFileCount.toString() }

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    radius: 18
                                    color: "#0F1A2C"
                                    border.color: "#22324A"
                                    Label {
                                        anchors.fill: parent
                                        anchors.margins: 14
                                        text: appState.currentTip
                                        color: "#AFC1D9"
                                        wrapMode: Text.WordWrap
                                        verticalAlignment: Text.AlignVCenter
                                        font.pixelSize: 14
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    color: "transparent"
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Rectangle {
                        anchors.centerIn: parent
                        width: Math.min(parent.width * 0.74, 860)
                        height: 300
                        radius: 28
                        color: "#0C1728"
                        border.color: "#243650"

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 28
                            spacing: 14
                            Label {
                                text: appState.text("manual_placeholder_title")
                                color: "#F7FAFF"
                                font.pixelSize: 30
                                font.bold: true
                            }
                            Label {
                                text: appState.text("manual_placeholder_body")
                                color: "#AFC1D9"
                                wrapMode: Text.WordWrap
                                font.pixelSize: 16
                            }
                            Label {
                                text: appState.text("manual_hint")
                                color: "#8FB0E1"
                                wrapMode: Text.WordWrap
                                font.pixelSize: 14
                            }
                            Item { Layout.fillHeight: true }
                            PrimaryButton {
                                text: appState.text("nav_workflow")
                                onClicked: appState.setPage("workflow")
                            }
                        }
                    }
                }
            }
        }
    }
}
