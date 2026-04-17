"""Instruction-following 코드 생성 API 서버 (llama-cpp-python + GGUF)"""
import os
import glob
from typing import Optional

try:
    from llama_cpp import Llama
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError as e:
    print(f"설치 필요: pip install llama-cpp-python fastapi uvicorn\n{e}")
    raise

# ── 설정 ──────────────────────────────────────────
MODEL_DIR = "D:/StarCoder3/models/gguf"
PORT = 8888
N_CTX = 4096       # 컨텍스트 길이
N_THREADS = 8      # CPU 스레드 수 (코어 수에 맞게 조정)
N_GPU_LAYERS = 0   # CPU 전용이므로 0

# 시스템 프롬프트 — Claude처럼 자연어 지시를 따름
SYSTEM_PROMPT = (
    "You are an expert C/C++ programming assistant. "
    "When the user asks you to write code, provide complete, working code. "
    "When creating project files, show the full file contents. "
    "Respond in the same language the user writes in (Korean if Korean, English if English). "
    "Keep explanations concise unless asked for details."
)

app = FastAPI(title="StarCoder3 Instruction API")
llm: Optional[Llama] = None
model_name: str = ""


def find_model() -> str:
    files = glob.glob(os.path.join(MODEL_DIR, "*.gguf"))
    if not files:
        raise FileNotFoundError(
            f"GGUF 모델이 없습니다: {MODEL_DIR}\n"
            "python scripts/download_model.py 로 다운로드하세요."
        )
    # 가장 큰 파일 = 품질 우선
    return max(files, key=os.path.getsize)


class ChatMessage(BaseModel):
    role: str   # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    max_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.95
    stream: bool = False


class GenerateRequest(BaseModel):
    prompt: str
    system: str = SYSTEM_PROMPT
    max_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.95
    stream: bool = False


class GenerateResponse(BaseModel):
    generated: str
    model: str
    prompt_tokens: int
    generated_tokens: int


@app.on_event("startup")
def load_model():
    global llm, model_name
    path = find_model()
    model_name = os.path.basename(path)
    print(f"모델 로딩: {model_name}")
    llm = Llama(
        model_path=path,
        n_ctx=N_CTX,
        n_threads=N_THREADS,
        n_gpu_layers=N_GPU_LAYERS,
        verbose=False,
    )
    print("서버 준비 완료")


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    if llm is None:
        raise HTTPException(503, "모델 로딩 중")

    messages = [
        {"role": "system", "content": req.system},
        {"role": "user",   "content": req.prompt},
    ]

    result = llm.create_chat_completion(
        messages=messages,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
    )
    choice = result["choices"][0]
    generated = choice["message"]["content"]
    usage = result.get("usage", {})

    return GenerateResponse(
        generated=generated,
        model=model_name,
        prompt_tokens=usage.get("prompt_tokens", 0),
        generated_tokens=usage.get("completion_tokens", 0),
    )


@app.post("/chat")
def chat(req: ChatRequest):
    """다중 턴 대화 — 클라이언트가 히스토리를 직접 전달"""
    if llm is None:
        raise HTTPException(503, "모델 로딩 중")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    if not messages or messages[0]["role"] != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    result = llm.create_chat_completion(
        messages=messages,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
    )
    choice = result["choices"][0]
    return {
        "message": choice["message"],
        "model": model_name,
        "usage": result.get("usage", {}),
    }


@app.get("/health")
def health():
    return {"status": "ok", "model": model_name}


if __name__ == "__main__":
    print(f"StarCoder3 API 서버 시작: http://localhost:{PORT}")
    print("자연어로 코드를 요청하세요 (instruction-following 모드)")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
