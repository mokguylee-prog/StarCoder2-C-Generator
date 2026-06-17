@echo off
chcp 65001 > nul
set OLLAMA_MODELS=D:\ollama\models
set OLLAMA_HOST=0.0.0.0:11434

cd /d D:\ollama
echo.
echo ==========================================
echo   Ollama 서버 실행
echo ==========================================
echo.
echo 모델: qwen-local
echo 포트: 11434
echo.
echo 웹 접속: http://localhost:11434
echo API: http://localhost:11434/api/chat
echo.
echo 모델 로드 중... (잠시 대기)
echo.

ollama.exe serve

pause
