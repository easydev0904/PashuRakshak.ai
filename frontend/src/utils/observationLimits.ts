// Mirrors backend/app/schemas/observation.py -- physically-plausible
// measurement bounds, not clinical thresholds. Keep these two files in sync.
export const MIN_PLAUSIBLE_TEMPERATURE_C = 30.0;
export const MAX_PLAUSIBLE_TEMPERATURE_C = 45.0;
export const MIN_PLAUSIBLE_MILK_YIELD_CHANGE_PCT = -100.0;
export const MAX_PLAUSIBLE_MILK_YIELD_CHANGE_PCT = 200.0;
