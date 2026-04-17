"""StarCoder2 FastAPI 서버 - HTTP API로 C 코드 생성 제공"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TextIteratorStreamer
from threading import Thread

try:
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("설치 필요: pip install fastapi uvicorn")
    raise

CHECKPOINT = "bigcode/starcoder2-7b"
PORT = 8888

app = FastAPI(title="StarCoder2 C Code API")

tokenizer = None
model = None


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.2
    top_p: float = 0.95
    stream: bool = False


class GenerateResponse(BaseModel):
    generated: str
    prompt_tokens: int
    generated_tokens: int


@app.on_event("startup")
def load_model():
    global tokenizer, model
    print(f"모델 로딩: {CHECKPOINT}")

    quant_config = None
    dtype = torch.bfloat16

    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory // 1024**3
        print(f"GPU: {torch.cuda.get_device_name(0)} ({vram_gb} GB)")
        if vram_gb < 14:
            print("→ 4-bit 양자화 적용")
            dtype = None
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
            )
    else:
        print("→ CPU 모드")
        dtype = torch.float32

    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model = AutoModelForCausalLM.from_pretrained(
        CHECKPOINT,
        device_map="auto",
        torch_dtype=dtype,
        quantization_config=quant_config,
    )
    model.eval()
    print("서버 준비 완료")


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    inputs = tokenizer.encode(req.prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=req.max_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_ids = outputs[0][inputs.shape[1]:]
    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    return GenerateResponse(
        generated=req.prompt + generated_text,
        prompt_tokens=inputs.shape[1],
        generated_tokens=len(generated_ids),
    )


@app.get("/health")
def health():
    return {"status": "ok", "model": CHECKPOINT}


if __name__ == "__main__":
    print(f"StarCoder2 API 서버 시작: http://localhost:{PORT}")
    print("사용 예시:")
    print(f'  curl -X POST http://localhost:{PORT}/generate \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "int factorial(int n) {\\n", "max_tokens": 128}\'')
    uvicorn.run(app, host="0.0.0.0", port=PORT)
