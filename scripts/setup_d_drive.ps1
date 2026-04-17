# StarCoder2 D 드라이브 설치 스크립트 (PowerShell)
# 실행: PowerShell에서 .\scripts\setup_d_drive.ps1

Write-Host "=== StarCoder2 D 드라이브 설치 ===" -ForegroundColor Cyan

# D 드라이브 경로 설정
$BASE = "D:\StarCoder2"
$MODEL_DIR = "$BASE\models\gguf"
$VENV_DIR = "$BASE\venv"

# 폴더 생성
New-Item -ItemType Directory -Force -Path $MODEL_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $VENV_DIR | Out-Null
Write-Host "[1/5] 폴더 생성 완료: $BASE" -ForegroundColor Green

# HuggingFace 캐시를 D 드라이브로
[Environment]::SetEnvironmentVariable("HF_HOME", "D:\StarCoder2\hf_cache", "User")
[Environment]::SetEnvironmentVariable("TRANSFORMERS_CACHE", "D:\StarCoder2\hf_cache\hub", "User")
Write-Host "[2/5] HuggingFace 캐시 경로 → D:\StarCoder2\hf_cache" -ForegroundColor Green

# pip 캐시를 D 드라이브로
[Environment]::SetEnvironmentVariable("PIP_CACHE_DIR", "D:\StarCoder2\pip_cache", "User")
Write-Host "[3/5] pip 캐시 경로 → D:\StarCoder2\pip_cache" -ForegroundColor Green

# Python 가상환경 생성 (D 드라이브)
Write-Host "[4/5] 가상환경 생성 중: $VENV_DIR" -ForegroundColor Yellow
python -m venv $VENV_DIR
Write-Host "      완료" -ForegroundColor Green

# 패키지 설치
Write-Host "[5/5] 패키지 설치 중..." -ForegroundColor Yellow
& "$VENV_DIR\Scripts\pip" install --cache-dir "D:\StarCoder2\pip_cache" `
    llama-cpp-python `
    huggingface_hub

Write-Host "`n=== 설치 완료 ===" -ForegroundColor Cyan
Write-Host "다음 단계:" -ForegroundColor White
Write-Host "  1. 가상환경 활성화: $VENV_DIR\Scripts\activate"
Write-Host "  2. 모델 다운로드:   python scripts\download_model.py"
Write-Host "  3. 코드 생성:       python scripts\generate_cpu_gguf.py"
