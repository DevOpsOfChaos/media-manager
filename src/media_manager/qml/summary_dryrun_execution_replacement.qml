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
                                                                                text: modelData.reason_label + "  •  " + modelData.size + "  •  " + modelData.operation_mode_label
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
                                                                    text: appState.language === "de" ? "Ausführungsvorschau" : "Execution preview"
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
                                                                      ? "Diese Vorschau zeigt, welche Schritte aus dem aktuellen exakten Duplikat-Dry-Run ausführbar, zurückgestellt oder blockiert wären."
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
                                                                        [appState.language === "de" ? "Ausführbar" : "Executable", appState.executionExecutableCount.toString()],
                                                                        [appState.language === "de" ? "Zurückgestellt" : "Deferred", appState.executionDeferredCount.toString()],
                                                                        [appState.language === "de" ? "Blockiert" : "Blocked", appState.executionBlockedCount.toString()],
                                                                        [appState.language === "de" ? "Löschzeilen" : "Delete rows", appState.executionDeleteCount.toString()]
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
                                                                                text: modelData.reason_label + "  •  " + modelData.size + "  •  " + modelData.operation_mode_label
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
                                                                      ? "Noch keine Ausführungszeilen sichtbar."
                                                                      : "No execution rows visible yet."
                                                                color: "#AFC1D9"
                                                                wrapMode: Text.WordWrap
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }