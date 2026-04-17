"""GGUF 모델 다운로드 - D 드라이브 저장"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# D 드라이브 저장 경로
MODEL_DIR = Path("D:/StarCoder2/models/gguf")  # D 드라이브 고정 경로
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# 모델 선택 (RAM에 따라 선택)
# RAM 8GB  → Q4_K_M (~2GB)
# RAM 16GB → Q5_K_M (~2.5GB) 품질 더 좋음
MODELS = {
    "3b-q4": {
        "repo": "second-state/StarCoder2-3B-GGUF",
        "file": "starcoder2-3b-Q4_K_M.gguf",
        "size": "~2 GB",
        "ram":  "4 GB RAM 필요",
    },
    "3b-q5": {
        "repo": "second-state/StarCoder2-3B-GGUF",
        "file": "starcoder2-3b-Q5_K_M.gguf",
        "size": "~2.5 GB",
        "ram":  "5 GB RAM 필요",
    },
    "7b-q4": {
        "repo": "second-state/StarCoder2-7B-GGUF",
        "file": "starcoder2-7b-Q4_K_M.gguf",
        "size": "~4 GB",
        "ram":  "8 GB RAM 필요",
    },
}

def main():
    print("=== StarCoder2 GGUF 모델 다운로드 ===")
    print(f"저장 위치: {MODEL_DIR}\n")

    print("사용 가능한 모델:")
    for key, info in MODELS.items():
        print(f"  [{key}] {info['file']}  {info['size']}  ({info['ram']})")

    print()
    choice = input("다운로드할 모델 선택 (기본값: 3b-q4): ").strip() or "3b-q4"

    if choice not in MODELS:
        print(f"잘못된 선택: {choice}")
        return

    model = MODELS[choice]
    dest = MODEL_DIR / model["file"]

    if dest.exists():
        print(f"이미 존재: {dest}")
        print("다시 다운로드하려면 파일을 삭제 후 실행하세요.")
        return

    print(f"\n다운로드 시작: {model['file']} ({model['size']})")
    print("(시간이 걸립니다. 기다려 주세요...)\n")

    hf_hub_download(
        repo_id=model["repo"],
        filename=model["file"],
        local_dir=str(MODEL_DIR),
        local_dir_use_symlinks=False,
    )

    print(f"\n완료! 저장 위치: {dest}")
    print(f"\n다음 실행:")
    print(f"  python scripts/generate_cpu_gguf.py")


if __name__ == "__main__":
    main()
