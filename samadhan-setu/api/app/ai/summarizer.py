import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 0]


def summarize(text: str, max_sentences: int = 3) -> str:
    sentences = _split_sentences(text)
    if len(sentences) <= max_sentences:
        return text.strip()

    vec = TfidfVectorizer(stop_words="english")
    try:
        matrix = vec.fit_transform(sentences)
    except ValueError:
        return " ".join(sentences[:max_sentences])

    sim = (matrix @ matrix.T).toarray()
    np.fill_diagonal(sim, 0)

    # Simple TextRank power-iteration over the sentence similarity graph
    n = sim.shape[0]
    row_sums = sim.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    transition = sim / row_sums

    scores = np.ones(n) / n
    damping = 0.85
    for _ in range(30):
        scores = (1 - damping) / n + damping * (transition.T @ scores)

    top_idx = np.argsort(scores)[::-1][:max_sentences]
    top_idx_sorted = sorted(top_idx)  # keep original order for readability
    return " ".join(sentences[i] for i in top_idx_sorted)
