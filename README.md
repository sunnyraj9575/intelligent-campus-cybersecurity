# Sentinel Campus — Intelligent Campus Cybersecurity Threat Detection System

Sentinel Campus is a supervised machine-learning project for identifying suspicious campus network activity and classifying likely security threats.

The repository includes:

- a reproducible synthetic network-flow generator for demonstrations;
- a scikit-learn training pipeline using a balanced Random Forest classifier;
- evaluation metrics and class-level reports;
- a command-line prediction tool;
- a FastAPI service with `/health`, `/predict`, and `/predict/batch` endpoints;
- a responsive project landing page in `index.html`;
- a short academic project report in `docs/PROJECT_REPORT.md`.

The demo data is intentionally synthetic. For a real deployment, replace it with labelled flow records collected under your institution's privacy, governance, and security policies.

## Threat classes

The baseline classifier distinguishes six classes:

`benign`, `brute_force`, `dos`, `port_scan`, `data_exfiltration`, and `malware_c2`.

Each flow contains traffic-volume, connection-behaviour, authentication, protocol, service, and source-reputation features. The authoritative feature list is in `src/features.py`.

## Quick start

Use Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Generate the demo dataset and train the model:

```powershell
python -m src.data_generator --output data/demo_network_flows.csv --samples-per-class 500
python -m src.train
```

Training writes the model to `models/threat_detector.joblib` and evaluation results to `reports/metrics.json`. These generated artifacts are ignored by Git so they can be rebuilt for each environment.

Run the test suite:

```powershell
pytest
```

## Run the API

```powershell
uvicorn src.api:app --reload
```

Open the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Example request:

```powershell
curl.exe -X POST http://127.0.0.1:8000/predict `
  -H "Content-Type: application/json" `
  -d "{\"duration_seconds\":12,\"bytes_sent\":180000,\"bytes_received\":24000,\"packets_sent\":1100,\"packets_received\":240,\"failed_logins\":0,\"unique_dst_ports\":2,\"connection_rate\":130,\"dns_queries\":1,\"external_connections\":25,\"payload_entropy\":2.1,\"src_reputation\":0.1,\"protocol\":\"tcp\",\"service\":\"http\",\"direction\":\"external_to_internal\",\"auth_method\":\"none\"}"
```

The response contains the predicted class, confidence, and probabilities for every learned class.

## Command-line prediction

Create a JSON file with one network flow using the fields in `src/features.py`, then run:

```powershell
python -m src.predict --input path\to\flow.json
```

## Use a real dataset

Export a CSV with the same column names as `data/demo_network_flows.csv`, including the labelled `attack_type` column. Then train with:

```powershell
python -m src.train --data path\to\your\labelled_flows.csv
```

Candidate sources for future work include institution-approved NetFlow/IPFIX exports, a carefully governed campus sensor, or a public intrusion-detection benchmark. Public benchmark labels and feature definitions should be mapped explicitly before training; do not assume that a benchmark model is valid for live campus traffic.

## Project layout

```text
src/
  api.py             FastAPI inference service
  data_generator.py  reproducible demo-data generator
  features.py        shared schema and class definitions
  predict.py         command-line inference
  train.py           preprocessing, training, and evaluation
tests/               automated tests
docs/                academic project report and methodology
index.html           project landing page
styles.css           landing-page styles
script.js            landing-page interactions
```

## Responsible use

This is a coursework and research baseline, not an autonomous incident-response system. Predictions should be reviewed by a security analyst, thresholds should be validated on local traffic, and sensitive network data must be collected, stored, and shared according to institutional policy. Model performance can degrade when campus traffic changes, so monitor drift and retrain with fresh labelled examples.
