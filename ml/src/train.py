"""Train the prototype early-warning classifier on synthetic data.

Run as: python -m ml.src.train   (from the repository root)

This is explicitly a PROTOTYPE model trained on synthetic/demo data.
It has not been validated against real veterinary outcomes and must
not be presented as clinically accurate. See docs/model-card.md.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml.src.constants import MODEL_VERSION
from ml.src.features import FEATURE_NAMES
from ml.src.synthetic_data import generate_synthetic_dataset

REPO_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = REPO_ROOT / "ml" / "models"
MODEL_PATH = MODEL_DIR / "risk_model.joblib"
METRICS_PATH = MODEL_DIR / "training_metrics.json"


def _group_split(x, y, groups, test_fraction: float, seed: int):
    splitter = GroupShuffleSplit(n_splits=1, test_size=test_fraction, random_state=seed)
    train_idx, test_idx = next(splitter.split(x, y, groups=groups))
    return train_idx, test_idx


def train_and_save(n_samples: int = 4000, seed: int = 42) -> dict:
    feature_rows, labels, group_ids = generate_synthetic_dataset(n_samples=n_samples, seed=seed)
    x = np.array(feature_rows, dtype=float)
    y = np.array(labels, dtype=int)
    groups = np.array(group_ids)

    # Group-aware split: no synthetic "farm" appears in more than one of
    # train/val/test, approximating farm-level separation on real data.
    train_idx, holdout_idx = _group_split(x, y, groups, test_fraction=0.3, seed=seed)
    x_train, y_train = x[train_idx], y[train_idx]
    x_holdout, y_holdout, groups_holdout = x[holdout_idx], y[holdout_idx], groups[holdout_idx]

    val_idx, test_idx = _group_split(
        x_holdout, y_holdout, groups_holdout, test_fraction=0.5, seed=seed
    )
    x_val, y_val = x_holdout[val_idx], y_holdout[val_idx]
    x_test, y_test = x_holdout[test_idx], y_holdout[test_idx]

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    pipeline.fit(x_train, y_train)

    from sklearn.metrics import brier_score_loss, precision_recall_fscore_support, roc_auc_score

    def _evaluate(x_split, y_split, name: str) -> dict:
        if len(x_split) == 0:
            return {"n": 0}
        proba = pipeline.predict_proba(x_split)[:, 1]
        preds = (proba >= 0.5).astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_split, preds, average="binary", zero_division=0
        )
        metrics = {
            "n": int(len(x_split)),
            "positive_rate": float(y_split.mean()),
            "roc_auc": float(roc_auc_score(y_split, proba)) if len(set(y_split)) > 1 else None,
            "brier_score": float(brier_score_loss(y_split, proba)),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
        }
        print(f"[{name}] {metrics}")
        return metrics

    metrics = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_samples": n_samples,
        "feature_names": FEATURE_NAMES,
        "train": _evaluate(x_train, y_train, "train"),
        "val": _evaluate(x_val, y_val, "val"),
        "test": _evaluate(x_test, y_test, "test"),
        "note": (
            "Trained entirely on synthetic/demo data. Not validated for "
            "clinical or field deployment."
        ),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "feature_names": FEATURE_NAMES,
            "model_version": MODEL_VERSION,
            "trained_at": metrics["trained_at"],
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"Saved model artifact to {MODEL_PATH}")
    print(f"Saved training metrics to {METRICS_PATH}")
    return metrics


if __name__ == "__main__":
    train_and_save()
