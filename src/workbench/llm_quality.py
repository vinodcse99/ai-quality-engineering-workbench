
def evaluate_response(response, required_terms=(), forbidden_terms=()):
    """
    Perform basic deterministic quality checks on an LLM response.

    These are initial lexical checks, not semantic LLM evaluation.
    """

    reasons = []

    if not isinstance(response, str) or not response.strip():
        return {
            "passed": False,
            "reasons": ["Response is empty or invalid."]
        }

    normalized_response = response.casefold()

    missing_terms = [
        term for term in required_terms
        if term.casefold() not in normalized_response
    ]

    forbidden_matches = [
        term for term in forbidden_terms
        if term.casefold() in normalized_response
    ]

    if missing_terms:
        reasons.append(
            f"Missing required terms: {missing_terms}"
        )

    if forbidden_matches:
        reasons.append(
            f"Forbidden terms detected: {forbidden_matches}"
        )

    return {
        "passed": len(reasons) == 0,
        "reasons": reasons
    }
