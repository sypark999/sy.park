import csv
import os

INPUT = os.path.join(os.path.dirname(__file__), "../명동_숙박시설_컨택시트.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "targets.csv")

if not os.path.exists(INPUT):
    raise FileNotFoundError(f"INPUT 파일을 찾을 수 없습니다: {INPUT}")

targets = []
fieldnames = None
with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        name = row.get("시설명", "").strip()
        zone = row.get("구역", "").strip()
        priority = row.get("방문우선순위", "").strip()
        if not name or name.startswith("=="):
            continue
        if zone == "A" and priority == "1":
            targets.append(row)

if not targets:
    print("조건에 맞는 시설이 없습니다.")
else:
    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(targets)

print(f"총 {len(targets)}개 시설 추출")
for t in targets:
    print(f"  - {t['시설명']} ({t.get('유형', '-')})")
