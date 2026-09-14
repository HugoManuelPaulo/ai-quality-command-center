from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ai_quality import evaluate_case, evaluate_suite, load_scenarios

app = FastAPI(
    title="AI Quality Command Center API",
    version="1.0.0",
    description="Provider-neutral evaluation API for LLM quality, safety and compliance checks.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai-quality-command-center"}


@app.get("/api/evaluations")
def evaluations():
    return evaluate_suite(load_scenarios())


@app.get("/api/summary")
def summary():
    return evaluate_suite(load_scenarios())["summary"]


@app.get("/api/evaluations/{case_id}")
def evaluation(case_id: str):
    case = next((item for item in load_scenarios() if item["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Evaluation case not found")
    return evaluate_case(case)


@app.post("/api/evaluate")
def evaluate(payload: dict):
    required = {"id", "category", "risk_level", "prompt", "response", "latency_ms", "cost_usd"}
    if not required.issubset(payload):
        raise HTTPException(status_code=422, detail="Missing required evaluation fields")
    payload.setdefault("reference_terms", [])
    payload.setdefault("expect_refusal", False)
    payload.setdefault("assistant_disclosed", True)
    payload.setdefault("allow_pii", False)
    payload.setdefault("high_impact", False)
    payload.setdefault("human_review", True)
    return evaluate_case(payload)
