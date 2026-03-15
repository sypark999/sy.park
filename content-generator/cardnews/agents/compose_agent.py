#!/usr/bin/env python3
"""
에이전트 3: 텍스트 합성
이미지 위에 텍스트를 렌더링하여 최종 카드뉴스를 완성합니다.
"""

import json
from pathlib import Path
from generate_image import ImageGenerator


def run(config: dict, output_dir: Path) -> Path:
    """텍스트 합성 에이전트 실행"""
    print("\n✏️  에이전트 3: 텍스트 합성")
    print("=" * 50)

    topic_path = output_dir / "topic.json"
    with open(topic_path, "r", encoding="utf-8") as f:
        topic = json.load(f)

    images_dir = output_dir / "images"
    base_path = Path(__file__).parent.parent
    config_path = base_path / "config.json"
    generator = ImageGenerator(str(config_path))

    cover_template = base_path / "templates" / "cover.json"
    content_template = base_path / "templates" / "content_card.json"
    cta_template = base_path / "templates" / "cta.json"

    slide_num = 1
    generated = []

    # 1. 표지 생성
    print(f"\n  [슬라이드 {slide_num}] 표지 생성 중...")
    cover_output = output_dir / f"{slide_num:02d}_cover.jpg"
    try:
        generator.generate(
            template_path=str(cover_template),
            images={"main_image": str(images_dir / "cover.jpg")},
            texts={
                "title": topic["topic"],
                "subtitle": topic.get("subtitle", ""),
            },
            output_path=str(cover_output),
        )
        print(f"  ✅ 표지 완료: {cover_output.name}")
        generated.append(cover_output)
    except Exception as e:
        print(f"  ❌ 표지 실패: {e}")
    slide_num += 1

    # 2. 본문 카드 생성
    for i, card in enumerate(topic["cards"]):
        print(f"\n  [슬라이드 {slide_num}] {card['title']} 생성 중...")
        card_image = images_dir / f"card_{i + 1:02d}.jpg"
        card_output = output_dir / f"{slide_num:02d}_card_{i + 1}.jpg"

        try:
            generator.generate(
                template_path=str(content_template),
                images={"main_image": str(card_image)},
                texts={
                    "card_title": card["title"],
                    "card_description": card["description"],
                },
                output_path=str(card_output),
            )
            print(f"  ✅ 카드 {i + 1} 완료: {card_output.name}")
            generated.append(card_output)
        except Exception as e:
            print(f"  ❌ 카드 {i + 1} 실패: {e}")
        slide_num += 1

    # 3. CTA 생성
    print(f"\n  [슬라이드 {slide_num}] CTA 생성 중...")
    cta_output = output_dir / f"{slide_num:02d}_cta.jpg"
    hashtag_text = " ".join(topic.get("hashtags", []))
    try:
        generator.generate(
            template_path=str(cta_template),
            texts={
                "cta_title": "关注 CATCHTABLE\n发现更多韩国美食",
                "cta_handle": "@catchtable.global",
                "cta_hashtags": hashtag_text,
            },
            output_path=str(cta_output),
        )
        print(f"  ✅ CTA 완료: {cta_output.name}")
        generated.append(cta_output)
    except Exception as e:
        print(f"  ❌ CTA 실패: {e}")

    # 4. SNS 캡션 저장
    caption_path = output_dir / "sns_caption.txt"
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(topic.get("sns_caption", ""))
        f.write("\n\n")
        f.write(hashtag_text)
    print(f"\n  📝 SNS 캡션 저장: {caption_path.name}")

    # 결과 요약
    print(f"\n{'=' * 50}")
    print(f"✅ 카드뉴스 생성 완료: {len(generated)}장")
    print(f"📂 출력 경로: {output_dir}")
    print(f"{'=' * 50}")

    return output_dir
