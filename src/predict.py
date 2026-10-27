"""Run a single threat prediction from a JSON object or JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from .features import CATEGORICAL_FEATURES, NUMERIC_FEATURES


def predict_flow(model_path: Path, flow: dict) -> dict:
    model = joblib.load(model_path)
    frame = pd.DataFrame([flow])[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    prediction = str(model.predict(frame)[0])
    probabilities = model.predict_proba(frame)[0]
    classes = model.named_steps["classifier"].classes_
    confidence = float(max(probabilities))
    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "probabilities": {
            str(label): round(float(probability), 4)
            for label, probability in zip(classes, probabilities)
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=Path("models/threat_detector.joblib"))
    parser.add_argument("--input", type=Path, help="JSON file containing one flow")
    args = parser.parse_args()
    if args.input:
        flow = json.loads(args.input.read_text(encoding="utf-8"))
    else:
        flow = json.loads(input("Paste flow JSON: "))
    print(json.dumps(predict_flow(args.model, flow), indent=2))


if __name__ == "__main__":
    main()
