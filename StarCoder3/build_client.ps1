chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"

$venvPython = "D:\StarCoder3\venv\Scripts\python.exe"
$venvPip    = "D:\StarCoder3\venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
    $venvPip    = "pip"
    Write-Host "[경고] 가상환경을 찾지 못했습니다. 시스템 Python을 사용합니다."
}

Write-Host ""
Write-Host "========================================"
Write-Host " StarCoder3 GUI Client - EXE 빌드 시작"
Write-Host "========================================"
Write-Host ""

# ── 1. PyInstaller 설치 확인 ──────────────────
Write-Host "[1/4] PyInstaller 설치 확인..."
$piCheck = & $venvPython -c "import PyInstaller" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "      PyInstaller 없음 -> 설치 중..."
    & $venvPip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[오류] PyInstaller 설치 실패. 종료합니다."
        exit 1
    }
    Write-Host "      PyInstaller 설치 완료."
} else {
    Write-Host "      PyInstaller 이미 설치되어 있습니다."
}

# ── 2. 이전 빌드 정리 ─────────────────────────
Write-Host ""
Write-Host "[2/4] 이전 빌드 파일 정리..."
if (Test-Path "dist\StarCoder3Client.exe") {
    Remove-Item "dist\StarCoder3Client.exe" -Force
    Write-Host "      dist\StarCoder3Client.exe 삭제됨."
}
if (Test-Path "build") {
    Remove-Item "build" -Recurse -Force
    Write-Host "      build\ 폴더 삭제됨."
}
if (Test-Path "StarCoder3Client.spec") {
    Remove-Item "StarCoder3Client.spec" -Force
    Write-Host "      StarCoder3Client.spec 삭제됨."
}

# ── 3. TCL/TK 경로 탐색 ──────────────────────
Write-Host ""
Write-Host "[3/4] TCL/TK 경로 확인..."
$pythonExe  = & $venvPython -c "import sys; print(sys.executable)"
$pythonDir  = Split-Path $pythonExe
$tclDataArg = ""
$tkDataArg  = ""

$tclDirs = @(
    (Join-Path $pythonDir "tcl\tcl8.6"),
    (Join-Path $pythonDir "Lib\tcl8.6"),
    (Join-Path (Split-Path $pythonDir) "tcl\tcl8.6")
)
$tkDirs = @(
    (Join-Path $pythonDir "tcl\tk8.6"),
    (Join-Path $pythonDir "Lib\tk8.6"),
    (Join-Path (Split-Path $pythonDir) "tcl\tk8.6")
)

foreach ($d in $tclDirs) {
    if (Test-Path $d) { $tclDataArg = "--add-data `"${d};tcl`""; Write-Host "      TCL: $d"; break }
}
foreach ($d in $tkDirs) {
    if (Test-Path $d) { $tkDataArg  = "--add-data `"${d};tk`"";  Write-Host "      TK : $d"; break }
}

# ── 4. PyInstaller 빌드 ───────────────────────
Write-Host ""
Write-Host "[4/4] PyInstaller 빌드 실행 중..."
Write-Host "      (시간이 1~3분 소요될 수 있습니다)"
Write-Host ""

$buildArgs = @(
    "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "StarCoder3Client",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.ttk",
    "--hidden-import", "tkinter.scrolledtext",
    "--hidden-import", "_tkinter",
    "--collect-all", "tkinter"
)
if ($tclDataArg) { $buildArgs += "--add-data"; $buildArgs += "$((Join-Path $pythonDir 'tcl\tcl8.6'));tcl" }
if ($tkDataArg)  { $buildArgs += "--add-data"; $buildArgs += "$((Join-Path $pythonDir 'tcl\tk8.6'));tk" }
$buildArgs += "gui_client.py"

& $venvPython @buildArgs

if ($LASTEXITCODE -eq 0) {
    # ── 4. 루트 폴더로 복사 ───────────────────────
    $dest = "$PSScriptRoot\StarCoder3Client.exe"
    Copy-Item "dist\StarCoder3Client.exe" -Destination $dest -Force
    Write-Host ""
    Write-Host "========================================"
    Write-Host " 빌드 성공!"
    Write-Host " 복사 완료: $dest"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "[주의] exe 실행 전 api_server(서버)가 먼저 구동되어 있어야 합니다."
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "[오류] 빌드 실패. 위 로그를 확인하세요."
    exit 1
}
