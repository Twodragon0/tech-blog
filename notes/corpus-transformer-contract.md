# 코퍼스 변환기 공통 계약

**Status:** 초판 2026-08-07 — `_posts/` 일괄 변환기 5종에서 귀납한 계약
**대상:** `_posts/` 아래 수십~수백 개 마크다운을 프로그램으로 일괄 수정하는 Python 스크립트
**관련:** `notes/digest-proper-noun-policy.md`(래칫 절), memory `corpus_transformer_protected_regions`,
`restore_digest_fence_protection`, `digest_structure_diff_ratchet`, `feedback_cover_empirical_first`

---

## 1. 왜 이 문서가 필요한가

세 번의 회귀가 전부 "변환기 자체는 옳았는데 **어디를 건드리면 안 되는지**를 몰랐다"에서 나왔다.

| 사고 | 무슨 일이 있었나 | PR |
|------|------------------|-----|
| 커버 이미지 3건 손상 | `linkify_bare_urls`의 줄 단위 `{%` 가드가 **다중 라인 Liquid 태그의 속성 줄**을 못 봤다. `image="…/https://s3…"` 처럼 URL 안에 중첩된 URL이 링크로 재작성돼 커버가 깨졌다 | #509 |
| 코드 펜스 내부 주석 훼손 | `restore_digest_structure` R1이 bash/yaml 펜스 안의 `# 예시` 를 `#### 예시` 로 강등. **토큰 multiset 무손실 검사는 마커만 바뀐 변경을 통과시켜** 결함을 은폐했고, 결국 사람이 손으로 찾았다 (2026-03-11, 03-27) | #500 |
| 래칫 오탐으로 개선 차단 | `check_digest_structure --ratchet`이 위반 **메시지 문자열**을 비교했는데, 메시지가 본문 텍스트를 embed한다. 순수 `안드로이드→Android` 치환이 결함 집합 6→6 불변인데도 "+1 new"로 차단됐다 (대상 포스트 2026-05-05, 실측 2026-08-04) | #492 |

공통점: 셋 다 **합성 데이터로는 절대 재현되지 않는다**. 실제 코퍼스를 대상으로 RUN 한 뒤에야 드러났다.

---

## 2. 5종 비교표

> 이 5종은 레포의 **전수가 아니라 귀납 표본**이다. `_posts/`에 쓰는 스크립트는 더 있다
> (`backfill_digest_structure.py`, `backfill_digest_commentary.py`, `backfill_digest_titles.py`,
> `check_digest_proper_nouns.py --fix` 등). 아래 `N/5` 비율은 이 표본 안에서의 준수율이지
> 레포 전체 커버리지가 아니다.

| | 구조 복원 | 참고자료 | 링크화 | 마침표 | 되감기 |
|---|---|---|---|---|---|
| **스크립트** | `scripts/restore_digest_structure.py` | `scripts/enrich_digest_references.py` | `scripts/linkify_bare_urls.py` | `scripts/backfill_card_summary_period.py` | `scripts/rewind_truncated_summaries.py` |
| **PR** | #496 (+ #497~#500 배치, #504 불변식 강화) | #507 파일럿 5 → #508 확산 153 | #509 (+ #510 게이트) | #512 (생성기 수정은 #511) | #513 (머지 커밋 `6e657a5f`) |
| **대상 선별** | `_is_digest_post` (파일명 `Weekly_Digest`) + `--posts-glob`/명시 경로 | 동일 + `## 참고 자료` 섹션 존재 | 모든 `_posts/*.md`, digest 한정 아님. **선별 가드 없음** — `_POST_PATH_RE`는 `--staged` 경로 필터일 뿐이고(`:104,125`), `--all`은 glob(`:150`), 명시 `paths`는 무필터 | `_is_digest_post` + `summary=` 값 길이 < 195 | `_is_digest_post` + `summary=` 값 길이 ≥ 195 |
| **보호 영역** | front matter(`_split_front_matter`), 코드 펜스(R0 `_fence_flags`), item-region 밖 전체, 전역 체크리스트의 중첩 불릿 | `## 참고 자료` 섹션 **밖 전부** (구조적으로 손대지 않음) | front matter, 코드 펜스, 인라인 코드(stash), **다중 라인 Liquid 블록**, 기존 md 링크/HTML 속성(`(?<![\(\[<"=])`) | `{% include news-card.html %}` 밖 전부, 카드 내 `summary=` 외 속성 ⚠️**이 표기를 복사하지 말 것 — C11 참조** | 동일 ⚠️ |
| **변경 적용** | 6개 룰(R5→R1→R2→R3→R6→R4)을 순서 고정 적용. 마커만 변환, 텍스트 무생성 | 표에 `용도` 열 추가(canonical 매핑 deny-by-default) + 본문 카드가 실제 인용한 출처 행 추가. LLM/네트워크 없음 | 줄 단위로 bare URL을 `[label](url)` 로 래핑. label은 코퍼스 관행(host−`www.` + 짧은 path) | 생성기의 `_restore_sentence_period` 를 **import** 해서 마침표 1개 추가 | 마지막 `다.` 까지 되감기 → 결과는 항상 원문의 접두사 |
| **무손실 검증(런타임)** | `lossless_tokens` 컨텍스트 인지 multiset + **별도 정의**된 `_audit_fence_flags`, 불일치 시 ABORT | `## 참고 자료` **앞** 구간 바이트 동일 아니면 ABORT (섹션 뒤는 구조상 불변, 런타임 미검사) | **없음** — 런타임 ABORT 조항 없음 | `_violates_narrow_diff`: 정규화 동등 + **길이 감소 금지**(마침표 '제거'까지 탐지) | `_violates_shrink_only`: 파일이 커지면 ABORT |
| **실행 모드** | `paths` / `--posts-glob` / `--dry-run` / `--limit` | 동일 | `paths` / `--posts-glob` / `--dry-run` / `--check` / `--staged` / `--all` | `paths` / `--posts-glob` / `--dry-run` | `paths` / `--posts-glob` / `--dry-run` |
| **게이트 배선** | `check_digest_structure.py --ratchet` (pre-commit, svg-lint CI `--changed BASE`), `check_digest_checklist_heading.py`(pre-commit 9d, CI `--all`), blogwatcher 발행 시 자가치유 | **없음** | `--check --staged` (pre-commit 12) + `--check --all` (svg-lint CI) + 배선 회귀 테스트 2건 | **없음** (재발 방지는 생성기 `_restore_sentence_period`) | **없음** (재발 방지는 #506 생성기 `_truncate_korean_sentence`) |
| **테스트** | `test_restore_digest_structure.py` (48건, 펜스 6룰 개별 + 순서 의존 + 코퍼스 전수 무손실) | `test_enrich_digest_references.py` (15건) | `test_linkify_bare_urls.py` (26건, 코퍼스 clean + 배선 가드) | `test_backfill_card_summary_period.py` (15건) | `test_rewind_truncated_summaries.py` (13건) |

> 되감기 열은 초안 작성 시점에 `fix/rewind-truncated-summaries` 브랜치에서 읽어 정리했고,
> 이후 #513이 머지되어 `scripts/rewind_truncated_summaries.py` 와 그 테스트가 main 계보에 들어왔다.
> 확인: `git cat-file -e origin/main:scripts/rewind_truncated_summaries.py` → 존재.

---

## 3. 필수 계약 (새 변환기 체크리스트)

### C1. 대상 선별은 파일명이 아니라 **판별 함수**로 (5/5 준수)

- digest 전용이면 `_is_digest_post(path)` 를 재사용한다. 5종 중 4종이 동일 구현을 각자 갖고 있다
  (`"Weekly_Digest" in path.name`). 링크화만 전체 포스트가 대상이라 예외.
- 선별에서 걸러진 파일은 **조용히 스킵**하고 종료 코드 0. 테스트로 고정한다
  테스트 이름은 제각각이다 — `test_non_digest_is_skipped`(마침표·되감기),
  `test_apply_writes_and_skips_non_digest`(구조 복원),
  `test_non_digest_post_is_skipped_by_the_cli`(참고자료), 링크화는 해당 없음.

### C2. 보호 영역을 코드로 선언한다 (5/5, 범위는 제각각)

최소한 다음을 **명시적으로** 건너뛰어야 한다. "정규식이 어차피 안 맞을 것"은 계약이 아니다.

| 보호 영역 | 반드시 필요한 경우 |
|-----------|--------------------|
| YAML front matter | 본문 줄 단위 변환기 전부 |
| 코드 펜스 (열림/닫힘 판정은 **`strip()` 한 라인**으로 — `2026-02-08`은 `  ``` `로 닫는다) | 마커/헤딩/불릿을 건드리는 전부 |
| 인라인 코드 `` `…` `` | 텍스트 치환형 |
| **다중 라인 Liquid 태그** (`{% include … %}` 가 여러 줄) | URL·텍스트를 건드리는 전부 |
| URL / CVE 식별자 / 인용된 원문 제목 | 고유명사·표기 치환형 (`check_digest_proper_nouns` 마스킹 참조) |

### C3. 좁은 diff — 전체 재작성 금지 (5/5)

- 5종 모두 `transform(text) -> text` 순수 함수이고, `new == original` 이면 **파일에 쓰지 않는다**.
- 무관한 재포맷·재정렬·공백 정리를 곁들이지 않는다. 구조 복원기조차 "마커만 바꾸고 단어는 그대로"다.

### C4. 런타임 무손실 계약 + ABORT (4/5 — 링크화만 미보유)

변환기마다 "이 변환이 **절대 할 수 없는 일**"을 한 줄로 정의하고, 쓰기 **전에** 파일 단위로 강제한다.

| 변환기 | 런타임 계약 |
|--------|-------------|
| 구조 복원 | 컨텍스트 인지 토큰 multiset 동일 |
| 참고자료 | 섹션 앞 구간 바이트 동일 |
| 마침표 | 붙는 변경은 `.` 하나뿐 + 길이가 줄면 안 됨 |
| 되감기 | 파일은 줄어들기만 함 |
| 링크화 | **없음** |

위반 시 그 파일만 건너뛰는 게 아니라 **프로세스를 exit 1로 중단**한다 (5종 중 4종 동일).

> **토큰 검사만으로는 부족하다.** 평평한 "마커 다 지우고 나머지 세기"는 마커-블라인드라
> 펜스 내부 `# 예시` → `#### 예시` 를 통과시켰다(#500). `restore_digest_structure.lossless_tokens`
> 는 이를 (a) front matter 라인-verbatim, (b) 펜스 라인 라인-verbatim(마커 포함),
> (c) 펜스 밖은 마커 제거하되 숫자는 **헤딩 선두 `N.` 슬롯일 때만** 제거 — 로 나눠 해결했다(#504).

### C5. 감사 검출기는 룰 검출기와 **따로** 정의한다 (1/5 — 구조 복원만)

`restore_digest_structure.py:318` 의 `_audit_fence_flags` 는 `_fence_flags` 를 호출하지 않고 같은
로직을 다시 쓴다. 감사가 룰의 검출기를 재사용하면 **검출 자체가 회귀할 때 양쪽이 같이 움직여서**
불변식이 구조적으로 눈이 먼다. 두 정의는 `test_audit_fence_flags_agree_with_rule_flags` 가
코퍼스 전수로 lockstep 유지한다.

### C6. 게이트 범위는 `--staged` / `--changed`, **절대 `--all` 기본값 금지** (해당 2/2)

- 게이트가 있는 것은 링크화(`--check --staged`)와 구조(`--ratchet --staged/--changed`) 둘뿐이고,
  둘 다 좁은 범위다. 링크화 CI만 `--check --all` 인데 이건 **읽기 전용 검사**라 코퍼스를 쓰지 않는다.
- 쓰기 모드에 `--all` 기본값을 두면 레거시 코퍼스를 일괄 오염시킨다
  (`digest_structural_normalization`·`digest_native_sections_backfill` 교훈).
- 예외적으로 `check_digest_checklist_heading.py --all` 은 코퍼스가 이미 0 위반이라 래칫이 불필요하다.

### C7. 파일 단위 baseline 대신 **diff 래칫**, 비교 키는 위반 **kind** (해당 1/1)

- 레거시 결함이 있는 파일에서 *무관한* 개선까지 막히면 캠페인이 정지한다. `--ratchet` 은 base
  리비전(`--staged`→HEAD, `--changed`→merge-base)과 비교해 **신규 위반만** 실패시킨다.
- 비교는 **메시지 문자열이 아니라 `_kind()`** (`violation.split(": ", 1)[0]`). 메시지가 본문을
  embed하기 때문에 문자열 비교는 리워딩을 신규 위반으로 오탐한다(#492).
- 같은 kind의 *추가* 인스턴스(H1 2→3)는 카운트 비교로 계속 검출된다 — 은폐가 아니다.

### C8. 재발 방지는 생성기에, 백필은 별도 작업으로 (3/5에서 명시적으로 분리)

- #511 = 생성기 수정, #512 = 코퍼스 백필. #506 = 생성기 문장 경계 절단, 되감기 = 코퍼스 백필.
- 백필이 생성기 헬퍼를 **재구현하지 말고 import** 한다
  (`backfill_card_summary_period.py:31` → `scripts.news.content_generator._restore_sentence_period`).
  단일 진실 원천이라 코퍼스와 생성기가 어긋날 수 없다. `test_uses_the_generator_helper_as_the_single_source_of_truth` 가 고정.
- import가 불가능해 복사할 수밖에 없다면(구조 복원기의 `ITEM_HEADING_RE`/`TOP_SECTION_RE`)
  **드리프트 가드 테스트**를 붙인다 (`test_shared_regexes_have_not_drifted`).

### C9. `--dry-run` 필수, 기본은 쓰기 없음 (5/5)

5종 모두 `--dry-run` 이 있고 테스트로 고정돼 있다. 다만 **이름은 통일돼 있지 않다** —
4종은 `test_cli_dry_run_does_not_write`, 구조 복원기만 `test_dry_run_does_not_write`
(`test_restore_digest_structure.py:417`). 이름이 아니라 *존재*가 계약이다.

### C10. 멱등성 (5/5)

5종 모두 `test_transform_is_idempotent`. 재실행이 두 번째 변경을 만들면 계약 위반이다.

### C11. 대상 재현율 — 「다 찾았는가」도 계약이다 (0/5 — 전부 미보유)

C1~C10은 전부 **"어디를 건드리면 안 되는가"**(보호)만 다룬다. 그 반대편,
**"대상을 다 찾았는가"**(재현율)에 대한 계약이 없어서 같은 실수가 반복됐다.

`_posts/`의 뉴스 카드는 **include 2종 × whitespace control 2형태**로 존재한다.

```
{% include news-card.html            1771
{%- include news-card.html            282   ← \s 는 '-' 를 매칭하지 않는다
{% include news-spotlight-item.html    64   ← 어떤 스크립트도 참조하지 않음
                          실제 총계   2117
```

2026-08-07 실측 — 같은 레포 안에서 정규식이 갈린다.

| 스크립트 | 패턴 | 매칭 / 누락 |
|---|---|---|
| `check_posts.py:510` | `\{%-?\s*include` | 2053 / **0** ✅ |
| `cleanup_news_cards.py:107` | `\{%-?\s*include` | 2053 / **0** ✅ |
| `fix_malformed_liquid_includes.py:336` | `\{%-?\s*include` | ✅ |
| `rewind_truncated_summaries.py:34` | `\{%\s*include` | 1771 / **282** ❌ |
| `backfill_card_summary_period.py:42` | `\{%\s*include` | 1771 / **282** ❌ |
| `backfill_digest_titles.py:135` | 문자열 `.count()` | 1771 / **282** ❌ |

결과: **#512(마침표)와 #513(되감기)은 틀린 수정이 아니라 덜 한 수정이다.**
사각지대 346건에 마침표 누락 2건 · 절단 요약 14건이 그대로 남아 있다.
두 클래스 모두 게이트가 없어(§2 "게이트 배선" 행) 조용히 통과했다.

**계약:**
1. 대상 패턴은 include 종류와 whitespace control(`{%-` / `-%}`) 변형을 **전수 열거**한다.
   ```python
   _CARD_RE = re.compile(
       r"\{%-?\s*include\s+(?:news-card|news-spotlight-item)\.html.*?-?%\}", re.DOTALL)
   ```
2. **`대상 매칭 수 == 코퍼스 실제 인스턴스 수` 를 테스트로 고정한다.** 보호 영역 테스트만으로는
   조용한 누락을 절대 잡을 수 없다 — 누락된 카드는 diff에 나타나지 않기 때문이다.
3. 착수 전 include 종류별 건수를 출력해 **분모를 먼저 확정**한다(§5 Step 0).

---

## 4. 함정 카탈로그

### T1 — 줄 단위 `{%` 가드는 다중 라인 Liquid의 속성 줄을 못 본다

- **증상:** 커버 이미지 3건 손상. `image="…/https://s3…"` 가 마크다운 링크로 재작성됨.
- **원인:** Liquid 태그가 `{% include news-card.html` / 속성들 / `%}` 로 **여러 줄에 걸친다.**
  `"{%" in line` 로 판정하면 중간 속성 줄은 보호되지 않는다. 게다가 URL 안에 URL이 중첩돼
  `(?<![\(\[<"=])` 룩비하인드도 무력했다(선행 문자가 `=`나 `"`가 아니라 `/`).
- **회피:** `in_liquid` **상태 머신**을 둔다. `{%` 가 있고 `%}` 가 없으면 열림, `%}` 를 만나면 닫힘.
  `scripts/linkify_bare_urls.py:88-99`. 회귀 테스트: `test_multiline_liquid_include_is_untouched`,
  `test_nested_url_inside_a_query_string_is_not_split`, `test_prose_after_a_liquid_block_is_still_linkified`.
- **근거:** PR #509.

### T2 — 토큰 multiset 무손실 검사가 마커 변경을 은폐한다

- **증상:** 코드 펜스 안 bash 주석 `# 예시` 가 `#### 예시` 로 바뀌었는데 불변식은 PASS.
- **원인:** "마커를 모두 지우고 나머지 토큰을 센다"면 마커**만** 바뀐 변경은 정의상 탐지 불가.
  전역 숫자 제외도 같은 모양의 구멍이었다(표 셀의 홀로 선 숫자 삭제가 투명).
- **회피:** 마커가 **바뀌어도 되는 구간**과 **아닌 구간**을 나눠 비교한다. 펜스 라인과 front matter는
  라인-verbatim, 펜스 밖만 마커 제거. 숫자는 헤딩 선두 `N.` 슬롯일 때만 제외.
  `scripts/restore_digest_structure.py:337-379`. 테스트:
  `test_fence_interior_heading_marker_change_is_caught`,
  `test_standalone_number_deletion_outside_headings_is_caught`,
  `test_invariant_backstops_an_r0_regression`.
- **근거:** PR #500(발견), #504(불변식 강화).

### T3 — 펜스 닫힘 판정을 raw 라인으로 하면 들여쓴 닫는 펜스를 놓친다

- **증상:** 2026-02-08 이후 전체가 "펜스 안"으로 잘못 인식되거나 그 반대.
- **원인:** 해당 포스트는 코드 블록을 `  ``` ` (선행 공백)로 닫는다.
- **회피:** `line.strip().startswith("```")` 로 토글. `check_digest_structure._strip_code_fences` 와
  동일 규약. 테스트: `test_indented_closing_fence_closes_the_block`.
- **근거:** memory `restore_digest_fence_protection`.

### T4 — 래칫 비교 키를 메시지 문자열로 두면 오탐한다

- **증상:** 결함 집합이 6→6으로 불변인데 게이트가 "+1 new"로 차단.
  (`check_digest_structure.py:153` 원문 `Measured 2026-08-04 on 2026-05-05` — 앞이 실측일, 뒤가 대상 포스트 날짜)
- **원인:** 위반 메시지가 본문을 embed한다
  (`body H1 heading found: # DevSecOps 관점 분석: … 안드로이드 …`). 그 줄의 단어가 바뀌면
  "기존 1건 소멸 + 신규 1건 등장"으로 읽힌다.
- **회피:** `_kind(v) = v.split(": ", 1)[0]` 로 kind만 비교하고 kind별 **개수**를 비교한다.
  `scripts/check_digest_structure.py:144-183`.
- **근거:** PR #492.

### T5 — 파일 단위 baseline은 레거시 개선을 막는다

- **증상:** 순수 고유명사 치환 PR이 자기가 만들지 않은 구조 결함으로 red.
- **원인:** 게이트가 파일 스코프라 pre-existing 결함이 그 파일의 모든 변경을 차단.
- **회피:** baseline 파일이 아니라 **diff 래칫**. 동기화할 상태가 없고, grandfather된 포스트도
  이후 회귀는 계속 검출된다(baseline은 등록 파일의 이후 회귀까지 통과시킨다).
- **근거:** PR #490, `notes/digest-proper-noun-policy.md` "구조 게이트 diff 래칫" 절.

### T6 — 룰 적용 순서는 설계 초안이 아니라 테스트가 정한다

- **증상:** 티어 C 6개 파일이 `#### 9. 실무 체크리스트` 로 강등돼 더 못 고치는 상태가 됨.
  재넘버링 결과에 `[1, 3]` 갭 발생.
- **원인:** R5(체크리스트 헤딩 canonical화)를 R1보다 뒤에 두면 `TOP_SECTION_RE` 가 번호 붙은
  형태를 못 알아봐 R1이 item 본문으로 오인해 강등한다. R4보다 뒤에 두면 체크리스트가 섹션
  인덱스를 소비한다.
- **회피:** 확정 순서 **R5 → R1 → R2 → R3 → R6 → R4**. 순서 의존 자체를 테스트로 고정한다
  (`test_order_matters_r5_before_r1`, `test_order_matters_r5_before_r4`,
  `test_r1_and_r2_are_order_independent`).
- **근거:** PR #496, memory `restore_digest_structure_rule_order`.

### T7 — 한 게이트를 고치면 다른 게이트가 깨진다

- **증상:** R3가 per-item 체크박스를 제거하자 `validate_post_quality.validate_checklists` 가
  2026-03-22 점수를 91→83으로 떨어뜨려 frozen quality baseline이 깨졌다.
- **원인:** 레거시 코퍼스에서 per-item `- [ ]` 가 그 파일의 **유일한** 체크박스였다.
  구조 게이트는 그것을 결함으로, 품질 게이트는 그것을 자산으로 센다.
- **회피:** baseline을 낮추는 게 아니라 **현재 생성기가 이미 내보내는 형태로 수렴**시킨다(R6:
  전역 `## 실무 체크리스트` 아래 평범한 `- x` 를 `- [ ] x` 로). 마커만 바뀌므로 여전히 무손실.
- **근거:** PR #496 (R6 `checkbox_global_checklist` 도입 커밋 `096d9af9`).
  #499·#500은 같은 게이트 상충의 후속 배치에서 baseline 이동을 다룬 것이라 관련은 있으나,
  91→83 과 R6 자체는 #496이다. memory `digest_checklist_score_inflation`.

### T8 — 합성 데이터로 설계하면 잘못된 전제를 세운다

- **증상:** "참고자료 부재 13개" → 실측 결과 12개는 표기 변형일 뿐 이미 보유, 1개만 진짜.
  "티어 D 8개는 체크리스트 생성 필요" → 8/8이 이미 보유, 제목 표기 문제였다.
  "절단 9건" → 실제는 79개 포스트 128건.
- **원인:** 정규식/키워드 스캔 결과를 실제 포스트로 검증하지 않고 규모 추정에 썼다.
- **회피:** 착수 전 **실제 코퍼스로 RUN 하고 분포를 표로 낸다.** 되감기 PR은 착수 전에
  "되감기 후 잔여 85%+ 18건 / 70-84% 34건 / 50-69% 55건 / 1-49% 19건, 완성 문장 없음 2건"을
  측정하고 방식(되감기 vs LLM 재요약)을 골랐다.
- **근거:** #501, #506/#513, memory `feedback_cover_empirical_first`,
  `digest_reference_section_missing_13_rejected`.

### T9 — 부분 매칭 백필이 결함을 위장한다

- **증상:** 200자 하드캡에 잘린 요약 9건이 우연히 종결어미로 끝나 마침표 백필 대상이 됐다.
  마침표를 붙이면 절단이 완결된 문장처럼 보여 #506이 고친 결함을 **숨긴다.**
- **원인:** "문장처럼 보임"과 "문장임"을 같은 검사로 판정.
- **회피:** `TRUNCATION_SUSPECT_LEN = 195` 길이 가드로 서로 배타적인 두 변환기로 분리
  (마침표 = `< 195`, 되감기 = `≥ 195`). 테스트: `test_truncated_summary_does_not_gain_a_period`,
  `test_short_summary_just_below_the_threshold_is_still_fixed`.
- **근거:** PR #512.

### T10 — 정규식 대안 하나가 코퍼스 전역 오탐을 만든다

- **증상:** `_SENTENCE_ENDING_RE` 의 bare `요$` 가 종결어미가 아니라 명사에 매칭
  (주요·중요·필요·소요) → `"…개선하기 위한 주요."`
- **원인:** 형태소 경계 없이 음절 하나로 어미를 판정.
- **회피:** 실측으로 정당 사례가 0건임을 확인하고 **대안 자체를 제거**했다. 새 어미 대안을
  추가할 때는 코퍼스에서 word-boundary 실측(정당/오탐)을 먼저 낸다
  (`digest-proper-noun-policy.md` 의 substring 트랩과 같은 종류).
- **근거:** PR #511 유입 → #512 수정.

---

## 5. 새 변환기 작성 절차

### Step 0 — 실측 (코드보다 먼저)

1. 결함을 **정규식이 아니라 실제 렌더링/포스트로** 확인한다. 링크화는 `_site/` 빌드 산출물에
   `href` 가 없다는 것을 확인하고서야 착수했다.
2. 규모를 표로 낸다: 몇 개 파일 / 몇 건 / 분포. 여기서 대개 초기 가설이 깨진다(T8).
3. 대안을 비교한다(생성 vs 변환, LLM vs 결정적). 되감기는 "결과가 항상 원문의 접두사라
   대조 검증할 사실이 없고 외부 호출이 없다"를 근거로 LLM 재요약을 기각했다.

### Step 1 — 좁은 diff 설계

4. `transform(text) -> text` 순수 함수 하나로 만든다. I/O는 `main()` 에만 둔다.
5. 보호 영역을 C2 표대로 코드에 선언한다. 특히 **다중 라인 Liquid 상태 머신**(T1)과
   **`strip()` 기반 펜스 토글**(T3).
6. 룰이 여럿이면 적용 순서를 정하고 **순서 의존을 테스트로 고정**한다(T6).

### Step 2 — 런타임 무손실 계약

7. "이 변환이 절대 할 수 없는 일"을 한 줄로 쓰고 `_violates_*(old, new)` 로 구현한다.
   길이 방향(증가/감소)을 반드시 포함한다 — 정규화 동등만으로는 '제거'를 못 잡는다(C4).
8. 토큰 검사를 쓸 거라면 마커-블라인드 구멍을 막는다(T2). 감사 검출기는 룰 검출기와
   **별도로** 정의하고 lockstep 테스트를 붙인다(C5).
9. 위반 시 `exit 1` 로 전체 중단.

### Step 3 — 파일럿 → 파티션 배치

10. `--dry-run` 으로 전수 확인 → 소수(5~20개) 파일럿 → 월/구조 유형별 파티션 배치.
    "단일 세션 blast 금지" 는 이 레포의 반복 결론이다.
11. 배치마다 게이트 6종을 돌린다: 구조·고유명사·미번역·체크리스트 제목·Liquid malformed·맨 URL.
    품질 baseline이 움직였는지도 본다(T7).

### Step 4 — 게이트 배선 (재발 경로가 있을 때만)

12. 재발 경로가 **사람 저술**이면 pre-commit + CI (링크화 #510: 8개 포스트 전부 수작업
    가이드였고 크론 digest는 0건 → 크론 배선 제외).
13. 재발 경로가 **생성기**면 게이트가 아니라 생성기를 고친다(C8). 백필은 헬퍼를 import 한다.
14. 레거시 결함이 남아 있으면 게이트는 `--staged`/`--changed` + `--ratchet`, kind 단위 비교(C6, C7).
15. `.githooks/pre-commit` 은 `install-hooks.sh` 가 heredoc으로 생성한다. **생성기 소스도 함께**
    고쳐야 한다 (memory `githooks_hookspath_gotcha`). 배선 회귀 테스트를 붙인다
    (`test_wired_into_precommit`, `test_wired_into_ci`).

---

## 6. 관련 스크립트 · 테스트 · 게이트

### 변환기

| 스크립트 | 테스트 |
|----------|--------|
| `scripts/restore_digest_structure.py` | `scripts/tests/test_restore_digest_structure.py` |
| `scripts/enrich_digest_references.py` | `scripts/tests/test_enrich_digest_references.py` |
| `scripts/linkify_bare_urls.py` | `scripts/tests/test_linkify_bare_urls.py` |
| `scripts/backfill_card_summary_period.py` | `scripts/tests/test_backfill_card_summary_period.py` |
| `scripts/rewind_truncated_summaries.py` | `scripts/tests/test_rewind_truncated_summaries.py` |

### 게이트

| 게이트 | 배선 |
|--------|------|
| `scripts/check_digest_structure.py --ratchet` | `.githooks/pre-commit` step 9 / `.github/workflows/svg-lint.yml:256` |
| `scripts/check_digest_checklist_heading.py` | pre-commit 9d / svg-lint `--all` (`svg-lint.yml:295`) / blogwatcher 자가치유 |
| `scripts/check_digest_proper_nouns.py` | pre-commit 9c (`--staged`) / `svg-lint.yml:286` (`--changed $BASE`) |
| `scripts/linkify_bare_urls.py --check` | pre-commit step 12 / `svg-lint.yml:303` (`--all`) |
| `scripts/validate_post_quality.py` | pre-commit step 11 (fail < 60) |

### 생성기 측 재발 방지

| 위치 | 내용 |
|------|------|
| `scripts/news/content_generator.py:2689` `_restore_sentence_period` | 한국어 종결어미 뒤 마침표 복원 (#511). 마침표 백필이 그대로 import |
| `scripts/news/content_generator.py:2943` `_truncate_korean_sentence(ko_summary, 200)` | 맹목 슬라이스 대신 문장 경계 절단 (#506) |

### 배경 문서

- `notes/digest-proper-noun-policy.md` — 래칫 도입 경위, allow-list deny-by-default, substring 트랩
- `docs/superpowers/specs/2026-08-04-digest-structure-backfill-design.md` — 구조 백필 캠페인 설계
- `docs/superpowers/plans/2026-08-05-restore-digest-structure.md` — 룰 순서 확정 플랜

---

## 7. 미검증 / 열린 항목

이 문서에서 **코드로 확인하지 못한** 것들. 계약으로 단정하지 않는다.

1. **구조 복원기의 Liquid 보호는 명시적이지 않다.** `restore_digest_structure.py` 는 front matter와
   코드 펜스만 보호 영역으로 선언한다. 실제로 손상이 관측된 적은 없고(6개 룰이 모두 라인 선두
   마커에만 매칭) 코퍼스 전수 무손실 테스트가 사후 방어하지만, **Liquid 블록이 보호 영역으로
   선언돼 있지는 않다.** 새 룰이 라인 중간 텍스트를 건드리면 T1이 재현될 수 있다.
2. **참고자료 변환기의 섹션 *뒤* 구간은 런타임 미검사다.** `transform` 구조상 `after` 는 그대로
   이어붙지만, ABORT 조항은 섹션 **앞** 구간만 비교한다
   (`enrich_digest_references.py:192`). 테스트(`test_trailing_section_after_references_survives`)로만
   보장된다.
3. **링크화 변환기에는 런타임 무손실 계약이 없다.** 5종 중 유일하다. #509의 손상이 바로 이
   변환기에서 났다는 점을 감안하면 `_violates_*` 추가가 자연스러워 보이지만, 이 문서는
   변경을 제안만 하고 적용하지 않았다.
4. **테스트 건수는 `def test_` 선언 수를 센 것**이라 parametrize 확장분은 반영돼 있지 않다.
   실제 실행 건수는 더 많다.
5. **참고자료·마침표·되감기 3종에는 게이트가 없다.** 마침표·되감기는 생성기 수정이 재발
   경로를 막지만, 참고자료(용도 열)는 재발 탐지 수단이 확인되지 않았다.
