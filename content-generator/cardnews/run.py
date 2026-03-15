#!/usr/bin/env python3
"""
카드뉴스 자동 생성 파이프라인

사용법:
    python3 run.py                    # 자동 주제 선별 → 이미지 생성 → 텍스트 합성
    python3 run.py --batch my_topic   # 배치명 지정
    python3 run.py --topic-only       # 주제 선별만
    python3 run.py --skip-topic       # topic.json이 이미 있을 때 (이미지+합성만)
"""

import json
import argparse
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from agents import topic_agent, image_agent, compose_agent


def load_config() -> dict:
    """config.json 로드 + 환경변수 오버라이드"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    import os
    if os.environ.get("OPENAI_API_KEY"):
        config["api"]["openai_api_key"] = os.environ["OPENAI_API_KEY"]
    if os.environ.get("SERP_API_KEY"):
        config["api"]["serp_api_key"] = os.environ["SERP_API_KEY"]

    if not config["api"].get("openai_api_key"):
        print("❌ OpenAI API 키가 설정되지 않았습니다.")
        print("   config.json의 api.openai_api_key를 설정하거나")
        print("   OPENAI_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    return config


def main():
    parser = argparse.ArgumentParser(
        description="한국 음식 트렌드 카드뉴스 자동 생성",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python3 run.py                     # 전체 파이프라인 자동 실행
  python3 run.py --batch street-food # 배치명 지정
  python3 run.py --topic-only        # 주제 선별만
  python3 run.py --skip-topic        # topic.json 있을 때 이미지+합성만
        """,
    )

    parser.add_argument(
        "--batch",
        default=None,
        help="배치 이름 (기본: 날짜 자동 생성, 예: 20260315_143022)",
    )
    parser.add_argument(
        "--topic-only",
        action="store_true",
        help="주제 선별만 실행 (topic.json만 생성)",
    )
    parser.add_argument(
        "--skip-topic",
        action="store_true",
        help="주제 선별 건너뛰기 (기존 topic.json 사용)",
    )

    args = parser.parse_args()

    batch_name = args.batch or datetime.now().strftime("%Y%m%d_%H%M%S")

    base_path = Path(__file__).parent
    output_dir = base_path / "output" / batch_name

    print(f"\n{'=' * 60}")
    print(f"🎴 카드뉴스 자동 생성 파이프라인")
    print(f"{'=' * 60}")
    print(f"  배치: {batch_name}")
    print(f"  출력: {output_dir}")

    config = load_config()

    if not args.skip_topic:
        topic_agent.run(config, output_dir)

    if args.topic_only:
        print("\n✅ 주제 선별 완료 (--topic-only 모드)")
        return

    topic_path = output_dir / "topic.json"
    if not topic_path.exists():
        print(f"\n❌ topic.json을 찾을 수 없습니다: {topic_path}")
        sys.exit(1)

    image_agent.run(config, output_dir)
    compose_agent.run(config, output_dir)

    print(f"\n🎉 카드뉴스 생성 완료!")
    print(f"📂 {output_dir}")


if __name__ == "__main__":
    main()
