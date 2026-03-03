# Instagram v2 Content Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 기존 Pillow 렌더링 엔진 위에 v2 인스타그램 캐러셀(표지 + 레스토랑 카드 + CTA) 생성 기능 구축

**Architecture:** 기존 `generate_image.py`(ImageGenerator, LayerRenderer)를 그대로 활용. v2용 JSON 템플릿 3종 + `generate_batch_v2.py` 엔트리포인트 추가. 영어 폰트 2종(세리프 + 산세리프) 추가.

**Tech Stack:** Python 3, Pillow, JSON 템플릿

---

### Task 1: 영어 폰트 추가

**Files:**
- Create: `content-generator/fonts/PlayfairDisplay-Bold.ttf` (다운로드)
- Create: `content-generator/fonts/Inter-Regular.ttf` (다운로드)
- Create: `content-generator/fonts/Inter-Bold.ttf` (다운로드)

**Step 1: 구글 폰트에서 다운로드**

```bash
cd /Users/songyeon/Desktop/sy.park/content-generator/fonts

# Playfair Display (세리프 - 표지 메인 타이틀)
curl -L -o PlayfairDisplay-Bold.ttf "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/static/PlayfairDisplay-Bold.ttf"

# Inter (산세리프 - 본문/카드)
curl -L -o Inter-Regular.ttf "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter_18pt-Regular.ttf"
curl -L -o Inter-Bold.ttf "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter_18pt-Bold.ttf"
```

**Step 2: 폰트 파일 존재 확인**

```bash
ls -la /Users/songyeon/Desktop/sy.park/content-generator/fonts/*.ttf
```

Expected: 4개 ttf 파일 (기존 Alimama + 신규 3개)

**Step 3: 커밋**

```bash
git add content-generator/fonts/*.ttf
git commit -m "feat: add English fonts (Playfair Display, Inter) for v2"
```

---

### Task 2: v2 config 및 레스토랑 카드 템플릿 생성

**Files:**
- Create: `content-generator/config_v2.json`
- Create: `content-generator/templates/v2/restaurant_card.json`

**Step 1: v2 config 파일 작성**

`content-generator/config_v2.json`:

```json
{
  "brand": {
    "primary_color": "#1A1A1A",
    "text_color": "#FFFFFF",
    "watermark_color": "#FFFFFF"
  },
  "fonts": {
    "serif": "fonts/PlayfairDisplay-Bold.ttf",
    "sans_bold": "fonts/Inter-Bold.ttf",
    "sans_regular": "fonts/Inter-Regular.ttf"
  },
  "output": {
    "format": "JPEG",
    "quality": 95
  }
}
```

**Step 2: 레스토랑 카드 템플릿 작성**

`content-generator/templates/v2/restaurant_card.json`:

```json
{
  "name": "v2 Restaurant Card",
  "size": [1080, 1350],
  "description": "풀블리드 사진 + 하단 그라디언트 + 흰색 텍스트",
  "layers": [
    {
      "type": "background_image",
      "position": [0, 0],
      "size": [1080, 1350],
      "fit": "cover"
    },
    {
      "type": "gradient_overlay",
      "position": [0, 740],
      "size": [1080, 610],
      "colors": ["rgba(0,0,0,0)", "rgba(0,0,0,200)"]
    },
    {
      "type": "text",
      "name": "watermark",
      "position": [1030, 50],
      "align": "right",
      "font": "sans_bold",
      "font_size": 24,
      "color": "#FFFFFF",
      "max_width": 300,
      "line_spacing": 0,
      "letter_spacing": 2
    },
    {
      "type": "text",
      "name": "restaurant_name",
      "position": [60, 1050],
      "align": "left",
      "font": "sans_bold",
      "font_size": 52,
      "color": "#FFFFFF",
      "max_width": 960,
      "line_spacing": 8,
      "letter_spacing": 0
    },
    {
      "type": "text",
      "name": "address",
      "position": [60, 1130],
      "align": "left",
      "font": "sans_regular",
      "font_size": 28,
      "color": "#FFFFFF",
      "max_width": 960,
      "line_spacing": 6,
      "letter_spacing": 0
    },
    {
      "type": "text",
      "name": "description",
      "position": [60, 1200],
      "align": "left",
      "font": "sans_regular",
      "font_size": 30,
      "color": "#FFFFFF",
      "max_width": 960,
      "line_spacing": 10,
      "letter_spacing": 0
    }
  ]
}
```

**Step 3: 커밋**

```bash
git add content-generator/config_v2.json content-generator/templates/v2/restaurant_card.json
git commit -m "feat: add v2 config and restaurant card template"
```

---

### Task 3: generate_image.py v2 호환 수정

기존 엔진이 v2 템플릿의 `font` 필드(폰트 이름 키)를 처리하도록 수정. 기존 동작은 그대로 유지.

**Files:**
- Modify: `content-generator/generate_image.py`

**Step 1: `render_text`에서 폰트 키 지원 추가**

현재 `render_text(canvas, layer, text, font_path)` 시그니처에서 `font_path`는 호출 시 `config['fonts']['default']`를 넘기고 있음.

v2에서는 레이어에 `"font": "sans_bold"` 같은 키가 있으므로, `ImageGenerator.generate()`의 text 렌더링 부분에서 레이어의 `font` 필드를 확인하여 적절한 폰트 경로를 결정하도록 수정.

`generate_image.py`의 `generate()` 메서드 내 텍스트 렌더링 부분 (현재 388-395줄):

```python
# 기존:
font_path = self.config['fonts']['default']

# 변경:
font_key = layer.get('font', None)
if font_key and font_key in self.config['fonts']:
    font_path = self.config['fonts'][font_key]
else:
    font_path = self.config['fonts'].get('default', self.config['fonts'].get('sans_regular', ''))
```

또한 텍스트 위치 계산에서 v2는 그룹 중앙 정렬 대신 절대 위치를 사용. 레이어에 `"absolute_position": true` 플래그가 있으면 그룹 중앙 정렬 로직을 건너뛰도록 수정.

**Step 2: 텍스트 위치를 절대 좌표로도 사용 가능하게**

현재 텍스트 렌더링에서 `current_y = y - total_height // 2` (중앙 정렬 기준). v2 템플릿은 좌측 하단 정렬이므로, `render_text()`에서 `layer.get('vertical_align', 'center')` 확인:

- `center` (기존 기본값): `current_y = y - total_height // 2`
- `top`: `current_y = y`

```python
# render_text 메서드의 current_y 계산 부분 수정:
vertical_align = layer.get('vertical_align', 'center')
if vertical_align == 'top':
    current_y = y
else:
    current_y = y - total_height // 2
```

**Step 3: 테스트 — 기존 v1 배치 생성이 깨지지 않는지 확인**

```bash
cd /Users/songyeon/Desktop/sy.park/content-generator
python3 -c "from generate_image import ImageGenerator; print('import OK')"
```

**Step 4: 커밋**

```bash
git add content-generator/generate_image.py
git commit -m "feat: support per-layer font key and vertical_align in text renderer"
```

---

### Task 4: 표지(Cover) 템플릿 생성

**Files:**
- Create: `content-generator/templates/v2/cover.json`

**Step 1: 표지 템플릿 작성**

```json
{
  "name": "v2 Cover",
  "size": [1080, 1350],
  "description": "풀블리드 사진 + 전체 오버레이 + 세리프 타이틀",
  "layers": [
    {
      "type": "background_image",
      "position": [0, 0],
      "size": [1080, 1350],
      "fit": "cover"
    },
    {
      "type": "gradient_overlay",
      "position": [0, 0],
      "size": [1080, 1350],
      "colors": ["rgba(0,0,0,80)", "rgba(0,0,0,80)"]
    },
    {
      "type": "text",
      "name": "cover_subtitle",
      "position": [540, 420],
      "align": "center",
      "font": "sans_regular",
      "font_size": 32,
      "color": "#FFFFFF",
      "max_width": 900,
      "line_spacing": 8,
      "letter_spacing": 2,
      "vertical_align": "top"
    },
    {
      "type": "text",
      "name": "cover_title",
      "position": [540, 500],
      "align": "center",
      "font": "serif",
      "font_size": 90,
      "color": "#FFFFFF",
      "max_width": 900,
      "line_spacing": 10,
      "letter_spacing": 0,
      "vertical_align": "top"
    },
    {
      "type": "text",
      "name": "cover_tag",
      "position": [540, 780],
      "align": "center",
      "font": "sans_regular",
      "font_size": 36,
      "color": "#FFFFFF",
      "max_width": 900,
      "line_spacing": 8,
      "letter_spacing": 1,
      "vertical_align": "top"
    },
    {
      "type": "text",
      "name": "logo",
      "position": [540, 1250],
      "align": "center",
      "font": "sans_bold",
      "font_size": 28,
      "color": "#FFFFFF",
      "max_width": 500,
      "line_spacing": 0,
      "letter_spacing": 4,
      "vertical_align": "top"
    }
  ]
}
```

**Step 2: 커밋**

```bash
git add content-generator/templates/v2/cover.json
git commit -m "feat: add v2 cover template"
```

---

### Task 5: CTA 템플릿 생성

**Files:**
- Create: `content-generator/templates/v2/cta.json`

**Step 1: CTA 템플릿 작성**

```json
{
  "name": "v2 CTA",
  "size": [1080, 1350],
  "description": "팔로우/다운로드 유도 마지막 장",
  "layers": [
    {
      "type": "background_color",
      "color": "#1A1A1A",
      "position": [0, 0],
      "size": [1080, 1350]
    },
    {
      "type": "text",
      "name": "cta_title",
      "position": [540, 550],
      "align": "center",
      "font": "serif",
      "font_size": 72,
      "color": "#FFFFFF",
      "max_width": 900,
      "line_spacing": 15,
      "letter_spacing": 0,
      "vertical_align": "top"
    },
    {
      "type": "text",
      "name": "cta_handle",
      "position": [540, 800],
      "align": "center",
      "font": "sans_regular",
      "font_size": 30,
      "color": "#999999",
      "max_width": 500,
      "line_spacing": 0,
      "letter_spacing": 1,
      "vertical_align": "top"
    }
  ]
}
```

**Step 2: 커밋**

```bash
git add content-generator/templates/v2/cta.json
git commit -m "feat: add v2 CTA template"
```

---

### Task 6: generate_batch_v2.py 엔트리포인트 생성

**Files:**
- Create: `content-generator/generate_batch_v2.py`

**Step 1: 배치 스크립트 작성**

핵심 동작:
1. `shop_image/[batch]/restaurant_info.json`에서 v2 포맷 데이터 읽기
2. 표지 1장 생성 (cover 템플릿 + cover.image)
3. 레스토랑별 카드 N장 생성 (restaurant_card 템플릿 + 각 레스토랑 image)
4. CTA 1장 생성 (cta 템플릿)
5. 전부 `output/[batch]_v2/` 폴더에 저장, 파일명에 순번 prefix (01_cover, 02_레스토랑명, ...)

```python
#!/usr/bin/env python3
"""
v2 인스타그램 캐러셀 배치 생성
표지 + 레스토랑 카드 + CTA 세트 생성

사용법:
    python3 generate_batch_v2.py --batch seongsu
"""

import json
import argparse
from pathlib import Path
from generate_image import ImageGenerator


class BatchGeneratorV2:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.generator = ImageGenerator(str(base_path / 'config_v2.json'))
        self.template_dir = base_path / 'templates' / 'v2'

    def find_image(self, batch_path: Path, image_name: str, restaurant_name: str = None) -> Path:
        """이미지 파일 찾기. image_name이 직접 경로이면 그대로, 아니면 레스토랑 폴더에서 탐색."""
        # 직접 경로
        direct = batch_path / image_name
        if direct.exists():
            return direct

        # 레스토랑 폴더 내
        if restaurant_name:
            for subdir in [batch_path, *batch_path.iterdir()]:
                if subdir.is_dir():
                    candidate = subdir / restaurant_name / image_name
                    if candidate.exists():
                        return candidate
                    # 이미지 이름 없이 폴더의 첫 번째 이미지
                    folder = subdir / restaurant_name if (subdir / restaurant_name).exists() else None
                    if folder and folder.is_dir():
                        images = sorted([
                            f for f in folder.iterdir()
                            if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
                            and not f.name.startswith('.')
                        ])
                        if images:
                            return images[0]
        return None

    def generate(self, batch_name: str):
        print(f"\n{'='*60}")
        print(f"v2 Carousel [{batch_name}] generation start")
        print(f"{'='*60}\n")

        batch_path = self.base_path / 'shop_image' / batch_name
        info_path = batch_path / 'restaurant_info.json'
        output_dir = self.base_path / 'output' / f'{batch_name}_v2'
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        slide_num = 1

        # 1. Cover
        cover = data.get('cover', {})
        cover_image = self.find_image(batch_path, cover.get('image', ''))
        if cover_image:
            output_path = output_dir / f"{slide_num:02d}_cover.jpg"
            self.generator.generate(
                template_path=str(self.template_dir / 'cover.json'),
                source_image_path=str(cover_image),
                texts={
                    'cover_subtitle': cover.get('subtitle', ''),
                    'cover_title': cover.get('title', ''),
                    'cover_tag': cover.get('tag', ''),
                    'logo': 'CATCHTABLE',
                },
                output_path=str(output_path),
            )
            print(f"  [{slide_num:02d}] Cover generated")
            slide_num += 1
        else:
            print(f"  Cover image not found, skipping")

        # 2. Restaurant cards
        restaurants = data.get('restaurants', {})
        for name, info in restaurants.items():
            image_file = info.get('image', '')
            img_path = self.find_image(batch_path, image_file, restaurant_name=name)
            if not img_path:
                print(f"  [{slide_num:02d}] {name}: image not found, skipping")
                continue

            output_path = output_dir / f"{slide_num:02d}_{name}.jpg"
            self.generator.generate(
                template_path=str(self.template_dir / 'restaurant_card.json'),
                source_image_path=str(img_path),
                texts={
                    'watermark': 'CATCHTABLE',
                    'restaurant_name': info.get('name_en', name),
                    'address': info.get('address_en', ''),
                    'description': info.get('description_en', ''),
                },
                output_path=str(output_path),
            )
            print(f"  [{slide_num:02d}] {name} card generated")
            slide_num += 1

        # 3. CTA
        cta = data.get('cta', {})
        output_path = output_dir / f"{slide_num:02d}_cta.jpg"
        self.generator.generate(
            template_path=str(self.template_dir / 'cta.json'),
            texts={
                'cta_title': cta.get('title', 'Book on\nCATCHTABLE'),
                'cta_handle': cta.get('handle', '@catchtable.global'),
            },
            output_path=str(output_path),
        )
        print(f"  [{slide_num:02d}] CTA generated")

        print(f"\n{'='*60}")
        print(f"Done! {slide_num} slides -> {output_dir}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='v2 Instagram carousel batch generator')
    parser.add_argument('--batch', required=True, help='Batch name (folder under shop_image/)')
    args = parser.parse_args()

    base_path = Path(__file__).parent
    gen = BatchGeneratorV2(base_path)
    gen.generate(args.batch)


if __name__ == '__main__':
    main()
```

**Step 2: 커밋**

```bash
git add content-generator/generate_batch_v2.py
git commit -m "feat: add v2 carousel batch generator"
```

---

### Task 7: 테스트 데이터로 예시 생성 및 검증

**Files:**
- Create: `content-generator/shop_image/test_v2/restaurant_info.json` (테스트 데이터)

**Step 1: 테스트 데이터 준비**

사용자가 제공하는 이미지와 텍스트로 테스트 데이터 작성. 이미지는 기존 배치에서 임시로 가져오거나 사용자가 제공.

**Step 2: 배치 실행**

```bash
cd /Users/songyeon/Desktop/sy.park/content-generator
python3 generate_batch_v2.py --batch test_v2
```

**Step 3: 출력 이미지 확인**

```bash
ls -la output/test_v2/
open output/test_v2/
```

**Step 4: 사용자 피드백 반영 후 커밋**

```bash
git add -A
git commit -m "feat: verify v2 carousel generation with test data"
```
