"""
api.py
-------
RAG asistanı ve log anomali tespitini bir REST API üzerinden erişilebilir kılar.
Çalıştırma: uvicorn src.api:app --reload
Sonra http://localhost:8000/docs adresinden interaktif olarak test edilebilir.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from src.rag_pipeline import generate_answer, Retriever
from src.anomaly_detection import detect_anomalies_zscore, summarize_anomaly

app = FastAPI(
    title="pandas Docs Copilot (Demo)",
    description="pandas dokümantasyon RAG asistanı + API log anomali tespiti",
    version="0.1.0",
)

_retriever = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    llm_used: bool


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    result = generate_answer(request.question, retriever=get_retriever())
    return AskResponse(
        answer=result.answer,
        sources=sorted(set(c.source_file for c in result.retrieved_chunks)),
        llm_used=result.llm_used,
    )


class LogCheckResponse(BaseModel):
    total_rows: int
    anomalies_found: int
    examples: list[str]


@app.get("/check-logs", response_model=LogCheckResponse)
def check_logs(limit: int = 5):
    df = pd.read_csv("data/logs/synthetic_api_logs.csv", parse_dates=["timestamp"])
    result_df = detect_anomalies_zscore(df)
    detected = result_df[result_df["predicted_anomaly"]].head(limit)
    examples = [summarize_anomaly(row) for _, row in detected.iterrows()]

    return LogCheckResponse(
        total_rows=len(df),
        anomalies_found=int(result_df["predicted_anomaly"].sum()),
        examples=examples,
    )


@app.get("/")
def root():
    return {
        "message": "pandas Docs Copilot demo API'sine hoş geldiniz.",
        "endpoints": ["/ask (POST)", "/check-logs (GET)", "/docs"],
    }
