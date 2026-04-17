chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

$venv = "D:\StarCoder3\venv\Scripts\python.exe"
if (-not (Test-Path $venv)) { $venv = "python" }

Write-Host "StarCoder3 서버 시작..."
& $venv server.py
