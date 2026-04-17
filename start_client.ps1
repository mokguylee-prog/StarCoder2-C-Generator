# StarCoder2 클라이언트 실행
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$VENV   = "D:\StarCoder2\venv\Scripts\python.exe"
$SCRIPT = "$PSScriptRoot\client.py"

# 서버 기동 여부 확인
try {
    $r = Invoke-RestMethod -Uri "http://localhost:8888/health" -TimeoutSec 5
    Write-Host "서버 확인 — 모델: $($r.model)`n"
} catch {
    Write-Host "[오류] 서버가 실행 중이지 않습니다."
    Write-Host "먼저 실행하세요: .\start_server.ps1`n"
    exit 1
}

& $VENV $SCRIPT
