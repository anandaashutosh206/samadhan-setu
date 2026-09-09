import re

from sklearn.feature_extraction.text import TfidfVectorizer

# Domain-relevant Hindi/Hinglish terms that commonly appear in citizen-submitted
# reports; if present in the text they get boosted so they surface as keywords
# even when TF-IDF alone would rank them below generic English terms.
HINGLISH_LEXICON = {
    "paani": "water", "jal": "water", "bijli": "electricity", "sadak": "road",
    "vidyalaya": "school", "aspatal": "hospital", "aanganwadi": "anganwadi",
    "kisan": "farmer", "fasal": "crop", "swasthya": "health", "shiksha": "education",
    "panchayat": "panchayat", "gram": "village", "mgnrega": "mgnrega",
    "ration": "ration", "pension": "pension",
}

STOPWORDS = {
    "the", "a", "an", "in", "on", "at", "of", "to", "for", "and", "or", "is",
    "are", "was", "were", "has", "have", "had", "with", "this", "that", "it",
    "as", "by", "from", "be", "been", "not", "no", "district", "report",
    "reports", "reported",
}


def extract_keywords(text: str, top_k: int = 8) -> list[str]:
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
    tokens = [t for t in cleaned.split() if t not in STOPWORDS and len(t) > 2]
    if not tokens:
        return []

    joined = " ".join(tokens)
    try:
        vec = TfidfVectorizer(ngram_range=(1, 2), max_features=40, stop_words="english")
        matrix = vec.fit_transform([joined])
        scores = matrix.toarray()[0]
        terms = vec.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
        keywords = [t for t, s in ranked if s > 0][:top_k]
    except ValueError:
        keywords = list(dict.fromkeys(tokens))[:top_k]

    # Boost lexicon hits present in the raw text (case-insensitive)
    lowered = text.lower()
    for hi_term, en_term in HINGLISH_LEXICON.items():
        if hi_term in lowered and en_term not in keywords:
            keywords.insert(0, en_term)

    # Deduplicate, cap
    seen: set[str] = set()
    result = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            result.append(k)
        if len(result) >= top_k:
            break
    return result
