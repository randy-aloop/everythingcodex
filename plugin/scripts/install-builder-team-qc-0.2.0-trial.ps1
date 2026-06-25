[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRoot,

    [string]$PluginRoot = "",

    [string]$Python = "python",

    [switch]$DryRun,

    [switch]$FreshInstall,

    [switch]$StartPhase,

    [string]$PhaseId = "phase-000",

    [string]$PhaseTitle = "Intake And Phase Selection",

    [string]$NextPhaseId = "",

    [string]$BuildPlan = "",

    [switch]$WriteInstallReport
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Write-Step {
    param([Parameter(Mandatory = $true)][string]$Message)
    Write-Host "[builder-team-qc 0.2.0-trial] $Message"
}

if ([string]::IsNullOrWhiteSpace($PluginRoot)) {
    $PluginRoot = Join-Path $PSScriptRoot ".."
}

$PluginRoot = Resolve-FullPath $PluginRoot
$TargetRoot = Resolve-FullPath $TargetRoot
$Installer = Join-Path $PluginRoot "scripts\install-builder-team-qc.ps1"
$QcRoot = Join-Path $TargetRoot ".qc"

if (-not (Test-Path -LiteralPath $Installer)) {
    throw "Missing canonical installer: $Installer"
}

Write-Step "Plugin root: $PluginRoot"
Write-Step "Target root: $TargetRoot"

$installerArgs = @{
    TargetRoot = $TargetRoot
    PluginRoot = $PluginRoot
    Python = $Python
    ExpectedVersion = "0.2.0-trial"
    ValidateInstalled = $true
}

if ($DryRun) {
    $installerArgs.DryRun = $true
}

if ($WriteInstallReport) {
    $installerArgs.WriteInstallReport = $true
}

if (-not $FreshInstall) {
    $installerArgs.SkipQcInit = $true
    $installerArgs.UpgradeFromPrototype = $true
    Write-Step "Upgrade mode: preserving existing .qc records by default."
}
else {
    Write-Step "Fresh-install mode: .qc initialization is allowed."
}

if (-not $FreshInstall -and -not (Test-Path -LiteralPath $QcRoot)) {
    Write-Step "No existing .qc folder found. Use -FreshInstall if this target has not been initialized yet."
}

if ($StartPhase) {
    $installerArgs.StartPhase = $true
    $installerArgs.PhaseId = $PhaseId
    $installerArgs.PhaseTitle = $PhaseTitle
    if ($NextPhaseId) {
        $installerArgs.NextPhaseId = $NextPhaseId
    }
    if ($BuildPlan) {
        $installerArgs.BuildPlan = Resolve-FullPath $BuildPlan
    }
}

& $Installer @installerArgs
if ($LASTEXITCODE -ne 0) {
    throw "0.2.0-trial installer failed with exit code $LASTEXITCODE"
}
