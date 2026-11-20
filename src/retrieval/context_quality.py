
import re


def _normalize_text(value):
    """Normalize text for deterministic phrase matching."""
    if not isinstance(value, str):
        raise TypeError("Text values must be strings.")

    return " ".join(re.findall(r"\w+", value.casefold()))


def _validate_text_list(values, field_name, allow_empty=True):
    if not isinstance(values, list):
        raise TypeError(f"{field_name} must be a list.")

    if not allow_empty and not values:
        raise ValueError(f"{field_name} cannot be empty.")

    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must contain non-empty strings."
            )


def evaluate_context_relevance(question, retrieved_contexts):
    """
    Measure lexical overlap between the question and each retrieved passage.

    This is a deterministic lexical proxy, not semantic relevance.
    """
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a non-empty string.")

    _validate_text_list(
        retrieved_contexts,
        "Retrieved contexts",
    )

    stop_words = {
        "a", "an", "and", "are", "as", "at", "be", "by",
        "for", "from", "how", "in", "is", "it", "of",
        "on", "or", "the", "to", "what", "when", "where",
        "which", "who", "why", "with",
    }

    query_terms = {
        term
        for term in _normalize_text(question).split()
        if term not in stop_words
    }

    if not query_terms or not retrieved_contexts:
        scores = [0.0] * len(retrieved_contexts)
    else:
        scores = []

        for context in retrieved_contexts:
            context_terms = set(_normalize_text(context).split())
            overlap = query_terms.intersection(context_terms)
            scores.append(round(len(overlap) / len(query_terms), 4))

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    return {
        "metric": "Context Relevance",
        "context_scores": scores,
        "average_context_relevance": round(average_score, 4),
        "context_count": len(retrieved_contexts),
    }


def evaluate_context_precision(
    retrieved_context_ids,
    relevant_context_ids,
):
    """
    Calculate rank-aware Average Precision for retrieved contexts.

    Relevance labels are supplied as ground truth.
    """
    _validate_text_list(
        retrieved_context_ids,
        "Retrieved context IDs",
    )
    _validate_text_list(
        relevant_context_ids,
        "Relevant context IDs",
        allow_empty=False,
    )

    if len(set(retrieved_context_ids)) != len(retrieved_context_ids):
        raise ValueError("Retrieved context IDs must be unique.")

    if len(set(relevant_context_ids)) != len(relevant_context_ids):
        raise ValueError("Relevant context IDs must be unique.")

    relevant_set = set(relevant_context_ids)

    relevant_found = 0
    precision_sum = 0.0

    for rank, context_id in enumerate(retrieved_context_ids, start=1):
        if context_id in relevant_set:
            relevant_found += 1
            precision_sum += relevant_found / rank

    average_precision = (
        precision_sum / len(relevant_set)
        if relevant_set
        else 0.0
    )

    return {
        "metric": "Context Precision",
        "context_precision": round(average_precision, 4),
        "relevant_contexts_found": relevant_found,
        "relevant_contexts_total": len(relevant_set),
    }


def evaluate_context_recall(retrieved_contexts, required_facts):
    """
    Measure how many reference facts appear in retrieved passages.

    A fact counts as found when its normalized phrase appears
    in at least one retrieved passage.
    """
    _validate_text_list(
        retrieved_contexts,
        "Retrieved contexts",
    )
    _validate_text_list(
        required_facts,
        "Required facts",
        allow_empty=False,
    )

    normalized_contexts = [
        _normalize_text(context)
        for context in retrieved_contexts
    ]

    found_facts = []
    missing_facts = []

    for fact in required_facts:
        normalized_fact = _normalize_text(fact)

        found = any(
            normalized_fact in context
            for context in normalized_contexts
        )

        if found:
            found_facts.append(fact)
        else:
            missing_facts.append(fact)

    recall = len(found_facts) / len(required_facts)

    return {
        "metric": "Context Recall",
        "context_recall": round(recall, 4),
        "found_facts": found_facts,
        "missing_facts": missing_facts,
        "required_fact_count": len(required_facts),
    }


def evaluate_answer_grounding(retrieved_contexts, answer_claims):
    """
    Check whether explicit evidence phrases for answer claims
    appear in the retrieved context.

    This is a phrase-matching proxy, not semantic entailment.
    """
    _validate_text_list(
        retrieved_contexts,
        "Retrieved contexts",
    )

    if not isinstance(answer_claims, list):
        raise TypeError("Answer claims must be a list.")

    if not answer_claims:
        raise ValueError("At least one answer claim is required.")

    normalized_context = " ".join(
        _normalize_text(context)
        for context in retrieved_contexts
    )

    grounded_claims = []
    unsupported_claims = []

    for item in answer_claims:
        if not isinstance(item, dict):
            raise TypeError("Each answer claim must be an object.")

        claim = item.get("claim")
        evidence = item.get("required_evidence")

        if not isinstance(claim, str) or not claim.strip():
            raise ValueError("Each claim must have non-empty text.")

        _validate_text_list(
            evidence,
            "Required evidence",
            allow_empty=False,
        )

        supported = all(
            _normalize_text(phrase) in normalized_context
            for phrase in evidence
        )

        if supported:
            grounded_claims.append(claim)
        else:
            unsupported_claims.append(claim)

    grounding_score = (
        len(grounded_claims) / len(answer_claims)
    )

    return {
        "metric": "Answer Grounding",
        "grounding_score": round(grounding_score, 4),
        "grounded_claims": grounded_claims,
        "unsupported_claims": unsupported_claims,
        "total_claims": len(answer_claims),
    }
