def apply_guardrails(score, threshold=0.5):
    """
    Lower score = better similarity (FAISS)
    """

    if score > threshold:
        return {
            "answer": "Not found in document",
            "sources": [],
            "confidence": 0.2
        }

    return None