$cacheDir = "$env:USERPROFILE\.buildozer_cache"
New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
Write-Host "== Zavod Nichego: building APK ==" -ForegroundColor Cyan
Write-Host "Cache: $cacheDir" -ForegroundColor Gray
Write-Host "First build ~30-60 min, repeat ~5-15 min" -ForegroundColor Yellow
Write-Host ""
$gameDir = Split-Path -Parent $MyInvocation.MyCommand.Path
docker run --rm --volume "$($gameDir -replace '\\','/'):/home/user/hostcwd" --volume "$($cacheDir -replace '\\','/'):/home/user/.buildozer" kivy/buildozer:latest android debug
if ($LASTEXITCODE -eq 0) {
    $apk = Get-ChildItem -Path "$gameDir\bin" -Filter "*.apk" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
    if ($apk) {
        Write-Host ""
        Write-Host "APK ready: $($apk.FullName)" -ForegroundColor Green
        Write-Host "Size: $([math]::Round($apk.Length / 1MB, 1)) MB" -ForegroundColor Green
    }
} else {
    Write-Host "Build failed. Check log above." -ForegroundColor Red
}