"""StarCoder2 FIM (Fill-in-the-Middle) - 코드 중간 채우기"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

CHECKPOINT = "bigcode/starcoder2-7b"

# FIM 특수 토큰
FIM_PREFIX = "<fim_prefix>"
FIM_SUFFIX = "<fim_suffix>"
FIM_MIDDLE = "<fim_middle>"

# ── FIM 예시들 ─────────────────────────────────────
# 형식: prefix (앞부분) + suffix (뒷부분) → middle(중간)을 채움

FIM_EXAMPLES = [
    {
        "desc": "배열 정렬 코드 삽입",
        "prefix": """\
#include <stdio.h>

int main() {
    int arr[] = {64, 34, 25, 12, 22, 11, 90};
    int n = 7;

    // Sort the array
""",
        "suffix": """\

    printf("Sorted: ");
    for (int i = 0; i < n; i++)
        printf("%d ", arr[i]);
    printf("\\n");
    return 0;
}""",
    },
    {
        "desc": "에러 처리 코드 삽입",
        "prefix": """\
#include <stdio.h>
#include <stdlib.h>

int* allocate_array(int size) {
    int* arr = (int*)malloc(size * sizeof(int));
""",
        "suffix": """\
    return arr;
}""",
    },
]


def build_fim_prompt(prefix: str, suffix: str) -> str:
    return f"{FIM_PREFIX}{prefix}{FIM_SUFFIX}{suffix}{FIM_MIDDLE}"


def main():
    print(f"모델 로딩: {CHECKPOINT}")
    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )
    model.eval()
    print("로딩 완료\n")

    for i, example in enumerate(FIM_EXAMPLES, 1):
        print(f"{'=' * 60}")
        print(f"[FIM 예시 {i}] {example['desc']}")
        print(f"\n앞부분:\n{example['prefix']}")
        print(f"뒷부분:\n{example['suffix']}")

        prompt = build_fim_prompt(example["prefix"], example["suffix"])
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=128,
                temperature=0.2,
                top_p=0.95,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=False)
        # FIM_MIDDLE 이후 부분만 추출
        middle_start = generated.find(FIM_MIDDLE)
        if middle_start != -1:
            middle_code = generated[middle_start + len(FIM_MIDDLE):]
            # EOS까지만
            eos = tokenizer.eos_token
            if eos and eos in middle_code:
                middle_code = middle_code[:middle_code.index(eos)]
            print(f"\n[채워진 중간 코드]:\n{middle_code}")
        else:
            print(f"\n[전체 출력]:\n{generated}")

        print()


if __name__ == "__main__":
    main()
