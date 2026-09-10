# Safety and Responsible AI

## What this system is, and is not

PashuRakshak AI is an **early-warning and case-management system**. It
is:

- An early-warning system that flags patterns in farmer-reported
  observations worth a closer look.
- A decision-support and case-management tool for veterinarians.
- A prevention and education platform.

It is **not**:

- A diagnostic device or laboratory replacement.
- A disease confirmation system.
- An autonomous treatment recommender or prescription generator.
- A replacement for a veterinarian.

**This rule is never broken anywhere in the codebase**: an AI
prediction is never presented as a confirmed disease. Every HIGH-risk
result displays, verbatim, exactly:

> AI screening alert - veterinarian assessment required.

That string is a single constant (`ml/src/constants.py::CLINICAL_DISCLAIMER`)
imported everywhere it's needed — in the scoring contract, the
observation-submission response, and the alert-detail response — so it
can never drift or be paraphrased into something weaker.

## Three concepts that are never merged

Every screen that shows risk information keeps these visually and
semantically distinct — labeled separately, never blended into one
narrative:

1. **Reported observation** — what the farmer entered, verbatim.
2. **AI screening** — what the software flagged (risk band, score,
   contributing factors, model version), always carrying the
   disclaimer.
3. **Veterinary assessment** — what a veterinarian determines, entered
   through the case workspace. `confirmed_condition` and
   `confirmation_basis` are fields on `Case`, populated only by a
   veterinarian/admin through vet-gated endpoints. The AI scoring path
   (`ml/src/predict.assess`) has no code path that can write to a
   `Case` row — it only ever produces a `RiskAssessment`.

See `AlertDetailPage.tsx` for where this shows up most concretely: three
separate cards, "Reported observation" / "AI screening" /
"Veterinary assessment", in that order.

## The scoring contract's output is structurally limited

`RiskAssessmentRead` (the API's response schema for any risk result)
has exactly these fields: `risk_score`, `risk_band`, `top_factors`,
`model_version`, `human_review_required`, `clinical_disclaimer`. There
is no `diagnosis`, `treatment`, or `prescription` field anywhere in the
schema — the API cannot return one even if a bug in the model or rule
engine tried to produce one. Tests assert this directly rather than
trusting it by inspection:

- `ml/tests/test_predict.py::test_assess_never_leaks_diagnosis_or_treatment_keys`
- `backend/tests/test_observations.py::test_never_returns_diagnosis_or_treatment_fields`
- `frontend/src/components/shared/RiskResultView.test.tsx::"never renders a diagnosis or treatment claim"`

## The rule engine (`ml/src/rules.py`)

A transparent, hand-written set of safety rules runs alongside the
statistical model. Its job is to catch clearly urgent combinations of
signs even when the model under-scores them (e.g. too few historical
examples of a dangerous pattern). Every threshold is documented in the
module docstring and file comments as a **prototype assumption**, not
a validated veterinary guideline — e.g. "temperature ≥ 40.5°C is
urgent" is a reasonable placeholder for a demo, not a number a real
deployment should trust without veterinary review.

Rules can only push risk *up*: `flags.urgent` forces the final band to
HIGH regardless of what the statistical model scored, and
`flags.minimum_risk_score` is combined with the model's probability via
`max()`. A rule can never suppress or lower a model's score.

## Human review requirement

`human_review_required` is `true` whenever the band is HIGH. The
farmer-facing result screen shows a prominent "Contact veterinarian"
action for MEDIUM and HIGH. The vet dashboard's alert queue is the
single place these are triaged — nothing in the system auto-resolves a
HIGH alert without a veterinarian action.

## Prevention content, not medical claims

Education content (`education_content` table) is written and reviewed
as prevention/hygiene/biosecurity guidance — see the seeded examples in
`seed/seed_data.py`. None of it makes treatment claims or names
specific drugs/dosages.

## Analytics never claim an outbreak

`GET /analytics/farm-trends` explicitly returns a `note` field reading
"These are aggregated early-warning observations for this farm, not a
confirmed outbreak or diagnosis." — never "this village has an
outbreak." ✅ `backend/tests/test_analytics.py`,
`frontend/src/pages/shared/AnalyticsPage.tsx`

## Terminology used consistently

The product deliberately uses: "Early-warning risk", "AI screening",
"Reported observation", "Veterinary assessment", "Contributing
signals", "Safe next steps", "Prevention". It avoids: "AI diagnosis",
"Confirmed by AI", "AI treatment/prescription", "guaranteed",
"100% accurate", or any accuracy-percentage claim about real-world
performance (see [model-card.md](model-card.md) for why).

## Farmer-facing language

Plain language is used throughout the farmer experience instead of
clinical jargon — "Signs you observed" instead of "clinical
symptomatology", "Early-warning level" instead of "risk
stratification", "Add today's observation" instead of "submit
biometric parameters". See `frontend/src/i18n/locales/en.json` /
`hi.json` for the actual copy.
