"""Transparent, documented safety-rule engine for the early-warning system.

These rules exist to catch clearly concerning combinations of reported
signs even when the statistical model under-scores them (e.g. very few
historical examples of a dangerous pattern). Every threshold below is a
PROTOTYPE ASSUMPTION for the SIH demo, not a validated veterinary
guideline. They are documented here so a real veterinary domain expert
can review and recalibrate them before any real-world use.

Severity bands map to a *minimum* risk score contribution so that a
rule can force the final risk band up (see ml/src/predict.py) even if
the learned model itself would have scored the case lower.
"""

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Documented prototype thresholds (NOT clinically validated)
# ---------------------------------------------------------------------------
TEMP_HIGH_FEVER_C = 39.5  # commonly cited upper-normal bound for cattle/buffalo
TEMP_URGENT_HIGH_C = 40.5
TEMP_LOW_HYPOTHERMIA_C = 36.5

MILK_YIELD_DROP_MEDIUM_PCT = -20.0
MILK_YIELD_DROP_HIGH_PCT = -40.0

REPEATED_ABNORMAL_WINDOW = 3  # look back this many prior observations
REPEATED_ABNORMAL_MIN_COUNT = 2  # this many "concerning" observations triggers escalation

SEVERITY_SCORES = {
    "low": 0.15,
    "medium": 0.45,
    "high": 0.75,
}


@dataclass
class TriggeredRule:
    rule: str
    reason: str
    severity: str  # "low" | "medium" | "high"

    def to_dict(self) -> dict:
        return {"rule": self.rule, "reason": self.reason, "severity": self.severity}


@dataclass
class RuleEngineResult:
    triggered: list = field(default_factory=list)  # list[TriggeredRule]
    minimum_risk_score: float = 0.0
    urgent: bool = False

    def as_factor_dicts(self) -> list:
        return [t.to_dict() for t in self.triggered]


def _is_concerning(observation: dict) -> bool:
    """Loose definition of "abnormal" used only for the repeated-observation rule."""
    if observation.get("appetite") in ("reduced", "none"):
        return True
    if observation.get("activity") in ("reduced", "lethargic"):
        return True
    if observation.get("respiratory_sign") in ("mild", "labored", "coughing"):
        return True
    if observation.get("dung_sign") in ("loose", "diarrhea", "bloody"):
        return True
    temp = observation.get("temperature_c")
    if temp is not None and (temp >= TEMP_HIGH_FEVER_C or temp <= TEMP_LOW_HYPOTHERMIA_C):
        return True
    milk_change = observation.get("milk_yield_change_pct")
    if milk_change is not None and milk_change <= MILK_YIELD_DROP_MEDIUM_PCT:
        return True
    return False


def evaluate_rules(observation: dict, history: Optional[list] = None) -> RuleEngineResult:
    """Evaluate the documented safety rules against one observation.

    Args:
        observation: current observation fields (appetite, activity,
            water_intake, respiratory_sign, dung_sign, temperature_c,
            milk_yield_change_pct).
        history: prior observations for the same animal, most-recent
            first, used only for the repeated-abnormal-observation rule.

    Returns:
        RuleEngineResult with every triggered rule, the minimum risk
        score those rules impose, and whether any rule is urgent
        (which forces the final risk band to HIGH regardless of the
        statistical model's score).
    """
    history = history or []
    triggered: list = []
    urgent = False

    appetite = observation.get("appetite")
    if appetite == "none":
        triggered.append(
            TriggeredRule(
                "appetite_loss", "Animal is reported to be refusing food entirely", "high"
            )
        )
        urgent = True
    elif appetite == "reduced":
        triggered.append(
            TriggeredRule("appetite_reduction", "Reported appetite is below normal", "medium")
        )

    activity = observation.get("activity")
    if activity == "lethargic":
        triggered.append(
            TriggeredRule(
                "activity_lethargic", "Animal is reported as lethargic / unwilling to move", "high"
            )
        )
        urgent = True
    elif activity == "reduced":
        triggered.append(
            TriggeredRule("activity_reduction", "Reported activity is below normal", "medium")
        )

    respiratory = observation.get("respiratory_sign")
    if respiratory == "labored":
        triggered.append(
            TriggeredRule("respiratory_labored", "Labored breathing was reported", "high")
        )
        urgent = True
    elif respiratory == "coughing":
        triggered.append(TriggeredRule("respiratory_coughing", "Coughing was reported", "medium"))
    elif respiratory == "mild":
        triggered.append(
            TriggeredRule("respiratory_mild", "Mild respiratory signs were reported", "low")
        )

    dung = observation.get("dung_sign")
    if dung == "bloody":
        triggered.append(TriggeredRule("dung_bloody", "Blood was reported in dung", "high"))
        urgent = True
    elif dung == "diarrhea":
        triggered.append(TriggeredRule("dung_diarrhea", "Diarrhea was reported", "medium"))
    elif dung == "loose":
        triggered.append(TriggeredRule("dung_loose", "Loose dung was reported", "low"))

    temp = observation.get("temperature_c")
    if temp is not None:
        if temp >= TEMP_URGENT_HIGH_C:
            triggered.append(
                TriggeredRule(
                    "temperature_high_urgent",
                    f"Recorded temperature ({temp:.1f}C) is markedly above the normal range",
                    "high",
                )
            )
            urgent = True
        elif temp >= TEMP_HIGH_FEVER_C:
            triggered.append(
                TriggeredRule(
                    "temperature_elevated",
                    f"Recorded temperature ({temp:.1f}C) is above the normal range",
                    "medium",
                )
            )
        elif temp <= TEMP_LOW_HYPOTHERMIA_C:
            triggered.append(
                TriggeredRule(
                    "temperature_low",
                    f"Recorded temperature ({temp:.1f}C) is below the normal range",
                    "medium",
                )
            )

    milk_change = observation.get("milk_yield_change_pct")
    if milk_change is not None:
        if milk_change <= MILK_YIELD_DROP_HIGH_PCT:
            triggered.append(
                TriggeredRule(
                    "milk_yield_sharp_decline",
                    f"Milk yield dropped sharply ({milk_change:.0f}%)",
                    "high",
                )
            )
        elif milk_change <= MILK_YIELD_DROP_MEDIUM_PCT:
            triggered.append(
                TriggeredRule(
                    "milk_yield_decline",
                    f"Milk yield decreased ({milk_change:.0f}%) compared to usual",
                    "medium",
                )
            )

    recent_history = history[:REPEATED_ABNORMAL_WINDOW]
    concerning_count = sum(1 for past in recent_history if _is_concerning(past))
    if concerning_count >= REPEATED_ABNORMAL_MIN_COUNT:
        triggered.append(
            TriggeredRule(
                "repeated_abnormal_observations",
                f"{concerning_count} of the last {len(recent_history)} observations also showed "
                "concerning signs",
                "medium",
            )
        )

    minimum_risk_score = max((SEVERITY_SCORES[t.severity] for t in triggered), default=0.0)

    return RuleEngineResult(
        triggered=triggered, minimum_risk_score=minimum_risk_score, urgent=urgent
    )
