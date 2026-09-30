def precision(true_positives: int, false_positives: int) -> float:
    return true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 1.0

def recall(true_positives: int, false_negatives: int) -> float:
    return true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 1.0

def f1_score(p: float, r: float) -> float:
    return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0

def action_concept_match(expected_concepts: list[str], predicted_actions: list[str]) -> tuple[int, int, int]:
    """
    Returns (true_positives, false_positives, false_negatives) based on basic keyword matching.
    """
    if not expected_concepts and not predicted_actions:
        return (0, 0, 0)
        
    tps = 0
    fps = 0
    fns = 0
    
    # Very naive matching for automated evaluation:
    # If the predicted action's description or intent matches an expected concept string
    pred_text = " ".join([pa.lower() for pa in predicted_actions])
    for concept in expected_concepts:
        if concept.lower() in pred_text:
            tps += 1
        else:
            fns += 1
            
    # Assuming any predicted action not containing ANY expected concept is a false positive
    for pa in predicted_actions:
        matched = False
        for concept in expected_concepts:
            if concept.lower() in pa.lower():
                matched = True
                break
        if not matched:
            fps += 1
            
    return tps, fps, fns
