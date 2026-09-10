// Mirrors backend/app/schemas and backend/app/models/enums.py.
// Keep in sync manually -- this is a small enough surface that a
// generated client would be more ceremony than it's worth here.

export type UserRole = "farmer" | "veterinarian" | "admin";
export type Language = "en" | "hi";
export type Species = "cattle" | "buffalo";
export type Sex = "male" | "female";
export type AnimalStatus = "active" | "sold" | "deceased";

export type AppetiteLevel = "normal" | "reduced" | "none";
export type ActivityLevel = "normal" | "reduced" | "lethargic";
export type WaterIntakeLevel = "normal" | "reduced" | "increased";
export type RespiratorySign = "none" | "mild" | "labored" | "coughing";
export type DungSign = "normal" | "loose" | "diarrhea" | "bloody";

export type RiskBand = "low" | "medium" | "high";
export type AlertPriority = "low" | "medium" | "high";
export type AlertStatus = "open" | "acknowledged" | "assigned" | "in_review" | "resolved";
export type CaseStatus = "open" | "under_review" | "follow_up" | "resolved" | "ruled_out";

export type EducationCategory =
  | "vaccination"
  | "hygiene"
  | "quarantine"
  | "nutrition"
  | "biosecurity"
  | "general_observation";
export type EducationAudience = "farmer" | "veterinarian" | "all";

export interface User {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  language: Language;
  role: UserRole;
  is_active: boolean;
}

export interface LoginRequest {
  email?: string;
  phone?: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Farm {
  id: string;
  name: string;
  village?: string | null;
  district?: string | null;
  state?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  consent_version?: string | null;
}

export interface Animal {
  id: string;
  farm_id: string;
  tag_id: string;
  species: Species;
  breed?: string | null;
  sex: Sex;
  dob?: string | null;
  status: AnimalStatus;
  photo_url?: string | null;
  notes?: string | null;
  created_at: string;
}

export interface AnimalSummary extends Animal {
  last_observation_at?: string | null;
  last_risk_band?: RiskBand | null;
  needs_checkin_today: boolean;
}

export interface ObservationInput {
  observed_at?: string;
  appetite: AppetiteLevel;
  activity: ActivityLevel;
  water_intake: WaterIntakeLevel;
  respiratory_sign: RespiratorySign;
  dung_sign: DungSign;
  temperature_c?: number | null;
  milk_yield_change_pct?: number | null;
  notes?: string | null;
  image_url?: string | null;
}

export interface Observation extends Omit<ObservationInput, "observed_at"> {
  id: string;
  animal_id: string;
  observed_at: string;
  entered_by?: string | null;
  created_at: string;
}

export interface ObservationWithRisk extends Observation {
  risk_assessment?: RiskAssessment | null;
}

export interface RiskFactor {
  rule: string;
  reason: string;
  severity: "low" | "medium" | "high";
}

export interface RiskAssessment {
  id: string;
  observation_id: string;
  model_version: string;
  risk_score: number;
  risk_band: RiskBand;
  top_factors: RiskFactor[];
  human_review_required: boolean;
  clinical_disclaimer: string;
  created_at: string;
}

export interface ObservationResult {
  observation: Observation;
  risk_assessment: RiskAssessment;
}

export interface Alert {
  id: string;
  assessment_id: string;
  priority: AlertPriority;
  status: AlertStatus;
  assigned_vet_id?: string | null;
  acknowledged_at?: string | null;
  resolution?: string | null;
  created_at: string;
}

export interface AlertDetail extends Alert {
  animal: Animal;
  observation: Observation;
  risk_assessment: RiskAssessment;
  farm_name: string;
}

export interface AlertReviewAction {
  action: "acknowledge" | "assign" | "request_follow_up" | "resolve";
  assigned_vet_id?: string;
  note?: string;
  follow_up_at?: string;
}

export interface CaseUpdate {
  id: string;
  case_id: string;
  author_id?: string | null;
  note: string;
  next_follow_up_at?: string | null;
  created_at: string;
}

export interface Case {
  id: string;
  animal_id: string;
  alert_id?: string | null;
  status: CaseStatus;
  suspected_condition?: string | null;
  confirmed_condition?: string | null;
  confirmation_basis?: string | null;
  opened_by?: string | null;
  closed_at?: string | null;
  created_at: string;
  updates?: CaseUpdate[];
}

export interface VaccinationRecord {
  id: string;
  animal_id: string;
  vaccine_name: string;
  dose_date?: string | null;
  due_date?: string | null;
  administered_by?: string | null;
  evidence_url?: string | null;
  created_at: string;
}

export interface EducationContent {
  id: string;
  category: EducationCategory;
  title: string;
  language: Language;
  body: string;
  audience: EducationAudience;
  is_published: boolean;
}

export interface FarmTrendPoint {
  date: string;
  observation_count: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
}

export interface FarmTrendsResponse {
  farm_id: string;
  farm_name: string;
  total_animals: number;
  total_observations: number;
  risk_band_counts: { risk_band: string; count: number }[];
  open_alerts: number;
  vaccinations_due: number;
  daily_trend: FarmTrendPoint[];
  note: string;
}

export interface ApiErrorBody {
  detail: string;
  errors?: unknown;
}
