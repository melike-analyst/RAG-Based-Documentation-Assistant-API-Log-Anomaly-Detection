"""
generate_api_logs.py
----------------------
Pandas tabanlı bir veri işleme servisinin (hayali bir "DataOps API") isteklerine ait
sentetik log verisi üretir. Gerçek bir servisin loglarına erişimimiz olmadığı için tamamen
sentetik ama gerçekçi bir dağılımla üretilmiştir.

Üretilen sütunlar:
- timestamp
- endpoint: /process, /aggregate, /merge, /export gibi hayali uç noktalar
- latency_ms: isteğin yanıt süresi
- status_code: HTTP durum kodu (200, 400, 500 vb.)
- rows_processed: işlenen satır sayısı
- memory_mb: işlem sırasında kullanılan yaklaşık bellek
- is_anomaly / anomaly_type: ground truth etiketi (sadece değerlendirme amaçlı, gerçek
  sistemde bulunmaz)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG_SEED = 7
N_REQUESTS = 3000
ENDPOINTS = ["/process", "/aggregate", "/merge", "/export"]

NORMAL_LATENCY_RANGE = (50, 400)      # ms
NORMAL_MEMORY_RANGE = (80, 350)       # MB
NORMAL_ROWS_RANGE = (100, 50000)


def generate_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    base_time = datetime(2026, 9, 1, 0, 0, 0)

    timestamps = [base_time + timedelta(seconds=int(30 * i)) for i in range(N_REQUESTS)]
    endpoints = rng.choice(ENDPOINTS, size=N_REQUESTS, p=[0.4, 0.3, 0.2, 0.1])

    rows_processed = rng.integers(*NORMAL_ROWS_RANGE, size=N_REQUESTS)
    # latency, işlenen satır sayısıyla hafifçe pozitif korelasyonlu (gerçekçi bir varsayım)
    base_latency = NORMAL_LATENCY_RANGE[0] + (rows_processed / NORMAL_ROWS_RANGE[1]) * (
        NORMAL_LATENCY_RANGE[1] - NORMAL_LATENCY_RANGE[0]
    )
    latency_ms = base_latency + rng.normal(0, 15, size=N_REQUESTS)
    latency_ms = np.clip(latency_ms, 10, None)

    memory_mb = rng.uniform(*NORMAL_MEMORY_RANGE, size=N_REQUESTS)
    status_code = rng.choice([200, 200, 200, 200, 400], size=N_REQUESTS, p=[0.85, 0.05, 0.05, 0.03, 0.02])

    df = pd.DataFrame({
        "timestamp": timestamps,
        "endpoint": endpoints,
        "latency_ms": latency_ms,
        "status_code": status_code,
        "rows_processed": rows_processed,
        "memory_mb": memory_mb,
    })
    return df


def inject_anomalies(df: pd.DataFrame, rng: np.random.Generator, anomaly_rate: float = 0.05) -> pd.DataFrame:
    df = df.copy()
    df["is_anomaly"] = False
    df["anomaly_type"] = "normal"

    n_anomalies = int(len(df) * anomaly_rate)
    anomaly_indices = rng.choice(df.index, size=n_anomalies, replace=False)

    for idx in anomaly_indices:
        anomaly_type = rng.choice(
            ["latency_spike", "error_spike", "memory_spike"], p=[0.45, 0.30, 0.25]
        )
        if anomaly_type == "latency_spike":
            df.loc[idx, "latency_ms"] = df.loc[idx, "latency_ms"] * rng.uniform(4, 8)
        elif anomaly_type == "error_spike":
            df.loc[idx, "status_code"] = rng.choice([500, 502, 504])
        else:
            df.loc[idx, "memory_mb"] = df.loc[idx, "memory_mb"] * rng.uniform(3, 5)

        df.loc[idx, "is_anomaly"] = True
        df.loc[idx, "anomaly_type"] = anomaly_type

    return df


if __name__ == "__main__":
    rng = np.random.default_rng(RNG_SEED)
    df = generate_dataset()
    df = inject_anomalies(df, rng)

    output_path = "data/logs/synthetic_api_logs.csv"
    df.to_csv(output_path, index=False)
    print(f"{len(df)} satırlık sentetik log verisi üretildi -> {output_path}")
    print(f"Toplam anomali sayısı: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.1f}%)")
    print(df["anomaly_type"].value_counts())
