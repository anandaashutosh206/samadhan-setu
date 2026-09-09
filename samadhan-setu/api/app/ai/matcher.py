from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer

from app.ai.dedupe import haversine_km


@dataclass
class UniversityCandidate:
    id: str
    name: str
    district: str
    disciplines: list[str]
    research_areas: list[str]
    has_incubation: bool
    naac_grade: str | None
    lat: float
    lng: float
    capacity_score: float
    active_project_count: int


@dataclass
class MatchResult:
    university_id: str
    name: str
    district: str
    match_score: float
    match_reasons: list[str]


NAAC_BONUS = {"A++": 0.1, "A+": 0.08, "A": 0.06, "B++": 0.03, "B+": 0.02, "B": 0.0}

DOMAIN_DISCIPLINE_MAP = {
    "education": ["education", "social sciences", "humanities"],
    "agriculture": ["agriculture", "agricultural engineering", "food technology", "biotechnology"],
    "healthcare": ["biotechnology", "pharmacy", "medicine", "public health", "life sciences"],
    "water_resources": ["civil engineering", "environmental engineering", "geology"],
    "environment": ["environmental science", "environmental engineering", "forestry"],
    "energy": ["electrical engineering", "renewable energy", "mechanical engineering"],
    "urban_development": ["civil engineering", "urban planning", "architecture"],
    "accessibility": ["design", "electronics", "computer science", "social sciences"],
    "public_administration": ["public policy", "management", "law"],
    "rural_livelihoods": ["management", "rural development", "agriculture", "social work"],
}


def _discipline_overlap_score(domain: str, disciplines: list[str]) -> float:
    target = set(d.lower() for d in DOMAIN_DISCIPLINE_MAP.get(domain, []))
    have = set(d.lower() for d in disciplines)
    if not target:
        return 0.0
    overlap = target & have
    return len(overlap) / len(target)


def match_universities(
    challenge_text: str,
    domain: str,
    district: str | None,
    lat: float | None,
    lng: float | None,
    universities: list[UniversityCandidate],
    top_n: int = 5,
) -> list[MatchResult]:
    if not universities:
        return []

    research_texts = [" ".join(u.research_areas) or u.name for u in universities]
    try:
        vec = TfidfVectorizer(stop_words="english")
        matrix = vec.fit_transform([challenge_text] + research_texts)
        research_sims = (matrix[0] @ matrix[1:].T).toarray()[0]
    except ValueError:
        research_sims = [0.0] * len(universities)

    results: list[MatchResult] = []
    for uni, research_sim in zip(universities, research_sims):
        reasons = []

        discipline_score = _discipline_overlap_score(domain, uni.disciplines)
        if discipline_score > 0:
            reasons.append(f"{round(discipline_score * 100)}% discipline overlap with '{domain}'")

        if research_sim > 0.15:
            reasons.append(f"Research focus closely matches challenge text ({round(research_sim * 100)}%)")

        incubation_bonus = 0.08 if uni.has_incubation else 0.0
        if uni.has_incubation:
            reasons.append("Has an active incubation centre")

        naac_bonus = NAAC_BONUS.get(uni.naac_grade or "", 0.0)
        if naac_bonus > 0:
            reasons.append(f"NAAC grade {uni.naac_grade}")

        distance_km = None
        proximity_score = 0.0
        if lat is not None and lng is not None:
            distance_km = haversine_km(lat, lng, uni.lat, uni.lng)
            proximity_score = max(0.0, 1 - min(distance_km, 300) / 300)
            if distance_km <= 60:
                reasons.append(f"Only {round(distance_km)} km from challenge location")
        elif district and uni.district.lower() == district.lower():
            proximity_score = 0.5
            reasons.append(f"Located in the same district ({district})")

        load_penalty = min(0.3, uni.active_project_count * 0.03)
        load_score = max(0.0, 1 - load_penalty)
        if uni.active_project_count > 5:
            reasons.append(f"Currently handling {uni.active_project_count} active projects (load considered)")

        raw_score = (
            0.30 * discipline_score
            + 0.25 * research_sim
            + 0.15 * proximity_score
            + incubation_bonus
            + naac_bonus
            + 0.12 * load_score
            + 0.05 * (uni.capacity_score / 100)
        )
        final_score = round(min(1.0, raw_score) * 100, 1)

        results.append(
            MatchResult(
                university_id=uni.id,
                name=uni.name,
                district=uni.district,
                match_score=final_score,
                match_reasons=reasons or ["General capability match"],
            )
        )

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results[:top_n]
