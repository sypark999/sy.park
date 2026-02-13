#!/usr/bin/env python3
"""
간단한 테스트 스크립트
워크플로우가 올바르게 작동하는지 확인합니다.
"""

import os
from pathlib import Path
from generate_image import ImageGenerator


def test_basic_generation():
    """기본 이미지 생성 테스트"""
    print("="*50)
    print("SNS 워크플로우 테스트")
    print("="*50)

    # 경로 설정
    base_path = Path('/Users/songyeon/Desktop/sy.park')
    shop_path = base_path / 'shop_image' / 'Korea_10_Famous_Korean_Restaurants_in_Hongdae'

    # 첫 번째 음식점과 이미지 찾기
    restaurants = [d for d in shop_path.iterdir() if d.is_dir()]
    if not restaurants:
        print("✗ 음식점 폴더를 찾을 수 없습니다.")
        return False

    restaurant = restaurants[0]
    print(f"\n테스트 음식점: {restaurant.name}")

    # 이미지 찾기
    images = [f for f in restaurant.iterdir()
              if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]

    if not images:
        print("✗ 이미지를 찾을 수 없습니다.")
        return False

    test_image = images[0]
    print(f"테스트 이미지: {test_image.name}")

    # 이미지 생성기 초기화
    try:
        generator = ImageGenerator(str(base_path / 'config.json'))
        print("✓ 이미지 생성기 초기화 완료")
    except Exception as e:
        print(f"✗ 초기화 실패: {e}")
        return False

    # 테스트 이미지 생성 (정사각형)
    try:
        output_path = base_path / 'output' / 'test_square.jpg'
        generator.generate(
            template_path=str(base_path / 'templates' / 'instagram_square.json'),
            source_image_path=str(test_image),
            texts={
                'title': '홍대 맛집 추천',
                'subtitle': '테스트 이미지'
            },
            output_path=str(output_path)
        )
        print(f"✓ 정사각형 템플릿 테스트 성공: {output_path}")
    except Exception as e:
        print(f"✗ 정사각형 템플릿 실패: {e}")
        return False

    # 테스트 이미지 생성 (세로형)
    try:
        output_path = base_path / 'output' / 'test_portrait.jpg'
        generator.generate(
            template_path=str(base_path / 'templates' / 'instagram_portrait.json'),
            source_image_path=str(test_image),
            texts={
                'title': '홍대 맛집 추천',
                'subtitle': '테스트 이미지'
            },
            output_path=str(output_path)
        )
        print(f"✓ 세로형 템플릿 테스트 성공: {output_path}")
    except Exception as e:
        print(f"✗ 세로형 템플릿 실패: {e}")
        return False

    print("\n" + "="*50)
    print("✓ 모든 테스트 통과!")
    print("="*50)
    print("\n생성된 테스트 이미지:")
    print(f"  - {base_path / 'output' / 'test_square.jpg'}")
    print(f"  - {base_path / 'output' / 'test_portrait.jpg'}")
    print("\n이제 'python3 sns_workflow.py'로 워크플로우를 시작할 수 있습니다.")

    return True


if __name__ == '__main__':
    success = test_basic_generation()
    exit(0 if success else 1)
