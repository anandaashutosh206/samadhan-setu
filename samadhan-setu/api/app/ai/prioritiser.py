from dataclasses import dataclass
from datetime import datetime, timezone

SEVERITY_WEIGHTS = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}

# Static district development index proxy (0-1, lower = more development-deficit
# → higher priority weight). In production this would come from a government
# dataset; here it's a reasonable illustrative proxy so the score is explainable
# rather than arbitrary.
DISTRICT_DEV_DEFICIT = {
    "Ranchi": 0.25, "Dhanbad": 0.3, "East Singhbhum": 0.3, "Bokaro": 0.3,
    "Hazaribagh": 0.45, "Deoghar": 0.45, "Ramgarh": 0.4, "Giridih": 0.55,
    "West Singhbhum": 0.6, "Palamu": 0.65, "Garhwa": 0.65, "Gumla": 0.7,
    "Simdega": 0.7, "Khunti": 0.65, "Lohardaga": 0.6, "Chatra": 0.65,
    "Koderma": 0.55, "Godda": 0.6, "Sahibganj": 0.65, "Pakur": 0.7,
    "Dumka": 0.6, "Jamtara": 0.6, "Latehar": 0.65, "Seraikela Kharsawan": 0.5,
}

DOMAIN_CRITICALITY = {
    "healthcare": 1.0, "water_resources": 0.95, "education": 0.8,
    "rural_livelihoods": 0.75, "agriculture": 0.75, "accessibility": 0.7,
    "environment": 0.65, "energy": 0.6, "urban_development": 0.55,
    "public_administration": 0.5,
}

WEIGHTS = {
    "severity": 0.28,
    "beneficiaries": 0.16,
    "upvotes": 0.10,
    "duplicate_cluster": 0.10,
    "domain_criticality": 0.16,
    "age": 0.10,
    "district_deficit": 0.10,
}


@dataclass
class PriorityFactor:
    factor: str
    raw_value: float
    weight: float
    contribution: float
    explanation: str


@dataclass
class PriorityResult:
    score: float  # 0-100
    factors: list[PriorityFactor]


def _normalize_beneficiaries(count: int) -> float:
    # log-ish scaling so 5000+ beneficiaries doesn't dwarf everything linearly
    if count <= 0:
        return 0.0
    if count >= 5000:
        return 1.0
    return min(1.0, count / 5000)


def _normalize_upvotes(count: int) -> float:
    if count <= 0:
        return 0.0
    return min(1.0, count / 100)


def _normalize_age_days(created_at: datetime) -> float:
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = max(0, (now - created_at).days)
    # unresolved challenges become more urgent the older they get, capped at 60 days
    return min(1.0, age_days / 60)


def compute_priority(
    severity: str,
    domain: str,
    district: str | None,
    beneficiaries_estimate: int,
    upvote_count: int,
    duplicate_cluster_size: int,
    created_at: datetime,
) -> PriorityResult:
    severity_val = SEVERITY_WEIGHTS.get(severity, 0.5)
    beneficiaries_val = _normalize_beneficiaries(beneficiaries_estimate)
    upvotes_val = _normalize_upvotes(upvote_count)
    duplicate_val = min(1.0, duplicate_cluster_size / 5)
    criticality_val = DOMAIN_CRITICALITY.get(domain, 0.5)
    age_val = _normalize_age_days(created_at)
    district_val = DISTRICT_DEV_DEFICIT.get(district or "", 0.5)

    raw = {
        "severity": severity_val,
        "beneficiaries": beneficiaries_val,
        "upvotes": upvotes_val,
        "duplicate_cluster": duplicate_val,
        "domain_criticality": criticality_val,
        "age": age_val,
        "district_deficit": district_val,
    }

    explanations = {
        "severity": f"Severity classified as '{severity}'",
        "beneficiaries": f"Estimated {beneficiaries_estimate} beneficiaries",
        "upvotes": f"{upvote_count} community upvotes",
        "duplicate_cluster": f"{duplicate_cluster_size} similar reports filed (signals widespread issue)",
        "domain_criticality": f"'{domain}' is a high-criticality domain" if criticality_val >= 0.75 else f"'{domain}' domain criticality",
        "age": "Unresolved report ageing" if age_val > 0.3 else "Recently submitted",
        "district_deficit": f"{district or 'Unknown district'} development-deficit weighting",
    }

    factors = []
    total = 0.0
    for key, weight in WEIGHTS.items():
        contribution = raw[key] * weight * 100
        total += contribution
        factors.append(
            PriorityFactor(
                factor=key,
                raw_value=round(raw[key], 3),
                weight=weight,
                contribution=round(contribution, 2),
                explanation=explanations[key],
            )
        )

    factors.sort(key=lambda f: f.contribution, reverse=True)
    return PriorityResult(score=round(min(100.0, total), 2), factors=factors)
