# -----------------------------------------------------------------------------
# SmartLead AI – Lead Scoring & Analysis Engine
# Weighted NLP scoring using domain keywords + TextBlob sentiment analysis.
# Produces interest scores, lead categories (HOT/WARM/COLD), and sentiment.
# -----------------------------------------------------------------------------

from textblob import TextBlob
from data.keywords import get_keywords_for_domain


# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------
_HIGH_INTENT_WEIGHT   = 35
_MEDIUM_INTENT_WEIGHT = 20
_LOW_INTENT_WEIGHT    = 8
_SENTIMENT_BOOST      = 10   # positive TextBlob polarity bonus
_SENTIMENT_PENALTY    = 5    # negative TextBlob polarity penalty
_BASE_SCORE           = 10

# Universal buying/enrollment intent signals (domain-agnostic)
_UNIVERSAL_HIGH = [
    "want to", "interested in", "need details", "how to apply", "fees",
    "price", "buy", "enroll", "admission", "join", "purchase",
    "booking", "registration", "apply", "inquiry", "planning to",
    "looking to", "which one should", "recommend", "best option"
]


def calculate_interest_score(comment: str, domain: str = "") -> int:
    """
    Calculate interest score (0–100) for a given comment.

    Scoring logic:
    - Base score of 10
    - +30 per high-intent keyword match
    - +18 per medium-intent keyword match
    - +8  per low-intent keyword match
    - ±10 based on TextBlob sentiment polarity
    """
    if not comment or not isinstance(comment, str):
        return _BASE_SCORE

    text = comment.lower()
    score = _BASE_SCORE

    # ── Universal intent signals (applied always) ───────────────────────────
    for phrase in _UNIVERSAL_HIGH:
        if phrase in text:
            score += 15
            break  # only count first universal match to avoid over-inflation

    # ── Domain-specific keyword matching ────────────────────────────────────
    if domain:
        kw = get_keywords_for_domain(domain)
        for phrase in kw.get("high_intent", []):
            if phrase in text:
                score += _HIGH_INTENT_WEIGHT

        for phrase in kw.get("medium_intent", []):
            if phrase in text:
                score += _MEDIUM_INTENT_WEIGHT

        for phrase in kw.get("low_intent", []):
            if phrase in text:
                score += _LOW_INTENT_WEIGHT

    else:
        # Generic fallback when no domain is provided
        _generic_high = [
            "want to buy", "want to join", "interested in", "enroll", "purchase",
            "fees", "price", "how to apply", "admission", "booking"
        ]
        _generic_mid = [
            "need details", "course", "training", "review", "compare",
            "recommend", "best", "which one", "guide"
        ]
        _generic_low = [
            "nice", "good", "great", "love", "like", "watch"
        ]
        for phrase in _generic_high:
            if phrase in text:
                score += _HIGH_INTENT_WEIGHT
        for phrase in _generic_mid:
            if phrase in text:
                score += _MEDIUM_INTENT_WEIGHT
        for phrase in _generic_low:
            if phrase in text:
                score += _LOW_INTENT_WEIGHT

    # ── TextBlob sentiment adjustment ───────────────────────────────────────
    try:
        polarity = TextBlob(comment).sentiment.polarity
        if polarity > 0.2:
            score += _SENTIMENT_BOOST
        elif polarity < -0.1:
            score -= _SENTIMENT_PENALTY
    except Exception:
        pass  # graceful fallback if TextBlob fails

    return max(5, min(100, score))


def get_lead_category(score: int) -> str:
    """Classify a lead based on interest score."""
    if score >= 80:
        return "HOT LEAD"
    elif score >= 50:
        return "WARM LEAD"
    else:
        return "COLD LEAD"


def get_sentiment_label(score: int) -> str:
    """Return human-readable sentiment label based on score."""
    if score >= 80:
        return "Highly Interested"
    elif score >= 50:
        return "Interested"
    else:
        return "Low Interest"


def analyze_dataframe(df, domain: str):
    """
    Apply full analysis pipeline to a leads DataFrame.

    Adds columns: Interest Score, Lead Category, Sentiment
    """
    df = df.copy()
    df["Interest Score"] = df["Comment"].apply(
        lambda c: calculate_interest_score(c, domain)
    )
    df["Lead Category"] = df["Interest Score"].apply(get_lead_category)
    df["Sentiment"]     = df["Interest Score"].apply(get_sentiment_label)
    return df