# Nile Key Developer Toolkit v2
# One-click startup and shutdown for Manual UAT
# Uses absolute executable paths - NO PATH dependency

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "status", "help")]
    [string]$Command = "help"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$LogFile = Join-Path $ProjectRoot "tools\nile-key.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    Write-Host $logEntry
}

function Start-Backend {
    Write-Log "Starting Backend Server..."
    
    # Use absolute path to venv Python
    $venvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
    
    if (-not (Test-Path $venvPython)) {
        # Fallback: try system python
        $venvPython = "python"
        Write-Log "WARNING: venv Python not found, using system python"
    }
    
    Write-Log "Starting uvicorn using: $venvPython -m uvicorn"
    
    # Use cmd /k to keep terminal open, run from backend directory
    $cmd = "cd /d `"$BackendDir`" && `"$venvPython`" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $cmd -WindowStyle Normal
    
    $maxAttempts = 30
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Log "Backend health check PASSED"
                return $true
            }
        } catch {
            # Server not ready yet
        }
        Start-Sleep -Seconds 1
        $attempt++
    }
    
    Write-Log "Backend failed to start within $maxAttempts seconds"
    return $false
}

function Start-Frontend {
    Write-Log "Starting Frontend Server..."
    
    # Find npm.cmd
    $npmPath = Join-Path $env:ProgramFiles "nodejs\node_modules\npm\bin\npm.cmd"
    if (-not (Test-Path $npmPath)) {
        $npmPath = "npm.cmd"
    }
    
    if (-not (Test-Path "node_modules")) {
        Write-Log "Installing frontend dependencies..."
        cmd /c "`"$npmPath`" install"
    }
    
    Write-Log "Starting Vite dev server on http://localhost:3000..."
    
    # Use cmd /k to keep terminal open, run from frontend directory
    $cmd = "cd /d `"$FrontendDir`" && `"$npmPath`" run dev"
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", $cmd -WindowStyle Normal
    
    Start-Sleep -Seconds 3
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
        Write-Log "Frontend server started successfully"
        return $true
    } catch {
        Write-Log "Frontend may still be initializing..."
        return $true
    }
}

function Open-Browser {
    Write-Log "Opening browser..."
    
    Start-Process "http://localhost:8000/health"
    Start-Sleep -Milliseconds 500
    Start-Process "http://localhost:3000"
    
    Write-Log "Browser opened - Backend: http://localhost:8000, Frontend: http://localhost:3000"
}

function Show-Ready {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  NILE KEY - DEVELOPMENT ENVIRONMENT" -ForegroundColor Green
    Write-Host "  READY FOR MANUAL UAT" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  Health: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Use 'tools\stop-all.bat' to stop servers" -ForegroundColor Yellow
    Write-Host ""
}

function Stop-Servers {
    Write-Log "Stopping all servers..."
    
    # Kill by port
    Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object {
        $pid = $_.OwningProcess
        if ($pid) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
    }
    
    Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object {
        $pid = $_.OwningProcess
        if ($pid) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
    }
    
    # Also try process name matching
    Get-Process -Name "uvicorn" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    
    Write-Log "All servers stopped"
    Write-Host "All development servers stopped." -ForegroundColor Yellow
}

function Show-Status {
    $backendRunning = $false
    $frontendRunning = $false
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $backendRunning = $true
        }
    } catch {}
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendRunning = $true
        }
    } catch {}
    
    Write-Host "Nile Key Development Environment Status:" -ForegroundColor Cyan
    Write-Host "  Backend (http://localhost:8000): " -NoNewline
    if ($backendRunning) {
        Write-Host "RUNNING" -ForegroundColor Green
    } else {
        Write-Host "STOPPED" -ForegroundColor Red
    }
    
    Write-Host "  Frontend (http://localhost:3000): " -NoNewline
    if ($frontendRunning) {
        Write-Host "RUNNING" -ForegroundColor Green
    } else {
        Write-Host "STOPPED" -ForegroundColor Red
    }
}

function Show-Help {
    Write-Host "Nile Key Developer Toolkit v2"
    Write-Host ""
    Write-Host "Usage: .\NileKeyToolkit.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  start    - Start backend and frontend, open browser"
    Write-Host "  stop     - Stop all development servers"
    Write-Host "  status   - Check if servers are running"
    Write-Host "  help     - Show this help message"
}

# Main execution
switch ($Command) {
    "start" {
        Write-Log "=== Nile Key Developer Toolkit v2 Started ==="
        
        $backendOk = Start-Backend
        if (-not $backendOk) {
            Write-Host "ERROR: Backend failed to start. Check $LogFile for details." -ForegroundColor Red
            exit 1
        }
        
        $frontendOk = Start-Frontend
        if (-not $frontendOk) {
            Write-Log "WARNING: Frontend may not have started properly"
        }
        
        Open-Browser
        Show-Ready
    }
    "stop" {
        Stop-Servers
    }
    "status" {
        Show-Status
    }
    "help" {
        Show-Help
    }
}