import os
import json
import re
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

IMAGES_DIR = Path(__file__).parent.parent / "images"
OUTPUT_FILE = IMAGES_DIR / "scores.json"

PROMPT = (
    "이 이미지가 음식(요리/음료) 위주인지 평가하세요. "
    "아래 기준으로 1~10점을 매기고 한 줄 이유를 JSON으로만 답하세요.\n"
    "- 9~10: 음식이 주인공, 클로즈업, 선명하고 식욕을 돋우는 이미지\n"
    "- 7~8: 음식 중심이나 테이블/공간도 포함\n"
    "- 4~6: 매장 내부/외관 위주, 음식은 부차적\n"
    "- 1~3: 음식 없음 (인테리어, 간판, 사람 위주)\n"
    '응답 형식: {"score": 숫자, "reason": "한 줄 이유"}'
)


def parse_response(text: str) -> dict:
    text = text.strip()
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"score": 0, "reason": "파싱 실패"}


def main():
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    image_files = sorted(
        p for p in IMAGES_DIR.glob("*.jpg")
    )

    if not image_files:
        print("이미지 파일이 없습니다.")
        return

    results = []
    print(f"이미지 {len(image_files)}개 분석 중...\n")

    for path in image_files:
        shop = path.stem
        try:
            img = Image.open(path)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[img, PROMPT]
            )
            data = parse_response(response.text)
            score = int(data.get("score", 0))
            reason = data.get("reason", "")
            results.append({"shop": shop, "score": score, "reason": reason})
            print(f"  ✓ {shop:<32} {score}/10")
        except Exception as e:
            results.append({"shop": shop, "score": -1, "reason": f"오류: {e}"})
            print(f"  ✗ {shop:<32} 오류: {e}")

    results.sort(key=lambda x: x["score"], reverse=True)

    print("\n" + "─" * 72)
    print(f"{'매장':<32} {'점수':>4}  판단")
    print("─" * 72)
    for r in results:
        score_str = f"{r['score']}/10" if r['score'] >= 0 else "오류"
        print(f"{r['shop']:<32} {score_str:>4}  {r['reason']}")
    print("─" * 72)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n결과 저장: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
