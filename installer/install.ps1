# NovaDesc Windows Installer
# Run as Administrator in PowerShell

$ErrorActionPreference = "Stop"
$Version = "0.1.0"
$NovaDescDir = "$env:USERPROFILE\.novadesc"
$EnvFile = "$NovaDescDir\.env"

function Write-Log($msg) { Write-Host "[NovaDesc] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

function Test-DockerInstalled {
    try {
        $null = docker compose version 2>&1
        Write-Log "Docker OK"
    } catch {
        Write-Warn "Docker Desktop not found."
        Write-Log "Opening Docker Desktop download page..."
        Start-Process "https://www.docker.com/products/docker-desktop/"
        Write-Err "Please install Docker Desktop, then re-run this installer."
    }
}

function New-SecretKey {
    -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
}

function Invoke-Configure {
    if (-not (Test-Path $NovaDescDir)) {
        New-Item -ItemType Directory -Path $NovaDescDir | Out-Null
    }

    if (Test-Path $EnvFile) {
        Write-Warn "Existing config found. Skipping configuration."
        return
    }

    Write-Log "Configuring NovaDesc..."

    $AdminUser = Read-Host "  Admin username [admin]"
    if (-not $AdminUser) { $AdminUser = "admin" }

    $AdminPassSS = Read-Host "  Admin password" -AsSecureString
    $AdminPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($AdminPassSS)
    )
    if (-not $AdminPass) { Write-Err "Password cannot be empty" }

    $FrontendPort = Read-Host "  Frontend port [80]"
    if (-not $FrontendPort) { $FrontendPort = "80" }

    Write-Host ""
    Write-Host "  AI Provider:"
    Write-Host "  1) Ollama (local, recommended for air-gapped networks)"
    Write-Host "  2) Anthropic Claude (requires API key + internet)"
    $AiChoice = Read-Host "  Choose [1]"

    $AiProvider = "ollama"
    $AnthropicKey = ""

    if ($AiChoice -eq "2") {
        $AiProvider = "anthropic"
        $KeySS = Read-Host "  Anthropic API key" -AsSecureString
        $AnthropicKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($KeySS)
        )
    }

    $SecretKey = New-SecretKey
    $DbPass = New-SecretKey | ForEach-Object { $_.Substring(0, 24) }

    @"
# NovaDesc Configuration
APP_VERSION=$Version

POSTGRES_USER=novadesc
POSTGRES_PASSWORD=$DbPass
POSTGRES_DB=novadesc

SECRET_KEY=$SecretKey
FRONTEND_PORT=$FrontendPort

AI_PROVIDER=$AiProvider
OLLAMA_MODEL=llama3
ANTHROPIC_API_KEY=$AnthropicKey

ADMIN_USER=$AdminUser
ADMIN_PASS=$AdminPass
"@ | Out-File -FilePath $EnvFile -Encoding UTF8

    Write-Log "Config saved to $EnvFile"
}

function Start-NovaDesc {
    Write-Log "Starting NovaDesc..."
    $Env = Get-Content $EnvFile | ConvertFrom-StringData
    $ProfileFlag = if ($Env.AI_PROVIDER -eq "ollama") { "--profile with-ollama" } else { "" }

    $ComposeFile = Join-Path $NovaDescDir "docker-compose.yml"
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Copy-Item (Join-Path $ScriptDir "..\docker-compose.yml") $ComposeFile

    $cmd = "docker compose --env-file `"$EnvFile`" -f `"$ComposeFile`" $ProfileFlag up -d"
    Invoke-Expression $cmd

    $port = if ($Env.FRONTEND_PORT) { $Env.FRONTEND_PORT } else { "80" }
    Write-Log "NovaDesc is running at http://localhost:$port"
}

Write-Host ""
Write-Host "  NovaDesc — Maintenance & Repair Management System v$Version"
Write-Host ""

Test-DockerInstalled
Invoke-Configure
Start-NovaDesc
