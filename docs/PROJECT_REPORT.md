# Project Report: Intelligent Campus Cybersecurity Threat Detection System

## 1. Problem statement

Campus networks connect students, faculty, research systems, IoT devices, and administrative services. A large volume of routine traffic makes manual review difficult. This project uses supervised machine learning to classify a network flow as benign or as one of five potential threat categories.

## 2. Objectives

1. Convert network-flow observations into a consistent machine-learning feature schema.
2. Train a multi-class classifier for suspicious activity.
3. Evaluate the model with accuracy, macro F1, a classification report, and a confusion matrix.
4. Expose predictions through a reproducible command-line workflow and an HTTP API.
5. Provide a path from synthetic demonstration data to institution-approved labelled traffic.

## 3. Methodology

The baseline pipeline uses a `ColumnTransformer`. Numeric features are standardized, categorical features are one-hot encoded, and a class-balanced `RandomForestClassifier` makes the final prediction. A stratified 80/20 train-test split is used so every threat class appears in both partitions.

The six labels are:

- benign traffic;
- brute-force authentication activity;
- denial-of-service-like traffic;
- port scanning;
- data-exfiltration-like traffic;
- malware command-and-control-like traffic.

The demo generator creates these labels from traffic-volume, packet, authentication, DNS, external-connection, entropy, and reputation signals. It is designed to make the software reproducible; it does not claim that synthetic distributions represent a real campus.

## 4. Evaluation

After running `python -m src.train`, inspect `reports/metrics.json`. The report includes overall accuracy, macro F1, per-class precision/recall/F1, and a confusion matrix. Macro F1 is emphasized because it weights each class equally and is more informative than accuracy when real data becomes imbalanced.

## 5. Limitations

- Synthetic data cannot measure real-world generalization.
- Flow-level features do not provide packet payload or host context.
- Labels may be noisy or incomplete in real incident data.
- Attack patterns evolve and can create concept drift.
- A prediction is a triage signal, not proof of malicious intent.

## 6. Future enhancements

- validate on a time-separated, institution-approved test set;
- compare Random Forest with gradient boosting and calibrated linear baselines;
- add explainability using feature importance and per-alert reason codes;
- add drift monitoring, alert suppression, and analyst feedback;
- integrate with a SIEM through an authenticated message queue;
- protect the API with authentication, rate limits, structured audit logs, and network segmentation.
