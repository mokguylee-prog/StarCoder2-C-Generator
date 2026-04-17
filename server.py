"""StarCoder2 코드 생성 API 서버 (CPU/GGUF 전용)"""
from pathlib import Path
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("설치 필요: pip install fastapi uvicorn")
    raise

try:
    from llama_cpp import Llama
except ImportError:
    print("설치 필요: pip install llama-cpp-python")
    raise

# ── 설정 ──────────────────────────────────────────
MODEL_DIR  = Path("D:/StarCoder2/models/gguf")
MODEL_FILE = "starcoder2-3b-Q4_K_M.gguf"
PORT       = 8888

FIM_PREFIX = "<fim_prefix>"
FIM_SUFFIX = "<fim_suffix>"
FIM_MIDDLE = "<fim_middle>"

# ── 앱 초기화 ──────────────────────────────────────
app = FastAPI(title="StarCoder2 API", version="1.0")
llm: Optional[Llama] = None


def find_model() -> Path:
    path = MODEL_DIR / MODEL_FILE
    if path.exists():
        return path
    found = list(MODEL_DIR.glob("*.gguf"))
    if found:
        return found[0]
    raise FileNotFoundError(f"모델 없음: {MODEL_DIR}\n먼저 실행: python scripts/download_model.py")


@app.on_event("startup")
def load_model():
    global llm
    model_path = find_model()
    print(f"모델 로딩: {model_path.name} ...")
    llm = Llama(model_path=str(model_path), n_ctx=4096, n_threads=None, verbose=False)
    print("준비 완료 — 서버 시작")


# ── 요청/응답 스키마 ───────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str                  # 부분 C 코드 (코드 완성 형식)
    max_tokens: int   = 256
    temperature: float = 0.2
    top_p: float      = 0.95

class FimRequest(BaseModel):
    prefix: str                  # 앞부분 코드
    suffix: str                  # 뒷부분 코드
    max_tokens: int   = 128
    temperature: float = 0.2

class GenerateResponse(BaseModel):
    generated: str
    tokens_generated: int


# ── 엔드포인트 ─────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_FILE}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """부분 C 코드를 받아 완성된 코드를 반환합니다."""
    if llm is None:
        raise HTTPException(503, "모델 로딩 중")

    out = llm(
        req.prompt,
        max_tokens=req.max_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        stop=["}\n\n", "\n\n\n"],
        echo=True,
    )
    text = out["choices"][0]["text"]
    tokens = out["usage"]["completion_tokens"]
    return GenerateResponse(generated=text, tokens_generated=tokens)


@app.post("/fim", response_model=GenerateResponse)
def fim(req: FimRequest):
    """앞부분 + 뒷부분을 받아 중간 코드를 채워 반환합니다."""
    if llm is None:
        raise HTTPException(503, "모델 로딩 중")

    prompt = f"{FIM_PREFIX}{req.prefix}{FIM_SUFFIX}{req.suffix}{FIM_MIDDLE}"
    out = llm(prompt, max_tokens=req.max_tokens, temperature=req.temperature, echo=False)
    middle = out["choices"][0]["text"]
    tokens = out["usage"]["completion_tokens"]
    return GenerateResponse(generated=middle, tokens_generated=tokens)


if __name__ == "__main__":
    print(f"StarCoder2 서버: http://localhost:{PORT}")
    print(f"API 문서:        http://localhost:{PORT}/docs")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
