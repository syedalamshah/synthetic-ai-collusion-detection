"""Metrics for binary paired detector evaluation."""
from typing import Iterable, Dict


def binary_metrics(labels: Iterable[int], predictions: Iterable[int]) -> dict:
    labels, predictions = list(labels), list(predictions)
    if len(labels) != len(predictions) or not labels:
        raise ValueError("labels and predictions must be non-empty and equal length")
    if any(x not in (0, 1) for x in labels + predictions):
        raise ValueError("labels and predictions must be binary")
    tp = sum(y == 1 and p == 1 for y, p in zip(labels, predictions))
    tn = sum(y == 0 and p == 0 for y, p in zip(labels, predictions))
    fp = sum(y == 0 and p == 1 for y, p in zip(labels, predictions))
    fn = sum(y == 1 and p == 0 for y, p in zip(labels, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"n": len(labels), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "accuracy": (tp + tn) / len(labels), "precision": precision,
            "recall": recall, "f1": f1, "specificity": specificity,
            "false_positive_rate": 1 - specificity,
            "balanced_accuracy": (recall + specificity) / 2}


def paired_disagreements(results: Dict[str, Dict[str, int]]) -> list:
    """Return case IDs where detector conditions disagree."""
    case_ids = sorted({case for result in results.values() for case in result})
    return [{"case_id": case, "predictions": {
        condition: results[condition].get(case) for condition in sorted(results)
    }} for case in case_ids
       if len({results[c].get(case) for c in results}) > 1]
