"""
Catchtable API에서 리뷰 이미지 다운로드
- recommendReviewListGlobal 기반 (영어 리뷰 이미지)
- 없으면 shop images 폴백
"""

import asyncio
import aiohttp
import json
from pathlib import Path
from typing import List, Dict, Optional

API_BASE = "https://api.catchtable.net/api/v3/shop/detail"
HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15",
    "accept-language": "en-US,en;q=0.9",
}
CONCURRENCY = 4
TIMEOUT_SEC = 15

CACHE_DIR = Path(__file__).parent.parent / "cache"


async def fetch_shop_detail(session: aiohttp.ClientSession, sem: asyncio.Semaphore,
                             shop: Dict) -> Dict:
    """매장 상세 API 호출 → 이미지 URL 목록 + 메타데이터 반환"""
    slug = shop["slug"]
    async with sem:
        try:
            async with session.get(
                f"{API_BASE}/{slug}",
                params={"localeCode": "en-US"},
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SEC),
            ) as resp:
                if resp.status != 200:
                    print(f"  [API] {slug}: HTTP {resp.status}")
                    return {**shop, "review_image_urls": [], "shop_image_urls": []}
                data = await resp.json(content_type=None)

            details = data.get("data", {}).get("shopDetails", [])
            if not details:
                return {**shop, "review_image_urls": [], "shop_image_urls": []}

            d = details[0]

            # 영문 메타데이터 보완
            enriched = {
                **shop,
                "name_en": d.get("shopNameEn") or shop.get("name_en", ""),
                "address_en": d.get("shopAddressEn") or shop.get("address_en", ""),
                "land_name_en": d.get("landNameEn") or shop.get("land_name_en", ""),
            }

            # 리뷰 이미지 (글로벌)
            review_urls = []
            for review in d.get("recommendReviewListGlobal", []):
                for photo in (review.get("photoList") or []):
                    url = photo.get("review_img_url") or photo.get("review_thumb_url")
                    if url:
                        review_urls.append(url)

            # 리뷰 이미지 (한국어) - 글로벌 없을 때 폴백
            if not review_urls:
                for review in (d.get("review", {}) or {}).get("recommendReviewList", []):
                    url = review.get("recomm_review_img_url")
                    if url:
                        review_urls.append(url)

            # 샵 공식 이미지 + 메뉴 이미지 (최종 폴백)
            shop_image_urls = []
            for img in (d.get("images") or []):
                url = img.get("imgUrl") or img.get("thumbUrl")
                if url:
                    shop_image_urls.append(url)
            for img in (d.get("shopMenuImgList") or []):
                url = img.get("img_url") or img.get("thumb_url")
                if url:
                    shop_image_urls.append(url)

            enriched["review_image_urls"] = review_urls
            enriched["shop_image_urls"] = shop_image_urls
            return enriched

        except asyncio.TimeoutError:
            print(f"  [API] {slug}: timeout")
            return {**shop, "review_image_urls": [], "shop_image_urls": []}
        except Exception as e:
            print(f"  [API] {slug}: {e}")
            return {**shop, "review_image_urls": [], "shop_image_urls": []}


async def download_image(session: aiohttp.ClientSession, sem: asyncio.Semaphore,
                          url: str, out_path: Path) -> bool:
    if out_path.exists():
        return True
    async with sem:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT_SEC)) as r:
                if r.status != 200:
                    return False
                out_path.write_bytes(await r.read())
                return True
        except Exception:
            return False


async def fetch_all(shops: List[Dict]) -> List[Dict]:
    """
    매장 목록에 대해:
    1. API로 이미지 URL 수집
    2. 이미지 로컬 다운로드
    3. 다운로드된 파일 경로를 shop dict에 추가하여 반환
    """
    CACHE_DIR.mkdir(exist_ok=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)

    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        # Step 1: API 호출 병렬
        detail_tasks = [fetch_shop_detail(session, sem, shop) for shop in shops]
        enriched_shops = await asyncio.gather(*detail_tasks)

        # Step 2: 이미지 다운로드 (리뷰 + 샵 이미지 모두)
        all_results = []
        for shop in enriched_shops:
            slug = shop["slug"]
            shop_cache = CACHE_DIR / slug
            shop_cache.mkdir(exist_ok=True)

            review_urls = shop["review_image_urls"][:10]
            shop_urls = shop["shop_image_urls"][:5]

            download_tasks = []
            out_paths = []

            for i, url in enumerate(review_urls):
                ext = url.split("?")[0].rsplit(".", 1)[-1]
                if ext not in ("jpg", "jpeg", "png", "webp"):
                    ext = "jpg"
                out_path = shop_cache / f"r_{i:02d}.{ext}"
                out_paths.append(out_path)
                download_tasks.append(download_image(session, sem, url, out_path))

            for i, url in enumerate(shop_urls):
                ext = url.split("?")[0].rsplit(".", 1)[-1]
                if ext not in ("jpg", "jpeg", "png", "webp"):
                    ext = "jpg"
                out_path = shop_cache / f"s_{i:02d}.{ext}"
                out_paths.append(out_path)
                download_tasks.append(download_image(session, sem, url, out_path))

            results = await asyncio.gather(*download_tasks)

            downloaded = [p for p, ok in zip(out_paths, results) if ok and p.exists()]
            shop["local_images"] = [str(p) for p in downloaded]

            r_cnt = sum(1 for p in downloaded if p.name.startswith("r_"))
            s_cnt = sum(1 for p in downloaded if p.name.startswith("s_"))
            print(f"  [fetch] {slug}: 리뷰 {r_cnt}장 + 샵 {s_cnt}장 = 총 {len(downloaded)}장")
            all_results.append(shop)

    return all_results


def fetch_shops(shops: List[Dict]) -> List[Dict]:
    return asyncio.run(fetch_all(shops))


if __name__ == "__main__":
    from shop_search import search_shops
    shops = search_shops("강남", "한우오마카세", limit=3)
    result = fetch_shops(shops)
    for s in result:
        print(f"{s['name_en']}: {len(s['local_images'])}장")
        for p in s["local_images"]:
            print(f"  {p}")
