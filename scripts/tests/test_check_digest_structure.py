import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
import check_digest_structure as cds
from check_digest_structure import check_post

_GOOD = """---
title: x
---
## 1. 보안 뉴스
### 1.1 항목
#### 기술적 배경
## 2. AI/ML 뉴스
## 실무 체크리스트
### P0 (즉시)
"""

# A clean post: global checklist with P0 checkboxes AFTER '## 실무 체크리스트',
# and a low-severity item's prose advisory (`- `, no `[ ]`) which is KEPT.
_GOOD = _GOOD.replace(
    "#### 기술적 배경\n",
    "#### 기술적 배경\n#### 권장 조치\n- 관련 시스템 목록 확인\n- 벤더 권고 확인\n",
).replace("### P0 (즉시)\n", "### P0 (즉시)\n- [ ] 긴급 패치 확인\n")

_BAD_H1 = _GOOD.replace("#### 기술적 배경", "# DevSecOps 관점 분석")
_BAD_NUM = _GOOD.replace("## 2. AI/ML 뉴스", "## 1. 기술적 배경")
# per-item CHECKBOX checklist injected into the item body (BEFORE the global checklist)
_BAD_DUP_CL = _GOOD.replace(
    "## 2. AI/ML 뉴스",
    "#### 대응 체크리스트\n- [ ] 패치\n- [ ] 모니터링\n## 2. AI/ML 뉴스",
)


def _write(txt):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(txt); f.close(); return f.name


def test_clean_post_has_no_violations():
    # prose `- ` advisory under '#### 권장 조치' is allowed; only checkbox
    # per-item checklists are the defect.
    assert check_post(_write(_GOOD)) == []


def test_flags_body_h1():
    assert any("H1" in v for v in check_post(_write(_BAD_H1)))


def test_flags_numbering_collision():
    assert any("numbering" in v.lower() for v in check_post(_write(_BAD_NUM)))


def test_flags_per_item_checkbox_checklist():
    assert any("checklist" in v.lower() or "체크리스트" in v
               for v in check_post(_write(_BAD_DUP_CL)))


def test_does_not_flag_prose_advisory():
    # '#### 권장 조치' followed by prose `- ` bullets (no `[ ]`) is kept.
    prose = _GOOD  # already contains a prose 권장 조치 block
    assert check_post(_write(prose)) == []


# A fenced code EXAMPLE block whose contents look like violations
# ('## 5. ...' numbering, '- [ ]' checkbox, '대응 체크리스트' heading) must be
# ignored by ALL checks, not just the H1 check. Outside the fence, the post
# has a single valid '## 실무 체크리스트' and no numbered headings at all
# (so the numbering check has nothing to flag) — i.e. the ONLY occurrences
# of these patterns anywhere in the body live inside the fence.
_GOOD_WITH_CODE_FENCE = """---
title: x
---
## 소개

다음은 예시 포맷입니다.

```markdown
## 5. 예시 섹션
- [ ] 예시 체크박스
#### 대응 체크리스트
```

본문 설명이 이어집니다.

## 실무 체크리스트
### P0 (즉시)
- [ ] 긴급 패치 확인
"""


def test_ignores_violations_inside_fenced_code_block():
    assert check_post(_write(_GOOD_WITH_CODE_FENCE)) == []


# ---------------------------------------------------------------------------
# CLI mode plumbing: digest-filename filter + --all exit code (Task A, PR
# follow-up). Every mode must filter to filenames containing "Weekly_Digest"
# — non-digest posts have different structure and would false-positive on
# these checks, so they are always skipped, even when explicitly named.
# ---------------------------------------------------------------------------


def test_non_digest_post_skipped_even_if_malformed(tmp_path, monkeypatch):
    # Malformed content (body H1) but a filename that is NOT a digest post.
    non_digest = tmp_path / "2026-07-11-Some_Regular_Post.md"
    non_digest.write_text(_BAD_H1, encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["check_digest_structure.py", str(non_digest)])
    with pytest.raises(SystemExit) as exc_info:
        cds.main()
    # Explicit-path mode filtered the non-digest file out -> nothing to
    # check -> clean pass, regardless of its (malformed) content.
    assert exc_info.value.code == 0


def test_all_mode_temp_dir_one_clean_one_bad_exits_nonzero(tmp_path, monkeypatch):
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    (posts_dir / "2026-07-11-Tech_Security_Weekly_Digest_Clean.md").write_text(
        _GOOD, encoding="utf-8"
    )
    (posts_dir / "2026-07-12-Tech_Security_Weekly_Digest_Bad.md").write_text(
        _BAD_H1, encoding="utf-8"
    )

    monkeypatch.setattr(cds, "REPO", tmp_path)
    monkeypatch.setattr(cds, "POSTS_DIR", posts_dir)
    monkeypatch.setattr(sys, "argv", ["check_digest_structure.py", "--all"])

    with pytest.raises(SystemExit) as exc_info:
        cds.main()
    assert exc_info.value.code != 0
