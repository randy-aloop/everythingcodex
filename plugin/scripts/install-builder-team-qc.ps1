[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRoot,

    [string]$PluginRoot = "",

    [string]$Python = "python",

    [string]$ExpectedVersion = "0.2.1-trial",

    [switch]$AllowVersionMismatch,

    [switch]$DryRun,

    [switch]$SkipProjectPluginCopy,

    [switch]$SkipQcInit,

    [switch]$ForceTemplates,

    [switch]$UpgradeFromPrototype,

    [switch]$ValidateInstalled,

    [switch]$WriteInstallReport,

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

function Copy-BundleDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        throw "Missing plugin bundle directory: $Source"
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    & robocopy $Source $Destination /E /COPY:DAT /DCOPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    $copyExitCode = $LASTEXITCODE
    if ($copyExitCode -gt 7) {
        throw "robocopy failed copying $Source to $Destination with exit code $copyExitCode"
    }
    $global:LASTEXITCODE = 0
}

function Assert-FileContains {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Needle,
        [Parameter(Mandatory = $true)][string]$Description
    )

    $path = Join-Path $Root $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "$Description is missing required file: $RelativePath"
    }

    $text = Get-Content -Raw -LiteralPath $path
    if (-not $text.Contains($Needle)) {
        throw "$Description missing expected marker in ${RelativePath}: $Needle"
    }
}

function Test-PluginShape {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [string]$ExpectedVersion = "",
        [switch]$AllowVersionMismatch
    )

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

    $trialRequired = @(
        "scripts\audit_builder_scope.py",
        "scripts\record_decision.py",
        "scripts\record_gate_decision.py",
        "scripts\record_ponytail_check.py",
        "scripts\record_test_result.py",
        "scripts\validate_phase_record.py",
        "docs\0.2.0-trial\hardening-implementation-report.md",
        "docs\phase-by-phase-run-plan.md",
        "docs\qc-record-schema.md",
        "assets\qc-templates\phase-board.json",
        "skills\phase-controller\SKILL.md",
        "skills\ponytail-adapter\SKILL.md"
    )

    foreach ($item in $trialRequired) {
        $path = Join-Path $Root $item
        if (-not (Test-Path -LiteralPath $path)) {
            throw "0.2.0-trial package is missing required item: $item"
        }
    }

    $manifestPath = Join-Path $Root ".codex-plugin\plugin.json"
    $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
    if ($manifest.name -ne "builder-team-qc") {
        throw "Unexpected plugin manifest name: $($manifest.name)"
    }
    if ($ExpectedVersion -and $manifest.version -ne $ExpectedVersion -and -not $AllowVersionMismatch) {
        throw "Unexpected plugin manifest version: $($manifest.version). Expected: $ExpectedVersion"
    }

    if ($ExpectedVersion -eq "0.2.1-trial" -or $manifest.version -eq "0.2.1-trial") {
        $patchRequired = @(
            "scripts\install-builder-team-qc-0.2.1-trial.ps1",
            "docs\docs-v03-sync-to-code-expanded-version-record-CORRECTED.md",
            "docs\0.2.0-trial\backups\DOC-V03-SYNC-TO-CODE-EXPANDED-20260625\manifest.json",
            "docs\0.2.0-trial\backups\DOC-V03-SYNC-TO-CODE-EXPANDED-20260625\README.md"
        )

        foreach ($item in $patchRequired) {
            $path = Join-Path $Root $item
            if (-not (Test-Path -LiteralPath $path)) {
                throw "0.2.1-trial package is missing required patch item: $item"
            }
        }

        $v31Docs = @(
            "docs\multi-agent-modes.md",
            "docs\phase-loop.md",
            "docs\qc-record-schema.md",
            "docs\orchestration-notes.md"
        )
        foreach ($doc in $v31Docs) {
            Assert-FileContains -Root $Root -RelativePath $doc -Needle "Version: V03.1" -Description "0.2.1-trial docs patch marker"
        }
        Assert-FileContains -Root $Root -RelativePath "docs\CHANGELOG.md" -Needle "0.2.0-trial docs V03.1 sync-to-code" -Description "0.2.1-trial changelog marker"
        Assert-FileContains -Root $Root -RelativePath "docs\docs-v03-sync-to-code-expanded-version-record-CORRECTED.md" -Needle 'Status | `Executed`' -Description "0.2.1-trial executed patch record"
        Assert-FileContains -Root $Root -RelativePath "docs\0.2.0-trial\backups\DOC-V03-SYNC-TO-CODE-EXPANDED-20260625\manifest.json" -Needle "git_baseline_everythingcodex_files" -Description "0.2.1-trial recovery-pack manifest"
    }
    return $manifest
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
$InstallReportPath = Join-Path $ProjectPluginRoot "install-report.json"

Write-Step "Plugin root: $PluginRoot"
Write-Step "Target root: $TargetRoot"

$manifest = Test-PluginShape -Root $PluginRoot -ExpectedVersion $ExpectedVersion -AllowVersionMismatch:$AllowVersionMismatch
Write-Step "Source manifest version: $($manifest.version)"

$effectiveSkipQcInit = $SkipQcInit.IsPresent
if ($UpgradeFromPrototype) {
    Write-Step "Prototype upgrade mode enabled."
    if ($ForceTemplates -and -not $SkipQcInit) {
        throw "UpgradeFromPrototype refuses -ForceTemplates unless -SkipQcInit is also supplied. Preserve existing .qc evidence by default."
    }
    if (Test-Path -LiteralPath $QcRoot) {
        $effectiveSkipQcInit = $true
        Write-Step "Existing .qc found; preserving QC records and skipping initialization."
    }
}

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
            $destination = Join-Path $ProjectPluginRoot $item
            Copy-BundleDirectory -Source $source -Destination $destination
        }
        Write-Step "Copied project-local plugin bundle to $ProjectPluginRoot"
    }
}
else {
    Write-Step "Skipped project-local plugin copy."
}

if (-not $effectiveSkipQcInit) {
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

if ($ValidateInstalled -and -not $SkipProjectPluginCopy) {
    if ($DryRun) {
        Write-Step "Dry run: would validate installed plugin bundle at $ProjectPluginRoot"
    }
    else {
        $installedManifest = Test-PluginShape -Root $ProjectPluginRoot -ExpectedVersion $ExpectedVersion -AllowVersionMismatch:$AllowVersionMismatch
        Write-Step "Installed manifest version: $($installedManifest.version)"
        Invoke-BuilderPython -ScriptPath (Join-Path $ProjectPluginRoot "scripts\validate_phase_record.py") -Arguments @(
            "--root", $TargetRoot,
            "--template-only",
            "--json"
        )
    }
}

if ($WriteInstallReport) {
    if ($DryRun) {
        Write-Step "Dry run: would write install report to $InstallReportPath"
    }
    else {
        $report = [ordered]@{
            schema_version = "1.0"
            plugin_name = "builder-team-qc"
            installed_version = $manifest.version
            expected_version = $ExpectedVersion
            target_root = $TargetRoot
            project_plugin_root = $ProjectPluginRoot
            qc_root = $QcRoot
            qc_preserved = $effectiveSkipQcInit
            upgrade_from_prototype = $UpgradeFromPrototype.IsPresent
            validate_installed = $ValidateInstalled.IsPresent
            timestamp = (Get-Date).ToString("o")
        }
        $report | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $InstallReportPath -Encoding UTF8
        Write-Step "Wrote install report to $InstallReportPath"
    }
}

Write-Step "Install method complete."
Write-Host ""
Write-Host "Project-local plugin path: $ProjectPluginRoot"
Write-Host "Project-local QC path:     $QcRoot"
Write-Host ""
Write-Host "Next command:"
Write-Host "  & '$Python' '$ProjectPluginRoot\scripts\validate_phase_record.py' --root '$TargetRoot' --template-only --json"
