"""StarCoder2 기본 C 코드 생성 스크립트 (bfloat16, GPU 권장)"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ── 설정 ──────────────────────────────────────────
# VRAM 14GB+ → starcoder2-7b, 6GB+ → starcoder2-3b
CHECKPOINT = "bigcode/starcoder2-7b"
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.2
TOP_P = 0.95

# ── C 코드 프롬프트 ────────────────────────────────
# 부분 코드를 제공하면 StarCoder2가 나머지를 완성합니다
PROMPTS = [
    # 1. 버블 정렬
    """\
#include <stdio.h>

// Sort array in ascending order using bubble sort
void bubble_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {""",

    # 2. 이진 탐색
    """\
#include <stdio.h>

// Binary search: returns index of target, -1 if not found
int binary_search(int arr[], int n, int target) {
    int left = 0, right = n - 1;""",

    # 3. 팩토리얼 (재귀)
    """\
// Recursive factorial
int factorial(int n) {
    if (n <= 1)
        return 1;""",
]

# ── 메인 ──────────────────────────────────────────

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"디바이스: {device}")
    if device == "cuda":
        vram = torch.cuda.get_device_properties(0).total_memory // 1024**3
        print(f"GPU VRAM: {vram} GB")

    print(f"모델 로딩: {CHECKPOINT}")
    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model.eval()
    print("모델 로딩 완료\n")
    return tokenizer, model


def generate(tokenizer, model, prompt: str) -> str:
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def main():
    tokenizer, model = load_model()

    for i, prompt in enumerate(PROMPTS, 1):
        print(f"{'=' * 60}")
        print(f"[예시 {i}] 프롬프트:")
        print(prompt)
        print(f"\n[생성 결과]:")
        result = generate(tokenizer, model, prompt)
        print(result)
        print()


if __name__ == "__main__":
    main()
