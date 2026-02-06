#!/usr/bin/env python3
"""
품질 모니터링 대시보드 생성
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

SCORE_FILE = Path("_data/quality_scores.json")

def load_scores():
    if SCORE_FILE.exists():
        with open(SCORE_FILE, 'r') as f:
            return json.load(f)
    return {"scores": []}

def save_score(filepath: str, result: dict):
    data = load_scores()

    entry = {
        "date": datetime.now().isoformat(),
        "file": filepath,
        "score": result['total'],
        "breakdown": result['scores'],
        "lines": result['lines']
    }

    data["scores"].append(entry)

    SCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCORE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_summary():
    """GitHub Actions Summary 출력"""
    data = load_scores()
    if not data["scores"]:
        return

    recent = data["scores"][-10:]
    avg = sum(s["score"] for s in recent) / len(recent)

    print("\n## 📊 Quality Trend")
    print(f"Average Score (last 10): {avg:.1f}/100")
    print("\n| Date | File | Score |")
    print("|------|------|-------|")
    for entry in recent[-5:]:
        date = entry["date"][:10]
        print(f"| {date} | {entry['file'][:40]} | {entry['score']}/100 |")

if __name__ == '__main__':
    generate_summary()
