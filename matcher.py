from typing import Any, Dict

FULL_DISH_CATEGORIES = {
    "炒粉麵", "碟頭飯", "粥品", "湯粉麵", "飲品", "點心", "小食", "早餐"
}


def _norm(v: Any) -> str:
    return "" if v is None else str(v).strip()


def score_result(item: Dict[str, Any], query: str) -> float:
    name = _norm(item.get("name"))
    category = _norm(item.get("category"))
    if not name:
        return -1

    score = 0.0
    if name == query:
        score += 1000
    elif query and query in name:
        score += 700
        score -= max(0, len(name) - len(query)) * 2
    else:
        # Token coverage: useful for multi-character food terms without
        # turning every fuzzy result into a high-confidence match.
        tokens = [c for c in query if c.strip()]
        if tokens:
            coverage = sum(1 for c in tokens if c in name) / len(tokens)
            score += coverage * 300

    # Prefer complete dishes over ingredient/component records for ambiguous
    # searches such as 牛河. Do not remove the ingredient results.
    if category in FULL_DISH_CATEGORIES:
        score += 80
    elif category == "配料":
        score -= 120

    return score


def rank_results(results, query):
    return sorted(results, key=lambda x: score_result(x, query), reverse=True)


def comparable(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """Only allow direct nutrition comparisons when the measurement basis matches."""
    basis_a = _norm(a.get("data_basis"))
    basis_b = _norm(b.get("data_basis"))
    unit_a = _norm(a.get("unit_description"))
    unit_b = _norm(b.get("unit_description"))

    if basis_a and basis_b and basis_a != basis_b:
        return False
    if unit_a and unit_b and unit_a != unit_b:
        return False

    # If one record is per 100g/ml and another is per dish/cup, they are not
    # directly comparable even if one of the metadata fields is absent.
    text_a = f"{basis_a} {unit_a}"
    text_b = f"{basis_b} {unit_b}"
    per_weight_a = "100g" in text_a or "100ml" in text_a
    per_weight_b = "100g" in text_b or "100ml" in text_b
    if per_weight_a != per_weight_b:
        return False
    return True
