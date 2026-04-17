# StarCoder2 - C 코드 생성 가이드

StarCoder2 (BigCode/HuggingFace) 를 이용한 C 언어 코드 생성 환경 구축 가이드

---

## 모델 선택 가이드

| 모델 | 파라미터 | VRAM (bfloat16) | VRAM (4-bit) | 권장 GPU |
|------|----------|-----------------|--------------|---------|
| `bigcode/starcoder2-3b`  | 3B  | ~6.3 GB  | ~2 GB  | RTX 3060 이상 |
| `bigcode/starcoder2-7b`  | 7B  | ~14.6 GB | ~4 GB  | RTX 3080 이상 |
| `bigcode/starcoder2-15b` | 15B | ~32 GB   | ~9 GB  | RTX 3090/4090 |
| `bigcode/starcoder2-15b-instruct-v0.1` | 15B | ~32 GB | ~9 GB | 지시형 응답 |

> **권장**: GPU VRAM이 부족하면 4-bit 양자화 또는 starcoder2-3b 사용

---

## 빠른 시작

```bash
# 1. 환경 설정
cd d:/work_web/StarCoder
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 2. HuggingFace 로그인 (토큰 필요)
huggingface-cli login

# 3. C 코드 생성 실행
python scripts/generate_c_code.py
```

---

## 문서 목차

| 문서 | 설명 |
|------|------|
| [docs/01_시스템요구사항.md](docs/01_시스템요구사항.md) | GPU/RAM/디스크 요구사항 |
| [docs/02_설치가이드.md](docs/02_설치가이드.md) | Python 환경 및 패키지 설치 |
| [docs/03_모델다운로드.md](docs/03_모델다운로드.md) | 모델 다운로드 방법 |
| [docs/04_C코드생성실행.md](docs/04_C코드생성실행.md) | C 코드 생성 사용법 |
| [docs/05_서버배포.md](docs/05_서버배포.md) | vLLM / llama.cpp 서버 구성 |
| [docs/06_양자화옵션.md](docs/06_양자화옵션.md) | 4-bit/8-bit 양자화 설정 |
| [docs/07_Windows설정.md](docs/07_Windows설정.md) | Windows 전용 설정 |

## 스크립트 목차

| 스크립트 | 설명 |
|----------|------|
| [scripts/generate_c_code.py](scripts/generate_c_code.py) | 기본 C 코드 생성 |
| [scripts/generate_4bit.py](scripts/generate_4bit.py) | 4-bit 양자화 버전 (저사양 GPU) |
| [scripts/fim_completion.py](scripts/fim_completion.py) | FIM(중간 채우기) 코드 완성 |
| [scripts/batch_generate.py](scripts/batch_generate.py) | 배치 코드 생성 |
| [scripts/check_env.py](scripts/check_env.py) | 환경 확인 스크립트 |

---

## 핵심 특징

- **컨텍스트 윈도우**: 16,384 토큰
- **학습 데이터**: The Stack v2 (600+ 프로그래밍 언어)
- **특화 기능**: FIM (Fill-in-the-Middle) 코드 완성
- **라이선스**: BigCode OpenRAIL-M v1
