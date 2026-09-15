"""
anomaly_detection.py
---------------------
API log verisi üzerinde açıklanabilir (z-score tabanlı) anomali tespiti.
Endpoint bazında ayrı ayrı z-score hesaplanır çünkü farklı uç noktaların (örn. /export vs
/process) normal gecikme/bellek profilleri farklı olabilir — bu, tek bir global eşik yerine
her endpoint için ayrı bir "normal" tanımlamanın neden daha doğru olduğunu gösterir.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class AnomalyThresholds:
    latency_z: float = 2.5
    memory_z: float = 2.5


def detect_anomalies_zscore(df: pd.DataFrame, thresholds: AnomalyThresholds = AnomalyThresholds()) -> pd.DataFrame:
    df = df.copy()
    df["z_latency"] = 0.0
    df["z_memory"] = 0.0

    for endpoint, group in df.groupby("endpoint"):
        for col, zcol in [("latency_ms", "z_latency"), ("memory_mb", "z_memory")]:
            mean, std = group[col].mean(), group[col].std()
            if std == 0 or np.isnan(std):
                continue
            df.loc[group.index, zcol] = (group[col] - mean) / std

    def classify(row):
        reasons = []
        if row["z_latency"] > thresholds.latency_z:
            reasons.append("latency_spike")
        if row["z_memory"] > thresholds.memory_z:
            reasons.append("memory_spike")
        if row["status_code"] >= 500:
            reasons.append("error_spike")
        return reasons

    df["detected_reasons"] = df.apply(classify, axis=1)
    df["predicted_anomaly"] = df["detected_reasons"].apply(lambda r: len(r) > 0)
    return df


def summarize_anomaly(row: pd.Series) -> str:
    parts = [
        f"Endpoint: {row['endpoint']}",
        f"Zaman: {row['timestamp']}",
        f"Gecikme: {row['latency_ms']:.0f}ms (z={row['z_latency']:.2f})",
        f"Bellek: {row['memory_mb']:.0f}MB (z={row['z_memory']:.2f})",
        f"Durum kodu: {row['status_code']}",
        f"Tespit edilen sapma(lar): {', '.join(row['detected_reasons']) if row['detected_reasons'] else 'yok'}",
    ]
    return " | ".join(parts)


def evaluate_against_ground_truth(df: pd.DataFrame) -> dict:
    """NOT: Gerçek dünyada ground truth etiketi olmaz; bu sadece projenin kendi doğruluğunu
    ölçmek için sentetik veriye özel bir değerlendirme adımıdır."""
    tp = ((df["is_anomaly"]) & (df["predicted_anomaly"])).sum()
    fp = ((~df["is_anomaly"]) & (df["predicted_anomaly"])).sum()
    fn = ((df["is_anomaly"]) & (~df["predicted_anomaly"])).sum()
    tn = ((~df["is_anomaly"]) & (~df["predicted_anomaly"])).sum()

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return {
        "true_positives": int(tp), "false_positives": int(fp),
        "false_negatives": int(fn), "true_negatives": int(tn),
        "precision": round(precision, 3), "recall": round(recall, 3), "f1_score": round(f1, 3),
    }


if __name__ == "__main__":
    df = pd.read_csv("data/logs/synthetic_api_logs.csv", parse_dates=["timestamp"])
    result_df = detect_anomalies_zscore(df)

    metrics = evaluate_against_ground_truth(result_df)
    print("=== Anomali Tespit Performansı (z-score, sentetik veri üzerinde) ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    print("\n=== Örnek tespit edilen anomaliler ===")
    detected = result_df[result_df["predicted_anomaly"]].head(5)
    for _, row in detected.iterrows():
        print("-", summarize_anomaly(row))

    result_df.to_csv("data/logs/api_logs_with_predictions.csv", index=False)
