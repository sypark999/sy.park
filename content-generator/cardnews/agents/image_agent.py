#!/usr/bin/env python3
"""
에이전트 2: 이미지 생성
topic.json의 각 카드별 프롬프트로 GPT Image를 생성합니다.
"""

import json
import base64
import time
from pathlib import Path
from openai import OpenAI


def generate_image(client: OpenAI, prompt: str, model: str, output_path: Path,
                   retries: int = 3) -> bool:
    """단일 이미지 생성 (재시도 포함)"""
    for attempt in range(retries):
        try:
            response = client.images.generate(
                model=model,
                prompt=prompt,
                n=1,
                size="1024x1024",
            )

            if hasattr(response.data[0], "b64_json") and response.data[0].b64_json:
                image_data = base64.b64decode(response.data[0].b64_json)
                with open(output_path, "wb") as f:
                    f.write(image_data)
            elif hasattr(response.data[0], "url") and response.data[0].url:
                import urllib.request
                urllib.request.urlretrieve(response.data[0].url, str(output_path))
            else:
                raise Exception("이미지 데이터 없음")

            return True

        except Exception as e:
            print(f"    ⚠️  시도 {attempt + 1}/{retries} 실패: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    return False


def create_placeholder(output_path: Path, color: str = "#333333"):
    """실패 시 플레이스홀더 이미지 생성"""
    from PIL import Image
    img = Image.new("RGB", (1024, 1024), color)
    img.save(str(output_path), "JPEG", quality=95)


def run(config: dict, output_dir: Path) -> Path:
    """이미지 생성 에이전트 실행"""
    print("\n🎨 에이전트 2: 이미지 생성")
    print("=" * 50)

    topic_path = output_dir / "topic.json"
    with open(topic_path, "r", encoding="utf-8") as f:
        topic = json.load(f)

    client = OpenAI(api_key=config["api"]["openai_api_key"])
    model = config["api"]["image_model"]
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    style_suffix = ", food photography, appetizing, vibrant colors, professional studio lighting, high resolution"

    print(f"\n  [표지] 생성 중...")
    cover_prompt = f"A stunning hero image representing {topic['topic']}. Korean food spread, top-down view{style_suffix}"
    cover_path = images_dir / "cover.jpg"
    if generate_image(client, cover_prompt, model, cover_path):
        print(f"  ✅ 표지 완료")
    else:
        print(f"  ❌ 표지 실패 — 플레이스홀더 사용")
        create_placeholder(cover_path)

    for i, card in enumerate(topic["cards"]):
        print(f"\n  [카드 {i + 1}] {card['title']} 생성 중...")
        prompt = card["image_prompt"] + style_suffix
        card_path = images_dir / f"card_{i + 1:02d}.jpg"
        if generate_image(client, prompt, model, card_path):
            print(f"  ✅ 카드 {i + 1} 완료")
        else:
            print(f"  ❌ 카드 {i + 1} 실패 — 플레이스홀더 사용")
            create_placeholder(card_path, "#444444")

    print(f"\n  💾 이미지 저장: {images_dir}")
    return images_dir
