# Model Card: PashuRakshak AI Early-Warning Model

## ⚠️ Prototype status

**This is a prototype model trained entirely on synthetic/demo data.
It has not been validated against real veterinary outcomes and must
not be presented, marketed, or relied on as clinically accurate.**
Every number below describes behavior on a caricatured synthetic
dataset generated for the SIH demo, not real-world performance.

## Model details

- **Version**: `prototype-v1` (`ml/src/constants.py::MODEL_VERSION`)
- **Type**: Logistic regression (`sklearn.linear_model.LogisticRegression`,
  `class_weight="balanced"`) inside a `StandardScaler` pipeline.
- **Why logistic regression**: its output probabilities are directly
  optimized against log-loss, making them meaningfully interpretable
  as risk probabilities without a separate calibration step — a
  reasonable, auditable choice for a triage tool where a veterinarian
  needs to understand *why* a score landed where it did. (Real
  calibration validation against ground truth is future work — see
  Limitations.)
- **Combined with**: a transparent, hand-written rule engine
  (`ml/src/rules.py`) that can force the final band to HIGH regardless
  of the model's score. The model never runs in isolation — see
  `ml/src/predict.py::assess` for the exact combination logic.

## Intended use

Screening triage only: flag observations that may warrant closer
attention, and route the ones most likely to need it toward a
veterinarian. **Not** intended for autonomous diagnosis, treatment
selection, or any use that bypasses veterinary judgment.

## Training data

100% synthetic. `ml/src/synthetic_data.py` generates observations from
a hand-specified generative process: a latent "at-risk" propensity
(28% base rate, 5% label noise) drives conditional distributions over
appetite/activity/respiratory/dung/temperature/milk-yield fields, plus
a short synthetic observation history per sample so the trend features
(baseline concern scores, repeated-abnormal count) have something real
to compute from. This is a caricature of plausible patterns, not a
sample of real animal health records — no real animal or farmer data
was used anywhere in this system.

- **n = 4,000 samples**, group-aware split (70% train / 15% val / 15%
  test) using `GroupShuffleSplit` on a synthetic "farm" id, so no
  synthetic farm appears in more than one split — the closest
  approximation to farm-level separation achievable without real farm
  identifiers.
- Regenerating the dataset (`python -m ml.src.train`) is fully
  deterministic given the same seed (`seed=42` default).

## Features

19 features, computed identically at training and serving time by the
single shared function `ml/src/features.py::build_feature_vector`
(this is deliberate: the #1 source of silent train/serve skew bugs is
computing features two different ways in two different places).

**Current observation**: appetite/activity/respiratory/dung ordinal
scores, water-intake-abnormal flag, temperature deviation from a
documented normal midpoint (38.5°C) with a missingness flag, milk
yield change with a missingness flag.

**Trend**: an overall "concern score" for the current observation,
7-day and 14-day baseline concern scores from prior observations,
change from the 14-day baseline, and a repeated-abnormal-observations
count over the last 3 prior observations.

**Context**: species (one-hot cattle/buffalo), an age band derived
from date of birth, a vaccination-overdue flag, and a season code
derived from the observation month.

## Evaluation methodology

`ml/src/train.py` reports train/val/test metrics from the group-aware
split above (ROC-AUC, Brier score, precision/recall/F1 at a 0.5
threshold on the raw model probability — not the final blended risk
band). `ml/src/evaluate.py` additionally reports:

- A 10-bin calibration curve on the test split.
- False-positive / false-negative rates specifically at the **HIGH
  band operating threshold** (0.65) — the operationally relevant
  question is "how often does the system's most urgent band fire
  wrongly or miss," not just overall accuracy.
- The same breakdown separately for the cattle and buffalo subgroups.

Both scripts write their output to `ml/models/training_metrics.json`
and `ml/models/evaluation_report.json` respectively — regenerate them
any time by rerunning the two commands; they are not committed to git
(the model artifact is a build product, not source).

### Latest run (synthetic data only — see the warning above)

| Split | n | ROC-AUC | Brier score | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| train | 2,798 | 0.917 | 0.082 | 0.847 | 0.847 | 0.847 |
| val | 601 | 0.926 | 0.082 | 0.848 | 0.870 | 0.859 |
| test | 601 | 0.913 | 0.083 | 0.849 | 0.849 | 0.849 |

Consistency across splits (no large train/val/test gap) indicates the
model isn't badly overfitting *the synthetic generative process* — it
says nothing about generalization to real animals.

At the HIGH-band operating threshold (0.65) on the test split:
overall false-positive rate ≈ 4.0%, false-negative rate ≈ 17.4%,
with the buffalo subgroup showing a higher false-positive rate
(~6.4% vs ~2.3% for cattle) and cattle showing a higher false-negative
rate (~21.8% vs ~11.3% for buffalo) — a reminder that even on
synthetic data, subgroup performance isn't uniform, and any real
deployment would need to check this on real, representative data
before trusting a single global threshold across species.

## Safety considerations

- The API response schema structurally cannot carry a diagnosis,
  treatment, or prescription field — see [safety.md](safety.md).
- The rule engine's thresholds are documented prototype assumptions,
  not clinical guidelines — see comments in `ml/src/rules.py`.
- `human_review_required` is always `true` for HIGH-band results, and
  the mandatory disclaimer is a single shared constant, not
  free-text that could be paraphrased away.
- Every risk assessment records `model_version`, so any future model
  change is traceable against historical results.

## Limitations

- **No real-world validation.** This is the single most important
  limitation and is repeated throughout this document deliberately.
- Calibration is reported (see the calibration curve in
  `evaluation_report.json`) but not validated against real outcomes —
  a well-calibrated model on synthetic data says nothing about
  calibration on real animals.
- The generative process for synthetic data encodes the authors'
  assumptions about what "at-risk" looks like; a real deployment would
  need labeled real data reviewed by veterinary domain experts before
  any of these thresholds or the model itself could be trusted.
- Region/location-based subgroup analysis is not implemented (no real
  location data exists to analyze).
- No accuracy percentage from this model card should ever be quoted
  as a real-world performance claim in a demo, pitch, or documentation
  — it describes behavior on a synthetic dataset only.
