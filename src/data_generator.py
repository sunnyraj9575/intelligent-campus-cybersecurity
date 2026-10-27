"""Generate a reproducible, synthetic campus network-flow dataset.

The generated data is for demonstrations and coursework only. It mirrors the
shape of common flow records; it is not a replacement for a real labelled
network capture or an operational security sensor.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .features import ATTACK_TYPES, FEATURE_COLUMNS, TARGET_COLUMN


def _positive_normal(rng: np.random.Generator, mean: float, std: float, size: int) -> np.ndarray:
    return np.maximum(0, rng.normal(mean, std, size))


def _integer_poisson(rng: np.random.Generator, mean: float, size: int) -> np.ndarray:
    return rng.poisson(mean, size).astype(float)


def generate_dataset(samples_per_class: int = 500, seed: int = 42) -> pd.DataFrame:
    """Create labelled network-flow rows with realistic class-specific signals."""

    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []

    for attack_type in ATTACK_TYPES:
        n = samples_per_class
        if attack_type == "benign":
            duration = _positive_normal(rng, 38, 20, n)
            bytes_sent = _positive_normal(rng, 18_000, 8_000, n)
            bytes_received = _positive_normal(rng, 42_000, 18_000, n)
            packets_sent = _integer_poisson(rng, 80, n)
            packets_received = _integer_poisson(rng, 150, n)
            failed_logins = _integer_poisson(rng, 0.3, n)
            unique_dst_ports = _integer_poisson(rng, 3, n) + 1
            connection_rate = _positive_normal(rng, 4, 2, n)
            dns_queries = _integer_poisson(rng, 4, n)
            external_connections = _integer_poisson(rng, 2, n)
            payload_entropy = np.clip(rng.normal(4.3, 0.8, n), 0, 8)
            src_reputation = np.clip(rng.normal(0.85, 0.1, n), 0, 1)
            protocol = rng.choice(["tcp", "udp", "icmp"], n, p=[0.65, 0.3, 0.05])
            service = rng.choice(["http", "https", "dns", "ssh", "other"], n)
            direction = rng.choice(["internal_to_internal", "internal_to_external"], n, p=[0.7, 0.3])
            auth_method = rng.choice(["none", "password", "kerberos", "certificate"], n)
        elif attack_type == "brute_force":
            duration = _positive_normal(rng, 95, 35, n)
            bytes_sent = _positive_normal(rng, 7_000, 3_000, n)
            bytes_received = _positive_normal(rng, 9_000, 4_000, n)
            packets_sent = _integer_poisson(rng, 48, n)
            packets_received = _integer_poisson(rng, 45, n)
            failed_logins = _integer_poisson(rng, 22, n) + 5
            unique_dst_ports = _integer_poisson(rng, 1.5, n) + 1
            connection_rate = _positive_normal(rng, 14, 4, n)
            dns_queries = _integer_poisson(rng, 1, n)
            external_connections = _integer_poisson(rng, 7, n)
            payload_entropy = np.clip(rng.normal(3.2, 0.7, n), 0, 8)
            src_reputation = np.clip(rng.normal(0.22, 0.12, n), 0, 1)
            protocol = rng.choice(["tcp", "udp"], n, p=[0.9, 0.1])
            service = rng.choice(["ssh", "rdp", "other"], n, p=[0.55, 0.35, 0.1])
            direction = np.array(["external_to_internal"] * n)
            auth_method = np.array(["password"] * n)
        elif attack_type == "dos":
            duration = _positive_normal(rng, 8, 4, n)
            bytes_sent = _positive_normal(rng, 180_000, 70_000, n)
            bytes_received = _positive_normal(rng, 25_000, 12_000, n)
            packets_sent = _integer_poisson(rng, 1_200, n)
            packets_received = _integer_poisson(rng, 260, n)
            failed_logins = _integer_poisson(rng, 0.5, n)
            unique_dst_ports = _integer_poisson(rng, 2, n) + 1
            connection_rate = _positive_normal(rng, 120, 35, n)
            dns_queries = _integer_poisson(rng, 1, n)
            external_connections = _integer_poisson(rng, 25, n)
            payload_entropy = np.clip(rng.normal(2.2, 0.6, n), 0, 8)
            src_reputation = np.clip(rng.normal(0.12, 0.08, n), 0, 1)
            protocol = rng.choice(["tcp", "udp", "icmp"], n, p=[0.55, 0.35, 0.1])
            service = rng.choice(["http", "https", "dns"], n, p=[0.6, 0.25, 0.15])
            direction = np.array(["external_to_internal"] * n)
            auth_method = np.array(["none"] * n)
        elif attack_type == "port_scan":
            duration = _positive_normal(rng, 24, 12, n)
            bytes_sent = _positive_normal(rng, 12_000, 5_000, n)
            bytes_received = _positive_normal(rng, 5_000, 3_000, n)
            packets_sent = _integer_poisson(rng, 180, n)
            packets_received = _integer_poisson(rng, 90, n)
            failed_logins = _integer_poisson(rng, 2, n)
            unique_dst_ports = _integer_poisson(rng, 45, n) + 10
            connection_rate = _positive_normal(rng, 55, 18, n)
            dns_queries = _integer_poisson(rng, 2, n)
            external_connections = _integer_poisson(rng, 15, n)
            payload_entropy = np.clip(rng.normal(2.8, 0.7, n), 0, 8)
            src_reputation = np.clip(rng.normal(0.18, 0.1, n), 0, 1)
            protocol = rng.choice(["tcp", "udp"], n, p=[0.75, 0.25])
            service = np.array(["other"] * n)
            direction = np.array(["external_to_internal"] * n)
            auth_method = np.array(["none"] * n)
        elif attack_type == "data_exfiltration":
            duration = _positive_normal(rng, 240, 80, n)
            bytes_sent = _positive_normal(rng, 900_000, 260_000, n)
            bytes_received = _positive_normal(rng, 60_000, 25_000, n)
            packets_sent = _integer_poisson(rng, 2_000, n)
            packets_received = _integer_poisson(rng, 300, n)
            failed_logins = _integer_poisson(rng, 1, n)
            unique_dst_ports = _integer_poisson(rng, 2, n) + 1
            connection_rate = _positive_normal(rng, 18, 7, n)
            dns_queries = _integer_poisson(rng, 8, n)
            external_connections = _integer_poisson(rng, 18, n)
            payload_entropy = np.clip(rng.normal(7.2, 0.4, n), 0, 8)
            src_reputation = np.clip(rng.normal(0.32, 0.14, n), 0, 1)
            protocol = np.array(["tcp"] * n)
            service = rng.choice(["https", "other", "dns"], n, p=[0.65, 0.25, 0.1])
            direction = np.array(["internal_to_external"] * n)
            auth_method = rng.choice(["certificate", "kerberos", "password"], n)
        else:  # malware_c2
            duration = _positive_normal(rng, 70, 30, n)
            bytes_sent = _positive_normal(rng, 22_000, 9_000, n)
            bytes_received = _positive_normal(rng, 18_000, 8_000, n)
            packets_sent = _integer_poisson(rng, 120, n)
            packets_received = _integer_poisson(rng, 110, n)
            failed_logins = _integer_poisson(rng, 1, n)
            unique_dst_ports = _integer_poisson(rng, 2, n) + 1
            connection_rate = _positive_normal(rng, 9, 3, n)
            dns_queries = _integer_poisson(rng, 28, n) + 5
            external_connections = _integer_poisson(rng, 20, n) + 3
            payload_entropy = np.clip(rng.normal(6.4, 0.6, n), 0, 8)
            src_reputation = np.clip(rng.normal(0.28, 0.12, n), 0, 1)
            protocol = rng.choice(["tcp", "udp"], n, p=[0.65, 0.35])
            service = rng.choice(["dns", "https", "other"], n, p=[0.5, 0.35, 0.15])
            direction = np.array(["internal_to_external"] * n)
            auth_method = rng.choice(["none", "password"], n)

        for i in range(n):
            row = {
                "duration_seconds": round(float(duration[i]), 3),
                "bytes_sent": round(float(bytes_sent[i]), 3),
                "bytes_received": round(float(bytes_received[i]), 3),
                "packets_sent": int(packets_sent[i]),
                "packets_received": int(packets_received[i]),
                "failed_logins": int(failed_logins[i]),
                "unique_dst_ports": int(unique_dst_ports[i]),
                "connection_rate": round(float(connection_rate[i]), 3),
                "dns_queries": int(dns_queries[i]),
                "external_connections": int(external_connections[i]),
                "payload_entropy": round(float(payload_entropy[i]), 3),
                "src_reputation": round(float(src_reputation[i]), 3),
                "protocol": str(protocol[i]),
                "service": str(service[i]),
                "direction": str(direction[i]),
                "auth_method": str(auth_method[i]),
                TARGET_COLUMN: attack_type,
            }
            rows.append(row)

    frame = pd.DataFrame(rows)
    return frame[FEATURE_COLUMNS + [TARGET_COLUMN]].sample(frac=1, random_state=seed).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/demo_network_flows.csv"))
    parser.add_argument("--samples-per-class", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_dataset(args.samples_per_class, args.seed)
    frame.to_csv(args.output, index=False)
    print(f"Wrote {len(frame):,} labelled flows to {args.output}")


if __name__ == "__main__":
    main()
