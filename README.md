# HK Food MCP v2.1

香港外食营养数据库 MCP + REST API。

## 主要改动

- REST 与 MCP 共用同一套查询逻辑
- 简体 → 香港繁体标准化
- 常见食品别名
- 香港常见口语/简称
- 字符顺序模糊匹配
- 营养指标筛选
- `/api/health`
- 将查询解析和数据库服务从 `server.py` 中拆出
- 保留原有 MCP 工具名称

## 环境变量

```env
SUPABASE_URL=...
SUPABASE_KEY=...
PORT=8000
```

## 启动

```bash
pip install -r requirements.txt
python server.py
```

## REST

```text
GET /api/search_food?keyword=凍檸茶
GET /api/health
```

## MCP

- `search_foods`
- `get_food_by_id`
- `filter_foods_by_nutrition`

## 同义词

编辑 `config/aliases.json`。

只添加确定属于同一食品的别名。
不要把有歧义的词强制映射，例如不要把“牛河”直接映射成“乾炒牛河”。
