# -----------------------------------------------------------------------------
# SmartLead AI – Interest Filter Engine
# Filters comments based on keyword matches and scores them.
# -----------------------------------------------------------------------------

from analysis.lead_scoring import calculate_interest_score, get_lead_category, get_sentiment_label
from data.keywords import get_keywords_for_domain
from analysis.lead_scoring import _UNIVERSAL_HIGH

def is_interested(comment_text: str, domain: str) -> bool:
    """
    Check if a comment expresses any interest in the specified domain.
    Returns True if the comment contains any high/medium/low intent keyword for the domain,
    or matches any universal high-intent phrase.
    """
    if not comment_text or not isinstance(comment_text, str):
        return False
    
    text = comment_text.lower()
    
    # Check universal high-intent phrases first
    for phrase in _UNIVERSAL_HIGH:
        if phrase in text:
            return True
            
    # Check domain-specific keywords
    kw = get_keywords_for_domain(domain)
    if kw:
        for phrase in kw.get("high_intent", []):
            if phrase in text:
                return True
        for phrase in kw.get("medium_intent", []):
            if phrase in text:
                return True
        for phrase in kw.get("low_intent", []):
            if phrase in text:
                return True
                
    # Fallback to general generic checks if no domain keywords matched or if domain keywords not found
    _generic_keywords = [
        "want to buy", "want to join", "interested in", "enroll", "purchase",
        "fees", "price", "how to apply", "admission", "booking", "need details",
        "course", "training", "review", "compare", "recommend", "best", "which one",
        "guide", "nice", "good", "great", "love", "like"
    ]
    for phrase in _generic_keywords:
        if phrase in text:
            return True
            
    return False

def score_comment(comment_text: str, domain: str) -> int:
    """
    Calculate the interest score (0-100) for a given comment.
    """
    return calculate_interest_score(comment_text, domain)
