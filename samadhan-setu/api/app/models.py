import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def gen_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --- Enums (plain strings; validated at the Pydantic layer, mirrored in TS) ---
ROLES = (
    "CITIZEN",
    "COMMUNITY_ORG",
    "UNIVERSITY_ADMIN",
    "FACULTY_MENTOR",
    "STUDENT",
    "INDUSTRY_PARTNER",
    "GOVT_OFFICIAL",
    "SUPER_ADMIN",
)

CHALLENGE_STATUSES = (
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
)

DOMAINS = (
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
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30))
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    district: Mapped[str | None] = mapped_column(String(80), nullable=True)
    org_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class University(Base):
    __tablename__ = "universities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(200))
    code: Mapped[str] = mapped_column(String(30), unique=True)
    district: Mapped[str] = mapped_column(String(80))
    type: Mapped[str] = mapped_column(String(50))
    disciplines: Mapped[list] = mapped_column(JSON, default=list)
    research_areas: Mapped[list] = mapped_column(JSON, default=list)
    has_incubation: Mapped[bool] = mapped_column(Boolean, default=False)
    naac_grade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    capacity_score: Mapped[float] = mapped_column(Float, default=50.0)
    active_project_count: Mapped[int] = mapped_column(Integer, default=0)


class Industry(Base):
    __tablename__ = "industries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(200))
    sector: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(30))  # INDUSTRY|STARTUP|MSME|CSR|LAB|INNOVATION_HUB
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    csr_budget_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    district: Mapped[str] = mapped_column(String(80))
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(300), nullable=True)


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(50))
    sub_domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")  # low|medium|high|critical
    status: Mapped[str] = mapped_column(String(20), default="SUBMITTED")
    district: Mapped[str] = mapped_column(String(80))
    block: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    submitted_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_keywords: Mapped[list] = mapped_column(JSON, default=list)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    duplicate_of_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=True)
    upvote_count: Mapped[int] = mapped_column(Integer, default=0)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    beneficiaries_estimate: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    submitter: Mapped["User"] = relationship(foreign_keys=[submitted_by_id])


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    challenge_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=True)
    proposal_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("proposals.id"), nullable=True)
    milestone_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("milestones.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Upvote(Base):
    __tablename__ = "upvotes"
    __table_args__ = (UniqueConstraint("challenge_id", "user_id", name="uq_upvote_challenge_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Routing(Base):
    __tablename__ = "routings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"))
    university_id: Mapped[str] = mapped_column(String(36), ForeignKey("universities.id"))
    match_score: Mapped[float] = mapped_column(Float)
    match_reasons: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default="SUGGESTED")  # SUGGESTED|OFFERED|ACCEPTED|DECLINED
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    challenge_id: Mapped[str] = mapped_column(String(36), ForeignKey("challenges.id"))
    university_id: Mapped[str] = mapped_column(String(36), ForeignKey("universities.id"))
    title: Mapped[str] = mapped_column(String(200))
    approach: Mapped[str] = mapped_column(Text)
    methodology: Mapped[str] = mapped_column(Text)
    expected_outcome: Mapped[str] = mapped_column(Text)
    budget_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    timeline_weeks: Mapped[int] = mapped_column(Integer, default=8)
    trl_level: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="DRAFT")  # DRAFT|SUBMITTED|APPROVED|REJECTED|FUNDED
    score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id"))
    name: Mapped[str] = mapped_column(String(150))


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    role_in_team: Mapped[str] = mapped_column(String(50))
    discipline: Mapped[str | None] = mapped_column(String(100), nullable=True)


class Collaboration(Base):
    __tablename__ = "collaborations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id"))
    industry_id: Mapped[str] = mapped_column(String(36), ForeignKey("industries.id"))
    type: Mapped[str] = mapped_column(String(30))  # MENTORSHIP|FUNDING|PROTOTYPING|PILOT|TECH_TRANSFER
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PROPOSED")  # PROPOSED|ACTIVE|COMPLETED
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    proposal_id: Mapped[str] = mapped_column(String(36), ForeignKey("proposals.id"))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deployment_status: Mapped[str] = mapped_column(String(30), default="NOT_STARTED")
    impact_metrics: Mapped[dict] = mapped_column(JSON, default=dict)


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING|IN_REVIEW|APPROVED|BLOCKED
    deliverable_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    approved_by_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)


class IPRecord(Base):
    __tablename__ = "ip_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    type: Mapped[str] = mapped_column(String(20))  # PATENT|COPYRIGHT|DESIGN|TRADEMARK
    title: Mapped[str] = mapped_column(String(200))
    app_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="FILED")
    filed_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    ledger_hash: Mapped[str] = mapped_column(String(64))
    prev_hash: Mapped[str] = mapped_column(String(64), default="0" * 64)


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    entity_type: Mapped[str] = mapped_column(String(30))  # challenge|proposal|project
    entity_id: Mapped[str] = mapped_column(String(36))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50), default="general")
    link: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    actor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(36))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    challenge_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("challenges.id"), nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("projects.id"), nullable=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
