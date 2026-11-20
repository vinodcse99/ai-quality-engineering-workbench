
def evaluate_retrieval(
    retrieved_document_ids,
    relevant_document_ids,
    k=None,
):
    """
    Evaluate retrieval quality using deterministic ranking metrics.

    Metrics:
    - Precision@K
    - Recall@K
    - F1@K
    - Hit Rate@K
    - Mean Reciprocal Rank@K (MRR)

    This implementation evaluates document IDs against known
    relevance labels. It does not evaluate semantic relevance.
    """

    if not isinstance(retrieved_document_ids, list):
        raise TypeError("Retrieved document IDs must be a list.")

    if not isinstance(relevant_document_ids, list):
        raise TypeError("Relevant document IDs must be a list.")

    if not relevant_document_ids:
        raise ValueError("At least one relevant document ID is required.")

    for document_id in retrieved_document_ids + relevant_document_ids:
        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("Document IDs must be non-empty strings.")

    if len(set(retrieved_document_ids)) != len(retrieved_document_ids):
        raise ValueError("Retrieved document IDs must be unique.")

    if len(set(relevant_document_ids)) != len(relevant_document_ids):
        raise ValueError("Relevant document IDs must be unique.")

    if k is not None:
        if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
            raise ValueError("K must be a positive integer.")

        retrieved_document_ids = retrieved_document_ids[:k]

    relevant_set = set(relevant_document_ids)
    retrieved_set = set(retrieved_document_ids)

    relevant_retrieved = retrieved_set.intersection(relevant_set)

    retrieved_count = len(retrieved_document_ids)
    relevant_count = len(relevant_document_ids)
    relevant_retrieved_count = len(relevant_retrieved)

    precision = (
        relevant_retrieved_count / retrieved_count
        if retrieved_count
        else 0.0
    )

    recall = relevant_retrieved_count / relevant_count

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    reciprocal_rank = 0.0

    for rank, document_id in enumerate(retrieved_document_ids, start=1):
        if document_id in relevant_set:
            reciprocal_rank = 1 / rank
            break

    return {
        "precision_at_k": round(precision, 4),
        "recall_at_k": round(recall, 4),
        "f1_at_k": round(f1_score, 4),
        "hit_rate_at_k": int(relevant_retrieved_count > 0),
        "mrr_at_k": round(reciprocal_rank, 4),
        "retrieved_count": retrieved_count,
        "relevant_count": relevant_count,
        "relevant_retrieved_count": relevant_retrieved_count,
    }
