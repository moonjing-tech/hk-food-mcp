from typing import Any, Dict, Optional

from resolver.aliases import expand_aliases
from resolver.matcher import rank_results
from resolver.normalize import normalize_query


SEARCH_FIELDS = (
    "id,name,category,calories_kcal,protein_g,fat_g,fat_ratio_pct,"
    "carbs_g,sugar_g,sodium_mg,cholesterol_mg,fiber_g,serving_g,"
    "data_basis,evidence_grade,data_notes,comparable_targets,source_org,"
    "report_name,report_year,sample_count,last_verified,source_status,"
    "research_id,content_id,usage_status,content_notes,unit_calories_kcal,"
    "unit_description,created_at,updated_at"
)


def _error(message: str, query: str = "") -> Dict[str, Any]:
    return {"status": "error", "query": query, "count": 0, "data": [], "message": message}


def search_food(supabase, query: str, category: Optional[str] = None, limit: int = 10):
    normalized = normalize_query(query)
    if not normalized:
        return _error("请输入食物名称。", query)

    limit = max(1, min(int(limit or 10), 50))
    terms = expand_aliases(normalized)
    collected = {}

    # Query each alias/canonical form, then rank locally. This keeps REST and
    # MCP behavior identical and makes alias matching deterministic.
    for term in terms:
        builder = supabase.table("foods").select(SEARCH_FIELDS).ilike("name", f"%{term}%")
        if category:
            builder = builder.eq("category", category)
        response = builder.limit(max(limit, 20)).execute()
        for item in response.data or []:
            collected[item.get("id")] = item

    ranked = rank_results(list(collected.values()), normalized)[:limit]
    return {"status": "success", "query": normalized, "count": len(ranked), "data": ranked}


def get_food_by_id(supabase, food_id: str):
    response = supabase.table("foods").select(SEARCH_FIELDS).eq("id", food_id).limit(1).execute()
    if not response.data:
        return _error("找不到对应食物。", food_id)
    return {"status": "success", "query": food_id, "count": 1, "data": response.data}


def filter_foods_by_nutrition(
    supabase,
    max_calories: Optional[float] = None,
    min_protein: Optional[float] = None,
    max_sodium: Optional[float] = None,
    limit: int = 10,
):
    builder = supabase.table("foods").select(
        "id,name,category,calories_kcal,protein_g,sodium_mg,serving_g,data_basis,unit_description"
    )
    if max_calories is not None:
        builder = builder.lte("calories_kcal", max_calories)
    if min_protein is not None:
        builder = builder.gte("protein_g", min_protein)
    if max_sodium is not None:
        builder = builder.lte("sodium_mg", max_sodium)
    response = builder.limit(max(1, min(int(limit or 10), 50))).execute()
    return {"status": "success", "count": len(response.data or []), "data": response.data or []}
