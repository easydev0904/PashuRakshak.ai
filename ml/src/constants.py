"""Single source of truth for model version and risk-band thresholds.

Both train.py (which stamps the artifact) and predict.py (which scores
with it) import from here so the two can never silently drift apart.
"""

MODEL_VERSION = "prototype-v1"

# Thresholds on the blended risk score (see predict.assess). Prototype
# values chosen for a demonstrable, non-degenerate LOW/MEDIUM/HIGH split
# on the synthetic dataset — not derived from clinical validation.
HIGH_THRESHOLD = 0.65
MEDIUM_THRESHOLD = 0.35

CLINICAL_DISCLAIMER = "AI screening alert - veterinarian assessment required."
