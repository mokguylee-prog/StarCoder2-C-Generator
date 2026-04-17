# StarCoder2 서버 백그라운드 실행
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$VENV     = "D:\StarCoder2\venv\Scripts\python.exe"
$SCRIPT   = "$PSScriptRoot\server.py"
$LOG      = "$PSScriptRoot\server.log"
$PID_FILE = "$PSScriptRoot\server.pid"

# 이미 실행 중인지 확인
if (Test-Path $PID_FILE) {
    $oldPid = Get-Content $PID_FILE
    if (Get-Process -Id $oldPid -ErrorAction SilentlyContinue) {
        Write-Host "서버 이미 실행 중 (PID: $oldPid)"
        Write-Host "중지하려면: .\stop_server.ps1"
        exit 0
    }
    Remove-Item $PID_FILE
}

# 백그라운드 실행 (cmd /c 로 stdout+stderr 단일 파일에 합산)
$proc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList "/c `"$VENV`" `"$SCRIPT`" >> `"$LOG`" 2>&1" `
    -WindowStyle Hidden `
    -PassThru

$proc.Id | Out-File $PID_FILE -Encoding utf8
Write-Host "서버 시작 (PID: $($proc.Id))"
Write-Host "로그:  $LOG"
Write-Host "중지:  .\stop_server.ps1"
Write-Host ""

# 3초 대기 후 기동 확인
Start-Sleep -Seconds 3
try {
    $r = Invoke-RestMethod -Uri "http://localhost:8888/health" -TimeoutSec 5
    Write-Host "상태: 정상 — 모델: $($r.model)"
} catch {
    Write-Host "상태: 아직 로딩 중 (모델 로딩에 30~60초 소요)"
    Write-Host "확인: python client.py health"
}
