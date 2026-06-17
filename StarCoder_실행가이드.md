# StarCoder3 - llama.cpp vs Ollama 실행 가이드

## 📋 설치 위치

```
D:\llama.cpp\              ← llama.cpp 바이너리
D:\ollama\                 ← Ollama 바이너리
D:\StarCoder3\             ← 프로젝트 폴더
D:\StarCoder3\models\gguf\ ← Qwen 모델 (4.4GB)
```

---

## 🚀 1. llama.cpp 서버 실행

### Windows PowerShell

```powershell
# 1단계: PowerShell 열기
# 2단계: 다음 명령 실행

$env:OLLAMA_MODELS = "D:\ollama\models"  # Ollama가 실행 중이면 종료

D:\llama.cpp\llama-server.exe `
  -m "D:/StarCoder3/models/gguf/qwen2.5-coder-7b-instruct-q4_k_m.gguf" `
  --port 8888 `
  --host 0.0.0.0 `
  -ngl 0
```

### 또는 배치 파일로 실행

`D:\run_llama_cpp.bat` 생성:
```batch
@echo off
cd /d D:\llama.cpp
llama-server.exe -m "D:/StarCoder3/models/gguf/qwen2.5-coder-7b-instruct-q4_k_m.gguf" --port 8888 --host 0.0.0.0 -ngl 0
pause
```

더블클릭 후 실행하면 됨.

### 접속
- **웹 인터페이스**: `http://localhost:8888`
- **API**: `http://localhost:8888/v1/chat/completions`

### API 테스트 예시
```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    model = "gpt-3.5-turbo"
    messages = @(
        @{role = "user"; content = "circle 그리는 C++ 코드"}
    )
    temperature = 0.3
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8888/v1/chat/completions" `
    -Method POST `
    -Headers $headers `
    -Body $body | Select-Object -ExpandProperty Content
```

---

## 🦙 2. Ollama 서버 실행

### Windows PowerShell

```powershell
# 1단계: 환경변수 설정
$env:OLLAMA_MODELS = "D:\ollama\models"
$env:OLLAMA_HOST = "0.0.0.0:11434"

# 2단계: 서버 시작
D:\ollama\ollama.exe serve
```

### 또는 배치 파일로 실행

`D:\run_ollama.bat` 생성:
```batch
@echo off
set OLLAMA_MODELS=D:\ollama\models
set OLLAMA_HOST=0.0.0.0:11434
cd /d D:\ollama
ollama.exe serve
pause
```

더블클릭 후 실행하면 됨.

### 접속
- **웹 인터페이스**: `http://localhost:11434`
- **API**: `http://localhost:11434/api/chat`

### CLI로 실행 (명령줄 대화)
```powershell
$env:OLLAMA_MODELS = "D:\ollama\models"
D:\ollama\ollama.exe run qwen-local "원하는 지시문"
```

### API 테스트 예시
```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    model = "qwen-local"
    messages = @(
        @{role = "user"; content = "circle 그리는 C++ 코드"}
    )
    temperature = 0.3
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:11434/api/chat" `
    -Method POST `
    -Headers $headers `
    -Body $body | Select-Object -ExpandProperty Content
```

---

## 비교

| 항목 | llama.cpp | Ollama |
|------|-----------|--------|
| 포트 | 8888 | 11434 |
| 시작 속도 | 빠름 | 보통 |
| 웹UI | 기본 | 좋음 |
| API | ✅ OpenAI 호환 | ✅ REST API |
| 모델 관리 | 수동 | 자동 |
| CPU 사용 | 효율적 | 효율적 |
| 권장 | 개발/테스트 | 프로덕션 |

---

## ⚙️ 주요 파라미터

### llama.cpp
```
-m <경로>        : 모델 파일 경로
--port <번호>    : 포트 (기본: 8000)
--host <주소>    : 바인드 주소
-ngl 0           : GPU 미사용 (CPU만 사용)
-n 1024          : 최대 생성 토큰
-c 4096          : 컨텍스트 길이
```

### Ollama
```
OLLAMA_MODELS    : 모델 저장 경로
OLLAMA_HOST      : 바인드 주소:포트
```

---

## 🛠️ 문제 해결

### "포트가 이미 사용 중" 오류
```powershell
# 기존 프로세스 종료
Get-Process llama-server | Stop-Process -Force
Get-Process ollama | Stop-Process -Force
```

### 모델이 로드되지 않음
- Qwen 모델 경로 확인: `D:\StarCoder3\models\gguf\qwen2.5-coder-7b-instruct-q4_k_m.gguf`
- 파일이 있는지 확인: `ls D:\StarCoder3\models\gguf\`

### 성능이 느린 경우
- CPU 코어 수 확인 (현재: 12개)
- 다른 프로그램 종료
- `N_THREADS` 조정 가능

---

## 📝 추가 정보

- **모델**: Qwen2.5-Coder-7B-Instruct-Q4_K_M (4.4GB)
- **CPU**: 12th Gen Intel i7-1260P
- **메모리**: 32GB (실제 사용: ~8.9GB)
- **컨텍스트 길이**: 4096~131072 토큰

---

최종 업데이트: 2026-06-17
