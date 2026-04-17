"""StarCoder2 CPU 전용 C 코드 생성 (llama.cpp + GGUF, D 드라이브)"""
from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:
    print("설치 필요: pip install llama-cpp-python")
    raise

# ── 설정 ──────────────────────────────────────────
MODEL_DIR = Path("D:/StarCoder2/models/gguf")  # D 드라이브 고정 경로

# 다운받은 모델 파일명 (download_model.py로 받은 파일)
MODEL_FILE = "starcoder2-3b-Q4_K_M.gguf"

MAX_TOKENS = 256
TEMPERATURE = 0.2
TOP_P = 0.95

# FIM 특수 토큰 (StarCoder2)
FIM_PREFIX = "<fim_prefix>"
FIM_SUFFIX = "<fim_suffix>"
FIM_MIDDLE = "<fim_middle>"

# ── C 코드 프롬프트 예시 ───────────────────────────
EXAMPLES = [
    {
        "desc": "버블 정렬",
        "prompt": """\
#include <stdio.h>

// Sort array in ascending order using bubble sort
void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {""",
    },
    {
        "desc": "팩토리얼 (재귀)",
        "prompt": """\
// Recursive factorial
int factorial(int n) {
    if (n <= 1)
        return 1;""",
    },
    {
        "desc": "이진 탐색",
        "prompt": """\
// Binary search - returns index, -1 if not found
int binary_search(int arr[], int n, int target) {
    int left = 0, right = n - 1;""",
    },
]


def find_model() -> Path:
    model_path = MODEL_DIR / MODEL_FILE
    if model_path.exists():
        return model_path

    # 폴더에 있는 gguf 파일 자동 탐색
    gguf_files = list(MODEL_DIR.glob("*.gguf"))
    if gguf_files:
        print(f"모델 자동 감지: {gguf_files[0].name}")
        return gguf_files[0]

    print(f"모델 파일을 찾을 수 없습니다: {MODEL_DIR}")
    print("먼저 실행하세요: python scripts/download_model.py")
    raise FileNotFoundError(f"{MODEL_DIR} 에 .gguf 파일 없음")


def main():
    model_path = find_model()
    print(f"=== StarCoder2 CPU 코드 생성 ===")
    print(f"모델: {model_path.name}")
    print(f"경로: {model_path}")
    print("로딩 중...\n")

    llm = Llama(
        model_path=str(model_path),
        n_ctx=4096,        # 컨텍스트 윈도우
        n_threads=None,    # CPU 코어 자동 감지
        verbose=False,
    )
    print("로딩 완료. 코드 생성 시작...\n")

    for i, ex in enumerate(EXAMPLES, 1):
        print(f"{'=' * 55}")
        print(f"[예시 {i}] {ex['desc']}")
        print(f"\n[프롬프트]")
        print(ex["prompt"])
        print(f"\n[생성 결과]")

        output = llm(
            ex["prompt"],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            stop=["}\n\n", "\n\n\n"],  # 함수 끝에서 멈춤
            echo=True,                  # 프롬프트 포함 출력
        )

        print(output["choices"][0]["text"])
        print()


if __name__ == "__main__":
    main()
