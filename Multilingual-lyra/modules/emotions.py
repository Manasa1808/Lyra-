from transformers import pipeline, __version__

from transformers import pipeline, __version__

class SentimentModel:
    """
    Uses a lightweight multilingual sentiment model.
    Maps to POSITIVE / NEGATIVE / NEUTRAL.
    """
    def __init__(self):
        try:
            self._pipe = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to load pipeline (Transformers version {__version__}). "
                f"Try: pip install --upgrade transformers\nError: {e}"
            )

    def classify(self, text: str) -> str:
        try:
            res = self._pipe(text[:512])[0]["label"]
            stars = int(res.split()[0])
            if stars >= 4:
                return "POSITIVE"
            if stars <= 2:
                return "NEGATIVE"
            return "NEUTRAL"
        except Exception:
            return "NEUTRAL"
class SentimentModel:
    """
    Uses a lightweight multilingual sentiment model.
    Maps to POSITIVE / NEGATIVE / NEUTRAL.
    """
    def __init__(self):
        try:
            self._pipe = pipeline(
                "sentiment-analysis", 
                model="nlptown/bert-base-multilingual-uncased-sentiment"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to load pipeline (Transformers version {__version__}). "
                f"Try: pip install --upgrade transformers\nError: {e}"
            )

    def classify(self, text: str) -> str:
        try:
            res = self._pipe(text[:512])[0]["label"]  # e.g., '5 stars'
            stars = int(res.split()[0])
            if stars >= 4:
                return "POSITIVE"
            if stars <= 2:
                return "NEGATIVE"
            return "NEUTRAL"
        except Exception:
            return "NEUTRAL"