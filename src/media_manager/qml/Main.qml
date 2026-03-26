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

    function pageIndex() {
        if (appState.currentPage === "home") return 0
        if (appState.currentPage === "workflow") return 1
        return 2
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
        onOpened: forceActiveFocus()
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
                    background: Rectangle { radius: 12; color: parent.hovered ? "#7A1E2D" : "#132033"; border.color: parent.hovered ? "#C94A61" : "#30465F" }
                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 18; font.bold: true }
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
                text: appState.text("duplicate_detail_hint")
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
                                            color: modelData.selected ? "#2F6FED" : "#122033"
                                            border.color: modelData.selected ? "#7BA7FF" : "#30465F"
                                            Layout.preferredWidth: 170
                                            Layout.preferredHeight: 30
                                            Label {
                                                anchors.centerIn: parent
                                                text: modelData.selected ? appState.text("duplicate_detail_selected") : ""
                                                color: "#F7FAFF"
                                                font.pixelSize: 12
                                                font.bold: true
                                            }
                                        }
                                    }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: 12
                                        Label { text: modelData.size; color: "#AFC1D9"; font.pixelSize: 13 }
                                        Label { text: modelData.date; color: "#AFC1D9"; font.pixelSize: 13 }
                                    }
                                    Label {
                                        text: appState.text("duplicate_detail_path") + ": " + modelData.path
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
                    text: appState.text("duplicate_detail_keep_selected")
                    onClicked: appState.keepSelectedDuplicateCandidate()
                    background: Rectangle { radius: 14; color: "#2F6FED" }
                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14; font.bold: true }
                }
                Button {
                    text: appState.text("duplicate_detail_keep_newest")
                    onClicked: appState.chooseDuplicateKeepNewest()
                    background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }
                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14; font.bold: true }
                }
                Button {
                    text: appState.text("duplicate_detail_keep_oldest")
                    onClicked: appState.chooseDuplicateKeepOldest()
                    background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }
                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14; font.bold: true }
                }
                Item { Layout.fillWidth: true }
                Button {
                    text: appState.text("duplicate_detail_close")
                    onClicked: duplicateDetailPopup.close()
                    background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }
                    contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14; font.bold: true }
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
        spacing: 16

        Rectangle {
            Layout.preferredWidth: 230
            Layout.fillHeight: true
            radius: 28
            color: "#0A1425"
            border.color: "#1E2C40"
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12
                Label { text: appState.text("app_title"); color: "#F7FAFF"; font.pixelSize: 30; font.bold: true; font.family: "SF Pro Display, Segoe UI Variable, Segoe UI, Arial" }
                Label { text: appState.text("nav_subtitle"); color: "#93A8C6"; wrapMode: Text.WordWrap; font.pixelSize: 13 }
                Item { Layout.preferredHeight: 10 }
                SidebarButton { text: appState.text("nav_home"); active: appState.currentPage === "home"; onClicked: appState.setPage("home") }
                SidebarButton { text: appState.text("nav_workflow"); active: appState.currentPage === "workflow"; onClicked: appState.setPage("workflow") }
                SidebarButton { text: appState.text("nav_duplicates"); active: appState.currentPage === "duplicates"; onClicked: appState.setPage("duplicates") }
                SidebarButton { text: appState.text("nav_organize"); active: appState.currentPage === "organize"; onClicked: appState.setPage("organize") }
                SidebarButton { text: appState.text("nav_rename"); active: appState.currentPage === "rename"; onClicked: appState.setPage("rename") }
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
                radius: 24
                color: "#0B1628"
                border.color: "#243650"
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 14
                    spacing: 8
                    Item { Layout.fillWidth: true }
                    Button {
                        Layout.preferredWidth: 60
                        Layout.preferredHeight: 40
                        ToolTip.visible: hovered
                        ToolTip.text: appState.text("language_tooltip")
                        onClicked: appState.toggleLanguage()
                        background: Rectangle { radius: 14; color: parent.down ? "#16263C" : (parent.hovered ? "#16263C" : "#122033"); border.color: "#30465F" }
                        contentItem: Image { source: appState.flagPath; fillMode: Image.PreserveAspectFit; anchors.fill: parent; anchors.margins: 6 }
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
                            spacing: 20
                            Item { Layout.preferredHeight: 8 }
                            Label { Layout.alignment: Qt.AlignHCenter; text: appState.text("home_title"); color: "#F7FAFF"; font.pixelSize: 64; font.bold: true; font.family: "SF Pro Display, Segoe UI Variable, Segoe UI, Arial" }
                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: Math.min(parent.width * 0.78, 940)
                                Layout.preferredHeight: appState.wizardVisible ? 620 : 250
                                radius: 34
                                color: "#0C1728"
                                border.color: "#243650"
                                Rectangle { anchors.top: parent.top; anchors.horizontalCenter: parent.horizontalCenter; width: parent.width * 0.74; height: 1; color: "#355988"; opacity: 0.55 }
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 34
                                    spacing: 18
                                    Label { Layout.alignment: Qt.AlignHCenter; text: appState.text("home_subtitle"); color: "#F7FAFF"; font.pixelSize: 24; font.bold: true; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; Layout.preferredWidth: Math.min(parent.width * 0.82, 760) }
                                    Repeater {
                                        visible: appState.wizardVisible
                                        model: ["full_cleanup", "ready_for_sorting", "ready_for_rename", "exact_duplicates_only"]
                                        delegate: LargeProblemButton { Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: Math.min(parent.width * 0.86, 760); title: appState.problemLabel(modelData); subtitle: appState.problemDescription(modelData); onClicked: appState.selectProblemAndStart(modelData) }
                                    }
                                    Item { Layout.fillHeight: true }
                                    Button {
                                        visible: appState.wizardVisible
                                        Layout.alignment: Qt.AlignHCenter
                                        text: appState.text("home_dismiss")
                                        background: Rectangle { radius: 16; color: parent.down ? "#182536" : (parent.hovered ? "#172638" : "#122033"); border.color: "#30465F" }
                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 15; font.bold: true }
                                        onClicked: appState.dismissWizard()
                                    }
                                    Button {
                                        visible: !appState.wizardVisible
                                        Layout.alignment: Qt.AlignHCenter
                                        text: appState.text("home_restart")
                                        background: Rectangle { radius: 18; color: parent.down ? "#285DCF" : (parent.hovered ? "#2A64D5" : "#2F6FED") }
                                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 16; font.bold: true }
                                        onClicked: appState.restartWizard()
                                    }
                                }
                            }
                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                Layout.preferredWidth: Math.min(parent.width * 0.78, 940)
                                Layout.preferredHeight: 240
                                radius: 30
                                color: "#0C1728"
                                border.color: "#243650"
                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 30
                                    spacing: 14
                                    Label { text: appState.text("home_info_title"); color: "#F7FAFF"; font.pixelSize: 32; font.bold: true }
                                    Label { text: appState.text("home_info_body"); color: "#AFC1D9"; wrapMode: Text.WordWrap; font.pixelSize: 17; Layout.fillWidth: true }
                                }
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
                        spacing: 14
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 122
                            radius: 28
                            color: "#0C1728"
                            border.color: "#243650"
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 24
                                spacing: 10
                                Label { text: appState.text("workflow_title"); color: "#F7FAFF"; font.pixelSize: 34; font.bold: true }
                                Label { text: appState.text("workflow_subtitle"); color: "#AFC1D9"; font.pixelSize: 16 }
                                ProgressBar {
                                    Layout.fillWidth: true
                                    from: 0
                                    to: appState.workflowTotalSteps
                                    value: appState.workflowStageIndex + 1
                                    background: Rectangle { radius: 8; color: "#101B2D" }
                                    contentItem: Item { Rectangle { width: parent.width * ((appState.workflowStageIndex + 1) / appState.workflowTotalSteps); height: parent.height; radius: 8; color: "#2F6FED" } }
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            radius: 30
                            color: "#0C1728"
                            border.color: "#243650"
                            Item {
                                anchors.fill: parent
                                anchors.margins: 28
                                ColumnLayout {
                                    anchors.fill: parent
                                    spacing: 16
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Rectangle {
                                            radius: 14
                                            color: "#11233A"
                                            border.color: "#27456E"
                                            height: 34
                                            Layout.preferredWidth: 160
                                            Label { anchors.centerIn: parent; text: (appState.workflowStageIndex + 1) + " / " + appState.workflowTotalSteps; color: "#B8D3FF"; font.pixelSize: 14; font.bold: true }
                                        }
                                        Item { Layout.fillWidth: true }
                                    }
                                    Label { text: appState.workflowStageTitle; color: "#F7FAFF"; font.pixelSize: 30; font.bold: true }
                                    Label { text: appState.workflowStageSubtitle; color: "#AFC1D9"; font.pixelSize: 16; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                                    Item {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        StackLayout {
                                            anchors.fill: parent
                                            currentIndex: appState.workflowStageIndex
                                            Item {
                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    spacing: 14
                                                    Label { text: appState.text("stage_sources_list_title"); color: "#F7FAFF"; font.pixelSize: 20; font.bold: true }
                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        Layout.fillHeight: true
                                                        radius: 20
                                                        color: "#091321"
                                                        border.color: "#22324A"
                                                        Loader { anchors.fill: parent; anchors.margins: 16; active: appState.sourceCount > 0; sourceComponent: sourceListComponent }
                                                        Label { visible: appState.sourceCount === 0; anchors.centerIn: parent; text: appState.text("stage_sources_empty"); color: "#8FB0E1"; font.pixelSize: 16 }
                                                    }
                                                    RowLayout {
                                                        Layout.fillWidth: true
                                                        PrimaryButton { text: appState.text("stage_sources_action"); onClicked: sourceFolderDialog.open() }
                                                        Button { text: appState.text("button_clear"); enabled: appState.sourceCount > 0; onClicked: appState.clearSourceFolders(); background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }; contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14; font.bold: true } }
                                                        Item { Layout.fillWidth: true }
                                                    }
                                                }
                                            }
                                            Item {
                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    spacing: 14
                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        Layout.fillHeight: true
                                                        radius: 20
                                                        color: "#091321"
                                                        border.color: "#22324A"
                                                        ColumnLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 18
                                                            spacing: 12
                                                            Label { text: appState.targetPath.length > 0 ? appState.targetPath : appState.text("stage_target_empty"); color: appState.targetPath.length > 0 ? "#F7FAFF" : "#8FB0E1"; wrapMode: Text.WordWrap; font.pixelSize: 16; Layout.fillWidth: true }
                                                            Item { Layout.fillHeight: true }
                                                            RowLayout {
                                                                Layout.fillWidth: true
                                                                PrimaryButton { text: appState.text("stage_target_action"); onClicked: targetFolderDialog.open() }
                                                                Button { text: appState.text("button_clear"); enabled: appState.targetPath.length > 0; onClicked: appState.clearTargetFolder(); background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }; contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14; font.bold: true } }
                                                                Item { Layout.fillWidth: true }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                            Item {
                                                ColumnLayout {
                                                    anchors.centerIn: parent
                                                    width: Math.min(parent.width * 0.76, 820)
                                                    spacing: 14
                                                    LargeProblemButton { title: appState.text("mode_copy"); subtitle: appState.operationMode === "copy" ? "Selected" : "Safer while you build trust in the workflow."; onClicked: appState.setOperationMode("copy") }
                                                    LargeProblemButton { title: appState.text("mode_move"); subtitle: appState.operationMode === "move" ? "Selected" : "Cleaner target result once the review decisions are stable."; onClicked: appState.setOperationMode("move") }
                                                    LargeProblemButton { title: appState.text("mode_delete"); subtitle: appState.operationMode === "delete" ? "Selected" : "Planned for later execution stages and explicit confirmation."; onClicked: appState.setOperationMode("delete") }
                                                }
                                            }
                                            Item {
                                                ColumnLayout {
                                                    anchors.fill: parent
                                                    spacing: 14
                                                    PrimaryButton { text: appState.text("stage_duplicates_action"); enabled: appState.sourceCount > 0; onClicked: appState.startDuplicatePreview() }
                                                    ProgressBar {
                                                        Layout.fillWidth: true
                                                        from: 0
                                                        to: 100
                                                        value: appState.duplicateProgress
                                                        background: Rectangle { radius: 8; color: "#101B2D" }
                                                        contentItem: Item { Rectangle { width: parent.width * (appState.duplicateProgress / 100.0); height: parent.height; radius: 8; color: "#2F6FED" } }
                                                    }
                                                    Label { text: appState.text("stage_duplicates_hint"); color: "#8FB0E1"; wrapMode: Text.WordWrap; font.pixelSize: 14 }
                                                    Label { text: appState.statusText; color: "#B8D3FF"; wrapMode: Text.WordWrap; font.pixelSize: 14; Layout.fillWidth: true }
                                                    Rectangle {
                                                        Layout.fillWidth: true
                                                        Layout.fillHeight: true
                                                        radius: 20
                                                        color: "#091321"
                                                        border.color: "#22324A"
                                                        ColumnLayout {
                                                            anchors.fill: parent
                                                            anchors.margins: 14
                                                            spacing: 8
                                                            Rectangle {
                                                                Layout.fillWidth: true
                                                                Layout.preferredHeight: 44
                                                                radius: 12
                                                                color: "#0F1A2C"
                                                                RowLayout {
                                                                    anchors.fill: parent
                                                                    anchors.margins: 10
                                                                    spacing: 8
                                                                    Repeater { model: [appState.text("table_name"), appState.text("table_size"), appState.text("table_date"), appState.text("table_matches"), appState.text("table_score"), appState.text("table_action")]; delegate: Label { Layout.fillWidth: true; text: modelData; color: "#F7FAFF"; font.pixelSize: 14; font.bold: true } }
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
                                                                            height: 54
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
                                                                                    onClicked: { appState.openDuplicateGroup(Number(modelData.index)); duplicateDetailPopup.open() }
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
                                                    width: Math.min(parent.width * 0.72, 760)
                                                    spacing: 18
                                                    Label { text: "Year / Month / Day"; color: "#F7FAFF"; font.pixelSize: 22; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                                    Label { text: appState.text("stage_sorting_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true; font.pixelSize: 15 }
                                                    PrimaryButton { text: appState.text("stage_sorting_action"); onClicked: appState.workflowNext() }
                                                }
                                            }
                                            Item {
                                                ColumnLayout {
                                                    anchors.centerIn: parent
                                                    width: Math.min(parent.width * 0.72, 760)
                                                    spacing: 18
                                                    Label { text: "Readable date + time + original stem"; color: "#F7FAFF"; font.pixelSize: 22; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                                    Label { text: appState.text("stage_rename_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true; font.pixelSize: 15 }
                                                    PrimaryButton { text: appState.text("stage_rename_action"); onClicked: appState.workflowNext() }
                                                }
                                            }
                                            Item {
                                                ColumnLayout {
                                                    anchors.centerIn: parent
                                                    width: Math.min(parent.width * 0.72, 760)
                                                    spacing: 18
                                                    Label { text: appState.text("stage_done_title"); color: "#F7FAFF"; font.pixelSize: 28; font.bold: true; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true }
                                                    Label { text: appState.text("stage_done_subtitle"); color: "#AFC1D9"; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter; Layout.fillWidth: true; font.pixelSize: 15 }
                                                    PrimaryButton { text: appState.text("button_home"); onClicked: appState.backToHome() }
                                                }
                                            }
                                        }
                                    }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        Button { text: appState.text("button_back"); onClicked: appState.workflowBack(); background: Rectangle { radius: 14; color: "#132033"; border.color: "#30465F" }; contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 15; font.bold: true } }
                                        Item { Layout.fillWidth: true }
                                        Button { visible: appState.workflowStageKey !== "sorting" && appState.workflowStageKey !== "rename" && appState.workflowStageKey !== "done"; enabled: appState.canAdvanceWorkflow; text: appState.text("button_next"); onClicked: appState.workflowNext(); background: Rectangle { radius: 14; color: parent.enabled ? "#2F6FED" : "#233247" }; contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 15; font.bold: true } }
                                    }
                                }
                            }
                        }
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 98
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
                                    Label { anchors.fill: parent; anchors.margins: 14; text: appState.currentTip; color: "#AFC1D9"; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter; font.pixelSize: 14 }
                                }
                            }
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Rectangle {
                        anchors.centerIn: parent
                        width: Math.min(parent.width * 0.74, 860)
                        height: 320
                        radius: 30
                        color: "#0C1728"
                        border.color: "#243650"
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 30
                            spacing: 14
                            Label { text: appState.text("manual_placeholder_title"); color: "#F7FAFF"; font.pixelSize: 32; font.bold: true }
                            Label { text: appState.text("manual_placeholder_body"); color: "#AFC1D9"; wrapMode: Text.WordWrap; font.pixelSize: 16 }
                            Label { text: appState.text("manual_hint"); color: "#8FB0E1"; wrapMode: Text.WordWrap; font.pixelSize: 14 }
                            Item { Layout.fillHeight: true }
                            PrimaryButton { text: appState.text("nav_workflow"); onClicked: appState.setPage("workflow") }
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
                    Label { Layout.fillWidth: true; text: modelData; color: "#E6EEF8"; font.pixelSize: 14; elide: Text.ElideMiddle }
                    Button {
                        text: appState.text("button_remove")
                        onClicked: appState.removeSourceFolder(index)
                        background: Rectangle { radius: 10; color: "#132033"; border.color: "#30465F" }
                        contentItem: Text { text: parent.text; color: "#F7FAFF"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.pixelSize: 12; font.bold: true }
                    }
                }
            }
        }
    }
}
