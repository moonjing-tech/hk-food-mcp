import re
import opencc

converter = opencc.OpenCC("s2hk")

QUERY_NOISE = [
    "幾多卡路里", "多少卡路里", "幾多熱量", "多少熱量",
    "幾多卡", "多少卡", "有幾多卡", "有多少卡",
    "有幾多熱量", "有多少熱量", "熱量是多少", "热量是多少",
    "營養成分", "营养成分", "營養", "营养", "卡路里",
]


def normalize_query(query: str) -> str:
    if not query:
        return ""

    value = converter.convert(query.strip())
    value = re.sub(r"[？?！!，,。．.：:；;]", "", value)
    value = re.sub(r"\s+", "", value)

    for noise in sorted(QUERY_NOISE, key=len, reverse=True):
        value = value.replace(noise, "")

    return value.strip()
