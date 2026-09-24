# HK Food MCP v2.1.1

针对香港外食营养数据库的搜索与 MCP 服务。

## 本版更新

- 修复 MCP `get_food_by_id` / `filter_foods_by_nutrition` 与 service 函数同名覆盖问题。
- REST 与 MCP 共用同一搜索逻辑。
- 简繁体转换与查询噪声清理。
- 增加常见食物别名映射。
- 增加搜索相关性排序：完整菜式优先于配料。
- 保留模糊搜索，不强行把“牛河”等模糊词映射成唯一菜品。
- 增加可比性判断工具，避免不同计量基准直接比较。
- NULL 营养字段原样保留，不做估算。
- OpenCC 使用 `s2hk`，兼容 `opencc-python-reimplemented`。

## 环境变量

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `PORT`（可选，默认 8000）

## 数据表

默认使用 Supabase `foods` 表。

## 本地测试

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python server.py
```

## Render

Procfile 已配置：

```text
web: python server.py
```
