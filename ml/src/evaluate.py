"""Evaluation report: calibration, false positive/negative rates at the
HIGH-band operating threshold, and a species subgroup breakdown.

Run as: python -m ml.src.evaluate   (after python -m ml.src.train)
"""

import json
from pathlib import Path

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GroupShuffleSplit

from ml.src.constants import HIGH_THRESHOLD, MODEL_VERSION
from ml.src.predict import load_model
from ml.src.synthetic_data import generate_synthetic_dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = REPO_ROOT / "ml" / "models" / "evaluation_report.json"


def _reconstruct_test_split(seed: int = 42, n_samples: int = 4000):
    feature_rows, labels, group_ids = generate_synthetic_dataset(n_samples=n_samples, seed=seed)
    x = np.array(feature_rows, dtype=float)
    y = np.array(labels, dtype=int)
    groups = np.array(group_ids)

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.3, random_state=seed)
    _, holdout_idx = next(splitter.split(x, y, groups=groups))
    x_holdout, y_holdout, groups_holdout = x[holdout_idx], y[holdout_idx], groups[holdout_idx]

    splitter2 = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed)
    _, test_idx = next(splitter2.split(x_holdout, y_holdout, groups=groups_holdout))
    return x_holdout[test_idx], y_holdout[test_idx]


def _subgroup_metrics(x, y, proba, mask, name: str) -> dict:
    if mask.sum() == 0:
        return {"name": name, "n": 0}
    y_sub, proba_sub = y[mask], proba[mask]
    high_band = proba_sub >= HIGH_THRESHOLD
    tn, fp, fn, tp = confusion_matrix(y_sub, high_band, labels=[0, 1]).ravel()
    return {
        "name": name,
        "n": int(mask.sum()),
        "positive_rate": float(y_sub.mean()),
        "high_band_rate": float(high_band.mean()),
        "high_band_false_positive_rate": float(fp / (fp + tn)) if (fp + tn) > 0 else None,
        "high_band_false_negative_rate": float(fn / (fn + tp)) if (fn + tp) > 0 else None,
    }


def run_evaluation() -> dict:
    bundle = load_model()
    pipeline = bundle["pipeline"]

    x_test, y_test = _reconstruct_test_split()
    proba = pipeline.predict_proba(x_test)[:, 1]

    fraction_of_positives, mean_predicted_value = calibration_curve(y_test, proba, n_bins=10)

    species_cattle_idx = 14  # index into FEATURE_NAMES; see ml/src/features.py
    species_buffalo_idx = 15
    cattle_mask = x_test[:, species_cattle_idx] == 1
    buffalo_mask = x_test[:, species_buffalo_idx] == 1

    report = {
        "model_version": MODEL_VERSION,
        "n_test": int(len(y_test)),
        "calibration_curve": {
            "mean_predicted_value": mean_predicted_value.tolist(),
            "fraction_of_positives": fraction_of_positives.tolist(),
        },
        "high_band_threshold": HIGH_THRESHOLD,
        "subgroups": {
            "cattle": _subgroup_metrics(x_test, y_test, proba, cattle_mask, "cattle"),
            "buffalo": _subgroup_metrics(x_test, y_test, proba, buffalo_mask, "buffalo"),
        },
        "overall": _subgroup_metrics(
            x_test, y_test, proba, np.ones(len(y_test), dtype=bool), "overall"
        ),
        "limitations": (
            "Evaluated entirely on synthetic/demo data with a caricatured generative "
            "process. Subgroup and calibration numbers describe the model's behavior "
            "on that synthetic data only and carry no claim about real-world accuracy."
        ),
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"Saved evaluation report to {REPORT_PATH}")
    return report


if __name__ == "__main__":
    run_evaluation()
