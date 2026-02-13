# SNS 워크플로우 빠른 시작 가이드

## 설치 완료! ✓

모든 파일과 의존성이 설치되었습니다. 이제 바로 사용할 수 있습니다.

## 바로 시작하기

```bash
cd /Users/songyeon/Desktop/sy.park
python3 sns_workflow.py
```

## 사용 가능한 음식점

현재 4개 음식점의 이미지가 준비되어 있습니다:

1. **Ilpyeon_Sirloin_Hongik_University** - 일편 소고기 홍대점
2. **OKDONGSIK** - 옥동식
3. **Woomoolzip_Hongdae** - 우물집 홍대
4. **ilpyeon_eel_hongdae** - 일편 장어 홍대

## 워크플로우 흐름

```
1. 음식점 선택
   ↓
2. 이미지 선택
   ↓
3. 템플릿 선택 (정사각형/세로형)
   ↓
4. 텍스트 입력 (제목/부제목)
   ↓
5. 미리보기 생성 → output/preview/ 폴더에 저장
   ↓
6. 확인 후 저장 or 수정
   ↓
7. 최종 이미지 저장 → output/ 폴더
```

## 출력 예시

생성된 이미지 위치:
- **미리보기**: `output/preview/preview_okdongsik_20260213_143022.jpg`
- **최종본**: `output/okdongsik_20260213_143022.jpg`

파일명 형식: `{음식점명}_{날짜}_{시간}.jpg`

## 템플릿 선택 가이드

### Instagram Square (1080x1080)
- 일반 피드 게시물용
- 정사각형 비율
- 그리드에서 깔끔하게 보임

### Instagram Portrait (1080x1350)
- 스토리/릴스용
- 세로형 비율 (4:5)
- 모바일 화면에 최적화

## 텍스트 작성 팁

### 제목 (Title)
- 짧고 임팩트 있게 (10-15자 권장)
- 예시:
  - "홍대 맛집 추천"
  - "최고의 한우 맛집"
  - "숨은 맛집 발견"

### 부제목 (Subtitle)
- 구체적인 정보 포함
- 예시:
  - "옥동식 한정식"
  - "일편 소고기 홍대점"
  - "합정역 도보 5분"

## 커스터마이징

### 색상 변경
`config.json` 파일 수정:
```json
{
  "brand": {
    "primary_color": "#FF6B6B",     // 메인 컬러
    "secondary_color": "#FFD700",   // 부제목 컬러 (골드)
    "text_color": "#FFFFFF"         // 제목 컬러 (화이트)
  }
}
```

### 텍스트 위치/크기 조정
`templates/instagram_square.json` 수정:
```json
{
  "type": "text",
  "name": "title",
  "position": [540, 850],    // [x좌표, y좌표]
  "font_size": 60,           // 폰트 크기
  "color": "#FFFFFF"         // 텍스트 색상
}
```

## 트러블슈팅

### 문제: 한글이 깨져 보임
**해결**: `fonts/NanumGothic.ttf` 파일 확인 (현재 설치됨 ✓)

### 문제: 이미지가 너무 크거나 작음
**해결**: 템플릿 JSON의 `size` 값 조정

### 문제: 텍스트가 잘림
**해결**: 템플릿의 `max_width` 값 늘리기

### 문제: 그라디언트가 너무 진함
**해결**: 템플릿의 `colors` 값에서 투명도 조정
- `rgba(0,0,0,0.7)` → `rgba(0,0,0,0.5)` (더 연하게)

## 파일 구조

```
sy.park/
├── sns_workflow.py          # 메인 실행 파일 ⭐
├── generate_image.py        # 이미지 생성 엔진
├── test_workflow.py         # 테스트 스크립트
├── config.json              # 전역 설정
├── requirements.txt         # 패키지 목록
├── README.md               # 상세 문서
├── QUICKSTART.md           # 이 파일
│
├── templates/              # 템플릿 설정
│   ├── instagram_square.json
│   └── instagram_portrait.json
│
├── fonts/                  # 폰트 파일
│   └── NanumGothic.ttf    # Noto Sans KR
│
├── output/                 # 생성된 이미지 ⭐
│   ├── preview/           # 미리보기
│   ├── test_square.jpg    # 테스트 이미지
│   └── test_portrait.jpg  # 테스트 이미지
│
└── shop_image/            # 원본 이미지
    └── Korea_10_Famous_Korean_Restaurants_in_Hongdae/
        ├── OKDONGSIK/
        ├── Ilpyeon_Sirloin_Hongik_University/
        ├── Woomoolzip_Hongdae/
        └── ilpyeon_eel_hongdae/
```

## 테스트 이미지 확인

테스트 이미지가 이미 생성되어 있습니다:
- `output/test_square.jpg` - 정사각형 템플릿 예시
- `output/test_portrait.jpg` - 세로형 템플릿 예시

이 이미지들을 열어서 품질과 레이아웃을 확인해보세요!

## 다음 단계

1. **테스트 이미지 확인**
   ```bash
   open output/test_square.jpg
   ```

2. **본격적으로 시작**
   ```bash
   python3 sns_workflow.py
   ```

3. **생성된 이미지 확인**
   ```bash
   open output/
   ```

## 추가 기능 아이디어

향후 추가 가능한 기능들:
- 🔄 일괄 처리 모드 (여러 이미지 한번에)
- 🎯 자동 해시태그 생성
- 🖼️ 로고 오버레이
- 🎨 필터/효과 적용
- 📅 게시 일정 관리
- 🌐 웹 UI 인터페이스

---

**질문이나 문제가 있으면 README.md를 참고하세요!**
