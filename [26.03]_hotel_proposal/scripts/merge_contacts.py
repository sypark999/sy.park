import csv
from pathlib import Path

BASE = Path(__file__).parent.parent
SOURCE = Path(__file__).parent / "targets_with_contacts.csv"
MASTER = BASE / "명동_숙박시설_컨택시트.csv"
OUTPUT = BASE / "명동_숙박시설_컨택시트_updated.csv"


def load_contacts(path: Path) -> dict:
    contacts = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("시설명", "").strip()
            if name:
                contacts[name] = {
                    "연락처(전화)": row.get("연락처(전화)", "").strip(),
                    "slug": row.get("slug", "").strip(),
                }
    return contacts


contacts = load_contacts(SOURCE)
rows = []

with open(MASTER, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = [fn for fn in reader.fieldnames if fn is not None]
    if "slug" not in fieldnames:
        fieldnames = fieldnames + ["slug"]
    for row in reader:
        # strip None keys caused by trailing commas in CSV
        row = {k: v for k, v in row.items() if k is not None}
        name = row.get("시설명", "").strip()
        if name in contacts:
            if not row.get("연락처(전화)", "").strip():
                row["연락처(전화)"] = contacts[name]["연락처(전화)"]
            row["slug"] = contacts[name]["slug"]
        else:
            if "slug" not in row:
                row["slug"] = ""
        rows.append(row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# 결과 확인
filled = sum(1 for r in rows if r.get("slug") and r.get("구역") == "A" and r.get("방문우선순위") == "1")
print(f"완료. {OUTPUT.name} 저장")
print(f"구역A + 우선순위1 slug 채워진 시설: {filled}개")
