<#
.SYNOPSIS
  Publie compliance-service sur IIS (Windows Server ou runner GitHub windows-latest) puis vérifie /health.
.EXAMPLE
  ./deploy/deploy-iis.ps1 -SiteName FundLensCompliance -Port 8085
#>
param(
    [string]$SiteName = "FundLensCompliance",
    [int]$Port = 8085,
    [string]$PublishDir = "C:\inetpub\fundlens-compliance"
)
$ErrorActionPreference = "Stop"

Import-Module WebAdministration -ErrorAction SilentlyContinue
if (-not (Get-Module WebAdministration)) {
    Install-WindowsFeature -Name Web-Server, Web-Mgmt-Tools | Out-Null
    Import-Module WebAdministration
}

Write-Host "Publication de l'application dans $PublishDir"
dotnet publish "$PSScriptRoot\..\src\Compliance\Compliance.csproj" -c Release -o $PublishDir

$poolName = "$SiteName-pool"
if (-not (Test-Path "IIS:\AppPools\$poolName")) {
    New-WebAppPool -Name $poolName | Out-Null
    Set-ItemProperty "IIS:\AppPools\$poolName" -Name managedRuntimeVersion -Value ""
}
if (Get-Website -Name $SiteName) { Remove-Website -Name $SiteName }
New-Website -Name $SiteName -Port $Port -PhysicalPath $PublishDir -ApplicationPool $poolName | Out-Null
Start-Website -Name $SiteName

$health = Invoke-RestMethod -Uri "http://localhost:$Port/health" -TimeoutSec 30
if ($health.status -ne "UP") { throw "Le service ne répond pas correctement : $health" }
Write-Host "compliance-service publié sur IIS : http://localhost:$Port"
