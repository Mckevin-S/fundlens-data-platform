<#
.SYNOPSIS
  Lance le robot UiPath (UiRobot.exe) pour la date donnée puis vérifie que les relevés sont arrivés dans la boîte d'entrée.
#>
param(
    [string]$AsOfDate = (Get-Date).ToString("yyyy-MM-dd"),
    [string]$PortalUrl = "http://localhost:8090",
    [string]$Inbox = "\\fundlens-airflow\inbox"
)
$ErrorActionPreference = "Stop"
$robot = "C:\Program Files\UiPath\Studio\UiRobot.exe"
$project = Join-Path $PSScriptRoot "uipath\project.json"
$inputJson = @{ in_PortalUrl = $PortalUrl; in_AsOfDate = $AsOfDate; in_InboxFolder = $Inbox } | ConvertTo-Json -Compress

& $robot execute --file $project --input $inputJson
if ($LASTEXITCODE -ne 0) { throw "Le robot a échoué (code $LASTEXITCODE)" }

$files = Get-ChildItem -Path $Inbox -Filter "positions-*-$AsOfDate.json"
if ($files.Count -eq 0) { throw "Aucun relevé déposé pour le $AsOfDate" }
Write-Host "$($files.Count) relevé(s) déposé(s) pour le $AsOfDate"
