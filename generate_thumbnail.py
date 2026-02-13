#!/usr/bin/env python3
"""
캐치테이블 썸네일 생성
4개 레스토랑의 이미지를 그리드로 배치
"""

import json
from pathlib import Path
from generate_image import ImageGenerator
import random


def generate_thumbnail():
    """캐치테이블 썸네일 생성"""
    print("="*60)
    print("캐치테이블 썸네일 생성")
    print("="*60)

    base_path = Path('/Users/songyeon/Desktop/sy.park')
    shop_path = base_path / 'shop_image' / 'Korea_10_Famous_Korean_Restaurants_in_Hongdae'
    output_dir = base_path / 'output' / 'examples'
    output_dir.mkdir(exist_ok=True)

    # 레스토랑 정보 로드
    with open(base_path / 'restaurant_info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        restaurants = data.get('restaurants', {})

    # 이미지 생성기 초기화
    generator = ImageGenerator(str(base_path / 'config.json'))

    # 각 레스토랑에서 대표 이미지 1개씩 수집
    selected_images = []

    for restaurant_id in restaurants.keys():
        restaurant_dir = shop_path / restaurant_id
        if not restaurant_dir.exists():
            continue

        # 이미지 찾기
        images = sorted([
            f for f in restaurant_dir.iterdir()
            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}
        ])

        if images:
            # 첫 번째 이미지 선택 (또는 랜덤)
            selected_images.append(images[0])
            print(f"✓ {restaurant_id}: {images[0].name}")

    if len(selected_images) < 4:
        print(f"\n⚠️  이미지가 부족합니다 (필요: 4개, 현재: {len(selected_images)}개)")
        # 부족하면 반복
        while len(selected_images) < 4:
            selected_images.append(selected_images[0])

    # 4개만 사용
    grid_images = selected_images[:4]

    print(f"\n총 {len(grid_images)}개 이미지 사용")

    # 썸네일 생성
    output_path = output_dir / 'catchtable_thumbnail.jpg'

    try:
        generator.generate(
            template_path=str(base_path / 'templates' / 'catchtable_thumbnail.json'),
            images={
                'grid_image_1': str(grid_images[0]),
                'grid_image_2': str(grid_images[1]),
                'grid_image_3': str(grid_images[2]),
                'grid_image_4': str(grid_images[3])
            },
            texts={
                'title': 'CATCHTABLE 精选',
                'subtitle': '首尔韩餐厅 TOP 10! - 弘大'
            },
            output_path=str(output_path)
        )
        print(f"\n✅ 썸네일 생성 완료!")
        print(f"📂 {output_path}")

    except Exception as e:
        print(f"\n❌ 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    generate_thumbnail()
