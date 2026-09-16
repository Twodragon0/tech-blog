# 게이트 상수 드리프트 감사 (2026-09-16)

앞선 감사([`ci-gate-audit-2026-08.md`](ci-gate-audit-2026-08.md))가 **"이 게이트가 한
번이라도 무언가를 막은 적이 있나"** 를 물었다면, 이번은 한 단계 안쪽을 묻는다:

> **게이트 안에 박혀 있는 상수가 지금도 실제 대상 집합과 같은가?**

이 질문이 나온 계기는 같은 세션에서 나온 네 건이다. 전부 "선언이 실제를 가리키지 않는데
아무것도 반대하지 않은" 모양이었다.

| 사례 | 어긋난 것 | PR |
|---|---|---|
| ruff | 워크플로 핀 `ruff==0.15.8` vs 선언 `ruff>=0.16.6` | #732 / #734 |
| TTS | 마커 `python_version < "3.14"` vs 실제 `Requires-Python <3.12` | #736 |
| `TOP_SECTION_RE` | 화이트리스트 vs 레거시 코퍼스의 실제 섹션명 | #737 |
| requirements | 선언 vs 실제 import (죽은 의존성 3건) | #739 / #740 |

## 감사 결과 — 게이트는 대체로 건강했다

| 검사 대상 | 상수 | 결과 |
|---|---|---|
| `svg_visual_baseline.TARGET_SVGS` | 32개 경로 | 건강 — 32/32 실존 |
| `reports/l20-visual-regression/run.py` | 날짜 30개 (01-23~03-31) + `REFERENCE_NAME` | 건강 — 30/30 포스트 실존, 참조 SVG 실존 |
| `pyproject.toml` coverage `include` | 9패턴 | 건강 — 9/9 매치 |
| 워크플로 `paths` 트리거 | verify/refresh/regression/svg-lint | **1건 어긋남** (아래) |
| `check_card_title_language.ENGLISH_TITLE_ALLOW` | 3개 | 건강 — 3/3 각 1회 발동, 카드 2582개 중 0 위반 |
| `check_actionlint_ratchet` | baseline | 건강 — 현재 11 = baseline 11 |
| `check_asset_hint_version` | 버전 상수 | 건강 — 27 템플릿 0 위반 |

## 유일한 어긋남 — L25 커버 시스템은 프로덕션 인스턴스가 0이다

- `_data/l25_covers/` 에 `.gitkeep` 뿐 (digest 33 / rollup 7 / l20 5 대비)
- L25 마커 `profile: high-quality-cover (2025 upgraded L25-single)` 를 가진 SVG **0건**
- `python3 scripts/upgrade_l25_cover.py --all` → `no specs to process`, exit 0
- `svg-lint.yml` 의 트리거 `_data/l25_covers/**.yml` 은 매치 0건 (54개 path 중 유일)

**단, 이것은 "미검증 휴면 게이트"가 아니다.** `scripts/tests/test_svg_l25_single.py` 가
합성 입력으로 이 경로를 검증한다. 그래서
[`dormant_gate_never_been_right`](../CLAUDE.md) 부류와는 다르다 — "한 번도 돌아본 적
없는" 것이 아니라 **"테스트된 채 실물이 없는"** 상태다.

**지우지 않기로 했다.** 단일 주제 커버가 필요해지면 다시 지어야 하고, 이 저장소는 게이트
항목 삭제가 곧 면제 발급이라는 것을 이미 비싸게 배웠다. 대신 CLAUDE.md 와 cover-system
스킬이 L25 를 현역 5개 시스템 중 하나로 서술하는 것과 실측이 어긋난다는 사실을 여기 남긴다.

부수로 `TARGET_SVGS` 안의 `# Jan 23-27 weekly digests (short filenames only)` 주석 아래에
항목이 0개다 — 없는 그룹을 설명하는 주석.

## 이번 감사의 진짜 소득 — 틀린 것은 게이트가 아니라 내 추출기였다

임시 추출기가 **한 세션에 5번** 틀렸다. 전부 "게이트가 고장났다"로 보고할 뻔한 것들이다.

| # | 추출기 | 오답 | 실제 | 원인 |
|---|---|---|---|---|
| 1 | `TARGET_SVGS` 정규식 | 18개 | **32개** (AST) | 비탐욕 `.*?` 가 조기 종료 |
| 2 | 워크플로 `paths` 셸 추출 | 전부 "매치 0건" | 전부 매치 | `- "` 와 따옴표를 경로에 남김 |
| 3 | allow-list 정규식 | 주석 문자열을 항목으로 | 3개 | `{...}` 블록 안의 설명 문자열까지 수집 |
| 4 | `tweepy` 정적 import grep | 0건 = 죽음 | **살아 있음** | `importlib.import_module("tweepy")` |
| 5 | `## N.` 상위 20종 출력 | `기술 뉴스` 없음 | 1건 실재 | 롱테일을 잘라 읽음 |

다섯 건 모두 **"결과가 균일하거나 문서와 다르면 데이터가 아니라 추출기를 의심"** 으로
잡혔다. 2번은 100% 0건이라 즉시 티가 났고, 1번과 5번은 문서/기존 서술과 숫자가 안 맞아서
걸렸다. 4번은 가장 위험했다 — 0건이 그럴듯했고, 제거했다면 SNS 공유가 조용히 죽었다.
그걸 막은 건 grep 이 아니라 **기존 테스트**
(`test_ci_secret_absence_guard.py::test_share_sns_script_is_kept_for_manual_use`)였다.

### 실천 규칙

- **구조를 가진 것은 정규식이 아니라 파서로 읽는다.** 파이썬 리터럴은 `ast`, YAML 은
  `yaml.safe_load`. 1·2·3번이 전부 이걸로 예방됐다.
- **0건과 균일한 결과는 결과가 아니라 알람이다.** 대조군(반드시 걸려야 하는 입력)을 하나
  넣고 그게 걸리는지 먼저 본다.
- **"사용되지 않음"을 주장하기 전에 동적 경로를 본다.** `importlib.import_module`,
  `__import__`, 문자열 참조, CLI 바이너리. 정적 import grep 은 이 중 어느 것도 못 본다.
- **내가 세운 수가 기존 문서와 다르면, 문서가 아니라 내 수를 먼저 의심한다.**

이건 이미 [[regex_group_offset_trap_twice]] · [[heuristic_right_next_door_is_wrong]] ·
[[mutation_probe_needs_control]] 로 기록된 교훈이다. 한 세션에 다섯 번 재현됐다는 것은
**경고문으로는 안 막힌다**는 뜻이고, 그래서 이 문서의 결론도 "조심하자"가 아니라 위의
네 줄짜리 절차다.

## 재현

아래 두 스니펫은 **작성 후 그대로 실행해 출력을 확인했다.** 첫 판은 `AttributeError` 로
죽었다 — 여섯 번째 추출기 오류이고, 돌려봤기 때문에만 잡혔다. 재현 블록을 적을 때는
붙여넣고 돌려볼 것.

```bash
# TARGET_SVGS — 정규식 말고 ast 로 읽을 것 (정규식은 18개로 읽었다; 실제 32)
python3 -c "
import ast, pathlib
tree = ast.parse(pathlib.Path('scripts/svg_visual_baseline.py').read_text())
node = next(n for n in tree.body if isinstance(n, ast.Assign)
            and any(getattr(t, 'id', None) == 'TARGET_SVGS' for t in n.targets))
paths = [e.value for e in node.value.elts]
print(len(paths), 'declared;',
      sum(not pathlib.Path(p).exists() for p in paths), 'missing')"

# 워크플로 paths 트리거 — 셸로 자르지 말고 yaml 로 읽을 것
python3 -c "
import glob, yaml, pathlib
d = yaml.safe_load(pathlib.Path('.github/workflows/svg-lint.yml').read_text())
on = d.get(True) or d.get('on')
for p in on['pull_request']['paths']:
    n = len(glob.glob(p.replace('**.svg', '**/*.svg'), recursive=True))
    print(f'{n:6d}  {p}')" | sort -n | head -3

python3 scripts/upgrade_l25_cover.py --all                # -> no specs to process
python3 scripts/check_card_title_language.py --all        # -> 3 allow-listed, 0 violations
python3 scripts/check_actionlint_ratchet.py               # -> 11 findings now, 11 in baseline
python3 scripts/check_asset_hint_version.py               # -> 27 template(s), 0 violations
grep -rlF 'profile: high-quality-cover (2025 upgraded L25-single)' assets/images/*.svg | wc -l
```
