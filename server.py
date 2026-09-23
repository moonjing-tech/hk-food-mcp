import os
import json
from typing import Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from supabase import create_client, Client
from fastapi import FastAPI, Query

load_dotenv()

# 1. 初始化独立的 FastAPI 应用
app = FastAPI(title="HongKong Food MCP & REST API")

# 2. 初始化 FastMCP
PORT = int(os.getenv("PORT", 8000))
mcp = FastMCP("HongKong Food Database MCP Server", host="0.0.0.0", port=PORT)

# 3. 初始化 Supabase 客户端
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量！")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==========================================
# 📍 1. 标准 HTTP GET 接口（供无 Python 环境的客户端使用）
# ==========================================
@app.get("/api/search_food")
async def api_search_food(keyword: str = Query(..., description="要查询的食物名称")):
    """支持外部客户端通过标准 HTTP GET 请求直接检索香港外食数据（支持简繁体与拆词匹配）"""
    try:
        # 1. 常见简繁体自动转换映射
        char_map = {'冻': '凍', '柠': '檸', '车': '車', '面': '麵', '饭': '飯', '鸡': '雞', '鸭': '鴨', '猪': '豬', '汤': '湯', '奶': '奶'}
        
        # 生成简体与繁体两个版本的关键词
        keyword_cn = keyword
        keyword_hk = "".join([char_map.get(c, c) for c in keyword])
        
        # 2. 构造 Supabase 的模糊查询条件
        # 如果搜 "冻柠茶" -> 同时模糊匹配 "%冻%柠%茶%" 和 "%凍%檸%茶%"
        pattern_cn = "%" + "%".join(list(keyword_cn)) + "%"
        pattern_hk = "%" + "%".join(list(keyword_hk)) + "%"
        
        # 使用 or_ 组合查询
        or_filter = f"name.ilike.{pattern_cn},name.ilike.{pattern_hk}"
        
        res = (
            supabase.schema("public")
            .table("foods")
            .select("*")
            .or_(or_filter)
            .limit(10)
            .execute()
        )
        
        if not res.data:
            return {"status": "empty", "message": f"未找到与 '{keyword}' 相关的食物。", "data": []}
            
        return {"status": "success", "count": len(res.data), "data": res.data}
    except Exception as e:
        return {"status": "error", "message": str(e), "data": []}

# ==========================================
# 📍 2. MCP Tools 逻辑 (保留不变)
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


# ==========================================
# 📍 3. 将 FastMCP 的 SSE 路径挂载到 FastAPI app
# ==========================================
app.mount("/", mcp.sse_app())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
