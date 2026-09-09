import json
import logging
from pathlib import Path

import joblib
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger("samadhan.ai.classifier")

AI_DIR = Path(__file__).parent
DATA_PATH = AI_DIR / "data" / "train_challenges.json"
MODELS_DIR = AI_DIR / "models"
DOMAIN_MODEL_PATH = MODELS_DIR / "domain_classifier.joblib"
SEVERITY_MODEL_PATH = MODELS_DIR / "severity_classifier.joblib"


def _build_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words="english")),
            ("clf", CalibratedClassifierCV(LinearSVC(), cv=3)),
        ]
    )


def _load_corpus() -> list[dict]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Training corpus not found at {DATA_PATH}. Run "
            "`python app/ai/data/generate_corpus.py` first."
        )
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


class ChallengeClassifier:
    """Wraps two calibrated LinearSVC pipelines (domain, severity). Trains
    automatically on first run if no persisted .joblib is found, then
    persists to disk so subsequent boots load instantly."""

    def __init__(self) -> None:
        self.domain_pipeline: Pipeline | None = None
        self.severity_pipeline: Pipeline | None = None
        self.training_examples = 0
        self._load_or_train()

    def _load_or_train(self) -> None:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        corpus = _load_corpus()
        self.training_examples = len(corpus)

        if DOMAIN_MODEL_PATH.exists() and SEVERITY_MODEL_PATH.exists():
            logger.info("Loading persisted AI classifiers from disk.")
            self.domain_pipeline = joblib.load(DOMAIN_MODEL_PATH)
            self.severity_pipeline = joblib.load(SEVERITY_MODEL_PATH)
            return

        logger.info("No persisted classifier found — training on %d examples...", len(corpus))
        texts = [f"{row['title']} {row['description']}" for row in corpus]
        domains = [row["domain"] for row in corpus]
        severities = [row["severity"] for row in corpus]

        domain_pipe = _build_pipeline()
        domain_pipe.fit(texts, domains)

        severity_pipe = _build_pipeline()
        severity_pipe.fit(texts, severities)

        joblib.dump(domain_pipe, DOMAIN_MODEL_PATH)
        joblib.dump(severity_pipe, SEVERITY_MODEL_PATH)

        self.domain_pipeline = domain_pipe
        self.severity_pipeline = severity_pipe
        logger.info("AI classifiers trained and persisted to %s", MODELS_DIR)

    def classify_domain(self, text: str) -> tuple[str, float, list[dict]]:
        assert self.domain_pipeline is not None
        proba = self.domain_pipeline.predict_proba([text])[0]
        classes = self.domain_pipeline.classes_
        ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
        top_label, top_conf = ranked[0]
        top3 = [{"domain": str(c), "confidence": round(float(p), 4)} for c, p in ranked[:3]]
        return str(top_label), round(float(top_conf), 4), top3

    def classify_severity(self, text: str) -> tuple[str, float]:
        assert self.severity_pipeline is not None
        proba = self.severity_pipeline.predict_proba([text])[0]
        classes = self.severity_pipeline.classes_
        ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
        top_label, top_conf = ranked[0]
        return str(top_label), round(float(top_conf), 4)


_classifier_singleton: ChallengeClassifier | None = None


def get_classifier() -> ChallengeClassifier:
    global _classifier_singleton
    if _classifier_singleton is None:
        _classifier_singleton = ChallengeClassifier()
    return _classifier_singleton
