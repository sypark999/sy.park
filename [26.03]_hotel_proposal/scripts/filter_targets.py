import csv
import os

INPUT = os.path.join(os.path.dirname(__file__), "../명동_숙박시설_컨택시트.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "targets.csv")

targets = []
with open(INPUT, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("시설명", "").strip()
        zone = row.get("구역", "").strip()
        priority = row.get("방문우선순위", "").strip()
        if not name or name.startswith("=="):
            continue
        if zone == "A" and priority == "1":
            targets.append(row)

with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=targets[0].keys())
    writer.writeheader()
    writer.writerows(targets)

print(f"총 {len(targets)}개 시설 추출")
for t in targets:
    print(f"  - {t['시설명']} ({t['유형']})")
