"""Feature definitions shared by data generation, training, and inference."""

from __future__ import annotations

NUMERIC_FEATURES = [
    "duration_seconds",
    "bytes_sent",
    "bytes_received",
    "packets_sent",
    "packets_received",
    "failed_logins",
    "unique_dst_ports",
    "connection_rate",
    "dns_queries",
    "external_connections",
    "payload_entropy",
    "src_reputation",
]

CATEGORICAL_FEATURES = [
    "protocol",
    "service",
    "direction",
    "auth_method",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "attack_type"
ATTACK_TYPES = [
    "benign",
    "brute_force",
    "dos",
    "port_scan",
    "data_exfiltration",
    "malware_c2",
]

