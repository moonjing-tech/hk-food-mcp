from resolver.aliases import resolve_alias
from resolver.normalize import normalize_query


def build_search_terms(query: str) -> list[str]:
    """
    生成搜索关键词。
    不会把有歧义的“牛河”等词强制映射为某一种具体食品。
    """
    cleaned = normalize_query(query)
    resolved = resolve_alias(cleaned)

    terms = []
    for value in (cleaned, resolved, cleaned.replace(" ", "")):
        if value and value not in terms:
            terms.append(value)

    return terms
