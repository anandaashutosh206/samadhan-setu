from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal[
    "CITIZEN",
    "COMMUNITY_ORG",
    "UNIVERSITY_ADMIN",
    "FACULTY_MENTOR",
    "STUDENT",
    "INDUSTRY_PARTNER",
    "GOVT_OFFICIAL",
    "SUPER_ADMIN",
]

ChallengeStatus = Literal[
    "SUBMITTED",
    "AI_TRIAGED",
    "UNDER_REVIEW",
    "VALIDATED",
    "ROUTED",
    "ASSIGNED",
    "IN_PROGRESS",
    "PILOT",
    "IMPLEMENTED",
    "CLOSED",
    "REJECTED",
    "DUPLICATE",
]

Domain = Literal[
    "education",
    "agriculture",
    "healthcare",
    "water_resources",
    "environment",
    "energy",
    "urban_development",
    "accessibility",
    "public_administration",
    "rural_livelihoods",
]

Severity = Literal["low", "medium", "high", "critical"]


# ---------- Auth ----------
class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: Role
    phone: str | None = None
    district: str | None = None
    org_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: Role
    phone: str | None = None
    district: str | None = None
    org_name: str | None = None
    avatar_url: str | None = None
    is_verified: bool
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Attachments ----------
class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_name: str
    mime_type: str
    size_bytes: int
    url: str
    created_at: datetime


# ---------- Challenges ----------
class ChallengeCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20)
    district: str
    block: str | None = None
    village: str | None = None
    lat: float | None = None
    lng: float | None = None
    beneficiaries_estimate: int = 0
    domain_hint: Domain | None = None  # citizen may pre-select; AI can override


class ChallengeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    domain: str
    sub_domain: str | None
    severity: str
    status: str
    district: str
    block: str | None
    village: str | None
    lat: float | None
    lng: float | None
    submitted_by_id: str
    ai_confidence: float | None
    ai_keywords: list[str]
    ai_summary: str | None
    duplicate_of_id: str | None
    upvote_count: int
    priority_score: float
    beneficiaries_estimate: int
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentOut] = []


class ChallengeListOut(BaseModel):
    items: list[ChallengeOut]
    total: int
    page: int
    page_size: int
    pages: int


class ChallengeStatusUpdate(BaseModel):
    status: ChallengeStatus
    reason: str | None = None


class ChallengeMapPoint(BaseModel):
    id: str
    title: str
    domain: str
    severity: str
    status: str
    lat: float
    lng: float


# ---------- AI ----------
class AIClassifyRequest(BaseModel):
    title: str
    description: str


class AIClassifyResponse(BaseModel):
    domain: str
    domain_confidence: float
    top_domains: list[dict[str, Any]]
    severity: str
    severity_confidence: float
    keywords: list[str]
    summary: str


class AIDuplicateCandidate(BaseModel):
    challenge_id: str
    title: str
    similarity: float
    reasons: list[str]
    distance_km: float | None = None


class AIDuplicateCheckRequest(BaseModel):
    title: str
    description: str
    district: str | None = None
    lat: float | None = None
    lng: float | None = None
    exclude_id: str | None = None


class AIDuplicateCheckResponse(BaseModel):
    is_likely_duplicate: bool
    candidates: list[AIDuplicateCandidate]


class AISummarizeRequest(BaseModel):
    text: str
    max_sentences: int = 3


class AISummarizeResponse(BaseModel):
    summary: str


class MatchUniversityOut(BaseModel):
    university_id: str
    name: str
    district: str
    match_score: float
    match_reasons: list[str]


class AIMatchRequest(BaseModel):
    challenge_id: str
    top_n: int = 5


class AIMatchResponse(BaseModel):
    matches: list[MatchUniversityOut]


class AIHealth(BaseModel):
    status: str
    mode: str  # "local" or "local+llm"
    classifier_loaded: bool
    training_examples: int


# ---------- Universities / Industries ----------
class UniversityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    district: str
    type: str
    disciplines: list[str]
    research_areas: list[str]
    has_incubation: bool
    naac_grade: str | None
    contact_email: str | None
    lat: float
    lng: float
    capacity_score: float
    active_project_count: int


class UniversityCreate(BaseModel):
    name: str
    code: str
    district: str
    type: str
    disciplines: list[str] = []
    research_areas: list[str] = []
    has_incubation: bool = False
    naac_grade: str | None = None
    contact_email: str | None = None
    lat: float
    lng: float
    capacity_score: float = 50.0


class IndustryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    sector: str
    type: str
    capabilities: list[str]
    csr_budget_range: str | None
    district: str
    contact_email: str | None
    website: str | None


class IndustryCreate(BaseModel):
    name: str
    sector: str
    type: str
    capabilities: list[str] = []
    csr_budget_range: str | None = None
    district: str
    contact_email: str | None = None
    website: str | None = None


# ---------- Routing ----------
class RoutingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    challenge_id: str
    university_id: str
    match_score: float
    match_reasons: list[str]
    status: str
    created_at: datetime


class RoutingAssignRequest(BaseModel):
    challenge_id: str
    university_id: str
    match_score: float = 0.0
    match_reasons: list[str] = []


# ---------- Proposals / Teams ----------
class ProposalCreate(BaseModel):
    challenge_id: str
    university_id: str
    title: str
    approach: str
    methodology: str
    expected_outcome: str
    budget_estimate: float = 0.0
    timeline_weeks: int = 8
    trl_level: int = 1


class ProposalStatusUpdate(BaseModel):
    status: Literal["DRAFT", "SUBMITTED", "APPROVED", "REJECTED", "FUNDED"]


class ProposalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    challenge_id: str
    university_id: str
    title: str
    approach: str
    methodology: str
    expected_outcome: str
    budget_estimate: float
    timeline_weeks: int
    trl_level: int
    status: str
    score: float
    created_at: datetime


class TeamMemberIn(BaseModel):
    user_id: str
    role_in_team: str
    discipline: str | None = None


class TeamCreate(BaseModel):
    name: str
    members: list[TeamMemberIn] = []


class TeamMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    role_in_team: str
    discipline: str | None


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    name: str
    members: list[TeamMemberOut] = []


# ---------- Collaborations ----------
class CollaborationCreate(BaseModel):
    proposal_id: str
    industry_id: str
    type: Literal["MENTORSHIP", "FUNDING", "PROTOTYPING", "PILOT", "TECH_TRANSFER"]
    amount: float | None = None
    notes: str | None = None


class CollaborationStatusUpdate(BaseModel):
    status: Literal["PROPOSED", "ACTIVE", "COMPLETED"]


class CollaborationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    industry_id: str
    type: str
    amount: float | None
    status: str
    notes: str | None
    created_at: datetime


# ---------- Projects / Milestones ----------
class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposal_id: str
    status: str
    progress_percent: int
    start_date: datetime | None
    end_date: datetime | None
    deployment_status: str
    impact_metrics: dict[str, Any]


class ProjectProgressUpdate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
    deployment_status: str | None = None


class ImpactMetricsUpdate(BaseModel):
    metrics: dict[str, Any]


class MilestoneCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    order: int = 0


class MilestoneStatusUpdate(BaseModel):
    status: Literal["PENDING", "IN_REVIEW", "APPROVED", "BLOCKED"]
    deliverable_url: str | None = None


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    description: str | None
    due_date: datetime | None
    status: str
    deliverable_url: str | None
    approved_by_id: str | None
    order: int


# ---------- IP records ----------
class IPRecordCreate(BaseModel):
    project_id: str
    type: Literal["PATENT", "COPYRIGHT", "DESIGN", "TRADEMARK"]
    title: str
    app_number: str | None = None
    status: str = "FILED"


class IPRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    type: str
    title: str
    app_number: str | None
    status: str
    filed_on: datetime
    ledger_hash: str
    prev_hash: str


class IPChainVerification(BaseModel):
    valid: bool
    total_records: int
    broken_at: str | None = None


# ---------- Comments ----------
class CommentCreate(BaseModel):
    entity_type: Literal["challenge", "proposal", "project"]
    entity_id: str
    body: str = Field(min_length=1, max_length=2000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str
    user_id: str
    body: str
    created_at: datetime


# ---------- Notifications ----------
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    body: str
    type: str
    link: str | None
    is_read: bool
    created_at: datetime


# ---------- Analytics ----------
class AnalyticsOverview(BaseModel):
    total_challenges: int
    total_universities: int
    total_industries: int
    total_proposals: int
    total_projects: int
    total_beneficiaries: int
    challenges_by_status: dict[str, int]


class DomainCount(BaseModel):
    domain: str
    count: int


class DistrictCount(BaseModel):
    district: str
    count: int
    avg_priority: float


class FunnelStage(BaseModel):
    stage: str
    count: int


class TimeseriesPoint(BaseModel):
    period: str
    submitted: int
    resolved: int


class LeaderboardEntry(BaseModel):
    university_id: str
    name: str
    proposals_count: int
    projects_count: int
    avg_score: float


class OutcomesSummary(BaseModel):
    patents_filed: int
    startups_spawned: int
    pilots_deployed: int
    total_beneficiaries_impacted: int


# ---------- Feedback ----------
class FeedbackCreate(BaseModel):
    challenge_id: str | None = None
    project_id: str | None = None
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    rating: int
    comment: str | None
    created_at: datetime
