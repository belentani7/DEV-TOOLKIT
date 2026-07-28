#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Limpieza profunda Windows 11
.DESCRIPTION
    Elimina archivos temporales, cache, logs, y optimiza el sistema.
    Basado en mejores prácticas de Microsoft y comunidad.
.NOTES
    Ejecutar como Administrador
#>

param(
    [switch]$DryRun,
    [switch]$Aggressive
)

$ErrorActionPreference = "SilentlyContinue"
$freed = 0

function Write-Status($msg) { Write-Host "[*] $msg" -ForegroundColor Cyan }
function Write-OK($msg) { Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Skip($msg) { Write-Host "[-] $msg" -ForegroundColor Yellow }

Write-Host "`n=== WINDOWS 11 DEEP CLEANUP ===" -ForegroundColor Magenta
Write-Host "Modo: $(if($DryRun){'DRY RUN'}else{'LIVE'})`n" -ForegroundColor Gray

# 1. Windows Temp
Write-Status "Limpiando Windows Temp..."
$before = (Get-ChildItem "$env:TEMP" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
if (-not $DryRun) {
    Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
}
$after = (Get-ChildItem "$env:TEMP" -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$freed += ($before - $after)
Write-OK "Temp: $([math]::Round(($before - $after)/1MB, 2)) MB liberados"

# 2. Windows Update Cache
Write-Status "Limpiando Windows Update Cache..."
$wuPath = "C:\Windows\SoftwareDistribution\Download"
if (Test-Path $wuPath) {
    $before = (Get-ChildItem $wuPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if (-not $DryRun) {
        Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
        Remove-Item "$wuPath\*" -Recurse -Force -ErrorAction SilentlyContinue
        Start-Service wuauserv -ErrorAction SilentlyContinue
    }
    $freed += $before
    Write-OK "WU Cache: $([math]::Round($before/1MB, 2)) MB liberados"
}

# 3. Windows Installer Cache
Write-Status "Revisando Installer Cache..."
$installerPath = "C:\Windows\Installer\$PatchCache$"
if (Test-Path $installerPath) {
    Write-Skip "Installer cache encontrado ($([math]::Round((Get-ChildItem $installerPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum/1MB,2)) MB) - requiere revisión manual"
}

# 4. Browser Caches
Write-Status "Limpiando caches de navegador..."
$browsers = @(
    @{Name="Chrome"; Path="$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"},
    @{Name="Firefox"; Path="$env:LOCALAPPDATA\Mozilla\Firefox\Profiles"},
    @{Name="Edge"; Path="$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"}
)
foreach ($browser in $browsers) {
    if (Test-Path $browser.Path) {
        $before = (Get-ChildItem $browser.Path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if (-not $DryRun) {
            Remove-Item "$($browser.Path)\*" -Recurse -Force -ErrorAction SilentlyContinue
        }
        $freed += $before
        Write-OK "$($browser.Name): $([math]::Round($before/1MB, 2)) MB"
    }
}

# 5. Recycle Bin
Write-Status "Vaciando papelera..."
if (-not $DryRun) {
    Clear-RecycleBin -Force -ErrorAction SilentlyContinue
}
Write-OK "Papelera vaciada"

# 6. DNS Cache
Write-Status "Limpiando DNS cache..."
if (-not $DryRun) {
    Clear-DnsClientCache -ErrorAction SilentlyContinue
}
Write-OK "DNS cache limpiado"

# 7. Thumbnail Cache
Write-Status "Limpiando thumbnail cache..."
$thumbPath = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
if (Test-Path $thumbPath) {
    $before = (Get-ChildItem "$thumbPath\thumbcache_*.db" -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if (-not $DryRun) {
        Remove-Item "$thumbPath\thumbcache_*.db" -Force -ErrorAction SilentlyContinue
    }
    $freed += $before
    Write-OK "Thumbnails: $([math]::Round($before/1MB, 2)) MB"
}

# 8. Windows Error Reporting
Write-Status "Limpiando Windows Error Reports..."
$werPath = "C:\ProgramData\Microsoft\Windows\WER"
if (Test-Path $werPath) {
    $before = (Get-ChildItem $werPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if (-not $DryRun) {
        Remove-Item "$werPath\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    $freed += $before
    Write-OK "WER: $([math]::Round($before/1MB, 2)) MB"
}

# 9. Delivery Optimization Cache
Write-Status "Limpiando Delivery Optimization..."
$doPath = "$env:LOCALAPPDATA\Microsoft\Windows\DeliveryOptimization\Cache"
if (Test-Path $doPath) {
    $before = (Get-ChildItem $doPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if (-not $DryRun) {
        Remove-Item "$doPath\*" -Recurse -Force -ErrorAction SilentlyContinue
    }
    $freed += $before
    Write-OK "Delivery Optimization: $([math]::Round($before/1MB, 2)) MB"
}

# 10. Aggressive: Old Windows Install
if ($Aggressive) {
    Write-Status "Modo agresivo: buscando old Windows install..."
    $oldWin = "C:\Windows.old"
    if (Test-Path $oldWin) {
        $size = (Get-ChildItem $oldWin -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Write-Skip "Windows.old encontrado: $([math]::Round($size/1MB, 2)) MB"
        Write-Skip "Ejecutar: Remove-Item 'C:\Windows.old' -Recurse -Force"
    }
}

# Resumen
Write-Host "`n=== RESUMEN ===" -ForegroundColor Magenta
Write-Host "Total liberado: $([math]::Round($freed/1MB, 2)) MB" -ForegroundColor Green
Write-Host "Modo: $(if($DryRun){'DRY RUN (ningún cambio aplicado)'}else{'LIVE'})" -ForegroundColor Gray

if (-not $DryRun) {
    Write-Host "`nTip: Ejecutar 'diskcleanup' para limpieza adicional de Windows" -ForegroundColor Yellow
}
