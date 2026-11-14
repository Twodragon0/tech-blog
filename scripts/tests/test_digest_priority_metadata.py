"""Publication metadata follows rendered news, without promoting event ads."""

from datetime import datetime, timezone

import yaml

from scripts.news import content_generator as generator


def _item(title: str, category: str = "security") -> dict:
    return {
        "title": title,
        "title_ko": title,
        "summary": "출처에 기반한 보안 운영 소식입니다.",
        "summary_ko": "출처에 기반한 보안 운영 소식입니다.",
        "source": "fixture",
        "source_name": "Fixture Source",
        "category": category,
        "url": "https://example.com/fixture",
    }


def _generate(monkeypatch, items: list[dict], categorized: dict) -> tuple[dict, str]:
    monkeypatch.setattr(
        generator,
        "generate_news_section",
        lambda item, number, **kwargs: f"### {number} {item['title']}\n\n",
    )
    result = generator.generate_post_content(
        items, categorized, datetime(2026, 11, 13, 9, tzinfo=timezone.utc)
    )
    _, raw, body = result.split("---", 2)
    return yaml.safe_load(raw), body


def test_promotional_story_is_retained_but_not_a_priority(monkeypatch) -> None:
    promo = _item("웨비나: Identity Blind Spots가 어떻게 SOC를 위험에 빠뜨리는지")
    incident = _item("Xloader 피싱 메일 주의")
    cloud = _item("Chrome Enterprise 의료 기술 보호", "cloud")
    front, body = _generate(
        monkeypatch,
        [promo, incident, cloud],
        {"security": [promo, incident], "cloud": [cloud]},
    )
    highlights = front["summary_card"]["highlights"]
    assert [entry["title"] for entry in highlights] == [
        incident["title"],
        cloud["title"],
    ]
    table = body.split("### 이번 주 하이라이트", 1)[1].split("---", 1)[0]
    assert promo["title"] not in table
    assert promo["title"] in body
    assert "Identity" not in front["image_alt"]
    assert "Identity" not in front["description"]


def test_all_promotions_have_neutral_highlights_without_dropping_body(
    monkeypatch,
) -> None:
    promo = _item("Webinar: Identity Blind Spots")
    front, body = _generate(monkeypatch, [promo], {"security": [promo]})
    assert front["summary_card"]["highlights"] == [
        {"source": "", "title": "오늘의 주요 뉴스를 확인하세요"}
    ]
    table = body.split("### 이번 주 하이라이트", 1)[1].split("---", 1)[0]
    assert "Webinar" not in table
    assert promo["title"] in body


def test_metadata_does_not_name_unrendered_fourth_story(monkeypatch) -> None:
    shown = [
        _item("Xloader 피싱 메일 주의"),
        _item("Linux 커널 보안 업데이트"),
        _item("Chrome 보호 개선"),
    ]
    hidden = _item("Critical BYOVD Ransomware Zero-Day Attack")
    front, body = _generate(
        monkeypatch, shown + [hidden], {"security": shown + [hidden]}
    )
    assert f"### 1.4 {hidden['title']}" not in body
    assert "BYOVD" not in front["title"]
    assert "BYOVD" not in front["image_alt"]
    assert "BYOVD" not in front["description"]
