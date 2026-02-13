#!/usr/bin/env python3
"""
레스토랑 템플릿 테스트
3개 이미지 합성 기능을 테스트합니다.
"""

import os
from pathlib import Path
from generate_image import ImageGenerator


def test_restaurant_template():
    """레스토랑 템플릿 (3개 이미지) 테스트"""
    print("="*50)
    print("레스토랑 템플릿 테스트 (3개 이미지 합성)")
    print("="*50)

    # 경로 설정
    base_path = Path('/Users/songyeon/Desktop/sy.park')
    shop_path = base_path / 'shop_image' / 'Korea_10_Famous_Korean_Restaurants_in_Hongdae'

    # OKDONGSIK 음식점 선택
    restaurant = shop_path / 'OKDONGSIK'
    print(f"\n테스트 음식점: OKDONGSIK")

    # 이미지 찾기
    images = [f for f in restaurant.iterdir()
              if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]

    if len(images) < 3:
        print(f"✗ 이미지가 3개 미만입니다 (현재: {len(images)}개)")
        return False

    # 3개 이미지 선택
    main_image = images[0]
    sub_image_1 = images[1] if len(images) > 1 else images[0]
    sub_image_2 = images[2] if len(images) > 2 else images[0]

    print(f"메인 이미지: {main_image.name}")
    print(f"서브 이미지 1: {sub_image_1.name}")
    print(f"서브 이미지 2: {sub_image_2.name}")

    # 이미지 생성기 초기화
    try:
        generator = ImageGenerator(str(base_path / 'config.json'))
        print("✓ 이미지 생성기 초기화 완료")
    except Exception as e:
        print(f"✗ 초기화 실패: {e}")
        return False

    # 레스토랑 템플릿으로 이미지 생성
    try:
        output_path = base_path / 'output' / 'test_restaurant.jpg'
        generator.generate(
            template_path=str(base_path / 'templates' / 'instagram_restaurant.json'),
            images={
                'main_image': str(main_image),
                'sub_image_1': str(sub_image_1),
                'sub_image_2': str(sub_image_2)
            },
            texts={
                'restaurant_name': '옥동식',
                'address': '서울 마포구 홍대입구'
            },
            output_path=str(output_path)
        )
        print(f"✓ 레스토랑 템플릿 테스트 성공: {output_path}")
    except Exception as e:
        print(f"✗ 레스토랑 템플릿 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "="*50)
    print("✓ 테스트 통과!")
    print("="*50)
    print(f"\n생성된 테스트 이미지: {output_path}")
    print("\n이제 'python3 sns_workflow.py'로 워크플로우를 시작할 수 있습니다.")

    return True


if __name__ == '__main__':
    success = test_restaurant_template()
    exit(0 if success else 1)
