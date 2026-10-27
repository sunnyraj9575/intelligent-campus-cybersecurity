from pathlib import Path

from src.data_generator import generate_dataset
from src.train import train_model


def test_generated_dataset_has_all_attack_types():
    frame = generate_dataset(samples_per_class=8, seed=7)
    assert len(frame) == 8 * 6
    assert set(frame["attack_type"]) == {
        "benign",
        "brute_force",
        "dos",
        "port_scan",
        "data_exfiltration",
        "malware_c2",
    }


def test_training_produces_metrics_and_model(tmp_path: Path):
    data_path = tmp_path / "flows.csv"
    model_path = tmp_path / "model.joblib"
    metrics_path = tmp_path / "metrics.json"
    generate_dataset(samples_per_class=20, seed=1).to_csv(data_path, index=False)
    metrics = train_model(data_path, model_path, metrics_path)
    assert model_path.exists()
    assert metrics_path.exists()
    assert metrics["accuracy"] > 0.7
