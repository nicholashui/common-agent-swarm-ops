<#
.SYNOPSIS
  Stop the Common Agent Swarm Ops backend and frontend.

.DESCRIPTION
  Stops project processes in this order:
  1. PIDs recorded by start_all.ps1 in .run\servers.json (wrapper trees)
  2. Any process still LISTENING on the configured backend/frontend ports
     (covers servers started outside start_all.ps1, orphaned node/uvicorn, etc.)

  Default ports match start_all.ps1: backend 8000, frontend 3001.
  Also clears a stale .run\servers.json unless -KeepPidFile is set.

.PARAMETER PidFile
  State file written by start_all.ps1. Defaults to .run\servers.json.

.PARAMETER BackendPort
  Backend listen port to free. Defaults to 8000.

.PARAMETER FrontendPort
  Frontend listen port to free. Defaults to 3001.

.PARAMETER BackendPid
  Explicit backend wrapper PID.

.PARAMETER FrontendPid
  Explicit frontend wrapper PID.

.PARAMETER KeepPidFile
  Keep the state file after stopping.

.PARAMETER SkipPortSweep
  Only stop recorded/explicit PIDs; do not kill by listen port.

.EXAMPLE
  .\stop_all.ps1
  .\stop_all.ps1 -FrontendPort 3001 -BackendPort 8000
  .\stop_all.ps1 -BackendPid 1234 -FrontendPid 5678
#>
[CmdletBinding()]
param(
  [string]$PidFile = "",

  [ValidateRange(1, 65535)]
  [int]$BackendPort = 8000,

  [ValidateRange(1, 65535)]
  [int]$FrontendPort = 3001,

  [ValidateRange(0, 2147483647)]
  [int]$BackendPid = 0,

  [ValidateRange(0, 2147483647)]
  [int]$FrontendPid = 0,

  [switch]$KeepPidFile,

  [switch]$SkipPortSweep
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

function Get-ListeningPids {
  param([Parameter(Mandatory = $true)][int]$Port)

  $ids = New-Object System.Collections.Generic.List[int]
  try {
    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
    foreach ($row in @($listeners)) {
      $id = [int]$row.OwningProcess
      if ($id -gt 0 -and -not $ids.Contains($id)) {
        $ids.Add($id) | Out-Null
      }
    }
  } catch {
    # Fallback when Get-NetTCPConnection is unavailable
    $matches = netstat.exe -ano | Select-String -Pattern ":$Port\s+.*LISTENING\s+(\d+)\s*$"
    foreach ($match in $matches) {
      $id = 0
      if ([int]::TryParse($match.Matches[0].Groups[1].Value, [ref]$id) -and $id -gt 0) {
        if (-not $ids.Contains($id)) {
          $ids.Add($id) | Out-Null
        }
      }
    }
  }
  return $ids
}

function Stop-ProcessTree {
  param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId,
    [string]$Reason = ""
  )

  if ($ProcessId -le 0) {
    return $true
  }

  $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
  if ($null -eq $process) {
    Write-Host "  PID $ProcessId is already stopped."
    return $true
  }

  $suffix = if ($Reason) { " — $Reason" } else { "" }
  Write-Host "  Stopping PID $ProcessId ($($process.ProcessName))$suffix..."
  & taskkill.exe /PID $ProcessId /T /F *> $null
  Start-Sleep -Milliseconds 200

  if ($null -eq (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)) {
    Write-Host "  Stopped process tree PID $ProcessId" -ForegroundColor Green
    return $true
  }

  try {
    Stop-Process -Id $ProcessId -Force -ErrorAction Stop
    Start-Sleep -Milliseconds 150
    if ($null -eq (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)) {
      Write-Host "  Stopped PID $ProcessId" -ForegroundColor Yellow
      return $true
    }
  } catch {
    # fall through
  }

  Write-Warning "  Failed to stop PID ${ProcessId}"
  return $false
}

function Add-UniquePid {
  param(
    [Parameter(Mandatory = $true)]
    [AllowEmptyCollection()]
    [System.Collections.Generic.List[int]]$List,

    [Parameter(Mandatory = $true)]
    [System.Collections.Generic.Dictionary[int, string]]$Reasons,

    [int]$ProcessId,
    [string]$Reason
  )
  if ($null -eq $List -or $ProcessId -le 0) { return }
  if (-not $List.Contains($ProcessId)) {
    [void]$List.Add($ProcessId)
  }
  if (-not $Reasons.ContainsKey($ProcessId)) {
    $Reasons[$ProcessId] = $Reason
  } elseif ($Reason -and $Reasons[$ProcessId] -notlike "*$Reason*") {
    $Reasons[$ProcessId] = "$($Reasons[$ProcessId]); $Reason"
  }
}

if (-not $PidFile) {
  $PidFile = $DefaultPidFile
} else {
  $PidFile = Resolve-ProjectPath -Path $PidFile -BasePath $Root
}

$processIds = New-Object System.Collections.Generic.List[int]
$reasons = New-Object 'System.Collections.Generic.Dictionary[int,string]'

if ($BackendPid -gt 0) {
  Add-UniquePid -List $processIds -Reasons $reasons -ProcessId $BackendPid -Reason "explicit -BackendPid"
}
if ($FrontendPid -gt 0) {
  Add-UniquePid -List $processIds -Reasons $reasons -ProcessId $FrontendPid -Reason "explicit -FrontendPid"
}

$portsFromState = New-Object System.Collections.Generic.List[int]
if ($processIds.Count -eq 0 -or (Test-Path -LiteralPath $PidFile -PathType Leaf)) {
  if (Test-Path -LiteralPath $PidFile -PathType Leaf) {
    try {
      $state = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
      Write-Host "Loaded process state from $PidFile"

      foreach ($processId in @($state.pids)) {
        if ($null -ne $processId) {
          Add-UniquePid -List $processIds -Reasons $reasons -ProcessId ([int]$processId) -Reason "servers.json pids"
        }
      }
      if ($null -ne $state.backend.pid) {
        Add-UniquePid -List $processIds -Reasons $reasons -ProcessId ([int]$state.backend.pid) -Reason "servers.json backend"
      }
      if ($null -ne $state.frontend.pid) {
        Add-UniquePid -List $processIds -Reasons $reasons -ProcessId ([int]$state.frontend.pid) -Reason "servers.json frontend"
      }
      if ($null -ne $state.backend.port) {
        $portsFromState.Add([int]$state.backend.port) | Out-Null
      }
      if ($null -ne $state.frontend.port) {
        $portsFromState.Add([int]$state.frontend.port) | Out-Null
      }
    } catch {
      Write-Warning "Failed to parse PID file '$PidFile': $_"
    }
  }
}

# Always free default (or requested) app ports unless skipped — this is what
# makes stop work when servers were started without start_all.ps1.
$portsToSweep = New-Object System.Collections.Generic.List[int]
if (-not $SkipPortSweep) {
  foreach ($port in @($BackendPort, $FrontendPort) + @($portsFromState)) {
    if ($port -gt 0 -and -not $portsToSweep.Contains($port)) {
      $portsToSweep.Add($port) | Out-Null
    }
  }
  foreach ($port in $portsToSweep) {
    foreach ($listenPid in (Get-ListeningPids -Port $port)) {
      Add-UniquePid -List $processIds -Reasons $reasons -ProcessId $listenPid -Reason "listening on port $port"
    }
  }
}

if ($processIds.Count -eq 0) {
  Write-Host "No Common Agent Swarm Ops processes found (no PID file, no listeners on ports $($portsToSweep -join ', '))." -ForegroundColor Yellow
  if ((Test-Path -LiteralPath $PidFile -PathType Leaf) -and -not $KeepPidFile) {
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Removed stale PID file: $PidFile"
  }
  exit 0
}

$failed = 0
Write-Host "Stopping Common Agent Swarm Ops..." -ForegroundColor Yellow
foreach ($processId in ($processIds | Select-Object -Unique)) {
  $reason = if ($reasons.ContainsKey($processId)) { $reasons[$processId] } else { "" }
  if (-not (Stop-ProcessTree -ProcessId $processId -Reason $reason)) {
    $failed++
  }
}

# Second pass: ports often rebind to child PIDs that outlive the wrapper cmd.exe
if (-not $SkipPortSweep) {
  Start-Sleep -Milliseconds 400
  foreach ($port in $portsToSweep) {
    foreach ($listenPid in (Get-ListeningPids -Port $port)) {
      Write-Host "  Port $port still held by PID $listenPid — retrying..." -ForegroundColor Yellow
      if (-not (Stop-ProcessTree -ProcessId $listenPid -Reason "port $port still listening")) {
        $failed++
      }
    }
  }
}

if ((Test-Path -LiteralPath $PidFile -PathType Leaf) -and -not $KeepPidFile) {
  Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
  Write-Host "Removed PID file: $PidFile"
}

# Final port report
if (-not $SkipPortSweep) {
  $stillOpen = @()
  foreach ($port in $portsToSweep) {
    $left = @(Get-ListeningPids -Port $port)
    if ($left.Count -gt 0) {
      $stillOpen += "port $port (PIDs: $($left -join ', '))"
    }
  }
  if ($stillOpen.Count -gt 0) {
    Write-Host "Still listening: $($stillOpen -join '; ')" -ForegroundColor Red
    $failed++
  } else {
    Write-Host "Ports free: $($portsToSweep -join ', ')" -ForegroundColor Green
  }
}

if ($failed -gt 0) {
  Write-Host "Completed with $failed failure(s)." -ForegroundColor Yellow
  exit 1
}

Write-Host "All project processes stopped." -ForegroundColor Green
exit 0
