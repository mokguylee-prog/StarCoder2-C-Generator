@echo off
chcp 65001 > nul
cd /d D:\llama.cpp
echo.
echo ==========================================
echo   llama.cpp 서버 실행
echo ==========================================
echo.
echo 모델: qwen2.5-coder-7b-instruct-q4_k_m.gguf
echo 포트: 8888
echo.
echo 웹 접속: http://localhost:8888
echo.
echo 모델 로드 중... (30~60초 소요)
echo.

llama-server.exe -m "D:/StarCoder3/models/gguf/qwen2.5-coder-7b-instruct-q4_k_m.gguf" --port 8888 --host 0.0.0.0 -ngl 0

pause
