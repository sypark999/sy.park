# Instagram v2 Content Generator Design

## Overview

CatchTable 글로벌 마케팅용 인스타그램 캐러셀 콘텐츠 자동 생성 시스템. 기존 샤오홍슈(중국어) 버전을 대체하는 영어 전용 인스타그램 포맷.

## Spec

| 항목 | 값 |
|------|-----|
| 플랫폼 | Instagram (캐러셀 포스트) |
| 언어 | 영어 |
| 이미지 사이즈 | 1080x1350 (4:5) |
| 캐러셀 구성 | 표지 + 레스토랑 카드 N장 + CTA 마지막장 |

## Card Types

### 1. Cover (표지)

TRAZY 레퍼런스 스타일. 대표 사진 위에 큰 타이포.

**레이아웃:**
- 배경: 대표 음식 사진 풀블리드 (1080x1350)
- 오버레이: 전체에 어두운 반투명 오버레이 (rgba(0,0,0,0.3) 정도)
- 상단 서브타이틀: 작은 산세리프 (예: "Top 10 Must-Visit")
- 중앙 메인 타이틀: 큰 세리프 폰트 (예: "Korean Restaurants")
- 하단 지역 태그: 중간 사이즈 (예: "in Seongsu")
- 하단 로고: "CATCHTABLE"

**텍스트 입력:**
- `cover_subtitle`: 상단 서브타이틀
- `cover_title`: 메인 타이틀
- `cover_tag`: 지역/카테고리 태그

### 2. Restaurant Card (레스토랑 카드)

Visit Seoul 레퍼런스 + 풀블리드 사진. 사진 전체 배경 + 하단 그라디언트.

**레이아웃:**
- 배경: 음식 사진 풀블리드 (1080x1350)
- 그라디언트: 하단 ~45% 영역에 투명→검정 세로 그라디언트 (rgba(0,0,0,0) → rgba(0,0,0,0.75))
- 우측 상단: "CATCHTABLE" 워터마크 (흰색, 작은 사이즈)
- 텍스트 (하단, 모두 흰색):
  - 레스토랑명: 굵은 산세리프, 큰 사이즈
  - 주소: 작은 사이즈, 핀 아이콘 prefix
  - 설명: 본문 사이즈, 2-3줄

**텍스트 입력:**
- `restaurant_name`: 레스토랑명 (영어)
- `address`: 주소 (영어)
- `description`: 설명 텍스트 (영어, 2-3줄)

### 3. CTA (마지막장)

팔로우/다운로드 유도.

**레이아웃:**
- 배경: 단색 (흰색 또는 브랜드 컬러)
- 중앙: "Book on CATCHTABLE" 큰 타이포
- 하단: 인스타 핸들 (@catchtable.global)

**텍스트 입력:**
- `cta_title`: 메인 CTA 텍스트
- `cta_handle`: 인스타 핸들

## Data Format

### restaurant_info.json (v2)

```json
{
  "cover": {
    "subtitle": "Top 10 Must-Visit",
    "title": "Korean\nRestaurants",
    "tag": "in Seongsu",
    "image": "cover.jpg"
  },
  "restaurants": {
    "백미우": {
      "name_en": "BEKMIWOO",
      "address_en": "17, Nonhyeon-ro 150-gil, Gangnam-gu, Seoul",
      "description_en": "Traditional Korean BBQ with premium hanwoo beef. A local favorite in Gangnam.",
      "image": "bekmiwoo.jpg"
    }
  },
  "cta": {
    "title": "Book on\nCATCHTABLE",
    "handle": "@catchtable.global"
  }
}
```

## Font Requirements

- 세리프 (표지 메인): Playfair Display 또는 유사 세리프체
- 산세리프 (본문/카드): Inter, Pretendard, 또는 유사 산세리프체
- 기존 중국어 폰트(AlimamaFangYuanTi)는 v2에서 미사용

## Technical Approach

기존 Pillow 기반 `generate_image.py` 렌더링 엔진을 활용.

- 새 템플릿 3종 생성 → `templates/v2/`
  - `cover.json`
  - `restaurant_card.json`
  - `cta.json`
- `generate_batch.py`에 v2 모드 추가 또는 별도 `generate_batch_v2.py` 생성
- 영어 폰트 파일 `fonts/`에 추가

## References

- 썸네일: `reference/SCR-20260303-julm.jpeg` (TRAZY 스타일)
- 내용: `reference/SCR-20260303-juya.jpeg` (Visit Seoul 스타일)
