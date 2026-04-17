# StarCoder2 실제 설치 환경 메모

## 실행 환경
- **GPU**: 없음 — CPU 전용 실행
- **실행 방식**: llama.cpp + GGUF 양자화 모델

## 설치 경로 (D드라이브)

| 항목 | 경로 |
|------|------|
| 루트 | `D:/StarCoder2/` |
| 가상환경 | `D:/StarCoder2/venv/` |
| 모델 | `D:/StarCoder2/models/gguf/` |
| HuggingFace 캐시 | `D:/StarCoder2/hf_cache/` |
| pip 캐시 | `D:/StarCoder2/pip_cache/` |

## 다운로드된 모델

| 파일명 | 경로 |
|--------|------|
| starcoder2-3b-Q4_K_M.gguf | `D:/StarCoder2/models/gguf/starcoder2-3b-Q4_K_M.gguf` |

## 주의사항
- C드라이브 용량 부족으로 모든 설치는 D드라이브에 위치
- GPU 관련 코드(bitsandbytes, CUDA, torch.cuda) 사용 불가
- 스크립트 실행 시 항상 `generate_cpu_gguf.py` 기준으로 작동
- 모델 추가 다운로드 시 `D:/StarCoder2/models/gguf/` 경로 사용
