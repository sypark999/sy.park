# 레스토랑 정보 관리 가이드

## 📋 레스토랑 정보 파일

주소와 레스토랑 정보는 **`restaurant_info.json`** 파일에 저장됩니다.

위치: `/Users/songyeon/Desktop/sy.park/restaurant_info.json`

## 📝 파일 구조

```json
{
  "restaurants": {
    "OKDONGSIK": {
      "name": "옥동식",
      "name_en": "OKDONGSIK",
      "address": "서울 마포구 홍대입구",
      "address_detail": "와우산로 21길 19",
      "phone": "02-1234-5678",
      "description": "한정식 전문점",
      "tags": ["한식", "한정식", "홍대맛집"]
    }
  }
}
```

## 🔑 필드 설명

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `name` | ✅ | 식당명 (한글) | "옥동식" |
| `name_en` | ❌ | 식당명 (영문) | "OKDONGSIK" |
| `address` | ✅ | 간단한 주소 | "서울 마포구 홍대입구" |
| `address_detail` | ❌ | 상세 주소 | "와우산로 21길 19" |
| `phone` | ❌ | 전화번호 | "02-1234-5678" |
| `description` | ❌ | 설명 | "한정식 전문점" |
| `tags` | ❌ | 태그 | ["한식", "한정식"] |

## ✨ 자동 불러오기 기능

워크플로우에서 레스토랑 템플릿을 사용할 때:

```
💡 저장된 정보:
   식당명: 옥동식
   주소: 서울 마포구 홍대입구

저장된 정보를 사용하시겠습니까? (y/n): y
```

- `y` 입력: 저장된 정보 자동 사용
- `n` 입력: 직접 입력

## 📂 폴더명 = 키 이름

**중요**: JSON의 키 이름은 `shop_image` 폴더의 이름과 **정확히 일치**해야 합니다.

예시:
```
shop_image/Korea_10_Famous_Korean_Restaurants_in_Hongdae/
├── OKDONGSIK/          ← 이 이름을
└── Woomoolzip_Hongdae/

restaurant_info.json:
{
  "restaurants": {
    "OKDONGSIK": { ... },          ← 여기에 동일하게
    "Woomoolzip_Hongdae": { ... }
  }
}
```

## 🆕 새 레스토랑 추가하기

### 1. 이미지 폴더 생성
```bash
shop_image/Korea_10_Famous_Korean_Restaurants_in_Hongdae/새레스토랑명/
```

### 2. restaurant_info.json 편집
```json
{
  "restaurants": {
    "새레스토랑명": {
      "name": "새로운 식당",
      "address": "서울 마포구 어디어디",
      "description": "맛있는 집"
    }
  }
}
```

### 3. 완료!
워크플로우를 실행하면 자동으로 인식됩니다.

## 💡 주소 작성 팁

### 간결하게 (address 필드)
```json
"address": "서울 마포구 홍대입구"
"address": "홍대입구역 5번 출구"
"address": "합정역 도보 3분"
```

이 값이 이미지에 표시됩니다.

### 상세하게 (address_detail 필드)
```json
"address_detail": "서울특별시 마포구 와우산로21길 19"
```

나중에 필요할 때 참고용.

## 🔧 정보 수정하기

`restaurant_info.json` 파일을 텍스트 에디터로 열어서 수정하면 됩니다.

**주의**: JSON 형식을 유지해야 합니다!
- 쉼표(,) 위치
- 중괄호({}) 짝 맞추기
- 따옴표("") 사용

## 📱 실제 사용 예시

### 자동 불러오기
```bash
$ python3 sns_workflow.py

음식점을 선택하세요:
1. OKDONGSIK
선택: 1

템플릿을 선택하세요:
3. Instagram Restaurant (3 Images)
선택: 3

💡 저장된 정보:
   식당명: 옥동식
   주소: 서울 마포구 홍대입구

저장된 정보를 사용하시겠습니까? (y/n): y
→ 자동으로 입력됨!
```

### 직접 입력
```bash
저장된 정보를 사용하시겠습니까? (y/n): n

식당명을 입력하세요: 옥동식 본점
주소를 입력하세요: 서울 마포구
→ 사용자 입력 사용
```

## 🎯 활용 팁

1. **미리 작성**: 모든 레스토랑 정보를 미리 작성해두면 빠르게 작업 가능
2. **일관성 유지**: 같은 스타일로 주소 작성 (예: 모두 "서울 XX구" 형식)
3. **태그 활용**: 나중에 검색/분류할 때 유용
4. **영문명 저장**: 영문 콘텐츠 제작 시 활용

## ❓ 자주 묻는 질문

### Q: 파일이 없으면 어떻게 되나요?
A: 자동으로 건너뛰고 직접 입력 모드로 진행됩니다.

### Q: 일부 레스토랑만 등록해도 되나요?
A: 네! 등록된 것만 자동 제안되고, 나머지는 직접 입력하면 됩니다.

### Q: 정보를 수정하면 바로 반영되나요?
A: 네! 워크플로우를 다시 실행하면 변경된 정보가 로드됩니다.

### Q: 다른 정보(전화번호, 영업시간)도 추가할 수 있나요?
A: 네! JSON에 원하는 필드를 추가하면 됩니다. 단, 현재는 `name`과 `address`만 이미지에 표시됩니다.

## 🚀 향후 확장 아이디어

- [ ] 전화번호/영업시간 표시 템플릿
- [ ] 태그 기반 자동 해시태그 생성
- [ ] 웹 UI로 정보 관리
- [ ] CSV/엑셀 파일 가져오기

---

**파일 위치**: `/Users/songyeon/Desktop/sy.park/restaurant_info.json`
