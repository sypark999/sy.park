#!/usr/bin/env python3
"""
SNS 콘텐츠 제작 워크플로우
대화형 인터페이스로 인스타그램 마케팅 이미지를 생성합니다.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

from generate_image import ImageGenerator


class SNSWorkflow:
    """SNS 이미지 제작 워크플로우"""

    def __init__(self):
        self.base_path = Path('/Users/songyeon/Desktop/sy.park')
        self.shop_image_path = self.base_path / 'shop_image' / 'Korea_10_Famous_Korean_Restaurants_in_Hongdae'
        self.templates_path = self.base_path / 'templates'
        self.output_path = self.base_path / 'output'
        self.preview_path = self.output_path / 'preview'

        # 디렉토리 확인
        if not self.shop_image_path.exists():
            raise Exception(f"shop_image 폴더를 찾을 수 없습니다: {self.shop_image_path}")

        # 이미지 생성기 초기화
        self.generator = ImageGenerator(str(self.base_path / 'config.json'))

    def get_restaurants(self) -> List[str]:
        """음식점 목록 가져오기"""
        restaurants = []
        for item in self.shop_image_path.iterdir():
            if item.is_dir():
                restaurants.append(item.name)
        return sorted(restaurants)

    def get_images(self, restaurant: str) -> List[str]:
        """특정 음식점의 이미지 목록 가져오기"""
        restaurant_path = self.shop_image_path / restaurant
        images = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}

        for item in restaurant_path.iterdir():
            if item.is_file() and item.suffix.lower() in valid_extensions:
                images.append(item.name)

        return sorted(images)

    def get_templates(self) -> Dict[str, str]:
        """템플릿 목록 가져오기"""
        templates = {}
        for template_file in self.templates_path.glob('*.json'):
            name = template_file.stem.replace('_', ' ').title()
            templates[name] = str(template_file)
        return templates

    def display_menu(self, title: str, items: List[str]) -> int:
        """메뉴 표시 및 선택"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print('='*50)

        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")

        while True:
            try:
                choice = input(f"\n선택 (1-{len(items)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    return idx
                else:
                    print(f"1부터 {len(items)} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("올바른 숫자를 입력하세요.")
            except KeyboardInterrupt:
                print("\n\n작업이 취소되었습니다.")
                sys.exit(0)

    def get_text_input(self, prompt: str, required: bool = True) -> str:
        """텍스트 입력 받기"""
        while True:
            try:
                text = input(f"\n{prompt}: ").strip()
                if text or not required:
                    return text
                print("필수 입력 항목입니다.")
            except KeyboardInterrupt:
                print("\n\n작업이 취소되었습니다.")
                sys.exit(0)

    def generate_filename(self, restaurant: str, prefix: str = "") -> str:
        """파일명 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        restaurant_clean = restaurant.lower().replace(' ', '_')
        if prefix:
            return f"{prefix}_{restaurant_clean}_{timestamp}.jpg"
        return f"{restaurant_clean}_{timestamp}.jpg"

    def run(self):
        """워크플로우 실행"""
        print("\n" + "="*50)
        print("SNS 이미지 콘텐츠 제작 워크플로우")
        print("="*50)

        # 1. 음식점 선택
        restaurants = self.get_restaurants()
        if not restaurants:
            print("음식점 이미지가 없습니다.")
            return

        restaurant_idx = self.display_menu("음식점을 선택하세요", restaurants)
        selected_restaurant = restaurants[restaurant_idx]

        # 2. 이미지 선택
        images = self.get_images(selected_restaurant)
        if not images:
            print(f"{selected_restaurant}에 이미지가 없습니다.")
            return

        image_idx = self.display_menu("이미지를 선택하세요", images)
        selected_image = images[image_idx]
        image_path = self.shop_image_path / selected_restaurant / selected_image

        # 3. 템플릿 선택
        templates = self.get_templates()
        template_names = list(templates.keys())
        template_idx = self.display_menu("템플릿을 선택하세요", template_names)
        selected_template_name = template_names[template_idx]
        selected_template = templates[selected_template_name]

        # 템플릿 설명
        if 'square' in selected_template_name.lower():
            print("\n선택됨: 정사각형 (1080x1080) - 피드용")
        else:
            print("\n선택됨: 세로형 (1080x1350) - 스토리/릴스용")

        # 4. 텍스트 입력 루프
        while True:
            print("\n" + "="*50)
            print("텍스트 입력")
            print("="*50)

            title = self.get_text_input("제목을 입력하세요", required=True)
            subtitle = self.get_text_input("부제목을 입력하세요", required=False)

            texts = {
                'title': title,
                'subtitle': subtitle
            }

            # 5. 미리보기 생성
            print("\n[미리보기 생성 중...]")
            preview_filename = self.generate_filename(selected_restaurant, "preview")
            preview_output = self.preview_path / preview_filename

            try:
                self.generator.generate(
                    template_path=selected_template,
                    source_image_path=str(image_path),
                    texts=texts,
                    output_path=str(preview_output)
                )
                print(f"\n✓ 미리보기 저장 완료: {preview_output}")
                print(f"\n이미지를 확인해주세요:")
                print(f"  {preview_output}")

            except Exception as e:
                print(f"\n✗ 이미지 생성 실패: {e}")
                retry = input("\n다시 시도하시겠습니까? (y/n): ").strip().lower()
                if retry == 'y':
                    continue
                else:
                    return

            # 6. 확인 및 저장
            print("\n" + "="*50)
            while True:
                choice = input("이미지를 확인하셨나요? (y: 저장, n: 다시 만들기, q: 종료): ").strip().lower()

                if choice == 'y':
                    # 최종 저장
                    final_filename = self.generate_filename(selected_restaurant)
                    final_output = self.output_path / final_filename

                    try:
                        self.generator.generate(
                            template_path=selected_template,
                            source_image_path=str(image_path),
                            texts=texts,
                            output_path=str(final_output)
                        )
                        print(f"\n✓ 최종 이미지 저장 완료: {final_output}")

                        # 계속할지 물어보기
                        another = input("\n다른 이미지를 만드시겠습니까? (y/n): ").strip().lower()
                        if another == 'y':
                            self.run()  # 재귀 호출
                        return

                    except Exception as e:
                        print(f"\n✗ 최종 이미지 저장 실패: {e}")
                        return

                elif choice == 'n':
                    # 텍스트 입력으로 돌아가기
                    break

                elif choice == 'q':
                    print("\n작업을 종료합니다.")
                    return

                else:
                    print("y, n, 또는 q를 입력하세요.")


def main():
    """메인 함수"""
    try:
        # 폰트 확인
        font_path = Path('/Users/songyeon/Desktop/sy.park/fonts/NanumGothic.ttf')
        if not font_path.exists():
            print("\n⚠ 경고: 한글 폰트가 없습니다!")
            print("\n다음 단계를 따라 폰트를 설치하세요:")
            print("1. 나눔고딕 폰트를 다운로드하세요:")
            print("   https://hangeul.naver.com/font/nanum")
            print("2. 다운로드한 NanumGothic.ttf 파일을 다음 경로에 복사하세요:")
            print(f"   {font_path.parent}")
            print("\n기본 폰트로 계속 진행합니다 (한글이 제대로 표시되지 않을 수 있습니다).\n")

            response = input("계속하시겠습니까? (y/n): ").strip().lower()
            if response != 'y':
                return

        workflow = SNSWorkflow()
        workflow.run()

    except Exception as e:
        print(f"\n오류 발생: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
