# LlamaServerGui

`llama.cpp`의 네이티브 `llama-server.exe`를 실행하고, 준비되면 웹페이지를 여는 WinForms(.NET) GUI 런처.

## 기능

- **서버 시작 / 정지** — `D:\llama.cpp\llama-server.exe`를 자식 프로세스로 띄우고, `/health`가 응답할 때까지 대기
- **웹페이지 열기 2종**
  - 창 안 임베디드 표시 (WebView2)
  - "브라우저로 열기" 버튼 → 기본 브라우저로 `http://127.0.0.1:8888`
- 서버 EXE / 모델 / 포트 경로를 UI에서 변경 가능 (기본값 내장)
- 서버 stdout/stderr를 하단 로그 창에 표시
- 창을 닫으면 서버 프로세스도 함께 종료

## 기본값

| 항목 | 값 |
| ---- | -- |
| 서버 EXE | `D:\llama.cpp\llama-server.exe` |
| 모델 | `D:\WP_AI_CODER\Sm_AICoder\models\gguf\qwen2.5-coder-7b-instruct-q4_k_m.gguf` |
| 포트 | `8888` |
| 실행 인자 | `--ctx-size 8192 --threads 8 --n-gpu-layers 0 --host 127.0.0.1` |

## 빌드 / 실행

```powershell
# 빌드
dotnet build LlamaServerGui.csproj -c Release

# 실행
dotnet run --project LlamaServerGui.csproj -c Release
# 또는
.\bin\Release\net9.0-windows\LlamaServerGui.exe
```

## 요구사항

- .NET SDK 9 이상
- Microsoft Edge WebView2 런타임 (Windows 11 기본 포함). 없으면 임베디드 뷰만 비활성화되고 "브라우저로 열기"는 정상 동작.
