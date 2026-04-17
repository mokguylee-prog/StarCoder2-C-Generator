"""StarCoder2 4-bit 양자화 C 코드 생성 (저사양 GPU용, VRAM 4GB+)"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# ── 설정 ──────────────────────────────────────────
# 4-bit: starcoder2-7b → ~4GB, starcoder2-3b → ~2GB
CHECKPOINT = "bigcode/starcoder2-7b"
MAX_NEW_TOKENS = 256
TEMPERATURE = 0.2

# 4-bit NF4 양자화 설정
BNB_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

# ── 프롬프트 ──────────────────────────────────────
PROMPT = """\
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Linked list node
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Insert node at front of list
Node* insert_front(Node* head, int data) {"""


def main():
    if not torch.cuda.is_available():
        print("경고: GPU 없음. bitsandbytes는 CUDA GPU가 필요합니다.")
        print("CPU 실행이 필요하면 generate_cpu.py 또는 GGUF 모델을 사용하세요.")
        return

    vram = torch.cuda.get_device_properties(0).total_memory // 1024**3
    print(f"GPU: {torch.cuda.get_device_name(0)} ({vram} GB VRAM)")
    print(f"모델: {CHECKPOINT} (4-bit 양자화)")
    print("모델 로딩 중...")

    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT,
        quantization_config=BNB_CONFIG,
        device_map="auto",
    )
    model.eval()

    vram_used = torch.cuda.memory_allocated() // 1024**2
    print(f"로딩 완료 - VRAM 사용: {vram_used} MB\n")

    print("프롬프트:")
    print(PROMPT)
    print("\n생성 중...")

    inputs = tokenizer.encode(PROMPT, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n결과:")
    print(result)


if __name__ == "__main__":
    main()
