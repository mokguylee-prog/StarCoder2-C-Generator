"""StarCoder2 배치 C 코드 생성 - 여러 프롬프트를 한 번에 처리"""
import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

CHECKPOINT = "bigcode/starcoder2-7b"
OUTPUT_DIR = Path("./output")

# C 코드 생성 배치 작업 목록
TASKS = [
    {"id": "factorial",    "prompt": "int factorial(int n) {\n    if (n <= 1)\n        return 1;\n"},
    {"id": "bubble_sort",  "prompt": "void bubble_sort(int arr[], int n) {\n    for (int i = 0; i < n - 1; i++) {\n"},
    {"id": "bin_search",   "prompt": "int binary_search(int arr[], int n, int target) {\n    int left = 0, right = n - 1;\n"},
    {"id": "str_reverse",  "prompt": "#include <string.h>\nvoid reverse_string(char str[]) {\n    int len = strlen(str);\n"},
    {"id": "linked_list",  "prompt": "typedef struct Node { int data; struct Node* next; } Node;\nNode* insert_front(Node* head, int data) {\n"},
    {"id": "stack",        "prompt": "#define MAX 100\ntypedef struct { int data[MAX]; int top; } Stack;\nvoid push(Stack* s, int val) {\n"},
    {"id": "queue",        "prompt": "#define MAX 100\ntypedef struct { int data[MAX]; int front, rear; } Queue;\nvoid enqueue(Queue* q, int val) {\n"},
    {"id": "fibonacci",    "prompt": "int fibonacci(int n) {\n    if (n <= 1) return n;\n"},
]


def load_model_auto():
    """GPU VRAM에 따라 자동으로 양자화 선택"""
    if not torch.cuda.is_available():
        print("GPU 없음 - CPU 실행 (느립니다)")
        tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
        model = AutoModelForCausalLM.from_pretrained(CHECKPOINT)
        return tokenizer, model

    vram_gb = torch.cuda.get_device_properties(0).total_memory // 1024**3
    print(f"GPU: {torch.cuda.get_device_name(0)} ({vram_gb} GB)")

    if vram_gb >= 14:
        print("→ bfloat16 모드")
        dtype = torch.bfloat16
        quant_config = None
    else:
        print("→ 4-bit 양자화 모드")
        dtype = None
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4",
        )

    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT,
        device_map="auto",
        torch_dtype=dtype,
        quantization_config=quant_config,
    )
    return tokenizer, model


def generate_one(tokenizer, model, prompt: str) -> str:
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=200,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"모델 로딩: {CHECKPOINT}\n")
    tokenizer, model = load_model_auto()
    model.eval()

    results = []
    for i, task in enumerate(TASKS, 1):
        print(f"[{i}/{len(TASKS)}] {task['id']} 생성 중...")
        code = generate_one(tokenizer, model, task["prompt"])
        results.append({"id": task["id"], "prompt": task["prompt"], "generated": code})

        out_file = OUTPUT_DIR / f"{task['id']}.c"
        out_file.write_text(code, encoding="utf-8")
        print(f"  → 저장: {out_file}")

    summary_file = OUTPUT_DIR / "results.json"
    summary_file.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"\n완료! {len(TASKS)}개 파일 생성 → {OUTPUT_DIR}/")
    print(f"요약: {summary_file}")


if __name__ == "__main__":
    main()
