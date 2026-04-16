$ErrorActionPreference = 'Stop'

$target = Join-Path $PSScriptRoot 'src\media_manager\qml\Main.qml'
if (-not (Test-Path $target)) {
    throw "Main.qml not found at: $target`
Extract this ZIP into the repo root before running the script."
}

$content = Get-Content -Path $target -Raw -Encoding UTF8
$content = $content -replace "`r`n", "`n"

if ($content.Contains('id: duplicateVisibleStatsCards')) {
    Write-Host "Already applied: $target"
    exit 0
}

$anchor = 'id: duplicatesToolColumn'
$anchorIndex = $content.IndexOf($anchor)
if ($anchorIndex -lt 0) {
    throw 'Could not find duplicatesToolColumn in Main.qml'
}

$statusBlock = @'
                                            Label {
                                                text: appState.statusText
                                                color: "#CFE1FF"
                                                wrapMode: Text.WordWrap
                                                font.pixelSize: 14
                                                Layout.fillWidth: true
                                            }
'@ -replace "`r`n", "`n"

$statusIndex = $content.IndexOf($statusBlock, $anchorIndex)
if ($statusIndex -lt 0) {
    throw 'Could not find manual duplicate status block after duplicatesToolColumn'
}

$insertPos = $statusIndex + $statusBlock.Length

$insertBlock = @'

                                            GridLayout {
                                                id: duplicateVisibleStatsCards
                                                Layout.fillWidth: true
                                                columns: 3
                                                columnSpacing: 10
                                                rowSpacing: 10

                                                Repeater {
                                                    model: [
                                                        [root.trKey("summary_groups"), appState.summaryExactGroupCount.toString()],
                                                        [root.trKey("summary_duplicate_files"), appState.summaryExactDuplicateFiles.toString()],
                                                        [root.trKey("summary_extra_duplicates"), appState.summaryExtraDuplicates.toString()],
                                                        [root.trKey("summary_resolved_groups"), appState.summaryResolvedDuplicateGroups.toString()],
                                                        [root.trKey("summary_unresolved_groups"), appState.summaryUnresolvedDuplicateGroups.toString()],
                                                        [root.trKey("summary_estimated_reclaimable_label"), appState.summaryEstimatedReclaimableSizeLabel]
                                                    ]

                                                    delegate: Rectangle {
                                                        required property var modelData
                                                        Layout.fillWidth: true
                                                        Layout.preferredHeight: 84
                                                        radius: 14
                                                        color: "#0F1A2C"
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
                                                                Layout.fillWidth: true
                                                            }
                                                        }
                                                    }
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 10

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    implicitHeight: manualDryRunCard.implicitHeight + 24
                                                    radius: 16
                                                    color: "#0F1A2C"
                                                    border.color: appState.dryRunReady ? "#47B36A" : "#D07A63"

                                                    ColumnLayout {
                                                        id: manualDryRunCard
                                                        anchors.fill: parent
                                                        anchors.margins: 12
                                                        spacing: 6

                                                        RowLayout {
                                                            Layout.fillWidth: true

                                                            Label {
                                                                text: root.trKey("dryrun_title")
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 17
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Rectangle {
                                                                radius: 10
                                                                color: appState.dryRunReady ? "#123926" : "#40241F"
                                                                border.color: appState.dryRunReady ? "#47B36A" : "#D07A63"
                                                                implicitWidth: manualDryRunStatus.implicitWidth + 18
                                                                implicitHeight: manualDryRunStatus.implicitHeight + 10

                                                                Label {
                                                                    id: manualDryRunStatus
                                                                    anchors.centerIn: parent
                                                                    text: appState.dryRunStatusLabel
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 11
                                                                    font.bold: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: appState.dryRunRowsCountLabel
                                                            color: "#B8D3FF"
                                                            font.pixelSize: 13
                                                            font.bold: true
                                                            Layout.fillWidth: true
                                                        }

                                                        Label {
                                                            text: root.trKey("dryrun_subtitle")
                                                            color: "#CFE1FF"
                                                            font.pixelSize: 12
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }
                                                    }
                                                }

                                                Rectangle {
                                                    Layout.fillWidth: true
                                                    implicitHeight: manualExecutionCard.implicitHeight + 24
                                                    radius: 16
                                                    color: "#0F1A2C"
                                                    border.color: appState.executionReady ? "#47B36A" : "#D07A63"

                                                    ColumnLayout {
                                                        id: manualExecutionCard
                                                        anchors.fill: parent
                                                        anchors.margins: 12
                                                        spacing: 6

                                                        RowLayout {
                                                            Layout.fillWidth: true

                                                            Label {
                                                                text: appState.language === "de" ? "Ausführungsvorschau" : "Execution preview"
                                                                color: "#F7FAFF"
                                                                font.pixelSize: 17
                                                                font.bold: true
                                                                Layout.fillWidth: true
                                                            }

                                                            Rectangle {
                                                                radius: 10
                                                                color: appState.executionReady ? "#123926" : "#40241F"
                                                                border.color: appState.executionReady ? "#47B36A" : "#D07A63"
                                                                implicitWidth: manualExecutionStatus.implicitWidth + 18
                                                                implicitHeight: manualExecutionStatus.implicitHeight + 10

                                                                Label {
                                                                    id: manualExecutionStatus
                                                                    anchors.centerIn: parent
                                                                    text: appState.executionReady ? (appState.language === "de" ? "bereit" : "ready") : (appState.language === "de" ? "blockiert" : "blocked")
                                                                    color: "#F7FAFF"
                                                                    font.pixelSize: 11
                                                                    font.bold: true
                                                                }
                                                            }
                                                        }

                                                        Label {
                                                            text: appState.executionRowsCountLabel
                                                            color: "#B8D3FF"
                                                            font.pixelSize: 13
                                                            font.bold: true
                                                            Layout.fillWidth: true
                                                        }

                                                        Label {
                                                            text: appState.executionStatusLabel
                                                            color: "#CFE1FF"
                                                            font.pixelSize: 12
                                                            wrapMode: Text.WordWrap
                                                            Layout.fillWidth: true
                                                        }
                                                    }
                                                }
                                            }
'@ -replace "`r`n", "`n"

$newContent = $content.Insert($insertPos, $insertBlock)
$backup = "$target.bak_before_visible_duplicate_page_upgrade"
Copy-Item -Path $target -Destination $backup -Force
Set-Content -Path $target -Value ($newContent -replace "`n", "`r`n") -Encoding UTF8 -NoNewline

Write-Host "Updated: $target"
Write-Host "Backup:  $backup"
