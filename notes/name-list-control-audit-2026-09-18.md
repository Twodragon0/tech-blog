# 이름 목록 기반 통제 전수 감사 (2026-09-18)

직전 두 감사가 물은 것과 이번이 물은 것:

| 감사 | 질문 | 대상 |
|---|---|---|
| [`ci-gate-audit-2026-08.md`](ci-gate-audit-2026-08.md) | 이 게이트가 한 번이라도 무언가를 막은 적이 있나 | CI 잡 |
| [`gate-constant-drift-audit-2026-09-16.md`](gate-constant-drift-audit-2026-09-16.md) | 게이트 안의 상수가 지금도 실제 대상 집합과 같은가 | **게이트** 상수 |
| 이번 | **이름으로 대상을 지정하는 통제의 그 이름이 아직 무언가와 일치하는가** | 게이트가 아닌 런타임 통제까지 |

## 계기 — A-H3 가 통합 시점부터 꺼져 있었다

`ops_health_orchestrator.check_github_actions` 의 자기-재실행 차단(2026-06-30 감사,
A-H3)은 워크플로 이름 리터럴 4개였다 — `Ops Multi Agent Loop`, `Ops Priority Loop`,
`Ultrawork Loop`, `AI Ops On Demand`. **4개 전부 현존 워크플로와 일치하지 않았다.**
넷이 `ops-orchestrator.yml` 하나(`name: Ops Orchestrator`)로 통합되며 목록이 갱신되지
않았다. `actions:write` 를 쥔 자율 재실행 연쇄 방지가 그 시점부터 무효였다. (#748 에서
`GITHUB_WORKFLOW` 런타임 유도 + 일치 단언으로 교체.)

**09-16 감사가 이것을 놓친 이유가 핵심이다.** 그 감사의 대상 목록은 "게이트"였고 A-H3 는
게이트가 아니라 런타임 통제다. 즉 **감사의 대상 목록 자체가, 감사 대상과 똑같은 방식으로
불완전했다.** 범위 선언도 이름 목록이고, 이름 목록은 썩는다.

## 방법

1. `scripts/**/*.py` 전체를 `ast.parse` — 정규식은 이 저장소에서 같은 일에 이미 틀렸다
   (`TARGET_SVGS` 를 18로 읽었고 실제는 32).
2. 문자열 리터럴만으로 된 `set`/`frozenset`/`list`/`tuple`/`dict`-keys 를 수집 →
   **모듈 레벨 298개**.
3. 그중 **외부 식별자를 가리키는** 것만 추림 (경로 / 테스트 함수명 / 시크릿명 /
   Title Case 워크플로·스텝 이름, 항목의 60% 이상이 해당 형태) → **42개**.
4. **함수 내부까지 재수집** → 9개. 이 단계가 필수다 — A-H3 의 `self_workflows` 는
   함수 안에 있었으므로 모듈 레벨 스캔만으로는 **못 찾았을 것**이다.
5. YAML·API 쪽: `workflow_run` 의 `workflows:`, `needs:` 잡 참조, 브랜치 보호
   required checks.

## 결과 — 음성. A-H3 에 형제는 없다

| 검사 대상 | 결과 |
|---|---|
| `test_ci_jekyll_soft_gate_guard.VALIDATION_STEPS` (8) / `REPORTING_STEPS` (2) | 건강 — `jekyll.yml` 실제 스텝 `name:` 과 10/10 일치 |
| `test_excerpt_quality_guard_integrity.REQUIRED_TESTS` (5) | 건강 — `test_excerpt_quality.py` 에 5/5 정의됨 |
| `test_ci_visual_baseline_verify_guard.families` (4 생성기 경로) | 건강 — 4/4 실존. `test_target_svgs_all_exist` 도 이미 보유 |
| `check_runtime_env_contract.REQUIRED`/`OPTIONAL`/`PLATFORM` (16) | 건강 — 16/16 `api/` 에서 참조됨 |
| `test_ci_secret_absence_guard.FAIL_CLOSED`(5)/`NEVER_CONFIGURED`(2)/`RETIRED_SOCIAL_SECRETS`(8) | 건강 |
| `test_ci_svg_lint_schedule_guard.CORPUS_WIDE_GATES` (4) | 건강 |
| `svg_visual_baseline.TARGET_SVGS` (32) | 건강 (09-16 과 동일) |
| `test_stats_consistency_corpus_ratchet.GRANDFATHERED` (23) | 건강 — 23/23 포스트 실존 |
| `test_l20_hero_visual.L20_MARCH_FILENAMES` (15) | 건강 |
| `test_svg_size_gate.inline_diagrams` (7) | 건강 — **부재 시 실패를 이미 단언 중** |
| `add_toc_field.MISSING_TOC_FILES` (13), `reduce_svg_text_nodes.REMOVAL_TARGETS` (7), `check_font_drift.GENERATOR_FILES` (2), `check_secret_contract._SELF_REFERENCES` (2), `test_api_key_not_in_url._EXEMPT` (3) | 건강 |
| `workflow_run` 의 `workflows:` | 1건(`indexnow-ping.yml` → `Deploy Jekyll to GitHub Pages`), 일치 |
| `needs:` 잡 참조 | 전건 일치 |
| 브랜치 보호 required checks | **0개 설정** — 낡은 이름은 없지만 그 자체가 별개 관찰 |

### 어긋난 것 2건 — 둘 다 수명이 끝난 일회성 마이그레이션 도구

| 상수 | 부재 | 성격 |
|---|---|---|
| `extract_cfg_to_yaml.DEFAULT_L22_SCRIPTS` | **5/5** | 커밋 `79b003ee`("unify digest-cover renderer — extract 5 scripts to YAML")가 마이그레이션을 완료하며 입력 5개를 삭제. 결과 스펙 33개가 `_data/digest_covers/`. 어떤 워크플로·훅도 이 도구를 부르지 않는다. `--all-l22-scripts` 는 첫 대상에서 `return 2` |
| `regenerate_generator_digest_svgs.TARGET_IMAGES` | **2/41** | `notes/per-pr/` 에서만 참조되는 일회성 재생성 도구. `--list` 는 계속 출력하고 재생성은 건너뛴다 |

보안 통제는 아니다. 사용자 판단으로 **도구는 남기고** 가드의 `KNOWN_DEAD` 에 퇴장 조건과
함께 기록했다.

## 이 감사에서 내가 틀린 것 — 추출기를 먼저 의심해야 했다

1차 실행이 부재 5건을 보고했는데 그중 **4건이 제 추출기 오류**였다. 각 상수가 어느
디렉토리를 기준으로 쓰였는지 제가 임의로 정했다.

| 상수 | 1차 판정 | 실제 |
|---|---|---|
| `test_index_scoring.INDEX_FILES` | 3/3 부재 | `_posts/` 기준 — 3/3 실존 |
| `test_news_card_patterns.CONSUMERS` | 4/4 부재 | `scripts/` 기준 — 4/4 실존 |
| `test_optional_narrowing_guards._SPEC_LOADER_FILES` | 5/5 부재 | `scripts/tests/` 기준 — 5/5 실존 |
| `test_l22_digest_svg.cases` | 부재 다수 | 파일명이 아니라 **제목 문자열** (정규식 입력) |

**신호는 "100% 균일한 부재"였다.** 이 저장소의
[`regex_group_offset_trap_twice`](../CLAUDE.md) 교훈과 같다 — 결과가 전부 0%거나 전부
100%면 데이터가 아니라 추출기를 의심한다. 그래서 가드는 기준 디렉토리를 **추측하지 않고**
`BASES` 중 하나에서라도 해석되면 통과시킨다.

## 기계화 — `test_path_list_constants_resolve.py`

음성 결과는 썩는다. 감사의 기계적인 절반만 가드로 남겼다: `scripts/**/*.py` 의 **모듈
레벨** 경로형 목록이 전부 실제 파일로 해석되는지. `DEFAULT_L22_SCRIPTS` 를 잡았을 것이다.

**배선 전에 돌려서 출력을 읽었고, 그게 오탐 3종을 잡았다.** 제외 없이 돌리면 6개 목록을
보고하는데 4개가 거짓이었다 — glob(`_posts/*.md`, `scripts/**/*.py`),
URL(`https://…json-en.html`), Liquid 조각(`{% include news-card.html`). 전부 "경로가
아닌 것"이므로 화이트리스트가 아니라 판정식(`_NOT_A_PATH`)으로 걸렀고, 그 네 문자열을
테스트로 고정했다.

범위를 **모듈 레벨로 제한한 것은 의도적이다.** 함수 내부 목록은 대부분 합성 테스트
픽스처(`a.yml`, `2026-02-01-Zeta.md`)이고 그것들은 **디스크에 없어야 정상**이다. 모듈
레벨로 자르면 화이트리스트 없이 구조적으로 제외된다 — 그리고 화이트리스트가 바로 썩는
그것이다.

**이 가드는 A-H3 자체를 잡지 못한다.** 워크플로 이름은 경로가 아니다. 그건
`test_ops_health_orchestrator.test_self_rerun_exclusions_match_live_workflows` 가
고정한다. 일반화되는 것은 정규식이 아니라 규칙이다 —
**대상을 이름으로 지정하는 통제에는 "그 이름이 아직 무언가와 일치하는가"를 물어야 한다.**

뮤테이션 프로브 5종, 대조군 포함: 목록에 죽은 경로 추가 / 면제 목록 무력화 / 추출기
무력화 / 비-경로 제외 제거 / 면제 이유 축약 — 전부 FAIL, 대조군 PASS.

## 다시 쓸 때

```bash
# 모듈 레벨 + 함수 내부 문자열 목록 전수 (ast, 정규식 금지)
python3 -m pytest scripts/tests/test_path_list_constants_resolve.py -q

# 워크플로 이름·스텝 이름 대조
python3 -c "
import pathlib, yaml
for p in sorted(pathlib.Path('.github/workflows').glob('*.y*ml')):
    s = yaml.safe_load(p.read_text())
    if isinstance(s, dict) and s.get('name'): print(s['name'], '->', p.name)
"
```

경로형이 아닌 이름 목록(워크플로명·스텝명·체크명·시크릿명)은 상수가 새로 생길 때마다
**그 목록 옆에 일치 단언을 같이 쓴다.** 범위 목록을 하나 더 만들지 말 것 — 09-16 감사의
"게이트" 목록이 A-H3 를 빼먹은 것이 그 방식의 실패 사례다.
