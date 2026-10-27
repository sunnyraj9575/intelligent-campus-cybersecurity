"""FastAPI service exposing the trained threat detector."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

MODEL_PATH = Path(os.getenv("SENTINEL_MODEL_PATH", "models/threat_detector.joblib"))
app = FastAPI(
    title="Sentinel Campus Threat Detection API",
    version="1.0.0",
    description="Supervised ML classification of campus network-flow security threats.",
)


class NetworkFlow(BaseModel):
    duration_seconds: float = Field(ge=0)
    bytes_sent: float = Field(ge=0)
    bytes_received: float = Field(ge=0)
    packets_sent: float = Field(ge=0)
    packets_received: float = Field(ge=0)
    failed_logins: float = Field(ge=0)
    unique_dst_ports: float = Field(ge=0)
    connection_rate: float = Field(ge=0)
    dns_queries: float = Field(ge=0)
    external_connections: float = Field(ge=0)
    payload_entropy: float = Field(ge=0, le=8)
    src_reputation: float = Field(ge=0, le=1)
    protocol: str
    service: str
    direction: str
    auth_method: str


@lru_cache(maxsize=1)
def get_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}. Run `python -m src.train` first.")
    return joblib.load(MODEL_PATH)


def _predict(flow: NetworkFlow) -> dict:
    try:
        model = get_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    values = flow.model_dump()
    frame = pd.DataFrame([values])[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    probabilities = model.predict_proba(frame)[0]
    classes = model.named_steps["classifier"].classes_
    prediction = str(model.predict(frame)[0])
    return {
        "prediction": prediction,
        "confidence": round(float(max(probabilities)), 4),
        "probabilities": {
            str(label): round(float(probability), 4)
            for label, probability in zip(classes, probabilities)
        },
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_available": MODEL_PATH.exists(), "model_path": str(MODEL_PATH)}


@app.post("/predict")
def predict(flow: NetworkFlow) -> dict:
    return _predict(flow)


@app.post("/predict/batch")
def predict_batch(flows: list[NetworkFlow]) -> dict:
    if not flows:
        raise HTTPException(status_code=400, detail="At least one flow is required")
    return {"count": len(flows), "results": [_predict(flow) for flow in flows]}
