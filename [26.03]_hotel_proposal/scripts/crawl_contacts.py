import csv
import time
import re
import os
import requests
from pathlib import Path

BASE = Path(__file__).parent
TARGETS_CSV = BASE / "targets.csv"
OUTPUT_CSV = BASE / "targets_with_contacts.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def search_phone(hotel_name: str) -> str:
    """구글 검색으로 전화번호 추출"""
    query = f"{hotel_name} 전화번호 서울"
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}&hl=ko&gl=kr"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        text = r.text
        patterns = [
            r'02[-\s)]\d{3,4}[-\s]\d{4}',
            r'0\d{1,2}[-\s)]\d{3,4}[-\s]\d{4}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
    except Exception as e:
        print(f"    오류: {e}")
    return ""


def hotel_to_slug(name: str) -> str:
    """호텔명 → UTM 슬러그"""
    replacements = {
        "호텔": "hotel", "밀리오레": "milliore", "사보이": "savoy",
        "라인": "line", "메트로": "metro", "로얄": "royal",
        "퍼시픽": "pacific", "그랜드": "grand", "마요네": "mayonne",
        "칼리스타": "callista", "스테이": "stay", "미조": "mizo",
        "온유": "onyu", "명동": "myeongdong", "뉴스테이": "newstay",
        "서울": "seoul", "솔라리아": "solaria", "소테츠": "sotetsu",
        "헨나": "henna", "게스트하우스": "gh", "호스텔": "hostel",
        "레지던스": "residence", "캡슐": "capsule", "슬립박스": "sleepbox",
    }
    slug = name.lower()
    for k, v in replacements.items():
        slug = slug.replace(k, v)
    slug = re.sub(r'[^a-z0-9]', '_', slug).strip('_')
    slug = re.sub(r'_+', '_', slug)
    return slug[:30]


# ── 실행 ─────────────────────────────────────────
if not TARGETS_CSV.exists():
    raise FileNotFoundError(f"먼저 filter_targets.py를 실행하세요: {TARGETS_CSV}")

with open(TARGETS_CSV, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"총 {len(rows)}개 시설 처리 시작\n")
found = 0

for row in rows:
    name = row.get("시설명", "").strip()
    existing_phone = row.get("연락처(전화)", "").strip()

    if existing_phone:
        phone = existing_phone
        print(f"  (기존) {name}: {phone}")
    else:
        print(f"  검색: {name}")
        phone = search_phone(name)
        if phone:
            found += 1
            print(f"    → {phone}")
        else:
            print(f"    → 미발견")
        time.sleep(1.5)

    row["연락처(전화)"] = phone
    row["slug"] = hotel_to_slug(name)

with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
    new_fieldnames = list(fieldnames) + (["slug"] if "slug" not in fieldnames else [])
    writer = csv.DictWriter(f, fieldnames=new_fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n완료. 신규 수집={found}개")
print(f"결과: {OUTPUT_CSV}")
