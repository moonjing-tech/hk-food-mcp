import json
from pathlib import Path

from resolver.normalize import normalize_query

ALIASES_FILE = Path(__file__).resolve().parent.parent / "config" / "aliases.json"

with ALIASES_FILE.open("r", encoding="utf-8") as f:
    RAW_ALIASES = json.load(f)


def resolve_alias(query: str) -> str:
    value = normalize_query(query)

    if not value:
        return ""

    if value in RAW_ALIASES:
        return value

    for canonical, aliases in RAW_ALIASES.items():
        if value in aliases:
            return canonical

    return value
