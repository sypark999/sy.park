#!/usr/bin/env python3
"""
모든 레스토랑의 중국어 콘텐츠 예시 생성
"""

import json
from pathlib import Path
from generate_image import ImageGenerator


def generate_all_examples():
    """모든 레스토랑의 예시 이미지 생성"""
    print("="*60)
    print("중국어 콘텐츠 예시 이미지 생성")
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

    results = []

    # 각 레스토랑별로 이미지 생성
    for restaurant_id, info in restaurants.items():
        print(f"\n{'='*60}")
        print(f"📍 {restaurant_id}")
        print(f"{'='*60}")

        restaurant_dir = shop_path / restaurant_id
        if not restaurant_dir.exists():
            print(f"⚠️  폴더 없음: {restaurant_dir}")
            continue

        # 이미지 찾기
        images = sorted([
            f for f in restaurant_dir.iterdir()
            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}
        ])

        if len(images) < 3:
            print(f"⚠️  이미지 부족 (필요: 3개, 현재: {len(images)}개)")
            # 이미지가 부족하면 반복 사용
            while len(images) < 3:
                images.append(images[0])

        # 중국어 정보 가져오기
        name_cn = info.get('name_cn_s', info.get('name', ''))
        address = info.get('address', '')

        print(f"식당명: {name_cn}")
        print(f"주소: {address}")
        print(f"사용 이미지: {len(images)}개")

        # 이미지 생성
        output_path = output_dir / f"{restaurant_id}_chinese.jpg"

        try:
            generator.generate(
                template_path=str(base_path / 'templates' / 'instagram_restaurant.json'),
                images={
                    'main_image': str(images[0]),
                    'sub_image_1': str(images[1] if len(images) > 1 else images[0]),
                    'sub_image_2': str(images[2] if len(images) > 2 else images[0])
                },
                texts={
                    'restaurant_name': name_cn,
                    'address': address
                },
                output_path=str(output_path)
            )
            print(f"✅ 생성 완료: {output_path.name}")
            results.append({
                'id': restaurant_id,
                'name': name_cn,
                'path': output_path
            })

        except Exception as e:
            print(f"❌ 생성 실패: {e}")

    # 결과 요약
    print("\n" + "="*60)
    print("🎉 생성 완료!")
    print("="*60)
    print(f"\n총 {len(results)}개 이미지 생성\n")

    for result in results:
        print(f"✓ {result['name']}")
        print(f"  → {result['path']}")
        print()

    print(f"📂 모든 이미지 위치: {output_dir}")

    return results


if __name__ == '__main__':
    generate_all_examples()
