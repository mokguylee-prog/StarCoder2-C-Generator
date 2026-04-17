chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$pidFile = "server.pid"
if (-not (Test-Path $pidFile)) {
    Write-Host "server.pid 없음 - 서버가 실행 중이지 않습니다."
    exit
}

$pid = Get-Content $pidFile
try {
    Stop-Process -Id $pid -Force
    Write-Host "서버 종료 (PID: $pid)"
} catch {
    Write-Host "프로세스를 찾을 수 없습니다 (이미 종료됨)"
}

Remove-Item $pidFile
