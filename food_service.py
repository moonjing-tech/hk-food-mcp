from typing import Any, Optional

from supabase import Client

from resolver.aliases import resolve_alias
from resolver.matcher import build_search_terms
from resolver.normalize import normalize_query

MAX_LIMIT = 50


def _safe_limit(limit: int) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        value = 10
    return max(1, min(value, MAX_LIMIT))


def _contains_pattern(value: str) -> str:
    return "%" + "%".join(list(value)) + "%"


def _result_score(item: dict[str, Any], normalized_query: str) -> int:
    name = str(item.get("name", "") or "")

    if not normalized_query:
        return 99
    if name == normalized_query:
        return 0
    if normalized_query in name:
        return 1
    return 2


def search_food(
    supabase: Client,
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
) -> dict[str, Any]:
    original_query = query
    safe_limit = _safe_limit(limit)

    cleaned = normalize_query(query)
    normalized = resolve_alias(cleaned)
    terms = build_search_terms(query)

    if not terms:
        return {
            "status": "empty",
            "message": "請提供食品名稱。",
            "data": [],
        }

    try:
        conditions = []
        for term in terms:
            conditions.append(f"name.ilike.%{term}%")
            if len(term) > 1:
                conditions.append(f"name.ilike.{_contains_pattern(term)}")

        builder = (
            supabase
            .schema("public")
            .table("foods")
            .select("*")
            .or_(",".join(conditions))
        )

        if category:
            builder = builder.eq("category", category)

        response = builder.limit(safe_limit).execute()
        data = response.data or []
        data.sort(key=lambda item: _result_score(item, normalized))

        if not data:
            return {
                "status": "empty",
                "query": original_query,
                "message": f"未找到与「{original_query}」相关的食物。",
                "data": [],
            }

        return {
            "status": "success",
            "query": original_query,
            "count": len(data),
            "data": data,
        }

    except Exception as exc:
        return {
            "status": "error",
            "query": original_query,
            "message": str(exc),
            "data": [],
        }


def get_food_by_id(
    supabase: Client,
    food_id: str,
) -> dict[str, Any]:
    try:
        response = (
            supabase
            .schema("public")
            .table("foods")
            .select("*")
            .eq("id", food_id)
            .limit(1)
            .execute()
        )

        data = response.data or []

        if not data:
            return {
                "status": "not_found",
                "message": f"未找到编号「{food_id}」。",
                "data": [],
            }

        return {"status": "success", "data": data[0]}

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "data": [],
        }


def filter_foods_by_nutrition(
    supabase: Client,
    max_calories: Optional[float] = None,
    min_protein: Optional[float] = None,
    max_sodium: Optional[float] = None,
    limit: int = 10,
) -> dict[str, Any]:
    safe_limit = _safe_limit(limit)

    try:
        builder = (
            supabase
            .schema("public")
            .table("foods")
            .select(
                "id,name,category,calories_kcal,protein_g,"
                "fat_g,carbs_g,sodium_mg,serving_g"
            )
        )

        if max_calories is not None:
            builder = builder.lte("calories_kcal", max_calories)

        if min_protein is not None:
            builder = builder.gte("protein_g", min_protein)

        if max_sodium is not None:
            builder = builder.lte("sodium_mg", max_sodium)

        response = builder.limit(safe_limit).execute()
        data = response.data or []

        return {
            "status": "success",
            "count": len(data),
            "data": data,
        }

    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc),
            "data": [],
        }
