"""Risk scorecard, CVE extraction, and MITRE mapping functions."""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional


def generate_risk_scorecard(
    news_items: List[Dict], report_date: Optional[datetime] = None
) -> str:
    """Generate risk scorecard ASCII art."""
    # Import here to avoid circular imports
    from scripts.news.content_generator import _determine_severity

    report_date = report_date or datetime.now(timezone.utc)
    scorecard = f"""```
+================================================================+
|          {report_date.strftime("%Y-%m-%d")} 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
"""

    critical_news = [
        n for n in news_items if _determine_severity(n) in ["Critical", "High"]
    ]

    for news in critical_news[:5]:
        title = news.get("title", "")[:30]
        severity = _determine_severity(news)
        score = 9 if severity == "Critical" else 7
        bars = "\u2588" * score + "\u2591" * (10 - score)
        priority = "[\uc989\uc2dc]" if severity == "Critical" else "[7\uc77c \uc774\ub0b4]"

        scorecard += f"|  {title:<24} {bars}  {score}/10   {priority:<15}     |\n"

    if critical_news:
        avg_score = sum(
            9 if _determine_severity(n) == "Critical" else 7 for n in critical_news
        ) / len(critical_news)
    else:
        avg_score = 5

    level = "HIGH" if avg_score >= 7 else "MEDIUM" if avg_score >= 5 else "LOW"
    bars = "\u2588" * int(avg_score) + "\u2591" * (10 - int(avg_score))

    scorecard += f"""|  ----------------------------------------------------------   |
|  종합 위험 수준: {bars} {level} ({avg_score:.1f}/10)                         |
|                                                                |
+================================================================+
```
"""
    return scorecard


def extract_cve_id(title: str, summary: str) -> Optional[str]:
    """Extract CVE ID from title or summary."""
    pattern = r"CVE-\d{4}-\d{4,7}"
    for text in [title, summary]:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def generate_mitre_mapping(cve_id: str, item: Dict) -> str:
    """Generate MITRE ATT&CK mapping."""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()

    techniques = []

    if any(kw in text for kw in ["rce", "remote code execution", "exploit"]):
        techniques.append("T1203  # Exploitation for Client Execution")

    if any(kw in text for kw in ["authentication", "credential", "bypass"]):
        techniques.append("T1078  # Valid Accounts")

    if any(kw in text for kw in ["injection", "sql", "xss"]):
        techniques.append("T1190  # Exploit Public-Facing Application")

    if any(kw in text for kw in ["privilege", "\uad8c\ud55c \uc0c1\uc2b9"]):
        techniques.append("T1068  # Exploitation for Privilege Escalation")

    if not techniques:
        techniques.append("T1190  # Exploit Public-Facing Application")

    techniques_yaml = "\n    - ".join(techniques)

    return f"""
#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - {techniques_yaml}
```
"""
