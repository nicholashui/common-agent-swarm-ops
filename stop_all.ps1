<#
.SYNOPSIS
  Stop the Common Agent Swarm Ops backend and frontend.

.DESCRIPTION
  Reads the process wrapper PIDs written by start_all.ps1 and terminates
  each recorded Windows process tree. It does not kill arbitrary processes
  that happen to be listening on the application ports.

.PARAMETER PidFile
  State file written by start_all.ps1. Defaults to .run\servers.json.

.PARAMETER BackendPid
  Explicit backend wrapper PID. Useful when the state file is unavailable.

.PARAMETER FrontendPid
  Explicit frontend wrapper PID. Useful when the state file is unavailable.

.PARAMETER KeepPidFile
  Keep the state file after stopping the recorded processes.

.EXAMPLE
  .\stop_all.ps1
  .\stop_all.ps1 -PidFile .\.run\servers.json
  .\stop_all.ps1 -BackendPid 1234 -FrontendPid 5678
#>
[CmdletBinding()]
param(
  [string]$PidFile = "",

  [ValidateRange(0, 2147483647)]
  [int]$BackendPid = 0,

  [ValidateRange(0, 2147483647)]
  [int]$FrontendPid = 0,

  [switch]$KeepPidFile
)

$ErrorActionPreference = "Continue"
$Root = [System.IO.Path]::GetFullPath($PSScriptRoot)
$DefaultPidFile = Join-Path $Root ".run\servers.json"

function Resolve-ProjectPath {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Path,

    [Parameter(Mandatory = $true)]
    [string]$BasePath
  )

  if ([System.IO.Path]::IsPathRooted($Path)) {
    return [System.IO.Path]::GetFullPath($Path)
  }

  return [System.IO.Path]::GetFullPath((Join-Path $BasePath $Path))
}

function Stop-ProcessTree {
  param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId
  )

  if ($ProcessId -le 0) {
    return $true
  }

  $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  if ($null -eq $process) {
    Write-Host "  PID $ProcessId is already stopped."
    return $true
  }

  Write-Host "  Stopping PID $ProcessId ($($process.ProcessName))..."
  & taskkill.exe /PID $ProcessId /T /F *> $null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "  Stopped process tree PID $ProcessId" -ForegroundColor Green
    return $true
  }

  try {
    Stop-Process -Id $ProcessId -Force -ErrorAction Stop
    Write-Host "  Stopped PID $ProcessId" -ForegroundColor Yellow
    return $true
  } catch {
    Write-Warning "  Failed to stop PID ${ProcessId}: $_"
    return $false
  }
}

if (-not $PidFile) {
  $PidFile = $DefaultPidFile
} else {
  $PidFile = Resolve-ProjectPath -Path $PidFile -BasePath $Root
}

$processIds = New-Object System.Collections.Generic.List[int]
if ($BackendPid -gt 0) {
  $processIds.Add($BackendPid) | Out-Null
}
if ($FrontendPid -gt 0) {
  $processIds.Add($FrontendPid) | Out-Null
}

if ($processIds.Count -eq 0 -and (Test-Path -LiteralPath $PidFile -PathType Leaf)) {
  try {
    $state = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
  } catch {
    Write-Error "Failed to parse PID file '$PidFile': $_"
    exit 1
  }

  foreach ($processId in @($state.pids, $state.backend.pid, $state.frontend.pid)) {
    if ($null -ne $processId) {
      $id = [int]$processId
      if ($id -gt 0 -and -not $processIds.Contains($id)) {
        $processIds.Add($id) | Out-Null
      }
    }
  }

  Write-Host "Loaded process state from $PidFile"
}

if ($processIds.Count -eq 0) {
  Write-Host "No Common Agent Swarm Ops processes are recorded as running."
  exit 0
}

$failed = 0
Write-Host "Stopping Common Agent Swarm Ops..." -ForegroundColor Yellow
foreach ($processId in ($processIds | Select-Object -Unique)) {
  if (-not (Stop-ProcessTree -ProcessId $processId)) {
    $failed++
  }
}

if ((Test-Path -LiteralPath $PidFile -PathType Leaf) -and -not $KeepPidFile) {
  Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
  Write-Host "Removed PID file: $PidFile"
}

if ($failed -gt 0) {
  Write-Host "Completed with $failed failure(s)." -ForegroundColor Yellow
  exit 1
}

Write-Host "All recorded project processes stopped." -ForegroundColor Green
exit 0
