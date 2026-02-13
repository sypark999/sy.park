#!/usr/bin/env python3
"""
이미지 생성 엔진
템플릿 기반으로 SNS 마케팅 이미지를 생성합니다.
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import re


class TextFormatter:
    """텍스트 포맷팅 및 줄바꿈 처리"""

    @staticmethod
    def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """텍스트를 최대 너비에 맞게 줄바꿈"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    @staticmethod
    def get_text_height(font: ImageFont.FreeTypeFont, text: str) -> int:
        """텍스트의 높이 계산"""
        bbox = font.getbbox(text)
        return bbox[3] - bbox[1]


class LayerRenderer:
    """각 레이어를 렌더링하는 클래스"""

    def __init__(self, config: Dict):
        self.config = config

    def render_background_color(self, canvas: Image.Image, layer: Dict) -> Image.Image:
        """단색 배경 렌더링"""
        if canvas is None:
            canvas_size = tuple(layer['size'])
            canvas = Image.new('RGB', canvas_size, layer['color'])
        return canvas

    def render_image_to_canvas(self, canvas: Image.Image, layer: Dict,
                              source_image: Image.Image) -> Image.Image:
        """이미지를 캔버스의 특정 위치에 렌더링"""
        img = source_image.copy()
        target_width, target_height = layer['size']

        # 비율 유지하며 크롭
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        if img_ratio > target_ratio:
            # 이미지가 더 넓음 - 높이 기준으로 맞춤
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            # 이미지가 더 높음 - 너비 기준으로 맞춤
            new_width = target_width
            new_height = int(new_width / img_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 중앙 크롭
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        img = img.crop((left, top, left + target_width, top + target_height))

        # 캔버스에 합성
        if canvas is None:
            canvas = Image.new('RGB', (1080, 1350), (255, 255, 255))

        canvas.paste(img, tuple(layer['position']))
        return canvas

    def render_background_image(self, layer: Dict, source_image: Image.Image,
                                canvas_size: Tuple[int, int]) -> Image.Image:
        """배경 이미지를 렌더링 (하위 호환성)"""
        canvas = Image.new('RGB', canvas_size, (255, 255, 255))
        return self.render_image_to_canvas(canvas, layer, source_image)

    def render_gradient_overlay(self, canvas: Image.Image, layer: Dict) -> Image.Image:
        """그라디언트 오버레이 렌더링"""
        overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        x, y = layer['position']
        width, height = layer['size']
        colors = layer['colors']

        # 색상 파싱
        def parse_rgba(color_str: str) -> Tuple[int, int, int, int]:
            if color_str.startswith('rgba'):
                match = re.match(r'rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)', color_str)
                if match:
                    r, g, b, a = match.groups()
                    return (int(r), int(g), int(b), int(float(a) * 255))
            return (0, 0, 0, 0)

        start_color = parse_rgba(colors[0])
        end_color = parse_rgba(colors[1])

        # 세로 그라디언트 생성
        for i in range(height):
            ratio = i / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            a = int(start_color[3] + (end_color[3] - start_color[3]) * ratio)

            draw.rectangle([x, y + i, x + width, y + i + 1], fill=(r, g, b, a))

        # 오버레이 합성
        canvas = canvas.convert('RGBA')
        canvas = Image.alpha_composite(canvas, overlay)
        return canvas.convert('RGB')

    def render_text(self, canvas: Image.Image, layer: Dict,
                   text: str, font_path: str) -> Image.Image:
        """텍스트 렌더링 (테두리 지원)"""
        canvas = canvas.convert('RGBA')
        txt_layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)

        # 폰트 로드
        try:
            font = ImageFont.truetype(font_path, layer['font_size'])
        except Exception as e:
            print(f"폰트 로드 실패: {e}")
            font = ImageFont.load_default()

        # 텍스트 줄바꿈
        lines = TextFormatter.wrap_text(text, font, layer['max_width'])

        # 색상 파싱
        color = layer['color']
        if color.startswith('#'):
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))

        # 테두리 색상 및 두께
        stroke_color = None
        stroke_width = 0
        if 'stroke_color' in layer:
            stroke_color = layer['stroke_color']
            if stroke_color.startswith('#'):
                stroke_color = tuple(int(stroke_color[i:i+2], 16) for i in (1, 3, 5))
            stroke_width = layer.get('stroke_width', 0)

        # 행간, 자간 설정
        line_spacing = layer.get('line_spacing', 10)
        letter_spacing = layer.get('letter_spacing', 0)

        # 텍스트 그리기
        x, y = layer['position']
        line_height = TextFormatter.get_text_height(font, 'Ay')
        total_height = line_height * len(lines) + (len(lines) - 1) * line_spacing
        current_y = y - total_height // 2

        for line in lines:
            # 자간이 음수이고 이모지가 포함된 경우 자간 적용 안함
            has_emoji = any(ord(char) > 0x1F300 for char in line)
            apply_letter_spacing = letter_spacing != 0 and not has_emoji

            if apply_letter_spacing:
                # 자간 적용 (이모지 없는 경우만)
                # 전체 너비 계산 (자간 포함)
                total_width = 0
                for i, char in enumerate(line):
                    bbox = font.getbbox(char)
                    char_width = bbox[2] - bbox[0]
                    total_width += char_width
                    if i < len(line) - 1:
                        total_width += letter_spacing

                # 정렬에 따른 시작 위치
                if layer['align'] == 'center':
                    text_x = x - total_width // 2
                elif layer['align'] == 'right':
                    text_x = x - total_width
                else:
                    text_x = x

                # 각 문자 그리기
                for char in line:
                    bbox = font.getbbox(char)
                    char_width = bbox[2] - bbox[0]

                    # 테두리
                    if stroke_color and stroke_width > 0:
                        draw.text((text_x, current_y), char, font=font, fill=stroke_color,
                                 stroke_width=stroke_width, stroke_fill=stroke_color)

                    # 메인 텍스트
                    draw.text((text_x, current_y), char, font=font, fill=color)

                    text_x += char_width + letter_spacing

            else:
                # 이모지 있거나 자간이 0인 경우 기본 방식
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]

                if layer['align'] == 'center':
                    text_x = x - text_width // 2
                elif layer['align'] == 'right':
                    text_x = x - text_width
                else:
                    text_x = x

                # 테두리가 있으면 먼저 그리기
                if stroke_color and stroke_width > 0:
                    draw.text((text_x, current_y), line, font=font, fill=stroke_color,
                             stroke_width=stroke_width, stroke_fill=stroke_color)

                # 메인 텍스트 그리기
                draw.text((text_x, current_y), line, font=font, fill=color)

            current_y += line_height + line_spacing

        canvas = Image.alpha_composite(canvas, txt_layer)
        return canvas.convert('RGB')


class ImageGenerator:
    """템플릿 기반 이미지 생성기"""

    def __init__(self, config_path: str = 'config.json'):
        """초기화"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.renderer = LayerRenderer(self.config)

    def load_template(self, template_path: str) -> Dict:
        """템플릿 로드"""
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_image(self, image_path: str) -> Image.Image:
        """이미지 로드 (HEIC 지원)"""
        try:
            if image_path.lower().endswith('.heic'):
                import pillow_heif
                heif_file = pillow_heif.read_heif(image_path)
                return Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                )
            else:
                return Image.open(image_path)
        except Exception as e:
            raise Exception(f"이미지 로드 실패 ({image_path}): {e}")

    def generate(self, template_path: str, source_image_path: str = None,
                texts: Dict[str, str] = None, output_path: str = None,
                images: Dict[str, str] = None) -> str:
        """이미지 생성

        Args:
            template_path: 템플릿 JSON 파일 경로
            source_image_path: 원본 이미지 경로 (단일 이미지용, 하위 호환성)
            texts: 텍스트 딕셔너리 (예: {'restaurant_name': '식당명', 'address': '주소'})
            output_path: 출력 파일 경로
            images: 다중 이미지 딕셔너리 (예: {'main_image': 'path1.jpg', 'sub_image_1': 'path2.jpg'})

        Returns:
            생성된 이미지 파일 경로
        """
        # 텍스트 기본값 설정
        if texts is None:
            texts = {}

        # 템플릿 로드
        template = self.load_template(template_path)

        # 이미지 로드
        loaded_images = {}

        # 단일 이미지 모드 (하위 호환성)
        if source_image_path:
            loaded_images['background_image'] = self.load_image(source_image_path)

        # 다중 이미지 모드
        if images:
            for key, path in images.items():
                loaded_images[key] = self.load_image(path)

        # 캔버스 초기화
        canvas_size = tuple(template['size'])
        canvas = None

        # 텍스트 레이어 사전 계산 (중앙 정렬을 위해)
        text_layers = [l for l in template['layers'] if l['type'] == 'text']
        if text_layers and texts:
            # 폰트 로드 및 전체 텍스트 높이 계산
            try:
                font_path = self.config['fonts']['default']
                total_text_height = 0
                text_heights = []

                for layer in text_layers:
                    text_name = layer['name']
                    text_content = texts.get(text_name, '')
                    if text_content:
                        font = ImageFont.truetype(font_path, layer['font_size'])
                        lines = TextFormatter.wrap_text(text_content, font, layer.get('max_width', 950))
                        line_height = TextFormatter.get_text_height(font, 'Ay')
                        line_spacing = layer.get('line_spacing', 10)
                        text_height = line_height * len(lines) + (len(lines) - 1) * line_spacing
                        text_heights.append(text_height)
                        total_text_height += text_height

                # 텍스트 간 간격 추가
                if len(text_heights) > 1:
                    # 첫 번째 텍스트(식당명)와 두 번째 텍스트(주소) 사이 간격
                    text_gap = text_layers[1]['position'][1] - text_layers[0]['position'][1]
                    total_text_height += text_gap - text_heights[0] // 2 - text_heights[1] // 2

                # 중앙 위치 계산 (1350 / 2 = 675)
                center_y = canvas_size[1] // 2
                start_y = center_y - total_text_height // 2

                # 첫 번째 텍스트 위치 조정
                if len(text_layers) > 0:
                    text_layers[0]['position'] = [text_layers[0]['position'][0], start_y + text_heights[0] // 2]

                # 두 번째 텍스트 위치 조정
                if len(text_layers) > 1:
                    second_y = start_y + text_heights[0] + (text_gap - text_heights[0] // 2 - text_heights[1] // 2) + text_heights[1] // 2
                    text_layers[1]['position'] = [text_layers[1]['position'][0], second_y]

            except Exception as e:
                print(f"텍스트 중앙 정렬 계산 실패 (기본 위치 사용): {e}")

        # 레이어별 렌더링
        for layer in template['layers']:
            layer_type = layer['type']

            if layer_type == 'background_color':
                canvas = self.renderer.render_background_color(canvas, layer)

            elif layer_type == 'background_image':
                if 'background_image' in loaded_images:
                    canvas = self.renderer.render_background_image(
                        layer, loaded_images['background_image'], canvas_size
                    )

            elif layer_type in ['main_image', 'sub_image_1', 'sub_image_2',
                              'grid_image_1', 'grid_image_2', 'grid_image_3', 'grid_image_4']:
                if layer_type in loaded_images:
                    canvas = self.renderer.render_image_to_canvas(
                        canvas, layer, loaded_images[layer_type]
                    )

            elif layer_type == 'gradient_overlay':
                if canvas:
                    canvas = self.renderer.render_gradient_overlay(canvas, layer)

            elif layer_type == 'text':
                if canvas:
                    text_name = layer['name']
                    text_content = texts.get(text_name, '')
                    if text_content:
                        font_path = self.config['fonts']['default']
                        canvas = self.renderer.render_text(
                            canvas, layer, text_content, font_path
                        )

        # 이미지 저장
        if canvas:
            output_format = self.config['output']['format']
            quality = self.config['output']['quality']

            # 디렉토리 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            canvas.save(output_path, format=output_format, quality=quality)
            return output_path

        raise Exception("이미지 생성 실패")


if __name__ == '__main__':
    # 테스트 코드
    generator = ImageGenerator()

    # 예시: 정사각형 템플릿으로 이미지 생성
    result = generator.generate(
        template_path='templates/instagram_square.json',
        source_image_path='shop_image/OKDONGSIK/image1.jpg',
        texts={
            'title': '홍대 맛집 추천',
            'subtitle': '옥동식 한정식'
        },
        output_path='output/test_output.jpg'
    )
    print(f"이미지 생성 완료: {result}")
