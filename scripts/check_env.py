"""환경 확인 스크립트 - 설치 상태를 점검합니다."""
import sys


def check(name, fn):
    try:
        result = fn()
        print(f"  [OK] {name}: {result}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def main():
    print("=" * 50)
    print("StarCoder2 환경 확인")
    print("=" * 50)

    print("\n[Python]")
    check("Python 버전", lambda: sys.version.split()[0])

    print("\n[PyTorch]")
    import_ok = check("torch import", lambda: __import__("torch").__version__)
    if import_ok:
        import torch
        check("CUDA 사용 가능", lambda: torch.cuda.is_available())
        if torch.cuda.is_available():
            check("GPU 이름", lambda: torch.cuda.get_device_name(0))
            vram = torch.cuda.get_device_properties(0).total_memory // 1024**3
            check("GPU VRAM", lambda: f"{vram} GB")

            if vram >= 14:
                print("  → 추천 모델: starcoder2-7b (bfloat16)")
            elif vram >= 8:
                print("  → 추천 모델: starcoder2-7b (4-bit) 또는 starcoder2-3b")
            elif vram >= 4:
                print("  → 추천 모델: starcoder2-3b (4-bit)")
            else:
                print("  → 주의: VRAM 부족. CPU 실행 또는 GGUF 모델 사용 권장")
        else:
            print("  → GPU 없음. CPU 전용 실행 (느림). GGUF 모델 권장")

    print("\n[HuggingFace]")
    check("transformers", lambda: __import__("transformers").__version__)
    check("accelerate", lambda: __import__("accelerate").__version__)
    check("huggingface_hub", lambda: __import__("huggingface_hub").__version__)

    print("\n[양자화 (선택)]")
    check("bitsandbytes", lambda: __import__("bitsandbytes").__version__)

    print("\n[HuggingFace 로그인 상태]")
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        user = api.whoami()
        print(f"  [OK] 로그인됨: {user['name']}")
    except Exception:
        print("  [주의] 로그인 안됨 - `huggingface-cli login` 실행 필요")

    print("\n" + "=" * 50)
    print("확인 완료")
    print("=" * 50)


if __name__ == "__main__":
    main()
