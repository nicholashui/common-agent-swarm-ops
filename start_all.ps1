<#
.SYNOPSIS
  Start the Common Agent Swarm Ops backend and frontend.

.DESCRIPTION
  Starts the FastAPI backend and Next.js frontend in development mode.
  The process wrapper PIDs are recorded in .run\servers.json so that
  stop_all.ps1 can terminate only the processes started by this script.

  Python dependencies must be installed for the backend, including uvicorn.
  Frontend dependencies must be installed under frontend\node_modules.

.PARAMETER BackendPort
  Backend listen port. Defaults to 8000.

.PARAMETER FrontendPort
  Frontend listen port. Defaults to 3001.

.PARAMETER PidFile
  State file written for stop_all.ps1. Defaults to .run\servers.json.

.EXAMPLE
  .\start_all.ps1
  .\start_all.ps1 -BackendPort 8100 -FrontendPort 3100
#>
[CmdletBinding()]
param(
  [ValidateRange(1, 65535)]
  [int]$BackendPort = 8000,

  [ValidateRange(1, 65535)]
  [int]$FrontendPort = 3001,

  [string]$PidFile = ""
)

$ErrorActionPreference = "Stop"
$Root = [System.IO.Path]::GetFullPath($PSScriptRoot)
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$RunDir = Join-Path $Root ".run"
$LogDir = Join-Path $RunDir "logs"

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

function Test-PortInUse {
  param(
    [Parameter(Mandatory = $true)]
    [int]$Port
  )

  try {
    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
    return $null -ne $listeners
  } catch {
    $listeners = netstat.exe -ano | Select-String -Pattern ":$Port\s+.*LISTENING"
    return $null -ne $listeners
  }
}

function Stop-ProcessTree {
  param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId
  )

  if ($ProcessId -le 0) {
    return
  }

  if ($null -ne (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)) {
    & taskkill.exe /PID $ProcessId /T /F *> $null
  }
}

if (-not $PidFile) {
  $PidFile = Join-Path $RunDir "servers.json"
} else {
  $PidFile = Resolve-ProjectPath -Path $PidFile -BasePath $Root
}

if (-not (Test-Path -LiteralPath $BackendDir -PathType Container)) {
  throw "Backend directory not found: $BackendDir"
}
if (-not (Test-Path -LiteralPath (Join-Path $BackendDir "app\main.py") -PathType Leaf)) {
  throw "Backend entry point not found: $BackendDir\app\main.py"
}
if (-not (Test-Path -LiteralPath (Join-Path $FrontendDir "package.json") -PathType Leaf)) {
  throw "Frontend package.json not found: $FrontendDir\package.json"
}
if (-not (Test-Path -LiteralPath (Join-Path $FrontendDir "node_modules") -PathType Container)) {
  throw "Frontend dependencies are not installed. Run npm install in $FrontendDir"
}

$pythonExecutable = Join-Path $BackendDir ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
  if ($null -eq $pythonCommand) {
    throw "Python was not found. Install Python 3.12+ or create backend\.venv."
  }
  $pythonExecutable = $pythonCommand.Source
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if ($null -eq $npmCommand) {
  throw "npm.cmd was not found. Install Node.js 20+ and ensure npm is on PATH."
}
$npmExecutable = $npmCommand.Source

$uvicornCheck = & $pythonExecutable -c "import uvicorn" 2>&1
if ($LASTEXITCODE -ne 0) {
  throw "uvicorn is not available to $pythonExecutable. Install the backend dependencies before starting the project."
}

if (Test-PortInUse -Port $BackendPort) {
  throw "Port $BackendPort is already in use. Run .\stop_all.ps1 or choose -BackendPort."
}
if (Test-PortInUse -Port $FrontendPort) {
  throw "Port $FrontendPort is already in use. Run .\stop_all.ps1 or choose -FrontendPort."
}
if (Test-Path -LiteralPath $PidFile -PathType Leaf) {
  throw "PID file already exists: $PidFile. Run .\stop_all.ps1 first, or remove a stale state file after confirming no project processes are running."
}

New-Item -ItemType Directory -Force -Path $RunDir, $LogDir | Out-Null

$backendOut = Join-Path $LogDir "backend.out.log"
$backendErr = Join-Path $LogDir "backend.err.log"
$frontendOut = Join-Path $LogDir "frontend.out.log"
$frontendErr = Join-Path $LogDir "frontend.err.log"
$backendProc = $null
$frontendProc = $null

# CASOPS_DEV_TRUST enables local trusted Host context so FE rewrites to /api/v1 work.
$backendCommand = "set PYTHONPATH=.&& set CASOPS_DEV_TRUST=1&& `"$pythonExecutable`" -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort"
$frontendCommand = "set BACKEND_API_ORIGIN=http://127.0.0.1:$BackendPort&& `"$npmExecutable`" run dev -- --hostname 127.0.0.1 --port $FrontendPort"

try {
  Write-Host "Starting backend on http://127.0.0.1:$BackendPort ..." -ForegroundColor Cyan
  $backendProc = Start-Process `
    -FilePath "cmd.exe" `
    -ArgumentList @("/d", "/c", $backendCommand) `
    -WorkingDirectory $BackendDir `
    -PassThru `
    -WindowStyle Minimized `
    -RedirectStandardOutput $backendOut `
    -RedirectStandardError $backendErr

  Write-Host "Starting frontend on http://127.0.0.1:$FrontendPort ..." -ForegroundColor Cyan
  $frontendProc = Start-Process `
    -FilePath "cmd.exe" `
    -ArgumentList @("/d", "/c", $frontendCommand) `
    -WorkingDirectory $FrontendDir `
    -PassThru `
    -WindowStyle Minimized `
    -RedirectStandardOutput $frontendOut `
    -RedirectStandardError $frontendErr

  Start-Sleep -Milliseconds 750
  foreach ($process in @($backendProc, $frontendProc)) {
    if ($null -eq (Get-Process -Id $process.Id -ErrorAction SilentlyContinue)) {
      throw "A project process exited during startup. Check the logs under $LogDir."
    }
  }

  $state = [ordered]@{
    schema_version = "1.0"
    started_at = (Get-Date).ToString("o")
    root = $Root
    pid_file = $PidFile
    mode = "development"
    backend = [ordered]@{
      name = "backend"
      pid = $backendProc.Id
      port = $BackendPort
      url = "http://127.0.0.1:$BackendPort"
      cwd = $BackendDir
      log_out = $backendOut
      log_err = $backendErr
      command = "python -m uvicorn app.main:app"
    }
    frontend = [ordered]@{
      name = "frontend"
      pid = $frontendProc.Id
      port = $FrontendPort
      url = "http://127.0.0.1:$FrontendPort"
      cwd = $FrontendDir
      log_out = $frontendOut
      log_err = $frontendErr
      command = "npm run dev"
    }
    pids = @($backendProc.Id, $frontendProc.Id)
  }

  $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $PidFile -Encoding utf8

  Write-Host ""
  Write-Host "Common Agent Swarm Ops started." -ForegroundColor Green
  Write-Host ("  Backend  PID {0,-8} http://127.0.0.1:{1}" -f $backendProc.Id, $BackendPort)
  Write-Host ("  Frontend PID {0,-8} http://127.0.0.1:{1}" -f $frontendProc.Id, $FrontendPort)
  Write-Host "  CASOPS_DEV_TRUST=1 (local Host trusted context)"
  Write-Host ("  BACKEND_API_ORIGIN=http://127.0.0.1:{0} (FE rewrite /api/v1 -> backend)" -f $BackendPort)
  Write-Host "  Logs:     $LogDir"
  Write-Host "  PID file: $PidFile"
  Write-Host ""
  Write-Host "Stop with: .\stop_all.ps1" -ForegroundColor Yellow
} catch {
  if ($null -ne $frontendProc) {
    Stop-ProcessTree -ProcessId $frontendProc.Id
  }
  if ($null -ne $backendProc) {
    Stop-ProcessTree -ProcessId $backendProc.Id
  }
  if (Test-Path -LiteralPath $PidFile -PathType Leaf) {
    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
  }
  throw
}
