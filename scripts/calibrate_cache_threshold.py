"""Script to calibrate semantic cache thresholds and margins."""
import json
import os
from pathlib import Path

from fixgraph.config import settings
from fixgraph.contracts.public import TroubleshootRequest
from fixgraph.data.loaders import load_deeplink_catalog
from fixgraph.service.troubleshoot import TroubleshootService


def run_calibration():
    # We use some of the hard negatives and positive paraphrases for calibration
    DATASET = [
        # Canonical, Paraphrases (Positives), Hard Negatives
        (
            "battery drains fast",
            ["phone battery dropping quickly", "battery life is very short"],
            ["battery won't charge", "phone overheats"]
        ),
        (
            "wifi disconnects",
            ["wireless network keeps dropping", "wifi keeps disconnecting"],
            ["mobile data disconnected", "hotspot not working"]
        ),
        (
            "location inaccurate",
            ["gps location is wrong", "map location accuracy wrong direction"],
            ["location permission denied", "compass is wrong"]
        )
    ]

    thresholds = [0.70, 0.75, 0.80, 0.85, 0.90]
    margins = [0.01, 0.03, 0.05, 0.10]

    results = []

    db_path = "data/calibrate_cache.db"

    catalog = load_deeplink_catalog(settings.deeplinks_path)

    for thresh in thresholds:
        for margin in margins:
            settings.similarity_threshold = thresh
            settings.cache_min_margin = margin

            if os.path.exists(db_path):
                os.remove(db_path)

            svc = TroubleshootService(catalog=catalog, cache_db_path=db_path)

            # Warm up
            for canonical, _, _ in DATASET:
                svc.troubleshoot(TroubleshootRequest(query=canonical))

            # Evaluate
            true_hits = 0
            false_hits = 0
            total_pos = 0
            total_neg = 0

            for canonical, positives, negatives in DATASET:
                for p in positives:
                    total_pos += 1
                    _, metrics = svc.troubleshoot(TroubleshootRequest(query=p))
                    if metrics.cache_hit:
                        true_hits += 1

                for n in negatives:
                    total_neg += 1
                    _, metrics = svc.troubleshoot(TroubleshootRequest(query=n))
                    if metrics.cache_hit:
                        false_hits += 1

            true_hit_rate = true_hits / total_pos if total_pos > 0 else 0
            false_hit_rate = false_hits / total_neg if total_neg > 0 else 0
            precision = true_hits / (true_hits + false_hits) if (true_hits + false_hits) > 0 else 1.0

            results.append({
                "threshold": thresh,
                "margin": margin,
                "true_hit_rate": round(true_hit_rate, 3),
                "false_hit_rate": round(false_hit_rate, 3),
                "precision": round(precision, 3)
            })

    Path("reports").mkdir(exist_ok=True)
    with open("reports/cache_threshold_calibration.json", "w") as f:
        json.dump(results, f, indent=2)

    with open("reports/cache_threshold_calibration.md", "w") as f:
        f.write("# Cache Threshold Calibration\n\n")
        f.write("| Threshold | Margin | True Hit Rate | False Hit Rate | Precision |\n")
        f.write("|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r['threshold']} | {r['margin']} | {r['true_hit_rate']} | {r['false_hit_rate']} | {r['precision']} |\n")

    print("Calibration Complete!")

if __name__ == "__main__":
    run_calibration()
