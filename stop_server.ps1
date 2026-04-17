# StarCoder2 서버 종료

$PID_FILE = "$PSScriptRoot\server.pid"

if (-not (Test-Path $PID_FILE)) {
    Write-Host "실행 중인 서버 없음"
    exit 0
}

$savedPid = Get-Content $PID_FILE
$proc = Get-Process -Id $savedPid -ErrorAction SilentlyContinue

if ($proc) {
    Stop-Process -Id $savedPid -Force
    Write-Host "서버 종료 (PID: $savedPid)"
} else {
    Write-Host "프로세스 없음 (이미 종료됨)"
}

Remove-Item $PID_FILE
