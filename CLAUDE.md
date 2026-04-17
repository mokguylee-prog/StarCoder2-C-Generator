# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

StarCoder2 기반 C 코드 생성 프레임워크. BigCode의 StarCoder2 모델(3B/7B/15B)을 사용해 C 언어 코드를 완성하는 환경이며, GPU/CPU 양쪽 실행 경로를 모두 지원한다.

**중요**: StarCoder2는 코드 완성(code completion) 모델이지 명령어 수행(instruction-following) 모델이 아니다. 프롬프트는 반드시 부분적인 C 코드 형태로 제공해야 한다 — 자연어 지시문 형태로 사용하면 올바른 결과가 나오지 않는다.

## Environment Setup

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# HuggingFace 로그인 (최초 1회)
huggingface-cli login

# 환경 검증
python scripts/check_env.py
```

Windows D드라이브 설치 시 PowerShell에서:
```powershell
.\scripts\setup_d_drive.ps1
```
이 스크립트는 `HF_HOME`, `TRANSFORMERS_CACHE`, `PIP_CACHE_DIR`을 D 드라이브로 설정하고 venv를 `D:/StarCoder2/venv`에 생성한다.

## Run Commands

| 목적 | 명령어 |
|------|--------|
| 환경 검증 | `python scripts/check_env.py` |
| C 코드 생성 (bfloat16, GPU) | `python scripts/generate_c_code.py` |
| C 코드 생성 (4-bit 양자화, 저VRAM GPU) | `python scripts/generate_4bit.py` |
| Fill-in-the-Middle 완성 | `python scripts/fim_completion.py` |
| 배치 처리 (8개 태스크 → .c 파일) | `python scripts/batch_generate.py` |
| CPU 전용 실행 (GGUF 모델) | `python scripts/generate_cpu_gguf.py` |
| GGUF 모델 다운로드 | `python scripts/download_model.py` |
| API 서버 실행 (port 8888) | `python scripts/api_server.py` |

## Architecture

### 실행 계층 구조

```
scripts/          ← 진입점 (CLI 스크립트 9개 + PowerShell 1개)
examples/         ← 재사용 가능한 C 코드 프롬프트 19종 (c_prompts.py)
docs/             ← 한국어 가이드 7편 (요구사항/설치/모델/실행/배포/양자화/Windows)
```

### 백엔드별 실행 경로

- **GPU (bfloat16)**: `generate_c_code.py` — HuggingFace transformers + torch.bfloat16
- **GPU (4-bit 양자화)**: `generate_4bit.py` — bitsandbytes NF4, VRAM ~4GB
- **CPU (GGUF)**: `generate_cpu_gguf.py` — llama-cpp-python, GGUF 파일은 `D:/StarCoder2/models/gguf/`
- **HTTP API**: `api_server.py` — FastAPI, `/generate` POST + `/health` GET

### 자동 정밀도 선택

`api_server.py`와 `batch_generate.py`는 VRAM이 14GB 미만이면 자동으로 4-bit 양자화로 전환한다.

### FIM (Fill-in-the-Middle)

`fim_completion.py`는 `<fim_prefix>`, `<fim_suffix>`, `<fim_middle>` 특수 토큰을 사용해 코드 중간 부분을 채운다. 생성된 응답에서 `<fim_middle>` 이후 부분만 추출해 출력한다.

### 프롬프트 라이브러리

`examples/c_prompts.py`의 딕셔너리 키:
- `ALGORITHM_PROMPTS`: bubble_sort, quick_sort, merge_sort, binary_search, factorial, fibonacci
- `DATA_STRUCTURE_PROMPTS`: linked_list, stack, queue, hash_table
- `STRING_PROMPTS`: reverse_string, is_palindrome, count_words
- `FILE_IO_PROMPTS`: read_lines, write_csv
- `MEMORY_PROMPTS`: dynamic_array, memory_pool

## Key Constants (per script)

각 스크립트 상단에 하드코딩된 설정값:
- `CHECKPOINT` — 사용할 모델 ID (예: `"bigcode/starcoder2-7b"`)
- `MAX_NEW_TOKENS` — 생성 토큰 수 (기본값 스크립트마다 다름)
- `DEVICE` — `"cuda"` 또는 `"cpu"`
- GGUF 모델 경로: `D:/StarCoder2/models/gguf/`

## Model Selection Guide

| VRAM | 권장 모델 | 정밀도 |
|------|----------|--------|
| 24GB+ | starcoder2-15b | bfloat16 |
| 12–16GB | starcoder2-7b | bfloat16 |
| 6–8GB | starcoder2-7b | 4-bit |
| GPU 없음 | 3b-q4 GGUF (~2GB) | GGUF |
