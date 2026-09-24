import json
from pathlib import Path

ALIASES_PATH = Path(__file__).resolve().parent.parent / "config" / "aliases.json"


def load_aliases():
    with ALIASES_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def expand_aliases(query: str):
    aliases = load_aliases()
    q = query.strip()
    values = [q]
    for canonical, terms in aliases.items():
        group = [canonical, *terms]
        if q in group:
            values.extend(group)
            break
    return list(dict.fromkeys(values))
