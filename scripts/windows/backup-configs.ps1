<#
.SYNOPSIS
    Backup de configuraciones importantes del sistema
.DESCRIPTION
    Exporta configs de Git, Claude, VS Code, terminal, y otros tools.
    Crea un ZIP con todo para迁移 o restore.
#>

param(
    [string]$OutputPath = "$HOME\Documents\configs-backup-$(Get-Date -Format 'yyyy-MM-dd')"
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n=== CONFIG BACKUP ===" -ForegroundColor Magenta

# Crear directorio temporal
$tempDir = "$env:TEMP\config-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Definir configs a backup
$configs = @(
    # Git
    @{Name="git-config"; Source="$HOME\.gitconfig"},
    @{Name="git-credentials"; Source="$HOME\.git-credentials"},
    
    # Claude Code
    @{Name="claude-config"; Source="$HOME\.claude.json"},
    @{Name="claude-settings"; Source="$HOME\.claude\settings.json"},
    @{Name="claude-projects"; Source="$HOME\.claude\projects"},
    
    # MiMo Code
    @{Name="mimocode-config"; Source="$HOME\.config\mimocode"},
    
    # VS Code
    @{Name="vscode-settings"; Source="$HOME\.vscode\settings.json"},
    @{Name="vscode-keybindings"; Source="$HOME\.vscode\keybindings.json"},
    @{Name="vscode-extensions"; Source="$HOME\.vscode\extensions.txt"},
    
    # Terminal
    @{Name="pwsh-profile"; Source="$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"},
    @{Name="windows-terminal"; Source="$LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"},
    
    # Node/NPM
    @{Name="npmrc"; Source="$HOME\.npmrc"},
    
    # Python
    @{Name="pip-config"; Source="$HOME\pip\pip.conf"},
    
    # PowerShell
    @{Name="ps-readline"; Source="$HOME\.config\powershell\PSReadLine"},
    
    # SSH
    @{Name="ssh-config"; Source="$HOME\.ssh\config"},
    @{Name="ssh-known-hosts"; Source="$HOME\.ssh\known_hosts"},
    
    # Docker
    @{Name="docker-config"; Source="$HOME\.docker\config.json"},
    
    # WSL
    @{Name="wsl-config"; Source="$HOME\.wslconfig"},
    
    # Windows Terminal themes
    @{Name="wt-themes"; Source="$LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\themes.json"},
    
    # ZSH
    @{Name="zshrc"; Source="$HOME\.zshrc"},
    @{Name="zsh-aliases"; Source="$HOME\.zsh_aliases"},
    
    # Aider
    @{Name="aider-config"; Source="$HOME\.aider.conf.yml"},
    
    # OpenCode
    @{Name="opencode-config"; Source="$HOME\Downloads\opencode.json"}
)

$backed = 0
$failed = 0

foreach ($config in $configs) {
    $source = $config.Source
    $name = $config.Name
    
    if (Test-Path $source) {
        $dest = "$tempDir\$name"
        
        if ((Get-Item $source).PSIsContainer) {
            # Directorio
            Copy-Item $source -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            # Archivo
            New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
            Copy-Item $source -Destination $dest -Force -ErrorAction SilentlyContinue
        }
        
        Write-Host "[+] $name" -ForegroundColor Green
        $backed++
    } else {
        Write-Host "[-] $name (no encontrado)" -ForegroundColor Yellow
        $failed++
    }
}

# Crear ZIP
$zipPath = "$HOME\Documents\configs-backup-$(Get-Date -Format 'yyyy-MM-dd').zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

# Limpiar temporal
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n=== RESUMEN ===" -ForegroundColor Magenta
Write-Host "Backupeados: $backed" -ForegroundColor Green
Write-Host "No encontrados: $failed" -ForegroundColor Yellow
Write-Host "ZIP: $zipPath" -ForegroundColor Cyan
Write-Host "Tamaño: $([math]::Round((Get-Item $zipPath).Length / 1KB, 2)) KB" -ForegroundColor Gray
