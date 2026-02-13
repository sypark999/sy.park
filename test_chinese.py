#!/usr/bin/env python3
"""
중국어 레스토랑 정보 테스트
"""

import json
from pathlib import Path
from generate_image import ImageGenerator


def test_chinese_restaurant():
    """중국어 레스토랑 템플릿 테스트"""
    print("="*50)
    print("중국어 레스토랑 템플릿 테스트")
    print("="*50)

    base_path = Path('/Users/songyeon/Desktop/sy.park')

    # 레스토랑 정보 로드
    with open(base_path / 'restaurant_info.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        restaurants = data.get('restaurants', {})

    # OKDONGSIK 정보 확인
    okdongsik = restaurants.get('OKDONGSIK', {})
    print(f"\n레스토랑: OKDONGSIK")
    print(f"중문명: {okdongsik.get('name_cn_s', '')}")
    print(f"주소: {okdongsik.get('address', '')}")

    # 이미지 경로
    shop_path = base_path / 'shop_image' / 'Korea_10_Famous_Korean_Restaurants_in_Hongdae' / 'OKDONGSIK'
    images = [f for f in shop_path.iterdir() if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]

    if len(images) < 3:
        print(f"✗ 이미지가 부족합니다")
        return False

    # 이미지 생성
    generator = ImageGenerator(str(base_path / 'config.json'))

    output_path = base_path / 'output' / 'test_chinese_restaurant.jpg'
    generator.generate(
        template_path=str(base_path / 'templates' / 'instagram_restaurant.json'),
        images={
            'main_image': str(images[0]),
            'sub_image_1': str(images[1]),
            'sub_image_2': str(images[2])
        },
        texts={
            'restaurant_name': okdongsik.get('name_cn_s', ''),
            'address': okdongsik.get('address', '')
        },
        output_path=str(output_path)
    )

    print(f"\n✓ 테스트 성공!")
    print(f"생성된 이미지: {output_path}")
    return True


if __name__ == '__main__':
    test_chinese_restaurant()
