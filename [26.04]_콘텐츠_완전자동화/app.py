#!/usr/bin/env python3
"""
콘텐츠 완전 자동화 웹 서버

실행:
    GEMINI_API_KEY=xxx python3 app.py
    → http://localhost:5050
"""

import csv
import json
import os
import queue
import sys
import threading
import time
from pathlib import Path

from flask import Flask, Response, jsonify, request, send_from_directory

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "pipeline"))

from shop_search import search_shops
from image_fetcher import fetch_shops
from image_scorer import score_shops
from content_generator import generate_cards

CSV_PATH = ROOT.parent / "total_shop.csv"

app = Flask(__name__, static_folder=str(ROOT / "web"))


# ─── 선택지 캐시 ─────────────────────────────────────────────

_options_cache = None

# 음식 종류 고정 카테고리 (substring 검색 커버용 — 짧을수록 더 많은 매장 매칭)
_FOOD_CATEGORIES = sorted([
    # 한식/구이
    "한식", "한정식", "코스요리", "파인다이닝", "뷔페", "호텔뷔페",
    "한우", "소고기구이", "돼지고기구이", "곱창", "보쌈",
    # 일식
    "오마카세", "스시", "회", "이자카야", "일식",
    "라멘", "돈가스", "야키토리", "카이세키",
    # 기타 아시아
    "중식", "냉면", "국수", "분식",
    # 카페/디저트
    "카페", "베이커리", "디저트", "브런치", "케이크",
    # 주류
    "와인", "칵테일", "전통주", "맥주",
    # 해산물/기타
    "해물", "참치", "닭요리", "장어요리", "양고기",
    # 세계음식
    "이탈리아음식", "프랑스음식", "스페인음식",
    "태국음식", "베트남음식", "인도음식", "멕시코음식", "아메리칸음식",
    # 양식
    "스테이크", "파스타", "피자", "햄버거", "샤브샤브", "퓨전음식",
    # English
    "Korean", "Japanese", "Chinese",
    "Italian", "French", "Spanish", "American", "European",
    "Thai", "Vietnamese", "Indian", "Mexican",
    "Omakase", "Sushi", "Sashimi", "Kaiseki",
    "Grilled Beef", "Grilled Pork", "BBQ", "Hanwoo",
    "Fine Dining", "Buffet", "Course",
    "Cafe", "Bakery", "Dessert", "Brunch",
    "Wine", "Cocktail", "Beer", "Bar", "Izakaya", "Pub",
    "Ramen", "Noodles",
    "Steak", "Pizza", "Pasta", "Hamburger",
    "Shabu-Shabu", "Seafood", "Chicken", "Eel",
    "Vegan", "Yakitori", "Teppanyaki", "Fusion",
])


def _dedup_regions(region_counts, min_count=20):
    """짧은(넓은) 지역명 우선 — 이미 canonical에 포함되면 제거."""
    items = [r for r, c in region_counts.items() if c >= min_count]
    items.sort(key=lambda x: (len(x), x))
    canonical = []
    for region in items:
        rl = region.lower()
        if any(c.lower() in rl for c in canonical):
            continue
        canonical.append(region)
    return sorted(canonical)


def load_options():
    global _options_cache
    if _options_cache:
        return _options_cache

    SKIP = {"null", "none", "n/a", ""}
    region_counts = {}

    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row.get("expose_catchtable_global_yn") != "Y":
                continue
            ln = (row.get("land_name") or "").strip()
            if ln and ln.lower() not in SKIP:
                region_counts[ln] = region_counts.get(ln, 0) + 1

    _options_cache = {
        "regions": _dedup_regions(region_counts, min_count=20),
        "foods": _FOOD_CATEGORIES,
    }
    return _options_cache


# ─── API 엔드포인트 ──────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(str(ROOT / "web"), "index.html")


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(str(ROOT / "output"), filename)


@app.route("/api/options")
def api_options():
    return jsonify(load_options())


@app.route("/api/generate")
def api_generate():
    """SSE 스트림으로 진행상황 전달 + 완료시 이미지 경로 반환"""
    region = request.args.get("region", "").strip()
    food = request.args.get("food", "").strip()
    limit = int(request.args.get("limit", 10))

    if not region or not food:
        return jsonify({"error": "region, food 필수"}), 400

    q = queue.Queue()

    def run_pipeline():
        def emit(msg, type_="log"):
            q.put({"type": type_, "message": msg})

        try:
            emit(f"매장 검색 중: {region} + {food}...")
            shops = search_shops(region, food, limit=limit)
            if not shops:
                emit(f"매장 없음: '{region}' + '{food}' 조건에 해당하는 글로벌 매장이 없습니다.", "error")
                q.put(None)
                return
            emit(f"{len(shops)}개 매장 발견", "success")

            emit("리뷰 이미지 다운로드 중...")
            shops = fetch_shops(shops)
            total_imgs = sum(len(s.get("local_images", [])) for s in shops)
            emit(f"이미지 {total_imgs}장 다운로드 완료", "success")

            emit("Gemini로 이미지 스코어링 중...")
            try:
                shops = score_shops(shops)
                emit("스코어링 완료", "success")
            except ValueError as e:
                emit(f"GEMINI_API_KEY 없음 — 순서대로 이미지 사용", "warn")
                for s in shops:
                    s["top_images"] = s.get("local_images", [])[:3]

            emit("콘텐츠 카드 생성 중...")
            out_dir = generate_cards(shops, region, food)
            emit("생성 완료!", "success")

            # 생성된 이미지 목록
            out_path = Path(out_dir)
            cards = sorted([
                f for f in out_path.iterdir()
                if f.suffix == ".jpg" and "_thumb" not in f.name
            ])
            thumbs = sorted([
                f for f in out_path.iterdir()
                if f.suffix == ".jpg" and "_thumb" in f.name
            ])

            images = []
            for card, thumb in zip(cards, thumbs):
                rel_card = card.relative_to(ROOT / "output")
                rel_thumb = thumb.relative_to(ROOT / "output")
                images.append({
                    "card": str(rel_card),
                    "thumb": str(rel_thumb),
                    "name": card.stem.split("_", 1)[-1].replace("_", " "),
                })

            q.put({"type": "done", "images": images})

        except Exception as e:
            q.put({"type": "error", "message": str(e)})
        finally:
            q.put(None)  # sentinel

    threading.Thread(target=run_pipeline, daemon=True).start()

    def stream():
        while True:
            item = q.get()
            if item is None:
                break
            yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            if item.get("type") in ("done", "error"):
                break

    return Response(stream(), mimetype="text/event-stream",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


if __name__ == "__main__":
    print("옵션 데이터 로딩 중...")
    load_options()
    print("완료. 서버 시작: http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
