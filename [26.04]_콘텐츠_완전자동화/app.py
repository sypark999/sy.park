#!/usr/bin/env python3
"""
콘텐츠 완전 자동화 웹 서버

실행:
    GEMINI_API_KEY=xxx python3 app.py
    → http://localhost:5050
"""

import csv
import datetime
import io
import json
import os
import queue
import shutil
import sys
import threading
import time
import zipfile
from pathlib import Path
from typing import List, Dict

from flask import Flask, Response, jsonify, request, send_from_directory

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "pipeline"))

from shop_search import search_shops
from image_fetcher import fetch_shops
from image_scorer import score_shops
from content_generator import generate_cards, _load_history

CSV_PATH       = ROOT.parent / "total_shop.csv"
DOWNLOADS_PATH = ROOT / "downloads.json"

app = Flask(__name__, static_folder=str(ROOT / "web"))

# 생성 완료 후 다운로드 전까지 slug 정보 임시 보관
_pending_downloads: Dict[str, Dict] = {}


def get_shops_by_slugs(slugs: List[str]) -> List[Dict]:
    """slug 순서대로 total_shop.csv에서 매장 정보 조회"""
    slug_set = set(slugs)
    slug_order = {s: i for i, s in enumerate(slugs)}
    result = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            slug = row.get("catchtable_url_path", "").strip()
            if slug in slug_set:
                result.append({
                    "shop_seq": row.get("shop_seq", "").strip(),
                    "slug": slug,
                    "name": row.get("shop_name", "").strip(),
                    "name_en": (row.get("shop_name_en") or row.get("shop_name", "")).strip(),
                    "food_kind": row.get("food_kind", "") or "",
                    "food_kind_en": row.get("food_kind_en", "") or "",
                    "land_name": row.get("land_name", "") or "",
                    "land_name_en": row.get("land_name_en", "") or "",
                    "address_en": row.get("shop_address_en") or row.get("shop_address", ""),
                    "reservation_cnt": 0,
                })
    result.sort(key=lambda s: slug_order.get(s["slug"], 999))
    return result


# ─── 선택지 캐시 ─────────────────────────────────────────────

_options_cache = None

# 음식 종류 고정 카테고리 (substring 검색 커버용 — 짧을수록 더 많은 매장 매칭)
_FOOD_CATEGORIES = [
    # 한국어 (자주 검색되는 핵심만)
    "한식", "일식", "중식",
    "오마카세", "한우", "이자카야", "카페",
    # 세계 요리
    "Korean", "Japanese", "Chinese",
    "Italian", "French", "Spanish", "American",
    "Thai", "Vietnamese", "Indian", "Mexican",
    # 파인다이닝 / 형식
    "Omakase", "Fine Dining", "Kaiseki", "Buffet", "Course",
    # 구이 / 육류
    "Korean BBQ", "Grilled Beef", "Grilled Pork", "Hanwoo", "Steak",
    # 일식 세부
    "Sushi", "Sashimi", "Ramen", "Izakaya", "Yakitori",
    # 카페 / 디저트
    "Cafe", "Bakery", "Dessert", "Brunch",
    # 주류
    "Wine", "Beer", "Cocktail", "Bar",
    # 기타 요리
    "Seafood", "Pasta", "Pizza", "Burger", "Noodles",
    "Shabu-Shabu", "Chicken", "BBQ", "Fusion", "Vegan",
]


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


@app.route("/cache/<path:filepath>")
def serve_cache(filepath):
    parts = filepath.split("/", 1)
    if len(parts) != 2:
        return "not found", 404
    slug, fname = parts
    return send_from_directory(str(ROOT / "cache" / slug), fname)


@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    from PIL import Image as PILImage
    data = request.json

    def url_to_path(url):
        return ROOT / url.lstrip("/")

    main_img   = url_to_path(data["main"])
    sub1_img   = url_to_path(data["sub1"])
    sub2_img   = url_to_path(data["sub2"])
    card_path  = ROOT / "output" / data["card"]

    from generate_image import ImageGenerator
    gen = ImageGenerator(str(ROOT / "config.json"))
    gen.generate(
        template_path=str(ROOT / "templates" / "restaurant_card.json"),
        texts={"restaurant_name": data["name"], "address": data["address"]},
        images={
            "main_image":  str(main_img),
            "sub_image_1": str(sub1_img),
            "sub_image_2": str(sub2_img),
        },
        output_path=str(card_path),
    )

    return jsonify({"ok": True, "ts": int(time.time())})


@app.route("/api/search")
def api_search():
    region = request.args.get("region", "").strip()
    food   = request.args.get("food", "").strip()
    limit  = int(request.args.get("limit", 10))
    if not region or not food:
        return jsonify({"error": "region, food 필수"}), 400

    try:
        all_shops = search_shops(region, food, limit=min(limit * 5, 100))
        history = _load_history()

        result = []
        for shop in all_shops:
            hist = history.get(shop["slug"], {})
            result.append({
                **shop,
                "used_count": hist.get("count", 0),
                "sessions":   hist.get("sessions", []),
            })
        result.sort(key=lambda s: s["used_count"])  # 미사용 우선

        return jsonify({"shops": result, "total": len(result), "limit": limit})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/options")
def api_options():
    return jsonify(load_options())


def _record_session(region: str, food: str, folder: str, count: int, date: str):
    """downloads.json에 다운로드 이력 추가"""
    records = []
    if DOWNLOADS_PATH.exists():
        try:
            records = json.loads(DOWNLOADS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    records.append({"date": date, "region": region, "food": food,
                    "folder": folder, "count": count})
    DOWNLOADS_PATH.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _safe_name(text: str) -> str:
    return "".join(c if c.isalnum() or c in "-_ " else "_" for c in text).strip().replace(" ", "_")


@app.route("/api/download", methods=["POST"])
def api_download():
    data   = request.json or {}
    folder = data.get("folder", "").strip()
    if not folder:
        return jsonify({"error": "folder 필요"}), 400

    out_dir = ROOT / "output" / folder
    if not out_dir.exists():
        return jsonify({"error": "not found"}), 404

    pending = _pending_downloads.get(folder, {})
    region  = pending.get("region", folder)
    food    = pending.get("food", "")
    slugs   = pending.get("slugs", [])
    date    = pending.get("date", datetime.date.today().strftime("%Y%m%d"))

    # 로컬 날짜_지역_음식 폴더에 복사
    dest_name = f"{date}_{_safe_name(region)}_{_safe_name(food)}"
    dest_dir  = ROOT / dest_name
    dest_dir.mkdir(exist_ok=True)
    copied = 0
    for f in sorted(out_dir.glob("*.jpg")):
        shutil.copy2(f, dest_dir / f.name)
        copied += 1

    # history.json 카운트 저장 (다운로드 시점)
    from content_generator import _load_history, _save_history
    if slugs:
        session_label = f"{_safe_name(region)}_{_safe_name(food)}_{date}"
        history = _load_history()
        _save_history(history, slugs, session_label)
        _pending_downloads.pop(folder, None)

    # downloads.json 이력 기록
    _record_session(region, food, dest_name, len(slugs) or copied, date)

    return jsonify({"ok": True, "saved_to": dest_name, "count": len(slugs) or copied})


@app.route("/api/sessions")
def api_sessions():
    if not DOWNLOADS_PATH.exists():
        return jsonify([])
    try:
        records = json.loads(DOWNLOADS_PATH.read_text(encoding="utf-8"))
        return jsonify(list(reversed(records)))
    except Exception:
        return jsonify([])


@app.route("/api/generate")
def api_generate():
    """SSE 스트림으로 진행상황 전달 + 완료시 이미지 경로 반환"""
    region      = request.args.get("region", "").strip()
    food        = request.args.get("food",   "").strip()
    limit       = int(request.args.get("limit", 10))
    slugs_param = request.args.get("slugs", "").strip()

    if not region or not food:
        return jsonify({"error": "region, food 필수"}), 400

    q = queue.Queue()

    def run_pipeline():
        def emit(msg, type_="log"):
            q.put({"type": type_, "message": msg})

        try:
            if slugs_param:
                slug_list = [s.strip() for s in slugs_param.split(",") if s.strip()]
                shops = get_shops_by_slugs(slug_list)
                if not shops:
                    emit("선택된 매장을 찾을 수 없습니다.", "error")
                    q.put(None)
                    return
                emit(f"{len(shops)}개 매장 로드", "success")
            else:
                emit(f"매장 검색 중: {region} + {food}...")
                shops = search_shops(region, food, limit=limit * 3)
                if not shops:
                    emit(f"매장 없음: '{region}' + '{food}' 조건에 해당하는 글로벌 매장이 없습니다.", "error")
                    q.put(None)
                    return
                history = _load_history()
                shops.sort(key=lambda s: history.get(s["slug"], {}).get("count", 0))
                shops = shops[:limit]
                emit(f"{len(shops)}개 매장 발견 (미사용 우선 정렬)", "success")

            emit("리뷰 이미지 다운로드 중...")
            shops = fetch_shops(shops)
            no_img = [s.get("name_en") or s["slug"] for s in shops if not s.get("local_images")]
            shops = [s for s in shops if s.get("local_images")]
            if no_img:
                emit(f"이미지 없음 자동 제외: {', '.join(no_img)}", "warn")
            if not shops:
                emit("이미지가 있는 매장이 없습니다.", "error")
                q.put(None)
                return
            total_imgs = sum(len(s.get("local_images", [])) for s in shops)
            emit(f"이미지 {total_imgs}장 다운로드 완료 ({len(shops)}개 매장)", "success")

            emit("Gemini로 이미지 스코어링 중...")
            try:
                shops = score_shops(shops)
                emit("스코어링 완료", "success")
            except ValueError as e:
                emit("GEMINI_API_KEY 없음 — 순서대로 이미지 사용", "warn")
                for s in shops:
                    s["top_images"] = s.get("local_images", [])[:3]

            emit("콘텐츠 카드 생성 중...")
            out_dir, cards_data, cover_path, thumbnail_path, slugs_used = generate_cards(shops, region, food)
            emit("생성 완료!", "success")

            # 다운로드 시점에 history 저장하기 위해 pending에 보관
            folder_name_tmp = Path(out_dir).name
            _pending_downloads[folder_name_tmp] = {
                "region": region,
                "food":   food,
                "slugs":  slugs_used,
                "date":   datetime.date.today().strftime("%Y%m%d"),
            }

            # 절대경로 → 웹 URL 변환
            cache_root = ROOT / "cache"
            def to_web(abs_path):
                try:
                    rel = Path(abs_path).relative_to(cache_root)
                    return f"/cache/{rel.as_posix()}"
                except ValueError:
                    return None

            images = []
            for d in cards_data:
                rel_card  = Path(d["card"]).relative_to(ROOT / "output")
                current_imgs = [to_web(p) or p for p in d["current_images"]]
                local_imgs   = [u for u in (to_web(p) for p in d["local_images"]) if u]
                images.append({
                    "card":           str(rel_card),
                    "name":           d["name_en"],
                    "name_zh":        d.get("name_zh", ""),
                    "food_kind_zh":   d.get("food_kind_zh", ""),
                    "slug":           d["slug"],
                    "address":        d["address"],
                    "used_count":     d.get("used_count", 0),
                    "current_images": current_imgs,
                    "local_images":   local_imgs,
                })

            # 커버 경로 변환
            cover_url = None
            if cover_path:
                try:
                    rel_cover = Path(cover_path).relative_to(ROOT / "output")
                    cover_url = str(rel_cover)
                except ValueError:
                    pass

            # 컬렉션 썸네일 경로 변환
            thumbnail_url = None
            if thumbnail_path:
                try:
                    rel_thumb = Path(thumbnail_path).relative_to(ROOT / "output")
                    thumbnail_url = str(rel_thumb)
                except ValueError:
                    pass

            # 폴더명 (다운로드용)
            folder_name = Path(out_dir).name

            q.put({
                "type":      "done",
                "images":    images,
                "cover":     cover_url,
                "thumbnail": thumbnail_url,
                "folder":    folder_name,
            })

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
