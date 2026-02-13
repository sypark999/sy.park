# SNS 이미지 콘텐츠 제작 워크플로우

인스타그램용 마케팅 이미지를 쉽고 빠르게 생성하는 Python 기반 워크플로우입니다.

## 특징

- 🎨 템플릿 기반 디자인 (정사각형 1080x1080, 세로형 1080x1350)
- 🖼️ 고품질 이미지 자동 크롭 및 리사이즈
- ✏️ 한글 텍스트 지원
- 👁️ 미리보기 기능
- ⚡ 대화형 CLI 인터페이스

## 설치 방법

### 1. 의존성 설치

```bash
pip3 install -r requirements.txt
```

### 2. 한글 폰트 설치 (필수)

한글 텍스트를 올바르게 표시하려면 폰트 파일이 필요합니다.

**나눔고딕 폰트 다운로드:**
1. https://hangeul.naver.com/font/nanum 방문
2. 나눔고딕 다운로드
3. `NanumGothic.ttf` 파일을 `fonts/` 폴더에 복사

**또는 다른 무료 한글 폰트:**
- 배달의민족 도현체: https://www.woowahan.com/fonts
- Noto Sans KR: https://fonts.google.com/noto/specimen/Noto+Sans+KR

## 사용 방법

### 기본 사용

```bash
python3 sns_workflow.py
```

### 워크플로우 단계

1. **음식점 선택**: 사용 가능한 음식점 목록에서 선택
2. **이미지 선택**: 선택한 음식점의 이미지 중 하나 선택
3. **템플릿 선택**:
   - Instagram Square (1080x1080) - 피드용
   - Instagram Portrait (1080x1350) - 스토리/릴스용
4. **텍스트 입력**: 제목과 부제목 입력
5. **미리보기 확인**: `output/preview/` 폴더에서 확인
6. **저장 또는 재작성**: 만족하면 저장, 아니면 텍스트 수정

### 예시

```
음식점을 선택하세요:
1. Ilpyeon_Sirloin_Hongik_University
2. OKDONGSIK
3. Woomoolzip_Hongdae
4. ilpyeon_eel_hongdae
선택: 2

이미지를 선택하세요:
1. 82f5b1d1b3e942b5ba4ae19434e4bd39.jpeg
선택: 1

템플릿을 선택하세요:
1. Instagram Square
선택: 1

제목을 입력하세요: 홍대 최고의 한우 맛집
부제목을 입력하세요: 옥동식 한정식

[미리보기 생성 중...]
✓ 미리보기 저장 완료: output/preview/preview_okdongsik_20260213_143022.jpg

이미지를 확인하셨나요? (y: 저장, n: 다시 만들기, q: 종료): y
✓ 최종 이미지 저장 완료: output/okdongsik_20260213_143022.jpg
```

## 프로젝트 구조

```
sy.park/
├── templates/              # 템플릿 설정 파일
│   ├── instagram_square.json
│   └── instagram_portrait.json
├── fonts/                  # 폰트 파일
│   └── NanumGothic.ttf
├── output/                 # 생성된 이미지
│   └── preview/           # 미리보기
├── shop_image/            # 원본 이미지
│   └── Korea_10_Famous_Korean_Restaurants_in_Hongdae/
├── config.json            # 전역 설정
├── requirements.txt       # Python 패키지
├── sns_workflow.py        # 메인 워크플로우
├── generate_image.py      # 이미지 생성 엔진
└── README.md             # 이 파일
```

## 커스터마이징

### 브랜드 컬러 변경

`config.json` 파일 수정:

```json
{
  "brand": {
    "primary_color": "#FF6B6B",
    "secondary_color": "#FFD700",
    "text_color": "#FFFFFF"
  }
}
```

### 템플릿 레이아웃 변경

`templates/instagram_square.json` 또는 `instagram_portrait.json` 수정:

- 텍스트 위치: `position` 배열 [x, y]
- 폰트 크기: `font_size`
- 텍스트 색상: `color`
- 최대 너비: `max_width`

### 새 템플릿 추가

1. `templates/` 폴더에 새 JSON 파일 생성
2. 기존 템플릿을 참고하여 레이어 구성
3. 워크플로우가 자동으로 인식합니다

## 지원 이미지 형식

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- HEIC (.heic) - iOS 이미지

## 문제 해결

### "폰트 로드 실패" 오류

- `fonts/NanumGothic.ttf` 파일이 있는지 확인
- 파일명이 정확한지 확인
- 폰트 파일이 손상되지 않았는지 확인

### 한글이 깨져 보임

- 한글을 지원하는 폰트를 사용했는지 확인
- `config.json`에서 폰트 경로가 올바른지 확인

### 이미지 품질이 낮음

`config.json`에서 품질 설정 변경:

```json
{
  "output": {
    "quality": 95  // 95-100 권장
  }
}
```

## 향후 개선 사항

- [ ] 일괄 처리 모드
- [ ] 웹 UI
- [ ] 자동 해시태그 생성
- [ ] 다양한 템플릿 추가
- [ ] 로고 오버레이 기능
- [ ] 필터/효과 적용

## 라이선스

이 프로젝트는 개인 사용을 위한 것입니다. 폰트 파일은 각 폰트의 라이선스를 따릅니다.
