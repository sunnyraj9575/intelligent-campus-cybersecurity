"""Train and evaluate the supervised campus threat classifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .features import ATTACK_TYPES, CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET_COLUMN


def build_pipeline(seed: int = 42) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=250,
        max_depth=18,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=seed,
        # One worker keeps the project portable to restricted Windows hosts.
        # Increase this after deployment if the execution environment permits
        # multiprocessing and the dataset becomes substantially larger.
        n_jobs=1,
    )
    return Pipeline([("preprocessor", preprocessor), ("classifier", classifier)])


def train_model(data_path: Path, model_path: Path, metrics_path: Path, seed: int = 42) -> dict:
    frame = pd.read_csv(data_path)
    expected = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN])
    missing = expected - set(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    x = frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = frame[TARGET_COLUMN]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=seed, stratify=y
    )

    pipeline = build_pipeline(seed)
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    labels = [label for label in ATTACK_TYPES if label in y.unique()]
    report = classification_report(y_test, predictions, labels=labels, output_dict=True, zero_division=0)
    metrics = {
        "model": "RandomForestClassifier",
        "dataset": str(data_path),
        "samples": int(len(frame)),
        "train_samples": int(len(x_train)),
        "test_samples": int(len(x_test)),
        "classes": labels,
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "macro_f1": round(float(f1_score(y_test, predictions, average="macro")), 4),
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=labels).tolist(),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/demo_network_flows.csv"))
    parser.add_argument("--model", type=Path, default=Path("models/threat_detector.joblib"))
    parser.add_argument("--metrics", type=Path, default=Path("reports/metrics.json"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    metrics = train_model(args.data, args.model, args.metrics, args.seed)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1:  {metrics['macro_f1']:.4f}")
    print(f"Model:     {args.model}")


if __name__ == "__main__":
    main()
