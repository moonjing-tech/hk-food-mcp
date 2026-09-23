import os
import json
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from supabase import create_client, Client
from fastapi import Query

load_dotenv()

# 1. 初始化 FastMCP，支持云端部署的 host 和 port 配置
PORT = int(os.getenv("PORT", 8000))
mcp = FastMCP("HongKong Food Database MCP Server", host="0.0.0.0", port=PORT)

# 2. 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量！")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================
# 📍 新增：供本地无 Python 环境客户端直接使用的 HTTP GET 接口
# ==========================================
@mcp.app.get("/api/search_food")
async def api_search_food(keyword: str = Query(..., description="要查询的食物名称")):
    """支持外部客户端通过标准 HTTP GET 请求直接检索香港外食数据"""
    try:
        res = supabase.table("foods").select("*").ilike("name", f"%{keyword}%").limit(10).execute()
        if not res.data:
            return {"status": "empty", "message": f"未找到与 '{keyword}' 相关的食物。", "data": []}
        return {"status": "success", "count": len(res.data), "data": res.data}
    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}


# ==========================================
# MCP Tools 逻辑 (保留不变)
# ==========================================
@mcp.tool()
def search_foods(query: str, category: Optional[str] = None, limit: int = 10) -> str:
    """根据食物名称模糊搜索香港外食数据库中的食物营养及热量信息。"""
    try:
        builder = supabase.table("foods").select("*").ilike("name", f"%{query}%")
        if category:
            builder = builder.eq("category", category)
        res = builder.limit(limit).execute()
        if not res.data:
            return json.dumps({"status": "empty", "message": f"未找到与 '{query}' 相关的食物。"}, ensure_ascii=False)
        return json.dumps({"status": "success", "count": len(res.data), "data": res.data}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


@mcp.tool()
def get_food_by_id(food_id: str) -> str:
    """根据食物唯一 ID（如 HK001）获取完整的营养成分数据。"""
    try:
        res = supabase.table("foods").select("*").eq("id", food_id).execute()
        if not res.data:
            return json.dumps({"status": "not_found", "message": f"未找到编号 '{food_id}'。"}, ensure_ascii=False)
        return json.dumps({"status": "success", "data": res.data[0]}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


@mcp.tool()
def filter_foods_by_nutrition(
    max_calories: Optional[float] = None,
    min_protein: Optional[float] = None,
    max_sodium: Optional[float] = None,
    limit: int = 10
) -> str:
    """按营养指标（热量、蛋白质、钠含量等）筛选食物。"""
    try:
        builder = supabase.table("foods").select("id, name, category, calories_kcal, protein_g, sodium_mg, serving_g")
        if max_calories is not None:
            builder = builder.lte("calories_kcal", max_calories)
        if min_protein is not None:
            builder = builder.gte("protein_g", min_protein)
        if max_sodium is not None:
            builder = builder.lte("sodium_mg", max_sodium)
        res = builder.limit(limit).execute()
        return json.dumps({"status": "success", "count": len(res.data), "data": res.data}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    # 以 SSE 传输方式启动，对外暴露 HTTP/SSE 接口
    mcp.run(transport="sse")
