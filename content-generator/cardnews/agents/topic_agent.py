#!/usr/bin/env python3
"""
에이전트 1: 주제 선별
웹 검색으로 한국 음식 트렌드를 파악하고 카드뉴스 주제를 선별합니다.
"""

import json
import os
from pathlib import Path
from openai import OpenAI


def search_trends(config: dict) -> list[dict]:
    """SerpAPI로 한국 음식 트렌드 검색"""
    serp_key = config["api"].get("serp_api_key", "")
    keywords = config["search"]["keywords"]
    max_results = config["search"]["max_results"]

    if not serp_key:
        print("  ⚠️  SerpAPI 키 없음 — LLM 지식 기반으로 주제 생성")
        return []

    try:
        from serpapi import GoogleSearch
    except ImportError:
        print("  ⚠️  serpapi 패키지 미설치 — LLM 지식 기반으로 주제 생성")
        return []

    results = []
    for keyword in keywords[:3]:
        params = {
            "q": keyword,
            "engine": "google",
            "hl": "zh-CN",
            "gl": "cn",
            "num": max_results // 3,
            "api_key": serp_key,
        }
        try:
            search = GoogleSearch(params)
            data = search.get_dict()
            for r in data.get("organic_results", []):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "link": r.get("link", ""),
                })
        except Exception as e:
            print(f"  ⚠️  검색 실패 ({keyword}): {e}")

    return results


def generate_topic(config: dict, search_results: list[dict], output_dir: Path) -> Path:
    """LLM으로 카드뉴스 주제 생성"""
    client = OpenAI(api_key=config["api"]["openai_api_key"])
    card_count = config["topic"]["card_count"]
    system_prompt = config["topic"]["system_prompt"]

    if search_results:
        context = "以下是最近的韩国美食相关搜索结果:\n\n"
        for i, r in enumerate(search_results[:15], 1):
            context += f"{i}. {r['title']}\n   {r['snippet']}\n\n"
    else:
        context = "没有搜索结果。请根据你对韩国美食趋势的知识生成主题。"

    user_prompt = f"""{context}

请根据以上信息，生成一个适合小红书卡片新闻的韩国美食趋势主题。

要求：
1. 主题要对中国年轻人有吸引力
2. 与韩国美食、韩国文化、K-pop相关
3. 生成恰好 {card_count} 张内容卡片
4. 每张卡片包含一个具体的美食/餐厅/趋势
5. image_prompt 用英文写，适合AI图像生成，风格为美食摄影

请严格按照以下JSON格式输出（不要添加任何其他文字）：

{{{{
  "topic": "主题标题（中文）",
  "subtitle": "副标题（中文）",
  "cards": [
    {{{{
      "title": "卡片标题（中文）",
      "description": "2-3句描述（中文）",
      "image_prompt": "English prompt for food photography, appetizing, vibrant colors, professional lighting"
    }}}}
  ],
  "hashtags": ["#韩国美食", "#首尔必吃", ...],
  "sns_caption": "小红书发布用的完整文案（中文）"
}}}}"""

    print("  LLM으로 주제 생성 중...")
    response = client.chat.completions.create(
        model=config["api"]["chat_model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )

    topic_data = json.loads(response.choices[0].message.content)

    output_dir.mkdir(parents=True, exist_ok=True)
    topic_path = output_dir / "topic.json"
    with open(topic_path, "w", encoding="utf-8") as f:
        json.dump(topic_data, f, ensure_ascii=False, indent=2)

    return topic_path


def run(config: dict, output_dir: Path) -> Path:
    """주제 선별 에이전트 실행"""
    print("\n🔍 에이전트 1: 주제 선별")
    print("=" * 50)

    print("  웹에서 트렌드 검색 중...")
    search_results = search_trends(config)
    print(f"  검색 결과 {len(search_results)}건 수집")

    topic_path = generate_topic(config, search_results, output_dir)

    with open(topic_path, "r", encoding="utf-8") as f:
        topic = json.load(f)
    print(f"\n  ✅ 주제: {topic['topic']}")
    print(f"  📝 카드 {len(topic['cards'])}장 구성")
    print(f"  💾 저장: {topic_path}")

    return topic_path
