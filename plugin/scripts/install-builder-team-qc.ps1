[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRoot,

    [string]$PluginRoot = "",

    [string]$Python = "python",

    [switch]$DryRun,

    [switch]$SkipProjectPluginCopy,

    [switch]$SkipQcInit,

    [switch]$ForceTemplates,

    [switch]$StartPhase,

    [string]$PhaseId = "phase-000",

    [string]$PhaseTitle = "Intake And Phase Selection",

    [string]$NextPhaseId = "",

    [string]$BuildPlan = ""
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Assert-ChildPath {
    param(
        [Parameter(Mandatory = $true)][string]$Child,
        [Parameter(Mandatory = $true)][string]$Parent,
        [Parameter(Mandatory = $true)][string]$Description
    )

    $childFull = Resolve-FullPath $Child
    $parentFull = (Resolve-FullPath $Parent).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $childFull.StartsWith($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Description resolved outside the target root: $childFull"
    }
}

function Write-Step {
    param([Parameter(Mandatory = $true)][string]$Message)
    Write-Host "[builder-team-qc] $Message"
}

function Test-PluginShape {
    param([Parameter(Mandatory = $true)][string]$Root)

    $required = @(
        ".codex-plugin\plugin.json",
        "assets",
        "docs",
        "scripts",
        "skills"
    )

    foreach ($item in $required) {
        $path = Join-Path $Root $item
        if (-not (Test-Path -LiteralPath $path)) {
            throw "Plugin root is missing required item: $item"
        }
    }

    $manifestPath = Join-Path $Root ".codex-plugin\plugin.json"
    $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    if ($manifest.name -ne "builder-team-qc") {
        throw "Unexpected plugin manifest name: $($manifest.name)"
    }
}

function Invoke-BuilderPython {
    param(
        [Parameter(Mandatory = $true)][string]$ScriptPath,
        [string[]]$Arguments = @()
    )

    $allArgs = @($ScriptPath) + $Arguments
    Write-Step ("python " + ($allArgs -join " "))
    & $Python @allArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Python helper failed with exit code $LASTEXITCODE"
    }
}

if ([string]::IsNullOrWhiteSpace($PluginRoot)) {
    $PluginRoot = Join-Path $PSScriptRoot ".."
}

$PluginRoot = Resolve-FullPath $PluginRoot
$TargetRoot = Resolve-FullPath $TargetRoot
$ProjectPluginRoot = Join-Path $TargetRoot ".codex\plugins\builder-team-qc"
$QcRoot = Join-Path $TargetRoot ".qc"

Write-Step "Plugin root: $PluginRoot"
Write-Step "Target root: $TargetRoot"

Test-PluginShape -Root $PluginRoot

if (-not $DryRun) {
    New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
}
else {
    Write-Step "Dry run: target directory would be created if missing."
}

if (-not $SkipProjectPluginCopy) {
    Assert-ChildPath -Child $ProjectPluginRoot -Parent $TargetRoot -Description "Project-local plugin install path"
    $copyItems = @(".codex-plugin", "assets", "docs", "scripts", "skills")

    if ($DryRun) {
        Write-Step "Dry run: would copy plugin bundle to $ProjectPluginRoot"
    }
    else {
        New-Item -ItemType Directory -Force -Path $ProjectPluginRoot | Out-Null
        foreach ($item in $copyItems) {
            $source = Join-Path $PluginRoot $item
            Copy-Item -LiteralPath $source -Destination $ProjectPluginRoot -Recurse -Force
        }
        Write-Step "Copied project-local plugin bundle to $ProjectPluginRoot"
    }
}
else {
    Write-Step "Skipped project-local plugin copy."
}

if (-not $SkipQcInit) {
    $initArgs = @("--root", $TargetRoot)
    if ($DryRun) { $initArgs += "--dry-run" }
    if ($ForceTemplates) { $initArgs += "--force-templates" }
    Invoke-BuilderPython -ScriptPath (Join-Path $PluginRoot "scripts\init_qc.py") -Arguments $initArgs
}
else {
    Write-Step "Skipped .qc initialization."
}

if ($StartPhase) {
    $phaseArgs = @(
        "--root", $TargetRoot,
        "--phase-id", $PhaseId,
        "--title", $PhaseTitle
    )
    if ($NextPhaseId) {
        $phaseArgs += @("--next-phase-id", $NextPhaseId)
    }
    if ($BuildPlan) {
        $phaseArgs += @("--build-plan", (Resolve-FullPath $BuildPlan))
    }
    if ($DryRun) {
        $phaseArgs += "--dry-run"
    }
    Invoke-BuilderPython -ScriptPath (Join-Path $PluginRoot "scripts\start_phase.py") -Arguments $phaseArgs
}

Write-Step "Install method complete."
Write-Host ""
Write-Host "Project-local plugin path: $ProjectPluginRoot"
Write-Host "Project-local QC path:     $QcRoot"
Write-Host ""
Write-Host "Next command:"
Write-Host "  & '$Python' '$PluginRoot\scripts\validate_phase_record.py' --root '$TargetRoot' --template-only --json"
