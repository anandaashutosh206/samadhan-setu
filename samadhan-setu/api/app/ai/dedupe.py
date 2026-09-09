from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


@dataclass
class ExistingChallenge:
    id: str
    title: str
    description: str
    district: str | None
    lat: float | None
    lng: float | None


@dataclass
class DuplicateCandidate:
    challenge_id: str
    title: str
    similarity: float
    reasons: list[str]
    distance_km: float | None


def find_duplicates(
    query_title: str,
    query_description: str,
    candidates: list[ExistingChallenge],
    threshold: float,
    query_district: str | None = None,
    query_lat: float | None = None,
    query_lng: float | None = None,
    max_results: int = 5,
) -> list[DuplicateCandidate]:
    if not candidates:
        return []

    query_text = f"{query_title} {query_description}"
    corpus_texts = [f"{c.title} {c.description}" for c in candidates]

    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vec.fit_transform([query_text] + corpus_texts)
        cosine_sims = (matrix[0] @ matrix[1:].T).toarray()[0]
    except ValueError:
        cosine_sims = [0.0] * len(candidates)

    results: list[DuplicateCandidate] = []
    for candidate, cos_sim in zip(candidates, cosine_sims):
        fuzzy_score = fuzz.token_set_ratio(query_text, f"{candidate.title} {candidate.description}") / 100.0
        combined = 0.6 * cos_sim + 0.4 * fuzzy_score

        distance_km = None
        geo_bonus = 0.0
        reasons = []

        if cos_sim > 0.3:
            reasons.append(f"Text similarity {round(cos_sim * 100)}%")
        if fuzzy_score > 0.5:
            reasons.append(f"Fuzzy phrase overlap {round(fuzzy_score * 100)}%")

        if query_lat is not None and query_lng is not None and candidate.lat is not None and candidate.lng is not None:
            distance_km = round(haversine_km(query_lat, query_lng, candidate.lat, candidate.lng), 1)
            if distance_km <= 15:
                geo_bonus = 0.1
                reasons.append(f"Only {distance_km} km apart")
        elif query_district and candidate.district and query_district.lower() == candidate.district.lower():
            geo_bonus = 0.05
            reasons.append("Same district")

        final_score = min(1.0, combined + geo_bonus)
        if final_score >= threshold:
            results.append(
                DuplicateCandidate(
                    challenge_id=candidate.id,
                    title=candidate.title,
                    similarity=round(final_score, 3),
                    reasons=reasons or ["Overall content similarity"],
                    distance_km=distance_km,
                )
            )

    results.sort(key=lambda r: r.similarity, reverse=True)
    return results[:max_results]
