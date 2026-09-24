import json
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from mcp.server.fastmcp import FastMCP
from supabase import Client, create_client

from services.food_service import (
    filter_foods_by_nutrition as service_filter_foods_by_nutrition,
    get_food_by_id as service_get_food_by_id,
    search_food as service_search_food,
)

load_dotenv()

PORT = int(os.getenv("PORT", "8000"))
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量！")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="HongKong Food MCP & REST API", version="2.1.1")
mcp = FastMCP("HongKong Food Database MCP Server", host="0.0.0.0", port=PORT)


@app.get("/api/search_food")
async def api_search_food(keyword: str = Query(..., description="要查询的香港食品名称")):
    return service_search_food(supabase=supabase, query=keyword, limit=10)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "hk-food-mcp", "version": "2.1.1"}


@mcp.tool()
def search_foods(query: str, category: Optional[str] = None, limit: int = 10) -> str:
    result = service_search_food(supabase=supabase, query=query, category=category, limit=limit)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_food_by_id(food_id: str) -> str:
    result = service_get_food_by_id(supabase=supabase, food_id=food_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def filter_foods_by_nutrition(
    max_calories: Optional[float] = None,
    min_protein: Optional[float] = None,
    max_sodium: Optional[float] = None,
    limit: int = 10,
) -> str:
    result = service_filter_foods_by_nutrition(
        supabase=supabase,
        max_calories=max_calories,
        min_protein=min_protein,
        max_sodium=max_sodium,
        limit=limit,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
