import csv
import os
import re
import qrcode
from pathlib import Path

# ── 설정 ─────────────────────────────────────────
BASE = Path(__file__).parent.parent
TARGETS_CSV = BASE / "scripts" / "targets_with_contacts.csv"
TARGETS_FALLBACK = BASE / "scripts" / "targets.csv"
LANDING_URL = "https://catchtable.com/myeongdong"  # 어드민 확정 후 교체
TEMPLATE_HTML = BASE / "b2c_leaflet_template.html"
OUTPUT_QR_DIR = BASE / "output" / "qr"
OUTPUT_LEAFLET_DIR = BASE / "output" / "leaflets"

OUTPUT_QR_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_LEAFLET_DIR.mkdir(parents=True, exist_ok=True)


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
        "스카이파크": "skypark", "이비스": "ibis", "앰배서더": "ambassador",
        "바이": "by", "필스테이": "philstay",
    }
    slug = name.lower()
    for k, v in replacements.items():
        slug = slug.replace(k, v)
    slug = re.sub(r'[^a-z0-9]', '_', slug).strip('_')
    slug = re.sub(r'_+', '_', slug)
    return slug[:30]


def make_qr(url: str, slug: str) -> Path:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#172b4d", back_color="white")
    path = OUTPUT_QR_DIR / f"{slug}.png"
    img.save(str(path))
    return path


def make_leaflet(slug: str, qr_path: Path) -> Path:
    with open(TEMPLATE_HTML, encoding="utf-8") as f:
        html = f.read()
    abs_qr = qr_path.resolve().as_uri()  # file:// URI for browser
    html = html.replace("{QR_IMAGE}", abs_qr)
    out_path = OUTPUT_LEAFLET_DIR / f"{slug}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


# ── 실행 ─────────────────────────────────────────
csv_path = TARGETS_CSV if TARGETS_CSV.exists() else TARGETS_FALLBACK

if not csv_path.exists():
    raise FileNotFoundError(f"CSV 파일 없음: {csv_path}")

with open(csv_path, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"총 {len(rows)}개 시설 처리 시작\n")
skipped = 0
slug_counter = {}

for row in rows:
    name = row.get("시설명", "").strip()
    if not name:
        continue

    # slug: CSV에 있으면 사용, 없으면 생성
    slug = row.get("slug", "").strip() or hotel_to_slug(name)
    if not slug:
        print(f"  ⚠️  슬러그 생성 실패: {name} — 건너뜀")
        skipped += 1
        continue

    if slug in slug_counter:
        slug_counter[slug] += 1
        slug = f"{slug[:27]}_{slug_counter[slug]}"
    else:
        slug_counter[slug] = 1

    utm_url = f"{LANDING_URL}?utm_source=hotel&utm_medium=qr&utm_campaign={slug}"
    qr_path = make_qr(utm_url, slug)
    leaflet_path = make_leaflet(slug, qr_path)

    print(f"  ✅ {name}")
    print(f"     slug: {slug}")
    print(f"     UTM:  {utm_url}")
    print(f"     HTML: {leaflet_path}\n")

print(f"완료. 생성={len(rows)-skipped}개, 건너뜀={skipped}개")
print(f"  QR:     {OUTPUT_QR_DIR}")
print(f"  리플릿: {OUTPUT_LEAFLET_DIR}")
