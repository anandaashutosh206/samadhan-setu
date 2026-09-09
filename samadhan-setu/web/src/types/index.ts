export type Role =
  | "CITIZEN"
  | "COMMUNITY_ORG"
  | "UNIVERSITY_ADMIN"
  | "FACULTY_MENTOR"
  | "STUDENT"
  | "INDUSTRY_PARTNER"
  | "GOVT_OFFICIAL"
  | "SUPER_ADMIN";

export type ChallengeStatus =
  | "SUBMITTED"
  | "AI_TRIAGED"
  | "UNDER_REVIEW"
  | "VALIDATED"
  | "ROUTED"
  | "ASSIGNED"
  | "IN_PROGRESS"
  | "PILOT"
  | "IMPLEMENTED"
  | "CLOSED"
  | "REJECTED"
  | "DUPLICATE";

export type Domain =
  | "education"
  | "agriculture"
  | "healthcare"
  | "water_resources"
  | "environment"
  | "energy"
  | "urban_development"
  | "accessibility"
  | "public_administration"
  | "rural_livelihoods";

export type Severity = "low" | "medium" | "high" | "critical";

export interface UserOut {
  id: string;
  name: string;
  email: string;
  role: Role;
  phone: string | null;
  district: string | null;
  org_name: string | null;
  avatar_url: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserOut;
}

export interface AttachmentOut {
  id: string;
  file_name: string;
  mime_type: string;
  size_bytes: number;
  url: string;
  created_at: string;
}

export interface ChallengeOut {
  id: string;
  title: string;
  description: string;
  domain: string;
  sub_domain: string | null;
  severity: string;
  status: string;
  district: string;
  block: string | null;
  village: string | null;
  lat: number | null;
  lng: number | null;
  submitted_by_id: string;
  ai_confidence: number | null;
  ai_keywords: string[];
  ai_summary: string | null;
  duplicate_of_id: string | null;
  upvote_count: number;
  priority_score: number;
  beneficiaries_estimate: number;
  created_at: string;
  updated_at: string;
  attachments: AttachmentOut[];
}

export interface ChallengeListOut {
  items: ChallengeOut[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ChallengeMapPoint {
  id: string;
  title: string;
  domain: string;
  severity: string;
  status: string;
  lat: number;
  lng: number;
}

export interface AIClassifyResponse {
  domain: string;
  domain_confidence: number;
  top_domains: { domain: string; confidence: number }[];
  severity: string;
  severity_confidence: number;
  keywords: string[];
  summary: string;
}

export interface AIDuplicateCandidate {
  challenge_id: string;
  title: string;
  similarity: number;
  reasons: string[];
  distance_km: number | null;
}

export interface AIDuplicateCheckResponse {
  is_likely_duplicate: boolean;
  candidates: AIDuplicateCandidate[];
}

export interface MatchUniversityOut {
  university_id: string;
  name: string;
  district: string;
  match_score: number;
  match_reasons: string[];
}

export interface AIMatchResponse {
  matches: MatchUniversityOut[];
}

export interface UniversityOut {
  id: string;
  name: string;
  code: string;
  district: string;
  type: string;
  disciplines: string[];
  research_areas: string[];
  has_incubation: boolean;
  naac_grade: string | null;
  contact_email: string | null;
  lat: number;
  lng: number;
  capacity_score: number;
  active_project_count: number;
}

export interface IndustryOut {
  id: string;
  name: string;
  sector: string;
  type: string;
  capabilities: string[];
  csr_budget_range: string | null;
  district: string;
  contact_email: string | null;
  website: string | null;
}

export interface ProposalOut {
  id: string;
  challenge_id: string;
  university_id: string;
  title: string;
  approach: string;
  methodology: string;
  expected_outcome: string;
  budget_estimate: number;
  timeline_weeks: number;
  trl_level: number;
  status: string;
  score: number;
  created_at: string;
}

export interface ProjectOut {
  id: string;
  proposal_id: string;
  status: string;
  progress_percent: number;
  start_date: string | null;
  end_date: string | null;
  deployment_status: string;
  impact_metrics: Record<string, unknown>;
}

export interface MilestoneOut {
  id: string;
  project_id: string;
  title: string;
  description: string | null;
  due_date: string | null;
  status: string;
  deliverable_url: string | null;
  approved_by_id: string | null;
  order: number;
}

export interface NotificationOut {
  id: string;
  title: string;
  body: string;
  type: string;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export interface CommentOut {
  id: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  body: string;
  created_at: string;
}

export interface AnalyticsOverview {
  total_challenges: number;
  total_universities: number;
  total_industries: number;
  total_proposals: number;
  total_projects: number;
  total_beneficiaries: number;
  challenges_by_status: Record<string, number>;
}

export interface DomainCount {
  domain: string;
  count: number;
}

export interface DistrictCount {
  district: string;
  count: number;
  avg_priority: number;
}

export interface FunnelStage {
  stage: string;
  count: number;
}

export interface TimeseriesPoint {
  period: string;
  submitted: number;
  resolved: number;
}

export interface LeaderboardEntry {
  university_id: string;
  name: string;
  proposals_count: number;
  projects_count: number;
  avg_score: number;
}

export interface OutcomesSummary {
  patents_filed: number;
  startups_spawned: number;
  pilots_deployed: number;
  total_beneficiaries_impacted: number;
}

export interface ApiErrorBody {
  detail: string | Record<string, unknown> | unknown[];
  code?: string;
}
