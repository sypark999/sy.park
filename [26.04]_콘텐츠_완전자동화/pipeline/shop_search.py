"""
total_shop.csv에서 지역 + 음식종류로 매장 필터링
"""

import csv
from pathlib import Path
from typing import List, Dict

CSV_PATH = Path(__file__).parent.parent.parent / "total_shop.csv"

# 음식 종류 별칭 — 선택한 키워드로 검색 시 함께 포함할 키워드
FOOD_ALIASES: dict = {
    "korean bbq": ["korean bbq", "grilled beef", "grilled pork", "구이", "삼겹살", "갈비"],
}

NEEDED_COLS = [
    "shop_seq", "shop_name", "shop_name_en",
    "food_kind", "food_kind_en",
    "land_name", "land_name_en",
    "shop_address", "shop_address_en",
    "catchtable_url_path",
    "expose_catchtable_global_yn",
    "reservation_cnt_of_month",
]


def search_shops(region: str, food: str, limit: int = 10) -> List[Dict]:
    """
    region, food 키워드로 total_shop.csv 필터링.
    글로벌 노출 매장 중 예약수 높은 순으로 최대 limit개 반환.
    """
    results = []

    region_kw = region.strip()
    food_kw = food.strip()

    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 글로벌 노출 필터
            if row.get("expose_catchtable_global_yn", "N") != "Y":
                continue

            slug = row.get("catchtable_url_path", "").strip()
            if not slug:
                continue

            # 음식 종류 매칭 (대소문자 무시, 별칭 포함)
            fk = row.get("food_kind", "") or ""
            fk_en = row.get("food_kind_en", "") or ""
            food_kw_lower = food_kw.lower()
            food_keywords = FOOD_ALIASES.get(food_kw_lower, [food_kw_lower])
            if not any(kw in fk.lower() or kw in fk_en.lower() for kw in food_keywords):
                continue

            # 지역 매칭 (land_name, shop_address 중 하나, 대소문자 무시)
            ln = row.get("land_name", "") or ""
            ln_en = row.get("land_name_en", "") or ""
            addr = row.get("shop_address", "") or ""
            addr_en = row.get("shop_address_en", "") or ""
            region_kw_lower = region_kw.lower()
            region_match = any(
                region_kw_lower in field.lower()
                for field in [ln, ln_en, addr, addr_en]
            )
            if not region_match:
                continue

            try:
                resv_cnt = int(row.get("reservation_cnt_of_month", 0) or 0)
            except ValueError:
                resv_cnt = 0

            results.append({
                "shop_seq": row.get("shop_seq", "").strip(),
                "slug": slug,
                "name": row.get("shop_name", "").strip(),
                "name_en": row.get("shop_name_en", "").strip() or row.get("shop_name", "").strip(),
                "food_kind": fk,
                "food_kind_en": fk_en,
                "land_name": ln,
                "land_name_en": ln_en,
                "address_en": addr_en or addr,
                "reservation_cnt": resv_cnt,
            })

    # 예약수 높은 순 정렬
    results.sort(key=lambda x: x["reservation_cnt"], reverse=True)

    print(f"[검색] '{region}' + '{food}' → {len(results)}개 매장 발견, 상위 {min(limit, len(results))}개 선택")
    return results[:limit]


if __name__ == "__main__":
    shops = search_shops("강남", "한우오마카세")
    for i, s in enumerate(shops, 1):
        print(f"  {i:2d}. {s['name_en']} ({s['slug']}) 예약:{s['reservation_cnt']}")
