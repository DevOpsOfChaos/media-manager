\
$ErrorActionPreference = "Stop"

$RepoRoot = Get-Location
$MainQml = Join-Path $RepoRoot "src\media_manager\qml\Main.qml"

if (-not (Test-Path $MainQml)) {
    throw "Main.qml not found: $MainQml"
}

$Content = Get-Content -Raw -Encoding UTF8 $MainQml
$Old = 'currentIndex: manualPageIndex'
$New = 'currentIndex: parent.manualPageIndex'

if ($Content -notlike "*$Old*") {
    throw "Expected text not found: $Old"
}

$Backup = "$MainQml.bak_before_manual_page_index_fix"
Copy-Item $MainQml $Backup -Force

$Updated = $Content.Replace($Old, $New)
Set-Content -Path $MainQml -Value $Updated -Encoding UTF8

Write-Host "Updated: $MainQml"
Write-Host "Backup:  $Backup"
