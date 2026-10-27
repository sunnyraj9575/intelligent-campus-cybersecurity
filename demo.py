"""Run the complete Sentinel Campus demonstration in one command.

Usage:
    python demo.py

This demo creates the reproducible sample data, trains the classifier, prints
evaluation metrics, and predicts two example network flows. It is intended for
classroom demonstration and does not connect to live campus traffic.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.data_generator import generate_dataset
from src.features import TARGET_COLUMN
from src.predict import predict_flow
from src.train import train_model


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "demo_network_flows.csv"
MODEL_PATH = ROOT / "models" / "threat_detector.joblib"
METRICS_PATH = ROOT / "reports" / "metrics.json"


def main() -> None:
    print("=" * 72)
    print("SENTINEL CAMPUS - INTELLIGENT CYBERSECURITY DEMONSTRATION")
    print("=" * 72)

    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_dataset(samples_per_class=500, seed=42)
    frame.to_csv(DATA_PATH, index=False)
    print(f"\n[1/4] Generated {len(frame):,} labelled network flows")
    print(f"      Threat classes: {', '.join(sorted(frame[TARGET_COLUMN].unique()))}")

    metrics = train_model(DATA_PATH, MODEL_PATH, METRICS_PATH, seed=42)
    print("\n[2/4] Trained Random Forest classifier")
    print(f"      Accuracy: {metrics['accuracy']:.4f}")
    print(f"      Macro F1:  {metrics['macro_f1']:.4f}")

    print("\n[3/4] Per-class F1 scores")
    for label in metrics["classes"]:
        score = metrics["classification_report"][label]["f1-score"]
        print(f"      {label:20s} {score:.4f}")

    benign = frame[frame[TARGET_COLUMN] == "benign"].drop(columns=[TARGET_COLUMN]).iloc[0].to_dict()
    suspicious = frame[frame[TARGET_COLUMN] == "port_scan"].drop(columns=[TARGET_COLUMN]).iloc[0].to_dict()
    print("\n[4/4] Example predictions")
    for name, flow in [("normal campus flow", benign), ("suspicious scanning flow", suspicious)]:
        result = predict_flow(MODEL_PATH, flow)
        print(f"\n      {name}")
        print(f"      prediction: {result['prediction']}")
        print(f"      confidence: {result['confidence']:.4f}")
        print(f"      probabilities: {json.dumps(result['probabilities'])}")

    print("\nArtifacts created:")
    print(f"  Dataset: {DATA_PATH.relative_to(ROOT)}")
    print(f"  Model:   {MODEL_PATH.relative_to(ROOT)}")
    print(f"  Metrics: {METRICS_PATH.relative_to(ROOT)}")
    print("\nTo show the interactive API, run:")
    print("  uvicorn src.api:app --reload")
    print("  Then open http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    main()
