# Decisions

아키텍처와 디자인 결정을 기록합니다.

## 2026-02

- **Vercel + GitHub Pages 이중 배포**: Vercel 메인, GitHub Pages 백업
- **Giscus 댓글**: GitHub Discussions 기반, 별도 DB 불필요
- **DeepSeek Chatbot**: 비용 효율적인 AI 챗봇 (Context Caching 활용)

## 2026-03

- **ai-summary-card 인라인 변환**: 외부 include 대신 Jekyll include 방식으로 통일 (PR-67)
- **포스트 제목 한국어화**: 영문 제목을 한국어로 전환하여 SEO/가독성 향상 (PR-68)
- **SVG 이미지 차별화**: 날짜별 SVG에 고유 레이아웃/색상 적용 (타임라인 vs 대시보드)
- **API Prisma 동적 import**: DB 미설정 환경에서도 graceful 503 응답하도록 변경
- **스크립트 정리 정책**: 완료된 마이그레이션/중복 스크립트는 `scripts/_archive/`로 이동
- **모델명 통일**: 문서 전체를 Opus 4.6 / Sonnet 4.6으로 일괄 업데이트

## 2026-05

- **summary_card frontmatter (Option A) 단일 형식 채택**: ai-summary-card include의 attribute 6개(title/categories_html/tags_html/highlights_html/period/audience)를 post frontmatter의 `summary_card:` YAML 블록으로 이전, body는 `{% include ai-summary-card.html %}` 단일 라인. 모든 168 posts 적용 완료.
  - **Why**: 두 render 경로(`page.summary_card` vs `include.*` attrs)가 공존하면서 YAML escape, ASCII apostrophe, 분리자 호환성 등 다층 회귀 발생. 단일 데이터 소스(YAML)로 통일하여 escape는 Jekyll filter(`| escape`)에 위임.
  - **호환성 분리자 게이트**: `migrate_summary_cards_to_frontmatter.py`의 `_is_separator_compatible`는 byte-identity 보존을 위해 `\n      ` separator만 허용. `unify_ai_summary_block.py` 출력(' ' 또는 '\n')을 가진 36개 posts는 `--allow-separator-divergence` flag로 우회 마이그레이션 (cosmetic-only HTML whitespace delta 수용).
  - **신규 publish 경로**: `scripts/news/content_generator.py`가 처음부터 Option A YAML을 emit하도록 변경 — `_emit_summary_card_yaml()` helper 추가, security/tech-blog 양쪽 mode 변경.
  - **Idempotency guard**: `scripts/unify_ai_summary_block.py`에 frontmatter `summary_card:` 존재 시 skip하는 가드 추가 — 향후 normalize 패스가 풍부한 highlights 데이터를 `포인트 N` placeholder로 덮어쓰는 회귀 방지.
  - **Regression guard**: `scripts/tests/test_post_summary_card_format.py`에서 모든 _posts/가 bare include + summary_card frontmatter를 사용하는지 자동 검증.

- **SVG 영어-only 3-layer defense**: weekly digest 자동발행에서 한국어 headline이 SVG `<text>` 요소로 leak되는 회귀가 반복 — check-svg quality gate가 한글 검출 시 fail. 3중 방어로 봉쇄.
  - **Layer 1 (data)**: `scripts/news/l20_dispatch.extract_three_stories`가 filename slug에서 영어 키워드를 추출(`_AI_AWS_Threat_Cloud` → `["AI","AWS","Threat","Cloud"]`), 한국어 segment를 자동 교체.
  - **Layer 2 (render)**: `scripts/lib/svg_l20_hero._escape` + `scripts/news/svg_generator._escape_svg_text`가 XML escape 전 Hangul (U+AC00..U+D7A3 + jamo) 강제 제거. 분리자 collapse 포함.
  - **Layer 3 (CI)**: `scripts/check_svg_quality.py`가 모든 SVG `<text>`에서 한글 검출 시 exit 1. `.github/workflows/check-svg.yml` PR 게이트.
  - **Tests**: `scripts/tests/test_svg_render_english_only.py` 13개 (render-time + escape helpers + end-to-end Korean post).

- **QR URL 버그 수정**: 모든 weekly digest cover의 QR이 404 URL 인코딩 (`Tech-Security-...` 하이픈 형식) — Jekyll permalink는 underscore 보존인데 `_post_url_from_filename`이 `slug.replace("_", "-")`를 적용했음. 추가로 manual `scripts/upgrade_*.py`는 `/security/.../slug.html` (404) 패턴을 하드코딩.
  - **Fix**: `_post_url_from_filename`에서 `replace` 제거.
  - **Patch existing covers**: `scripts/fix_qr_url_in_covers.py`로 63 covers의 QR `<g>` 블록만 surgical replace (manual artwork 보존).
  - **CI gate**: `scripts/check_cover_qr_urls.py`가 모든 cover SVG의 QR path data를 `gen_qr(_post_url_from_filename(name))`과 byte-equal 비교. `.github/workflows/check-svg.yml`에 추가.
  - **Round-trip test**: `qrcode` lib을 `requirements-ci.txt`에 추가 + path-data 일치 확인 테스트로 회귀 차단.
  - **Live verification**: 6개 sample URL 모두 `200 OK` 확인 (https://twodragon0.github.io/tech-blog/posts/...).

- **2026-05-08~09 Vercel Production Outage — 종합 incident report**: Vercel deploy 11회 연속 실패 + 모든 Bot 차단 + L22 ultra SVG 품질 저하 — 3개 root cause 동시 식별 및 해결.

  ### Root cause #1 — `vercel.json` `(?i)` regex flag (`15229987`)
  - 증상: `headers[18].has[].value`에 `(?i)` 케이스 무시 flag → path-to-regexp `Error: Unhandled type: "ColonToken" :` → 모든 production 배포 실패.
  - Fix: `(?i).*(googlebot|...).*` → `.*([Gg]ooglebot|...).*` 캐릭터 클래스로 치환.

  ### Root cause #2 — `middleware.js` `config.matcher` 부정 lookahead (`bb992d41`)
  - 증상: `matcher: '/((?!assets|...).*)'`의 `(?!`을 path-to-regexp가 `(?:!...)` 명명 파라미터로 오인 → 동일 ColonToken 에러 발생.
  - Fix: `config.matcher` 제거 + 함수 내부 `SKIP_PREFIXES` / `SKIP_EXACT` 조기 return으로 정적 에셋 필터링.
  - 참고: aaad1f9f (2026-05-07) 커밋부터 11회 deploy 실패 → 라이브 사이트가 stale deployment 서빙 (구 Challenge Mode + 깨진 QR 그대로).

  ### Root cause #3 — Vercel Bot Protection managed rule (대시보드)
  - 증상: 사용자가 Attack Challenge Mode를 OFF 했음에도 모든 봇이 429 + `x-vercel-mitigated: challenge` 응답.
  - 진단: `vercel api /v1/security/firewall/config/active`로 `managedRules.bot_protection: {active: true, action: "challenge"}` 확인. Attack Mode와 별개 setting.
  - Fix: Vercel API PATCH로 `action: "challenge"` → `"log"` 변경 (사용자 수동 적용).
  - 후속: `scripts/backup_vercel_firewall.py` + 매주 월요일 cron 추가하여 미래 silent drift 감지 (`docs/backups/vercel-firewall/*.json`).

  ### 2차 작업 — May 8개 cover SVG L20 → L22 ultra 승격 (`23a71818`)
  - 기존 L20 hero (34 KB, 7 lines body) → L22 ultra (67 KB, 470+ lines, hand-curated 3 bands × red/amber/green).
  - 각 band: 실제 CVE 번호, 벤더명, 운영 mitigation, KPI badge, 2 mini-cards, 테마별 visual.
  - QR URL 버그 동시 수정으로 모바일 스캔 시 200 OK 보장.

  ### 3차 작업 — Multi-tool harness env best-practices (`4efb3f7f`)
  - `docs/setup/MULTI_TOOL_HARNESS_ENV.md`: Claude Code/Codex/Gemini/OMC/CCG 환경변수 카테고리화 (LLM keys, models, OAuth, CI flags, Vercel runtime).
  - `.github/workflows/dependabot-auto-merge.yml`: patch/minor 자동 머지, major 코멘트 안내.
  - Repo settings: `allow_auto_merge: true, delete_branch_on_merge: true` 활성화.

  ### 검증 메트릭
  - Vercel deploy: ● Ready (4분, production)
  - check-svg: 210 PASS / 0 FAIL
  - check_cover_qr_urls: 97 OK / 0 FAIL
  - 1410 tests pass / 3 skip
  - Live URLs: `/`, `/sitemap.xml`, `/robots.txt`, `/posts/.../`, `/assets/images/...` 모두 200 OK (Googlebot UA 포함)
  - Googlebot probe (CI runner): 모든 경로 200 (이전 모두 429)
  - 4 Dependabot PRs (305/306/307/345) + 2 own PRs (#342/#338) 머지 완료

  ### Lessons
  - **path-to-regexp는 정규식 superset이 아님**: `(?i)`, `(?!`, `(?=` 등 lookaround/flag 비지원. 캐릭터 클래스로 우회.
  - **Vercel managed rule은 Attack Mode와 분리**: 대시보드에서 Attack Mode toggling 만으로는 봇 차단 해제 안 됨. `vercel api /v1/security/firewall/config/active`로 직접 검증 필요.
  - **Silent drift 위험**: Vercel 대시보드 변경은 repo audit log에 남지 않음. 주간 backup cron 필수.

## 2026-05-28: 2025-12-19 8b-4wk Vuln+ISMS-P spec — SKIP_PERMANENTLY

After architect-agent deep-read, the 2025-12-19 post is a CISO-perspective
rewrite of the same territory as the 2025-05-09 7batch-4wk Inspector+ISMS-P
spec (MY09). The 12-19 post adds MITRE ATT&CK cloud-matrix mapping + a
FinOps cross-cut, but neither generates the numeric band payload required
to fill `metric`/`metric_b`/`mini`/`mini2` fields without fabrication.
Forward-looking ROI estimates are insufficient signal for visual bands.

Decision: do NOT author a separate spec. Treat MY09 as the canonical
ISMS-P cover for the 8batch series. If the MITRE ATT&CK section warrants
its own cover later, evaluate as a standalone "ATT&CK Cloud Matrix" topic
rather than another ISMS-P recap.

Confidence: high. Architect agent ID: a8367758da5c76502 (session
aee548e8-62e0-4c61-9a89-deeb59c191e2).

## 2026-06-01: L20 side-panel headline cap — surgical patch over regeneration

L20 Hero+2-Card SVG covers had a structural overflow bug:
`<text x="670" y="140|404" font-size="24" font-weight="800">` rendered
side-panel headlines without a character cap. Headlines longer than
~27 chars extended past x=1024 into the KPI card zone (1024-1164),
producing visible text/illustration overlap in 21 production covers.

Two repair strategies were considered:

1. **Full regeneration** (`generate_post_images.py --force`) — runs
   `extract_three_stories()` which derives headlines from title+excerpt+
   filename only. Loses the rich body-H3-derived headlines that the
   original L22 path had produced (e.g. "AWS Serverless AI Defense
   Architecture" → "Cloud", "25 Password Manager Recovery Attacks" →
   "Agent"). Verified on `2026-02-17-...AI_Agent_Cloud_Security.svg`.

2. **Surgical in-place patch** — read each SVG, regex-match the two
   side-panel `<text>` elements, apply `_fit_panel_headline()` to the
   headline string only, write back. Preserves all other content
   verbatim. Implemented in `scripts/fix_panel_headline_overflow.py`.

Decision: surgical patch (commit 14d51115). Reasoning:
- Editorial value of body-derived headlines (CVE names, vendor + impact
  phrases) outweighs the cosmetic gain from regenerating illustrations.
- 21 file diff stays content-stable, easier to review and revert.
- Future digests are protected because `render_l20_hero()` now wraps
  both call sites with `_fit_panel_headline()`.

Cap algorithm: `max_chars=27`, budget=24 (3-char ellipsis reserved),
word-boundary preferred unless latest space < budget-10 (then hard cut).
Unit tests in `scripts/tests/test_l20_panel_headline_cap.py` cover all
10 behavioral paths including parametrized real-world overflow cases
(commit 6b5a621b).

## 2026-06 — CodeQL HIGH alert triage (26 alerts)

Context: after merging the large cover-honesty PR (#381, 1153 files), the
"CodeQL" default-setup PR check failed. Investigation showed 26 open HIGH
alerts + 3 medium. A read-only opus security review (+ direct spot-checks
of the 5 highest-stakes claims) classified **all 26 HIGH as false
positives** (0 true positives requiring code change):

- `py/clear-text-logging` (9) / `py/clear-text-storage` (2): every flagged
  value is public content (news titles, blog commentary, generated post
  markdown, cover SVGs) or the masking sink itself (`logging_utils.py:42`).
  The only real secret (`_GEMINI_API_KEY`) travels in the request URL
  (`enhancer.py:46`), never in a logged/stored expression.
- `py/incomplete-url-substring-sanitization` (2): pytest assertion oracles
  in `test_fix_links.py`, not trust validation → dismissed `used in tests`.
- `rb/incomplete-multi-character-sanitization` (2): single-pass tag strip on
  trusted single-author front-matter; output is JSON-encoded then
  JS-escaped. Loop-until-stable hardening rejected — risks shifting live
  archive-card excerpt truncation (`[0,77]`/`[0,157]`+"...") for zero real
  gain (Karpathy: don't fix what isn't broken).
- `js/xss-through-dom` (8): all `setAttribute('src',…)`/`.src=` from
  Jekyll-rendered `data-*` attrs or same-origin literals — not HTML sinks.
- `js/incomplete-multi-character-sanitization` (3): regex strips assigned to
  `textContent` (inert); the real XSS boundary is the `DOMPurify.sanitize`
  allowlist at `chat-widget.js:218/654`, which is correct.

Decisions:
1. **Dismiss all 26 HIGH via code-scanning API** (`false positive`, or
   `used in tests` for the 2 test alerts) with per-alert evidence comments.
   No runtime code touched — patching working code to satisfy a static FP
   would risk regressions. Verified: open HIGH count 26 → 0.
2. **Fix the 3 real medium `actions/missing-workflow-permissions`** by
   adding least-privilege `permissions:` blocks to svg-lint, lighthouse
   (`contents: read`) and indexnow-ping (`contents: read` + `actions: read`
   for its `gh api` workflow-runs lookup). Branch `fix/codeql-hardening`,
   commit 729fcadf. These auto-close on merge when CodeQL re-scans main.

Note: the "CodeQL" check itself failing on #381 was ALSO a large-diff
false attribution (see memory `codeql_large_diff_false_attribution.md`) —
it is not a required status, so the merge proceeded as UNSTABLE.

---

## 2026-06-18 — L20 digest 헤드라인 "Class D" 영구 deferred (한국어 소유격 "의")

**결정**: `build_lead_headline()`(scripts/news/l20_dispatch.py)에서 한국어 소유격
"의" 패턴으로 인한 weak 헤드라인(대표 사례 "Strategy Michael", from "Strategy의
Michael Saylor")은 **결정론적으로 수정 불가**로 확정하고 영구 보류한다. 재시도 금지.

**근거 (경험적)**: "의" 마커는 고쳐야 할 bad 케이스와, 반드시 보존해야 하는 good
케이스에서 **byte-identical**이다:
- bad:  `Strategy의 Michael Saylor` → "Strategy Michael" (원하지 않음)
- good: `Anthropic의 Claude` → "Anthropic Claude" (보존 필요, test_l20_realcontent.py:1302)
- good: `Broadcom의 VMware`  → "Broadcom VMware"  (보존 필요, :1303)

"의" 기반 split/reorder 규칙은 위 good 케이스를 깨뜨리거나, surname/place 탐지를
요구한다. surname/place 탐지는 실제 위협 행위자명 오탐 위험 때문에 모듈이 명시적으로
금지한다(l20_dispatch.py:911-913, :1097-1101). 두 부류를 가르는 결정론적 신호가 없다.

**대안**: 해당 스토리가 본문/하이라이트에서 약하면 source-fallback(`_src_fallback`)으로
사이드카드 강등되어 자연히 가려진다. 헤드라인 추출을 더 공격적으로 만들 필요 없음.

**관련**: 같은 감사에서 채택한 honest 수정은 Fix A(generic format noun "url"을
`_GENERIC_TRAILING`에 추가 → "FBI URL" junk bigram 제거, TestUrlBigramReject).
부제 content-descriptor + route_hint 디커플링은 PR #417 참조.

---

## 2026-06-18 — Legacy honesty-baseline 커버는 baselined 유지 (regen/마이그레이션 안 함)

**결정**: `scripts/cover_honesty_baseline.txt`에 grandfathered된 30건(L20 16 + L22 14)의
legacy 커버를 honesty FAIL 해소 목적으로 **재생성하거나 L22→L20 마이그레이션하지 않는다.**
현재 baseline을 영구 floor로 받아들인다.

**근거 (경험적)**:
- 이 커버들은 일반 long-form 보안 포스트(가이드/코스/사고분석)용이며, honesty FAIL 사유는
  rich attack-chain 비주얼(`hub_spoke` HUB/RELAY/VICTIM, `data_exfil`, `cve_chain`,
  `code_injection` C2_URL/exfil_keys 등)이 본문 evidence 토큰 없이 위협을 'assert'하기 때문.
- **그러나 이 rich 스타일은 사용자가 품질 reference로 명시한 커버**(2026-01-14 AWS Cloud
  Security IAM→EKS, 2026-01-14 ISMS-P)와 **동일**하다. 즉 honesty를 통과시키려 regen하면
  references가 보존하려는 바로 그 비주얼을 honest-neutral로 벗겨내 일관성이 깨진다.
- baseline은 grandfathered라 CI를 **막지 않는다**(svg-lint honesty gate는 NEW 회귀만 FAIL).
- 보안 아키텍처/사고분석 글에서 attack-chain 비주얼은 illustrative로 적절하다고 본다.

**적용**:
- baseline 30건 = 영구 floor. "baseline 0" 추구하지 말 것.
- 신규 digest 커버는 honesty-safe(neutral/advisory/market) 유지(자동 생성, 무인 cron).
- 향후 누군가 "baseline 줄이자"고 하면 이 결정을 먼저 참조. regen은 시각 품질 저하 +
  references 불일치 trade-off가 있음을 상기.
- L22 14건 마이그레이션도 동일 사유로 보류(ralplan 분석 결론: 비용 대비 시각 손실).

**관련**: false-orphan 오판 정정(image: 필드 기준 매칭), empirical-first 원칙.

## 2026-08

- **CI 게이트 실효성 감사**: "게이트 존재"와 "게이트가 막는다"를 분리해 측정. 최근 30 PR 실측상 21개 체크 중 **차단 이력이 있는 것은 5개**. 상세는 [ci-gate-audit-2026-08.md](ci-gate-audit-2026-08.md) (PR #529–#538)
- **크론 봇 push는 push·PR 트리거 둘 다 회피**: `GITHUB_TOKEN` 직push가 워크플로를 안 깨우므로, 봇이 만드는 산출물을 검사하는 게이트는 **`schedule`이 필수**. 커버 SVG 최근 40커밋 중 35개가 봇 (#529)
- **경로 필터된 체크는 required status check로 지정 불가**: 미실행 시 PR 영구 pending. 지금 걸 수 있는 실질 게이트는 `build` 하나뿐 → required checks 도입 **보류**
- **fail-closed는 조건부로만 옳다**: 100%가 위반하는 임계값(front matter 1000자)이나 영구 부재 시크릿에 fail-closed를 적용하면 "무시되는 red"를 생산한다. 전자는 래칫으로, 후자는 cron 폐기로 처리 (#534, #536)
- **자가치유에는 재검증이 필수**: `fixer || true` 뒤에 checker 재실행이 없으면 "고치려 했다"가 "고쳐졌다"로 위장된다. 크론 자가치유 4곳 중 1곳에 없었다 (#537)
- **가드는 뮤테이션으로 자기검증한다**: 새 가드를 믿기 전에 각 수정을 되돌려 잡히는지 확인. 누적 60여 종 전부 caught. 반복 함정 — 검사 대상 파일의 주석이 안티패턴을 언급하므로 주석 제거 후 검사

### CSP Path B 보류 — Google Translate 유지 (2026-08-12)

**결정**: enforcing CSP의 `script-src`에서 `'unsafe-inline'`을 제거하는 Path B를 **보류**하고
Google Translate를 유지한다.

**근거 (추론 아님, 실측)**: Report-Only는 차단하지 않으므로 "Translate가 깨질 것"은 그동안
추론이었다. 응답 헤더를 인플라이트로 바꿔 Report-Only를 enforcing으로 승격시킨 A/B로 측정:

| | 현재 정책 | Path B enforcing |
|---|---|---|
| 본문 한글 잔존 | 0자 | 1061자 (26.6%) |
| Google `<font>` 마커 | 446개 | 0개 |
| `<html>` | `lang=en` / `translated-ltr` | `lang=ko` (미번역) |

Path B는 Translate를 **저하시키는 게 아니라 완전히 비활성화**한다.

**기각한 대안 — iframe 격리 후 별도 CSP**: 위반 문서는 `about:blank`이고 about:blank는
임베더의 CSP를 상속한다. Chrome은 iframe `csp` 속성을 제거했고, Translate는 호스트 문서
자체를 재작성해야 동작하므로 프레임에 가둘 수 없다. (명세·구현 논거이며 별도 A/B 미실시.)

**적용**:
- `csp_interaction_baseline.txt`의 1건은 "제거 대상 blocker"가 아니라 **수용된 trade-off**다.
  Path B 재개 없이 이 줄을 지우지 말 것.
- `csp-interaction-check.yml`의 임무는 "baseline이 비워질 때까지 감시"에서 **"두 번째 위반
  등장 감지"**로 바뀐다. 다른 통합이 `unsafe-inline`에 새로 의존하기 시작하면 그것이 신호다.
- 재개 조건: Google Translate 제거를 받아들이거나, about:blank 인라인 부트스트랩을 쓰지 않는
  번역 수단으로 교체할 때.

### Report-Only 존폐와 번역 아키텍처는 둘 다 "측정 먼저" (2026-08-12)

Path B 보류 직후 두 후속 질문이 나왔고, 둘 다 **데이터 없이는 결정 불가**로 판정했다.

**1. Report-Only 헤더를 계속 둘 것인가.** 두 정책의 지시자 17개 중 14개가 동일하고, 차이는
`script-src`/`script-src-elem`(해시 vs `'unsafe-inline'`)과 `upgrade-insecure-requests`(RO에선
무시되므로 enforcing 전용)뿐이다. 즉 RO 헤더는 **정확히 Path B 가설 하나만** 시험하며, 그
가설은 닫혔다. 남은 신호("두 번째 위반 등장")는 `csp-interaction-check` 크론이 매일 커버한다.

그런데 비용 쪽에 구조적 모순이 있다: `sentry-init.js:39-42` 의 `ignorePatterns` 는 CSP·확장
이벤트를 **명시적으로 버리는데**, `report-uri`/`report-to` 는 SDK 를 우회해 Sentry ingest 로
직접 간다. SDK 가 버리기로 한 노이즈가 다른 문으로 무샘플 유입된다. SDK 의 월 5000 가드도
`localStorage` 기반이라 **방문자별**로 세므로 전역 소비량을 못 본다.

→ 제거/유지 결정은 실제 볼륨에 달렸다. `scripts/sentry_csp_volume.py` 를
`sentry-healthcheck.yml` 에 붙여 매일 job summary 로 집계한다(게이팅 아님, 리포팅).
시크릿이 이미 그 job 에 있으므로 토큰을 다른 곳으로 옮기지 않는다.

**2. 번역 아키텍처(A 유지 / B 정적 사전번역 / C 온디맨드 / D 포기).** 코퍼스는 263 포스트
469만 자, 4개 언어면 1,880만 자다. B 안은 최초 ~$376 + 페이지 263→1,315개 + sitemap/hreflang
전면 재작업이다. **그런데 언어 토글에 계측이 전혀 없었다**(`gtag`/`dataLayer` grep 0건).
쓰는 사람이 있는지 모르는 채로 B 를 검토하는 건 순서가 뒤바뀐 것 — 사용량이 미미하면 D 가
$0 에 Path B 를 연다.

→ `window.__track` (버퍼 후 flush) + `lang_toggle_open` / `lang_select` 이벤트를 먼저 넣는다.
**버퍼가 필요한 이유**: GA 는 첫 상호작용에 지연 로드되고 `gtag('config')` 는 그 onload 에서만
실행된다. config 보다 먼저 dataLayer 에 들어간 이벤트는 앞서 처리되어 유실되는데, lang-toggle
클릭은 GA 로드 트리거이자 측정 대상이라 무버퍼 계측은 **정확히 첫 사용 신호를 잃는다.**
첫 클릭은 `header-runtime.js` 만 볼 수 있다(그 클릭이 `google-translate.js` 를 내려받게 하는
클릭이므로). 2회차 이후는 `google-translate.js` 가 센다 — 중복 없음.

## 2026-09

### "무엇이 코드인가" 를 접는 함수를 하나로 — 7벌 → 2함수 (2026-09-19)

[공허성 감사](guard-vacuity-audit-2026-09-18.md) 의 부수 발견을 실행했다. 같은 방어가
**7벌** 있었고 서로 동작이 달랐다. 같은 스니펫을 먹였을 때:

| 토큰 위치 | 줄-접두사 계열 (4벌) | tokenize 계열 (2벌) |
|---|---|---|
| 독스트링 안 | 유지 | 제거 |
| 끝주석 `X = 1  # TOKEN` | **유지** | 제거 |
| 문자열 안 `"a # TOKEN"` | 유지 | **제거** |
| 전줄 주석 | 제거 | 제거 |

**어느 쪽도 "정답" 이 아니라, 둘이 서로 다른 일을 하고 있었다.** 그래서 하나로 합치면
안 되고, 의미를 이름에 박은 **두 함수**가 맞다 (`scripts/lib/source_text`):

- `without_comments` — 주석·독스트링만 제거, **문자열 리터럴은 유지**. 찾는 대상이
  문자열 안에 사는 경우에 쓴다: CLI 플래그(`run_command(["ruff", "--fix"])`), URL,
  워크플로 명령.
- `code_tokens_only` — 주석 + **모든 문자열 리터럴** 제거. 문자열이 오탐인 경우에 쓴다:
  `symbol(` 호출 지점 탐색.

이 구분이 실제로 중요하다. `test_api_key_not_in_url` 은 URL 을 **f-string 으로 만드는**
코드를 찾으므로 `code_tokens_only` 로 옮겼다면 **가드가 공허해졌을 것**이다. 반대로
`test_inline_gate_registry` 는 문자열 속 `symbol(` 이 오탐이라 반드시 `code_tokens_only`
여야 한다.

둘 다 **같은 길이 공백으로 제자리 치환**한다 — `test_inline_gate_registry` 가 문자
오프셋으로 순서를 단언하고 `test_api_key_not_in_url` 이 줄 번호를 사람에게 보고한다.

**옮긴 곳 8군데**: 테스트 6개(`test_ci_soft_spot_triage_guard`,
`test_ci_ops_failure_issue_inlines_report`, `test_trend_single_source`,
`test_inline_gate_registry`, `test_ci_python_lint_gate`, `test_api_key_not_in_url`),
프로덕션 `check_secret_contract.code_consumers`, 도구 `probe_guard_vacuity`.

**폴백은 넣지 않았다.** 파싱 못 하는 입력에 대해 더 약한 fold 로 조용히 내려가면
호출자는 "검사하고 있다" 고 믿으면서 덜 검사한다 — 이 모듈이 없애려는 결함 그 자체다.
대신 `SyntaxError` 하나로 올린다. 여기서 실제 버그를 하나 잡았다: `tokenize.TokenError`
는 `SyntaxError` 의 하위 클래스가 **아니라서**(3.13 실측), 호출자가 쓴 자연스러운
`except SyntaxError` 가 미종료 문자열에서 크래시했을 것이다. 모듈이 변환해 올린다.

**검증** — 옮긴 가드 6건 전부 뮤테이션 프로브로 확인했다. 대조군 PASS + 변이 CAUGHT:

| 변이 | 결과 |
|---|---|
| `monthly-quality-report.yml` 에 미검토 `\|\| true` 추가 | CAUGHT |
| `ops-orchestrator.yml` dedup 을 날짜 완전일치로 원복 | CAUGHT |
| `content_generator.py` 에서 단언 호출 제거 | CAUGHT |
| `ops_health_orchestrator.py` 에 `ruff --fix` 재도입 | CAUGHT |
| URL 에 자격증명 f-string 삽입 | CAUGHT |
| 같은 문자열을 **주석 안**에 삽입 | 오탐 없음 (fold 가 과잉이 아님) |
| 퍼블리셔에서 게이트 호출 제거 | CAUGHT |

`scripts/tests/test_source_text.py` 가 위 표를 그대로 고정한다 — 양방향이다. 과소 접기는
산문이 가드를 만족시키고, 과대 접기는 살아있는 것을 죽었다고 선언한다.

`test_font_tier_split._strip_comments` 는 HTML 주석이라 범위 밖으로 두었다.


### Gemini 이미지 플래그 — 기본값 Flash 통일 + 래스터 경로 opt-in (2026-09-18)

"로컬 기본값을 Pro/Flash 중 어느 쪽으로 통일할지" 를 비용·품질 판단으로 열어 뒀는데,
실측하니 **문제가 Pro/Flash 가 아니었다.**

**세 갈래로 갈라져 있었다.**

| 위치 | 기본값 |
|---|---|
| `generate_post_images.py:146` | `"true"` → Gemini 3 Pro |
| `generate_missing_diagrams.py:42` | `"false"` → Gemini 2.5 Flash |
| `generate-images.yml` (2곳) | `'false'` → Flash |
| `docs/setup/MULTI_TOOL_HARNESS_ENV.md` | `true` |

**CI 는 애초에 Gemini 를 안 쓴다.** `use_api` 는 workflow_dispatch 입력이고 기본값이
`false` 라, push 트리거에서는 `GEMINI_API_KEY` 가 `''` 로 전달된다. 최근 12회 실행이
전부 push 였고 로그의 실제 출력은 `📝 Using SVG fallback generator (no API cost)` 다.
즉 CI 에서 이 플래그는 **API 호출에 도달한 적이 없다.** 비용·품질 비교가 성립하는
무대 자체가 없었다.

**진짜 문제는 로컬의 선점이었다.** `generate_post_images.py` 에서 Gemini 경로의 유일한
가드가 `if GEMINI_API_KEY:` 였다. 셸에 키를 export 해 둔 것만으로 (a) 이미지 API 를
호출하고 (b) 성공 시 `True` 를 반환해 그 아래 `if not image_generated:` 블록 —
**L20/L22/L25/rollup SVG 커버 생성기, honesty 스코어러, 블로킹 게이트 전부** — 를
건너뛴다. 포스트의 `image:` 는 `.svg` 를 가리키는데 성공한 Gemini 호출은
`<stem>.png` 를 쓰므로, 참조되는 SVG 는 생성되지 않는다.

**발화한 적은 없다.** 2026-09-18 실측: `image:` 가 해석되지 않는 포스트 **0건**. 기존
커버가 있으면 `has_image and not force` 에서 조기 반환하고 CI 는 키를 넘기지 않기
때문이다. 잠재 함정이지 사고가 아니다 — 다만 `--force` 로 다이제스트를 훑는 실행이
정확히 이걸 건드리고, CLAUDE.md 는 이미 그 명령을 **다른 이유로** 경고하고 있다.

**결정**
1. 기본값을 `false`(Flash)로 통일. Pro 는 `--use-pro-image` 또는 저장소 변수로 명시 요청.
2. 래스터 경로에 opt-in 게이트 `USE_GEMINI_IMAGE_API` / `--use-api` 추가 (기본 OFF).
   CI 동작은 불변 — `generate-images.yml` 이 같은 `api_check` 판정을 새 변수로도
   넘긴다. 이미 opt-in 이었으므로 의미가 바뀌지 않는다.
3. 문서 정정 (`MULTI_TOOL_HARNESS_ENV.md` 가 `true` 라고 적고 있었다).
4. Segment 스텝의 `USE_GEMINI_PRO_IMAGE` 제거 — 그 스텝의 스크립트
   `generate_segment_images.py` 는 아카이브돼 없고 워크플로가 warning 후 exit 0 한다.

**가드**: `scripts/tests/test_gemini_image_flag_defaults.py` 8건.

**뮤테이션 프로브가 내 가드의 결함을 잡았다.** 첫 판은 호출 지점 가드를
`"USE_IMAGE_API and GEMINI_API_KEY" in source` 부분문자열로 검사했는데, **같은 문자열이
로그 줄에도 있어서** 호출 지점을 원래 함정으로 되돌려도 통과했다. 오늘 세 번째로 같은
결함이다([`substring_scan_counts_comments_as_usage`](../CLAUDE.md)). `ast` 로 호출을
감싸는 `if` 조건을 직접 읽도록 고쳤다. 재프로브에서 7/7 전부 FAIL, 대조군 PASS.


### main 에 required status check 5개 — ruleset + Actions 봇 bypass (2026-09-18)

[이름 목록 통제 감사](name-list-control-audit-2026-09-18.md) 중 별개 관찰로 나왔다:
main 에 보호 설정은 있지만 **required status check 가 0개**였다 (force-push·삭제만
차단, enforce_admins=false, 필수 리뷰 없음).

**전제가 되는 제약이 하나 있다.** `ai-blogwatcher`·`generate-images`·
`vercel-firewall-backup`·`visual-baseline-refresh` 4개 워크플로가
`secrets.GITHUB_TOKEN` 으로 main 에 **직접 push** 한다 (최근 200 커밋 중 크론 봇
직접 push 24건). classic 브랜치 보호의 required check 는 push 자체를 거부하므로,
그대로 걸면 매일 발행이 멈춘다. 이 저장소는 이미
[`branch_protection_bot_token`](../CLAUDE.md) 로 같은 결론을 기록해 뒀다.

그래서 classic 보호가 아니라 **ruleset** 을 쓴다 — bypass actor 를 지정할 수 있는
유일한 수단이고, 이 저장소의 ruleset 은 0개였다. bypass actor 는 GitHub Actions 앱
(`actor_id: 15368`, `Integration`, `bypass_mode: always`).

한계를 분명히: **크론 산출물은 여전히 미검사**다. 기존 사각지대
([`ci_gates_blind_to_cron_bot_push`](../CLAUDE.md))가 유지된다는 뜻이고, 이 변경은
사람 PR 에만 게이트를 건다. 사각지대를 닫으려면 4개 크론을 PR 경로로 바꿔야 하는데,
blogwatcher 는 이미 신뢰 경계로 분기(외부 `repository_dispatch` → 브랜치+PR 격리,
스케줄 → main 직접 push)하고 있어 그 설계 결정을 뒤집는 일이 된다. 지금은 하지 않는다.

**자격 기준은 실측으로 정했다.** 최근 병합 PR 8건에서 체크별 결론을 수집했다.

| 걸 수 있음 (8/8 실제 결론) | 근거 |
|---|---|
| `ruff` | `python-lint.yml`, paths 필터·`if:` 없음 |
| `build` | `if:` 가 `github.event_name == 'pull_request'` 를 무조건 포함 — PR 에서 skip 불가 |
| `Security Audit Summary` | `if: always()` |
| `CodeQL` | `github-advanced-security` 앱의 집계 게이트 |
| `GitGuardian Security Checks` | 8/8 ok, 공개 저장소 시크릿 스캔 |

| 뺀 것 | 이유 |
|---|---|
| paths 필터 걸린 잡 13개 | **워크플로가 안 돌면 상태가 아예 보고되지 않아 PR 이 영구 pending.** `Validate action pin consistency` 가 표본 8건 중 **4건에서 미보고** 로 실측됐다 |
| `check-changes` | `jekyll.yml` 과 `security-audit.yml` 이 **같은 잡 이름**을 쓴다. 이름 매칭으로는 어느 쪽이 만족시켰는지 알 수 없다 |
| `Analyze (actions|javascript-typescript|python|ruby)` | 이름이 **탐지된 언어 목록에 결합**된다. Ruby 를 저장소에서 빼는 날 `Analyze (ruby)` 가 생산되지 않아 전 PR 차단 — A-H3 를 머지 큐에 조준한 셈. 집계 `CodeQL` 이 같은 판정을 담으므로 손실 없다 |
| `auto-merge`, `npm Security Audit`, `Ruby Gem Security Audit` | 표본 8/8 skip |
| `Vercel Preview Comments` | 품질 신호가 아니다 |

**중요한 구분**: 영구 pending 을 만드는 것은 잡의 `if:` 가 아니라 **워크플로 레벨
`paths:` 필터**다. `if:` 로 건너뛴 잡은 `skipped` 로 **보고된다** — `auto-merge`·
`npm Security Audit`·`Ruby Gem Security Audit` 가 표본 8건 전부에서 그랬다. 워크플로가
트리거되지 않으면 보고 자체가 없다.

`strict_required_status_checks_policy` 는 **false** 로 둔다. true 면 모든 PR 브랜치를
최신으로 강제하는데, #735 가 auto-merge 거짓 red 의 일부 원인을 리베이스가 형제 실행을
교착시킨 것으로 추적했다.

**required 목록 자체가 이름 목록이라서** UI 에만 두지 않고
`.github/rulesets/main-required-status-checks.json` 으로 선언하고
`scripts/check_required_checks_contract.py` + 테스트 18건이 검증한다. 생산하는 잡을
리네임하면 전 PR 이 영구 차단되는데, 그 변이가 뮤테이션 프로브 7종 중 하나로
확인됐다(대조군 PASS, 변이 FAIL).

**적용은 별도 단계다.** ruleset 생성(`POST /repos/.../rulesets`)이 세션 권한
분류기에 막혀 파일만 커밋했다. `--gh` 는 현재 `NOT APPLIED` 를 보고하며 적용 명령을
출력한다:

```bash
gh api --method POST repos/Twodragon0/tech-blog/rulesets \
  --input .github/rulesets/main-required-status-checks.json
python3 scripts/check_required_checks_contract.py --gh   # 적용·동기 확인
```


### A-H3 자기-재실행 차단이 무효였다 — 이름 목록에서 런타임 유도로 (2026-09-18)

`ops_health_orchestrator.py` 에 테스트를 붙이려다 발견했다. `check_github_actions`
는 `--auto-recover-gha` 로 실패한 워크플로를 자동 재실행하는데, **자기 자신과 형제
ops 루프는 재실행하면 안 된다** — 재실행하면 그 안에서 auto-recover 가 또 돌아
actions:write 를 쥔 자율 재실행 연쇄가 되기 때문이다 (2026-06-30 감사, A-H3).

차단 기준이 워크플로 이름 **리터럴 4개**였다:
`Ops Multi Agent Loop` / `Ops Priority Loop` / `Ultrawork Loop` / `AI Ops On Demand`.

**2026-09-18 실측: 4개 전부 현존 워크플로와 일치하지 않는다.** 넷이
`ops-orchestrator.yml` 하나로 통합되면서 `name:` 이 `Ops Orchestrator` 가 됐는데
목록은 갱신되지 않았다. `gh run list` 가 돌려주는 name 실측에서도 최근 15회 중 4회가
`Ops Orchestrator` 다. 즉 통합 시점부터 이 보안 통제는 **꺼져 있었다.**

사고가 안 난 이유는 보호받아서가 아니라 운이다 — 최근 50회 실행에서 Ops Orchestrator
가 실패한 적이 없다. 2026-03/04/06 에 쌓인 ops 실패 이슈 21건이 실패한다는 증거다.
`AUTO_RECOVER_GHA` 는 스케줄 경로에서 기본 `'true'` 라 크론이 실제로 플래그를 넘긴다.

**수정 — 두 겹으로 바꿨다.**
1. `GITHUB_WORKFLOW` (Actions 가 주입하는 실행 중 워크플로 이름). 유지보수가 필요
   없고 자기-재실행을 정확히 덮는다.
2. `SELF_RERUN_WORKFLOWS` (선언된 형제). 모든 항목이 실제 워크플로 `name:` 과
   일치하는지 `test_ops_health_orchestrator.py` 가 단언한다 — 이름을 바꾸면 CI 가
   죽지, 보호가 조용히 사라지지 않는다.

CLAUDE.md 의 "정규 문자열 게이트는 변형에 눈이 멀다" 가 그대로 재현됐다. 이번 변형은
오탈자가 아니라 **리팩터링으로 바뀐 이름**이었다. 교훈 갱신: 문자열 목록으로 대상을
지정하는 통제는 **그 문자열이 여전히 무언가와 일치하는지**를 테스트가 물어야 한다.

### ops_health_orchestrator.py 테스트 34건 신설 (2026-09-18)

6시간 주기 크론이 `actions:write` + `issues:write` 로 도는 코드인데 import 하거나
실행하는 테스트가 **0건**이었다 (`test_ci_python_lint_gate.py` 가 텍스트로 읽어
`ruff --fix` 금지만 검사). 위 A-H3 무효화가 첫 수확이다.

고정한 불변식: A-H3 차단(+공허하지 않음 대조군), `rerun_limit` 폭발 반경, `skipped`/
`cancelled`/`in_progress` 를 실패로 세지 않기(priority 레인이 크론 게이트 OFF 라
상시 `skipped` 를 낸다), 통과한 체크가 전역 priority 를 올리지 않기, **lint-and-types
만 blocking**(외부 서비스 장애로 크론을 red 로 만들면 그게 알림을 뮤트시키는 길이다),
빈 문자열 env 를 unset 으로 취급하지 않기(`${{ vars.X }}` 는 미설정 시 "" 로 렌더된다),
그리고 자격증명 값이 리포트에 도달하지 않기(#746 이후 리포트는 공개 이슈 본문에
인라인된다).

뮤테이션 프로브 11종 전부 대조군 PASS + 변이 FAIL.


### PAGESPEED_API_KEY 를 등록하지 않고 소비자를 제거한다 (2026-09-18)

시크릿 계약에서 유일하게 판정이 없던 이름이었다. 소비자는 셋 — `check_uiux()`
(`ops_health_orchestrator.py`), `monitor_vercel_builds.sh` 의 CWV 블록, 그리고
워크플로 참조 3개. 키는 한 번도 등록된 적이 없다.

**"안 쓰니까 지운다" 가 아니다. 등록하는 쪽이 해로웠다.** `check_uiux()` 는
`perf_score >= 0.75 and lcp_ms <= 2500 and cls <= 0.1` 로 판정하고 실패 시 **P1**
을 낸다. P1 은 ops 실패 이슈를 여는 조건이고 크론은 6시간 주기다. 그런데 그 세 항은
이 저장소가 이미 폐기했거나 더 엄격하게 대체한 것들이다 (`lighthouse.yml` 주석에
기록된 60회 실측):

| 조건 | 실측 | 판정 |
|---|---|---|
| `perf_score >= 0.75` | 동일 콘텐츠 60회에서 0.55~0.86 | "produced random red" 로 게이트에서 제거됨 |
| `lcp_ms <= 2500` | 이봉분포 4218~4373ms(55) / 6921~9695ms(5) | 두 봉우리 모두 임계값 초과 |
| `cls <= 0.1` | `lighthouse.yml` 이 0.05 로 게이트 중 | 중복이며 더 느슨 |

즉 이 키를 등록했다면, 방금 #746 에서 고친 이슈 파이프라인에 노이즈 P1 을
6시간마다 먹였을 가능성이 높다.

**기능 손실 없음.** CWV 는 `lighthouse-ci.yml`(PR, head 대 base LCP 5회 비교)과
`lighthouse.yml`(push+PR, CLS 0.05 절대 예산)이 잰다. 둘 다 현역이다.

**부수 발견 두 가지.**
- shell 쪽 블록은 `first-input-delay` 를 물었는데 그건 Lighthouse 감사 항목이 아니다
  (FID 는 필드 지표였고 INP 로 대체). 세 수치 중 하나는 애초에 N/A 만 나올 수 있었다.
- `monitor_vercel_builds.sh` 가 LCP/FID/CLS "Target Thresholds" 를 출력하고 있었는데
  비교하는 코드는 없었다. 재지 않는 목표를 출력하는 것이 게이트가 "강제하는 것처럼
  보이면서 아무것도 강제하지 않는" 전형이라 함께 제거했다.

**계약 검사기도 같이 고쳤다.** 제거 직후 `check_secret_contract.py` 가 "0 violations"
를 냈는데, `code_consumers()` 의 `git grep` 이 **제거 사유를 적은 주석 3개**를 소비자로
세고 있었다. 같은 날 AI Gateway 이름 3건이 가드 주석에만 남아 통과한 것과 같은 결함이다.
전줄 주석을 제외하도록 고쳤고, 살아있는 이름(VERCEL_TOKEN 등)이 여전히 잡히는지
대조군으로 확인했다. 한계는 명시해 뒀다 — docstring 본문의 언급은 여전히 소비자로
읽힌다(안전한 방향이다).

**되돌리는 조건:** PSI(구글 인프라) 쪽에서 수치가 안정적임을 실측하고, 반올림 숫자가
아니라 그 분포에서 유도한 임계값을 제시할 것. 위 60회는 GitHub 러너 Lighthouse/Lantern
이라 그대로 이전되지 않는다. 키 없는 PSI 요청은 2026-09-18 실측에서 HTTP 429(익명 쿼터
소진)였으므로 키 없이 되살리는 것도 불가능하다.


### 레거시 디제스트 19건의 섹션·번호를 복원하지 않는다

`restore_digest_structure` 의 R1/R4 가 과거 포스트를 손상시킨다는 것이 확인되어
(#737 에서 R7 로 차단), 후속으로 "화이트리스트 확장 + R4 항목번호 동기화" 를
검토했다. **하지 않는다.** 측정(2026-09-16, 224 포스트 코퍼스)이 제안 자체를
세 군데에서 무너뜨린다.

**1. R4 동기화는 대상이 없다.** 224 포스트 전부 `## N.` 번호열이 이미 1..N
연속이다(갭 0건). R4 는 **R1 이 방금 만든 구멍을 메울 때만** 발화한다. R7 이
R1 의 범위를 막은 시점에 R4 는 이미 no-op 이고, 밀린 재매김 부채는 없다.

**2. "섹션↔항목 번호 불일치 65건" 은 하나의 결함이 아니다.** 2026-02-01 에는
`### 2.1`, `### 3.1`, `### 4.1`~`4.7` 이 있는데 `## 2.`/`## 3.`/`## 4.` 헤딩이
**아예 없다**. 번호를 틀린 게 아니라 섹션 제목을 안 쓴 것이다. 항목을
`1.4, 1.5…` 로 재매김하면 서로 다른 네 주제가 한 섹션으로 합쳐진다 — 복원이
아니라 손실이고, 올바른 수리는 빠진 헤딩을 **새로 쓰는 것**이라 이 모듈의
"무손실 마커 변환" 헌장 밖이다.

**3. 화이트리스트는 19건 중 9건에만 닿고, 단독으로는 회귀를 만든다.**
미인식 섹션 제목 30종 중 22종이 1회성이고 대부분 기사 헤드라인이다
(`## 1. Ollama AI 서버 175,000대 인터넷 노출`). 즉 코퍼스에는 레거시 레이아웃이
둘 있다 — 카테고리별(`## N. 보안 뉴스`)과 **기사별**(`## N. <헤드라인>`). 후자
10 포스트는 화이트리스트로 표현할 수 없다. 나머지 9(카테고리명 5 + 번호형
부가섹션 4)를 풀도록 시뮬레이션하면 5 포스트가 변환 대상이 되는데, 그중
2026-01-24 에서 `## 🔗 관련 포스트` 가 `####` 로 강등된다 — **R7 은 번호매긴
`## N.` 만 검사하므로 번호 없는 닫는 섹션을 보호하지 못한다.**

**결정적 근거 — 아무 게이트도 이 포스트들을 문제 삼지 않는다.**

```
[digest-structure]         OK — 224 digest post(s) checked, 0 violations.
[digest-checklist-heading] OK — 224 digest(s), 0 violations.
```

확장이 풀어주는 5 포스트는 **전부 이미 통과 상태**다. 그러니 확장은 "아무도
불평하지 않는 포스트를 도구 자신의 내부 구조관에 맞추려고 다시 쓰는" 일이 된다.
이 저장소는 그 대가를 안다 — 재생성한 블롭은 영원히 남고, HEAD 트리 141 MB 에
저장소는 1,420 MB 다.

**앵커 위험**: 코퍼스 내 앵커 링크 39개 중 번호매긴 헤딩을 가리키는 것은 0건
(`#day-2026-04-XX` 롤업 앵커와 `#실무-체크리스트` 뿐). 다만 외부 유입 링크는
측정 불가이므로, 번호를 바꾸면 공개 앵커가 바뀐다는 잔여 위험이 남는다.

**재검토 조건** — 다음 중 하나가 참이 되면 이 결정을 다시 연다.
- `check_digest_structure` 또는 후속 게이트가 이 19건을 위반으로 잡기 시작한다.
- 생성기가 `## N. <헤드라인>` 레이아웃을 다시 내보내기 시작한다(그러면 레이아웃
  B 가 레거시가 아니라 현역이므로 스키마 쪽을 고쳐야 한다).
- 화이트리스트를 넓히는 별개 이유가 생긴다 — 그때는 **번호 없는 닫는 섹션
  (`## 결론`/`## 마무리`/`## 🔗 관련 포스트*`, 8건/6포스트/전부 ≤2026-02-01)을
  반드시 함께 처리한다.** 따로 하면 위 3번의 회귀가 그대로 난다.

재현: `python3 scripts/restore_digest_structure.py --dry-run --posts-glob '_posts/*.md'`

---

## 2026-09-21 — 09-19 직접 push 3건 사후 리뷰: 결함 2건 수정

`cf8d265a` / `fa2c46f8` / `9efefcd1` 은 PR 없이 main 에 들어왔다. 기존 가드와
충돌하지 않는 것은 확인됐지만 리뷰가 없었다. 사후 리뷰에서 결함 2건이 나왔고,
둘 다 고쳤다.

### Finding 1 — `--workers 4` 가 전역 소켓 타임아웃을 경합으로 만들었다

`socket.setdefaulttimeout` 은 **프로세스 전역**이다. `fetch_rss_feed` 가 피드마다
저장/복원하고 있었는데, 수집이 순차일 때는 무해했다. `9efefcd1` 이 두 프로덕션
호출자(`ai-blogwatcher.yml`, `morning_autopost_cron.sh`) 모두에 `--workers 4` 를
넣으면서 경합이 됐다.

첫 번째 재현 시도는 **실패했다**. 모든 스레드가 같은 값을 쓰므로 대부분의
인터리빙이 무해하기 때문이다. 순서를 직접 구성해야 나온다 — `old=15` 를 읽은
스레드가 마지막에 끝나는 경우:

```
T1 폴백 시점에 본 값: 15.0   T1 복원: None
T2 폴백 시점에 본 값: None   ← 아직 받아오는 중인데 타임아웃이 사라졌다
T2 복원: 15.0
종료 후 전역값: 15.0         ← 누수
```

결정론적이 아니라 **순서 의존**이다. 소스 30여 개에 워커 4면 자주 나지만,
테스트는 순서를 구성해야지 우연에 기대면 안 된다.

영향 둘. (1) 아직 받아오는 중인 스레드가 전역값이 `None` 으로 돌아간 것을 보면,
per-call 타임아웃이 없는 유일한 경로인 `feedparser.parse(url)` 폴백이 무한정
돈다 — 10초 타임아웃을 넣은 이유가 바로 그 행이었다. `ai-blogwatcher.yml` 은
`timeout 480` 으로 스텝 전체를 막지만 `morning_autopost_cron.sh` 는 외곽 제한이
없고 `|| true` 라, 거기서는 크론이 조용히 멈춘다. (2) 수집이 끝나도 전역값이
샌다.

수정: `fetch_rss_feed` 에서 조작을 없애고, `fetch_all_news` 가 풀 시작 전 1회
설정하고 `finally` 에서 복원한다. 모든 호출자가 같은 값을 쓰므로 동치다.
가드: `scripts/tests/test_collect_tech_news_thread_safety.py`.

### Finding 2 — 참고자료 헤딩의 두 번째 표기에 소비자 넷이 눈이 멀었다

`content_generator` 가 상호참조가 있으면 `## 관련 포스트 및 참고 자료`, 없으면
`## 참고 자료` 를 낸다. 변형은 옛 문자열을 **부분문자열로 포함하지 않는다**.

실측: 변형을 단 포스트 **13건 전부**가 `## 참고 자료` 를 갖고 있지 않았고,
`enrich_digest_references` 는 13/13 에서 섹션이 없다고 보고했다. 수정 후 13/13
을 찾고 13/13 이 실제 수정 대상이 된다(수정 적용은 별건).

CLAUDE.md 가 이름 붙여 둔 실패다 — *a content gate keyed to one exact string is
blind to the variant*. **"세 군데에 문자열 하나씩 더 적기"는 답이 아니다.** 목록만
길어진 같은 결함이고, 실제로 네 번째 소비자에서 그대로 재발했다.

`scripts/lib/digest_headings.py` 하나를 만들고 생산자 1 + 소비자 4 가 전부 읽게
했다.

### 이번에 드러난 진짜 교훈 — 멤버십 드리프트 가드는 단방향이다

`restore_digest_structure` 는 `backfill_digest_structure.transform_body` 의
function-local 정규식을 **손으로 복사**해 갖고 있었고, "두 정의가 갈라지면
실패시킨다"는 드리프트 가드가 붙어 있었다. 그 가드는 고정 목록의 각 원소가
양쪽에 들어 있는지만 봤다. 멤버십 검사는 한쪽에만 원소를 **추가**하면 통과한다.
실제로 이번에 backfill 에만 변형을 추가했고 가드는 통과했다.

구성한 케이스로 결과를 확인했다 — restore 가 변형을 섹션 경계로 보지 못해
아이템 영역이 닫히지 않았고, 참고자료 섹션 안의 `###` 소제목이 `####` 로
강등됐다. 다만 **코퍼스에서는 아직 미실현**이다: 변형 13건은 참고자료 섹션에
소제목 없이 표만 쓰므로 옛/새 정규식의 restore 출력이 동일하다(0건 차이).
도달 가능하되 아직 터지지 않은 결함이다.

고친 방식은 목록을 늘리는 게 아니라 **사본을 없앤 것**이다. 정규식을
backfill 쪽 모듈 레벨로 올리고 restore 가 import 한다. 가드는 멤버십에서
`is` 동일성 단언으로 바꿨고, 정규식만 보면 공허해지므로 두 표기 각각에 대해
결과로 확인하는 테스트를 함께 뒀다.

**일반화: 사본을 동기화하는 가드보다 사본을 없애는 편이 낫다.** 동기화 가드를
쓸 수밖에 없다면 양방향이어야 한다 — 고정 목록 멤버십은 추가를 못 본다.

뮤테이션 프로브 4건(A: 전역 조작 재도입, B: 사본 부활, C: enrich 옛 문자열,
D: native_sections 옛 문자열) 전부 대조군이 깨끗한 채로 CAUGHT.

---

## 2026-09-21 — 참고자료 보강은 배선된 적이 없었다 (stale 30건)

#763 에서 변형 표기 14건을 보강한 뒤, 옛 표기 쪽 stale 을 판단하려고 재면서
원인이 드러났다. **`enrich_digest_references.py` 는 어디에서도 호출되지
않았다** — 워크플로 0, 훅 0, 파이프라인 0.

2026-08-06 에 5건 파일럿(#507)으로 들어왔고, 누군가 2026-01~07 을 백필했다.
그 뒤로는 사람이 기억해서 돌려야 했다. 용도 칼럼 보유 현황(2026-09-21 실측):

```
2026-01  보유  2 / 없음  7      2026-05  보유 30 / 없음  0
2026-02  보유 13 / 없음  9      2026-06  보유 30 / 없음  0
2026-03  보유 19 / 없음  9      2026-07  보유 30 / 없음  0
2026-04  보유 30 / 없음  0      2026-08  보유  6 / 없음 25   ← 백필 이후
                                 2026-09  보유 14 / 없음  5
```

**생성기는 용도 칼럼을 내보내지 않는다.** 이 스크립트가 유일한 생산자이므로,
배선이 없으면 발행되는 모든 다이제스트가 결손 상태로 태어난다. 그날 아침
발행된 09-21 다이제스트도 born-stale 이었다 — 내가 #763 을 머지한 **뒤에**
발행됐는데도 그렇다. 스크립트를 고치는 것과 돌게 만드는 것은 다른 일이다.

### 적용 판단

무손실 실측 — **옛 표기 stale 29건**을 대상으로: URL 소실 0, 삭제 토큰 0,
표 행 +191 순증, 29/29 가 "용도 칼럼 신설"이고 삭제는 없다. 순수 가산이라 적용했다.

적용은 **30건**이다. 위 29건에 변형 표기 stale 1건(09-21, 그날 아침 발행분)을
더한 값이다. 두 숫자가 섞이기 쉬우므로 분리해 적는다 — `+191` 과 `29/29` 는
29건의 측정치이지 30건의 것이 아니다.

2026-08-06 에 기각했던 13건과 혼동하지 말 것 — 그쪽은 참고자료 섹션 자체가
없는 레거시이고, 그때 기각 이유는 변형 쪽이 canonical 보다 **이미 풍부**해서
수정이 churn 이라는 것이었다. 이번 30건은 성격이 반대다.

### 배선 — 자가치유가 아니라 무조건 실행 + 사후조건

형제 pre-flight 들(`restore_digest_structure`, `rewrite_template_echo_summaries`)
은 전부 "게이트 실패 → 자가치유 → 재검증/차단" 형태다. 보강은 여기 맞지 않는다:
**용도 칼럼 부재를 실패시키는 검사기가 없다.**

그렇다고 코퍼스 전역 검사기를 새로 만들면 태어날 때부터 red 다. 레거시 13건은
참고자료 섹션이 없고 01~03 월에도 칼럼 없는 포스트가 남아 있다. CLAUDE.md 의
규칙 그대로 — **휴면 게이트는 배선 전에 돌려서 출력을 읽을 것.** 그래서 새
게이트를 만들지 않고, 그날 발행분 하나에만 거는 **포스트 범위 사후조건**으로
했다: 참고자료 섹션이 있는가 + 용도 칼럼이 실제로 생겼는가. 후자가 없으면
스텝이 no-op 으로 끝나도 통과하는데, 30건이 쌓인 방식이 정확히 그것이다.

배선은 코퍼스 게이트 **앞**에 둔다. 뒤에 두면 그날 발행분은 보강 전 상태로
검사받는다.

### 전체 스위트가 잡아낸 것

코퍼스 30건을 바꾸자 `test_index_scoring::test_non_index_scores_byte_identical`
이 1건 실패했다 — `2026-08-14`, 93 → 94. 원인은 포스트가 392 → 401 줄로 늘어
`length` 세부점수가 400줄 임계를 넘은 것이다. **회귀가 아니라 개선**이므로
`scripts/regen_quality_baseline.py` 로 재생성했다(diff 2줄, 상승 1건, 신규·제거 0).

30건을 바꿨는데 점수가 움직인 건 1건뿐이라는 게 중요하다. "많이 바꿨으니
baseline 을 통째로 갱신하자"가 아니라, **무엇이 왜 움직였는지 확인한 뒤**
재생성했다. 관련: 메모리 `regen_quality_baseline_stale_cron`,
`digest_checklist_score_inflation`("복원 후 baseline 실패는 회귀 아님").

뮤테이션 프로브 5건 전부 대조군 깨끗한 채 CAUGHT — 사후조건 공허화(E),
스텝 삭제(F), `|| true` 무력화(G), 사후조건 제거(H), 순서 뒤바꿈(I).

---

## 2026-09-21 — 배선 없는 코퍼스 스크립트 전수 조사: 두 번째 enrich 는 없다

#764 이후 "고쳤지만 안 돈다"가 더 있는지 전수로 쟀다. 결론부터: **없다.**
코드 변경 없음.

### 감사기 자체의 오판을 먼저 고쳤다

첫 판은 "호출처 0" 을 단순 grep 으로 셌고, `scripts/lib/digest_headings.py`
**docstring 의 언급**을 호출처로 셌다. 메모리에 있는 그 함정이다
(`substring_scan_counts_comments_as_usage`). 공용 fold(`without_comments`)로
접고 다시 세자 고아가 37 → 42 로 늘었다 — 8개가 주석에 가려져 있었다.

감사 도구도 게이트와 같은 규칙을 받는다: **인용과 사용을 구별하지 못하는
스캔은 정리를 잘 할수록 더 눈이 먼다.**

### 판별 기준

"호출처 0" 자체는 결함이 아니다. 대부분은 일회성 마이그레이션 도구고, 수동인
게 맞다. enrich 계열인지를 가르는 것은 하나다 — **생성기가 만들지 않는 것을
만들어서, 새 포스트가 결손 상태로 태어나는가.** 그래서 최근 생성 다이제스트
(2026-09, 19건)에 dry-run 으로 돌려 실측했다. 쓰기·네트워크·이미지 작업은
제외했고, 부작용 0(변경 파일 0) 확인했다.

### 결과

| 스크립트 | 최근 19건 대상 | 판정 |
|---|---|---|
| `backfill_digest_native_sections` | **0/19 변경** | 생성기가 흡수. 완료된 캠페인 |
| `backfill_card_summary_period` | 0/19 | 완료 |
| `rewind_truncated_summaries` | 0/19 | 완료 |
| `migrate_summary_cards_to_frontmatter` | 19 skipped | 완료 |
| `backfill_digest_titles` | 0/229 | 완료 |
| `fix_code_block_languages` | 0 | 완료 |
| `fix_unclosed_code_blocks` | 305 clean | 완료 |
| `add_missing_tags` | 0 | 완료 |

**사용자가 지목한 `backfill_digest_native_sections` 는 같은 계열이 아니다.**
0/19 다. 생성기가 native section 을 이미 내보내므로 배선이 없는 게 맞다.

### 배선하면 안 되는 것 2건 (실측 근거)

- **`trim_front_matter`** — 304/305 를 바꾸겠다고 하지만 enrich 계열이 아니라
  **파괴적 정규화기**다. excerpt 를 150자로 자르고 `keywords:` 를 삭제한다.
  CLAUDE.md 의 front matter 규격은 excerpt 를 **150-200 chars** 로 적고 있어
  이 도구의 상한이 문서와 충돌한다. 게다가 excerpt 는 지금 게이트 14
  (`check_excerpt_promises`)가 본문과 대조하는 대상이다. 배선 금지.
- **`backfill_digest_commentary --no-llm`** — 2026-09 6건에 돌리면 문단 6개가
  나오는데 **꼬리 문장이 1종**이다(6/6 동일). 게이트 11
  (`check_post_boilerplate`)이 막으려고 만들어진 바로 그 모양이다. 배선 금지.

### 판단 보류 1건

> ⚠️ **아래 문단은 틀렸다.** 결손이 아니라 305/305 가 이미 필드를 갖고 있고,
> 갱신은 이득이 0 이 아니라 음수다. 같은 날 "add_last_modified_at 기각" 항목에서
> 정정했다. 이 문단은 판단 경로를 남기려고 보존한다 — 인용하지 말 것.

- **`add_last_modified_at`** — 304/305 가 대상이고, 이건 실재하는 결손이다.
  `sitemap.xml:47,72` 과 `_includes/head.html:115` 이 `last_modified_at` 을
  실제로 읽는다(없으면 `page.date` 로 폴백). 다만 front matter 304건 일괄
  추가는 `check_front_matter_growth` 게이트가 있는 영역이고, 폴백이 동작하므로
  당장 깨진 것은 없다. **이득(SEO lastmod 정확도) 대비 churn 을 재기 전에는
  손대지 않는다.** 착수한다면 먼저 셀 것 — 실제로 본문이 수정된 적 있는
  포스트가 몇 건인지. 전부 `date == last_modified_at` 이면 이득이 0 이다.

---

## 2026-09-21 — `add_last_modified_at` 기각 (직전 노트의 판단 보류를 정정한다)

바로 앞 노트에서 이 스크립트를 "304/305 가 대상이고 **실재하는 결손**"으로 적고
판단을 보류했다. **두 군데가 틀렸다.**

### 정정 1 — 결손이 아니다. 305/305 가 이미 필드를 갖고 있다

dry-run 의 `Changed/Added : 304 / Kept (manual) : 1` 을 "304건에 필드를 추가"로
읽었는데, 실제로는 **값을 갱신**한다는 뜻이었다. 실측: `last_modified_at` 을 가진
포스트 **305/305**. 없는 포스트는 0건이다.

합산 라벨 하나를 읽고 구성을 확인하지 않은 결과다. 세어 보면 5초였다.

### 정정 2 — 이득이 0 이 아니라 음수다

값은 `git log -1 --format=%cI -- <file>` 이다. **이유를 불문하고 파일을 마지막에
건드린 커밋**이다. 갱신 대상 304건을 유발한 커밋을 전건 분류했다:

```
106x  fix(seo): 4월 통합 정리 + 죽은 내부 링크 파이프라인 복구 …  (#711)
 41x  fix(ci,seo): … closer 1 문장 교체                        (#716)
 39x  fix(digest): 근접중복 카드요약 66건 제거                  (#714)
 30x  fix(digest): 참고자료 보강 stale 30건 백필                (#764)  ← 오늘, 내 작업
 14x  fix(scripts): 변형 헤딩 다이제스트 14건 참고자료 보강      (#763)  ← 오늘, 내 작업
 58x  perf(posts): elevate N posts to 9X+ …                   (일괄 품질 패스)
 16x  기타 일괄 패스
```

**304/304 가 일괄 기계 패스다. 사람이 쓴 독자 대상 개정은 0 건이다.**

그중 **44 건은 오늘 날짜로 찍힌다** — 표에 `용도` 칼럼 하나가 생긴 것 때문에.
`sitemap.xml:47,72` 이 이 값을 `<lastmod>` 로 내보내므로, 크롤러에게 "이 44개
페이지가 오늘 갱신됐다"고 말하게 된다. 독자가 보는 변화는 표 칼럼 하나다.

그러니 이건 churn 대비 이득을 재는 문제가 아니었다. **이득 자체가 음수다.**
현재 값은 낡았지만 안정적이고, 낡고 안정적인 lastmod 가 매 기계 패스마다
갱신되는 lastmod 보다 낫다.

### 결정: 기각. 배선도 하지 않고 수동 실행도 하지 않는다.

`page.date` 폴백(`sitemap.xml` 의 `| default: page.date`)이 이미 동작하므로
깨진 것도 없다.

**재검토 조건** — 다음이 참이 되면 다시 연다.
- 스크립트가 타임스탬프를 **본문 변경 커밋**에서만 유도하도록 바뀐다. 커버·
  front matter·표만 바뀐 커밋을 제외해야 하는데, 그 판정 자체가
  `scripts/lib/source_text` 급의 별도 작업이다.
- 사람이 실제로 포스트 본문을 개정하는 일이 생긴다. 지금 코퍼스에는 그 사례가
  마지막 커밋 기준 0 건이다.

### 일반화 — 이번에 두 번 같은 실수를 했다

합산 라벨(`Changed/Added : 304`)과 건수(`304/305 가 대상`)를 **결손의 근거로
읽었다.** 둘 다 "무엇이 왜 그런가"를 세기 전의 숫자였고, 세어 보니 방향이
반대였다. 같은 날 `enrich` 판단에서는 dry-run diff 본문을 읽고 무손실을 측정한
뒤 진행했는데, 여기서는 요약 줄만 보고 "결손"이라고 적었다.

**규칙: 건수는 판단 근거가 아니다. 그 건수를 만든 원인을 분류하기 전까지는.**
관련: `dont_tail_a_gate_output`(잘라 읽지 말 것),
`digest_reference_section_missing_13_rejected`("부재" 진단은 스캔의 산물일 수 있다).

---

## 2026-09-21 — 배선 금지 2건을 문서에서 통제로 옮겼다

전수 조사(#765)에서 "배선하면 안 된다"고 판단한 2건이 `notes/` 에만 있었다.
다음 사람이 같은 dry-run 숫자를 보고 같은 판단을 반복한다 — 이 저장소가 이미
여러 번 치른 비용이다. 옮기면서 근거를 다시 쟀고, **직전 노트의 논거 하나가
틀린 것도 확인했다.**

### `backfill_digest_commentary --no-llm` — 런타임 거부 (실제 통제)

`--no-llm` 은 결정론적 가짜 문단을 만든다(`_fake_commentary`). 2026-09 여섯
건에 돌리면 문단 6개의 **꼬리 문장이 1종**이다.

실측으로 두 가지를 확인했다.

1. **`--no-llm --commit` 은 실제로 쓴다.** 세 포스트를 대상으로 돌려 1건이
   쓰였다(2건은 이미 섹션 보유로 멱등 skip). 311행이 무조건 write 다.
2. **하류 게이트가 잡지 못한다.** 그 상태로 `check_post_boilerplate --all` 을
   돌리니 **exit 0** 이었다. 게이트 11 은 Mermaid 펜스와 체크리스트를 비교하지,
   `## 분석가 시점` 문단을 보지 않는다.

막을 수 있는 지점이 소스뿐이므로 `main()` 이 그 조합을 거부한다.
`--no-llm --dry-run` 은 그대로 동작한다(대조 테스트로 고정).

### `trim_front_matter` — 배선 부재 + 측정치를 docstring 에

304/305 를 바꾸겠다고 보고하지만 backlog 가 아니다. 바뀌는 것 둘 다 저장소가
다른 곳에서 내린 결정에 대한 회귀다.

- **excerpt 150자 절단** — CLAUDE.md 규격은 `150-200 chars`. 305건 중 288건이
  150자를 넘고 **그중 287건이 문서화된 150-200 범위 안**이다. 자르면 287건을
  규격 **밖으로** 밀어낸다.
- **`keywords:` 삭제** — 300/305 가 보유하고 `_includes/head.html:79` 가 읽는다
  (`page.keywords | default: page.tags`). 삭제하면 300페이지의 meta keywords
  출처가 조용히 큐레이션 목록에서 raw tags 로 바뀐다.

**정정** — 직전 노트에서 "excerpt 는 게이트 14 가 본문과 대조하는 대상"이라는
것을 논거로 들었다. 과했다. 다섯 건에 `--fix` 를 적용하고 돌려 보니
`check_excerpt_promises` 는 **그대로 통과**했다(305 clean). 위 두 가지가 근거이고,
게이트 충돌은 근거가 아니다.

도구의 `FIELD_LIMITS` 자체를 고치는 것은 별개 판단이라 손대지 않았다.

### 가드가 나를 두 번 잡았다

- `test_the_reason_is_recorded_where_the_reader_is` 가 `backfill_digest_commentary`
  헤더에 근거를 안 적은 것을 잡았다. 스크립트를 연 사람이 테스트 파일까지
  찾아가지는 않으므로, 사유는 스크립트 안에 있어야 한다.
- **뮤테이션 프로브가 코퍼스에 썼다.** 거부를 제거한 상태로 `--commit` 을
  `_posts/` glob 에 돌렸고, 09-10 포스트에 가짜 문단 + `last_modified_at` 변경이
  들어갔다. `git diff --stat` 으로 발견해 되돌렸다.

  두 번째가 더 중요하다 — **검사가 자기가 막으려는 사고를 일으켜서는 안 된다.**
  가드 테스트도 `_posts/` 를 직접 가리키고 있었으므로, 거부가 회귀하는 순간
  테스트 자신이 같은 짓을 한다. `tmp_path` 에 사본을 두고 그것만 가리키는
  fixture 로 바꿨다. 거부를 제거한 채 재프로브해 **코퍼스 변경 0건**을 확인했다.

뮤테이션 프로브 4건 전부 대조군 깨끗한 채 CAUGHT — 거부 제거(J), 워크플로 배선(K),
거부를 `--dry-run` 까지 확대한 과잉 차단(L, 대조 테스트가 잡음), 샌드박스 검증(J2).

---

## 2026-09-21 — `trim_front_matter` 한계값 화해 시도: 전제가 틀렸다

"`FIELD_LIMITS["excerpt"]` 를 CLAUDE.md 규격 200 으로 맞추고 `keywords` 삭제를
빼면 도구를 살릴 수 있는가"를 쟀다. **살릴 수 없다. 숫자 문제가 아니었다.**

그리고 그 재검토 조건을 적은 것이 나다 — 직전 PR(#767)의 docstring 에
"150-200 으로 맞추면 다시 열라"고 썼다. 그대로 따랐다면 같은 손상을 더 큰
숫자로 출시했을 것이다. 조건을 정정했다.

### excerpt — 200 으로 올려도 서술어가 잘린다

200 상한에서 초과는 4건뿐이다(288 → 4). 그런데 **4/4 가 닫는 서술어를 잃는다.**

```
before (204):  … 주요 보안 이슈와 DevSecOps 실무 대응 포인트를 주차 단위로 종합 정리합니다.
after  (197):  … DevSecOps 실무 대응 포인트를 주차 단위로...
```

`truncate_at_word` 는 `rfind(" ")` 로 자른다. 한국어는 어절 사이에 공백이
있으므로 공백이 안전한 절단점이 **아니다** — 문장은 서술어로 끝나고, 그 앞
공백에서 자르면 부사어만 남는다. 아끼는 글자는 7~43자이고, 대가는 목록
페이지·RSS·구글 결과에 나가는 줄이 깨지는 것이다.

### description — 작은 문제가 아니라 아예 무의미하다

`_includes/head.html:56` 이
`{% assign raw_description = page.excerpt | default: page.description %}` 이고
**305/305 가 excerpt 를 갖고 있다.** `page.description` 은 렌더링되지 않는다.
한계값 초과 159건을 다듬어도 아무도 보지 않는다.

### 남는 것은 `image_alt` 하나

> ⚠️ **아래 문단은 수치도 결론도 틀렸다.** 정규식이 작은따옴표 YAML 스칼라를
> 잘못 벗겨 29건/109자로 셌고, YAML 로 파싱하면 44건/112자/91단어 소실이다.
> 그리고 80 에는 외부 근거가 없다. 같은 날 "image_alt 도 기각" 항목에서
> 정정했다. 이 문단은 판단 경로를 남기려고 보존한다 — 인용하지 말 것.

80 초과 29건, 최대 109. 이 필드는 접미사를 붙이지 않고(`suffix=""`), alt 텍스트는
잃을 서술어가 없다. 이 도구가 하는 일 중 방어 가능한 것은 이것뿐이다.

### 통과한 게이트를 근거로 쓰지 말 것

절단 후에도 `check_excerpt_promises` 는 통과한다(150 상한 5건, 200 상한 4건,
양쪽 다 305 clean). **중립이 아니라 더 나쁘다** — 절단이 닫는 주장을 파괴하므로
게이트가 **더 쉽게** 통과한다. 여기서 게이트 통과는 품질 근거가 아니다.

직전 노트에서 "excerpt 는 게이트 14 가 대조하는 대상"을 논거로 든 것도
이것 때문에 틀렸다. 이미 #767 에서 정정했고, 여기 측정으로 확정한다.

### 가드를 두 번 고쳤다 — 두 번째가 중요하다

1. 서술어 어미를 접미사로 찾는 초안은 오탐을 냈다. `남겼습니다. 다음...` 에서
   다음 어절의 `다` 를 서술어 끝으로 읽었다.
2. "원문의 마지막 문장이 온전히 남는가" 로 바꿨더니 **뮤테이션을 놓쳤다.**
   문장 경계 절단기로 교체해도 10건 전부 통과했다 — 마지막 문장을 통째로
   버리는 것과 중간에서 자르는 것을 구별하지 못하기 때문이다. 그 검사의 존재
   이유가 바로 "재검토 조건이 충족됐다"는 신호인데, 정확히 그걸 못 봤다.

   **대조군만 보고 넘어갔으면 몰랐다.** 뮤테이션을 넣어 봤기 때문에 드러났다.

끝 모양(`말줄임표를 걷어낸 뒤 문장 종결부호로 끝나는가`)으로 보면 갈린다:

```
현재 절단기(공백 기준)    150자   0/288,  200자 0/4  가 문장으로 끝남
문장 경계 절단기          150자 270/288,  200자 4/4  가 문장으로 끝남
```

### 결정

한계값을 바꾸지 않는다. 배선도 하지 않는다(#767 가드 유지). 재검토 조건을
**"숫자를 고쳐라"에서 "문장 경계로 자르는 절단기를 쓰거나 excerpt 처리를 빼라"**
로 정정했고, 그 조건이 충족되면 새 가드가 실패해서 알려 준다.

---

## 2026-09-21 — `image_alt` 도 기각. `trim_front_matter` 는 남은 일이 없다

직전 노트에서 `image_alt` 를 "이 도구가 하는 일 중 방어 가능한 유일한 것
(80 초과 29건, 최대 109)" 이라고 적었다. **수치도 결론도 틀렸다.**

### 수치 — 정규식이 작은따옴표 스칼라를 잘못 벗겼다

`^image_alt:\s*"?(.*?)"?\s*$` 로 읽고 있었다. 큰따옴표만 처리하므로 작은따옴표
값에서는 따옴표가 값에 섞이고 non-greedy 매칭이 일찍 멈춘다. YAML 로 파싱하면:

```
              정규식   YAML
80 초과        29건  →  44건
최대 길이     109자  → 112자
사라지는 단어  49개  →  91개
```

`excerpt` 쪽 수치(288 / 4, 절단 후 문장 종결 0건)는 **우연히 일치했다.** 우연은
근거가 아니므로 가드의 추출기를 `yaml.safe_load` 로 바꿨다.

같은 조사에서 "값이 따옴표로 시작하는 포스트 41건" 을 데이터 이상으로 의심했는데,
그것도 같은 정규식 결함이었다. 정상 YAML 인용이다.

### 결론 — "서술어가 없으니 안전하다" 가 틀렸다

영어 alt 텍스트에 잃을 서술어가 없는 것은 맞다. 사라지는 것은 **의미**다.

```
container supply chain attacks digest  →  container supply
prompt injection defense digest        →  prompt injection
```

그리고 **80 에 외부 근거가 없다.** 이 필드에 길이를 강제하는 곳은 저장소 안에
`sitemap.xml:94` 의 `truncate: 160` 하나뿐이고, 가장 긴 값이 112 로 이미 그 아래다.
`og:image:alt`(head.html:184), `twitter:image:alt`(head.html:211), 그리고 실제
렌더링되는 `<img alt>`(_layouts/post.html:140) 는 아무 제한도 걸지 않는다.
80 은 excerpt 의 150 과 똑같이 이 파일이 스스로 고른 숫자다.

마지막으로 `<img alt>` 는 **접근성 표면**이다. CLAUDE.md 가 WCAG 2.1 AA 를
선언하고 있으므로, 자체 상한을 맞추려고 alt 를 덜 서술적으로 만드는 것은 정리가
아니라 회귀다.

**세 필드 모두 실패한다. 이 도구에는 방어 가능한 남은 일이 없다.**

### 같은 자리에서 세 번 틀렸다 — 패턴을 적어 둔다

`trim_front_matter` 하나를 두고 판단을 세 번 정정했다.

1. "excerpt 150 이 문제다, 200 으로 올리면 된다" → 200 에서도 4/4 가 깨진다
2. "게이트 14 가 대조하니 근거가 된다" → 절단해도 통과한다(오히려 더 쉽게)
3. "image_alt 는 방어 가능하다" → 44건에서 91단어가 사라지고 근거가 되는 상한이
   애초에 없다

세 번 모두 같은 모양이다 — **남은 이득을 재지 않고 "이건 괜찮겠지" 로 넘겼다.**
매번 재 보니 방향이 반대였다. 앞의 `add_last_modified_at` 교훈("건수는 원인을
분류하기 전까지 근거가 아니다")의 변형이고, 여기서는 **"범위를 좁힐 때마다 다시
재라"** 가 맞는 규칙이다. 좁혀진 범위는 새 주장이지 앞선 측정의 따름정리가 아니다.

가드도 한 번 더 고쳤다. `test_trimming_an_excerpt_...` 의 "마지막 문장이 온전한가"
판은 문장 경계 절단기로 교체해도 통과했다 — 재검토 조건 충족을 알리는 것이 그
검사의 목적인데 정확히 그걸 못 봤다. 끝 모양으로 바꾸니 갈린다(공백 절단기
0/288·0/4 vs 문장 절단기 270/288·4/4).

뮤테이션 프로브 O(image_alt 상한 무력화)·P(sitemap truncate 를 100 으로 낮춤)
모두 대조군 깨끗한 채 CAUGHT.

---

## 2026-09-22 — front matter 정규식 파싱 전수 조사

#769 에서 내 감사기가 작은따옴표 YAML 스칼라를 잘못 벗긴 것이 드러났다. 같은
결함이 프로덕션에도 있는지 전수로 쟀다. **눈으로 고르지 않고**, 각 파일의 정규식
리터럴을 AST 로 뽑아 큰따옴표/작은따옴표 두 표본에 실제로 돌려 판별했다.

### 결과 — 3개 파일, 5개 패턴

```
scripts/auto_publish_news.py          ^title: / ^excerpt:   작은따옴표 → 따옴표째 추출
scripts/regen_l20_digest_covers.py    ^title: / ^excerpt:   작은따옴표 → 따옴표째 추출
scripts/seo_inject_related_links.py   ^title:               작은따옴표 → None
```

코퍼스 실측: `title` 작은따옴표 **51건**(2025-04 ~ 2026-02, 이후 0건),
`image_alt` 39건, `description` 19건, `excerpt` **0건**.

### 지금 터지지 않는 이유 — 세 겹이고, 전부 우연이 아니다

1. `auto_publish_news` 는 **방금 생성한 포스트**만 처리한다. 생성기는
   `title: "{yaml_title}"` 로 큰따옴표를 하드코딩하므로 작은따옴표가 나올 수 없다.
2. `regen_l20_digest_covers` 와 `seo_inject_related_links` 는 **미배선**이다
   (2026-09-21 전수 조사). 수동 실행에서만 51건/9건이 걸린다.
3. 제목 안의 따옴표는 `sanitize_quotes_for_yaml` 이 전부 작은따옴표로 정규화한다.

### 진짜 발견 — 3번이 단언된 적이 없었다

`[^\n"]+` 는 값 안의 `"` 를 만나면 멈춘다. 이스케이프된 큰따옴표가 든 제목이면
매치가 **통째로 실패**하고, 그러면 `post_info_for_l20["title"]` 이 초기값 빈
문자열로 남는다(본문이 `---` 로 시작하므로 그 폴백 조건도 거짓이다).

재현했다 — 빈 제목으로 L20 을 부르면 커버는 **정상 생성되고**(28 KB) 헤드라인만
`Security Update` 라는 일반 문구로 바뀐다. 실패가 아니라 **조용한 치환**이다.
커버 정직성 게이트를 가진 저장소에서 제목이 소리 없이 사라지는 셈이다.

그 경로가 닫혀 있는 이유는 정규식이 견고해서가 아니라 sanitizer 때문이다. 즉
**생산자와 소비자가 한 가정을 공유하는데 그 가정을 아무도 단언하지 않았다.**
`test_auto_publish_sanitize.py` 는 sanitizer 의 *동작*만 검사했고, 그것이 커버
제목 추출의 전제라는 사실은 어디에도 없었다. 이 저장소가 이미 대가를 치른 모양이다
(`producer_gate_must_import_one_fold`).

### 한 일

정규식을 고치지 않았다. 발행 경로의 hot path 이고 지금 옳게 동작하며, 세 겹 중
어느 것도 오늘 깨져 있지 않다. 대신 **결합을 걸었다** —
`TestCoverTitleExtractionDependsOnSanitizer` 가 sanitizer 를 통과한 제목이
프로덕션 정규식으로 복원되는지 확인한다. 정규식은 사본을 두지 않고
`auto_publish_news.py` 소스에서 읽어 온다(사본을 두면 저쪽이 바뀌어도 옛 패턴을
계속 통과시킨다).

대조군도 함께 뒀다 — sanitizer 를 거치지 않은 제목은 실제로 추출에 실패해야 한다.
정규식이 견고해지면 이 단언이 깨져서 "결합이 풀렸다"고 알려 준다.

뮤테이션 프로브 Q(sanitizer 를 항등함수로)·R(정규식을 `(.+?)` 로 견고하게) 모두
대조군 깨끗한 채 CAUGHT.

### 남긴 것

`regen_l20_digest_covers` 9건, `seo_inject_related_links` 51건은 **고치지 않았다.**
둘 다 미배선이라 자동으로 돌지 않고, 손대면 커버 재생성 블롭이 따라온다
(CLAUDE.md: 2,930 이미지에 29,177 리비전). 수동으로 돌릴 일이 생기면 그때
정규식부터 고칠 것.

---

## 2026-09-22 — 스케줄러 지연 베이스라인이 3배 낡아 있었다

`ai-blogwatcher` 가 선언 스케줄(`0 0 * * *`)보다 늦게 도는 것을 문서화하려다,
이미 그 일을 하는 도구(`check_cron_firing.py`, #630)가 있고 **그 docstring 의
수치가 낡았다**는 것을 발견했다.

### 측정

그 docstring 은 "this repo's scheduler is 30-100 minutes late as its normal
baseline" 이라고 단정하고, 근거로 `deploy-pages`(`30 0 * * *`)의 5일치 시작
시각(01:57 / 02:09 / 02:07 / 02:01 / 02:08Z, 즉 87~99분)을 들었다.

2026-09-22 재측정 — 13개 워크플로, 7일 윈도:

```
lag 전체 범위               118 ~ 409 분
워크플로별 min lag 중앙값        272 분
워크플로별 max lag 중앙값        328 분
deploy-pages (그 근거 자체)  262 ~ 286 분   (당시 87~99분)
```

**추세가 아니라 변동이다.** `ai-blogwatcher` 월별 중앙값: 31(06월) → 110(07월)
→ 61(08월) → 133(09월)분. "상시 140분" 이라고 적는 것도 틀린 말이 된다 — 내가
처음에 4건만 보고 그렇게 말했고, 90건으로 늘리니 전체 중앙값은 110분이었다.

### 무엇을 고쳤나 — 숫자를 다시 적지 않았다

CLAUDE.md 가 세 번 대가를 치르고 적어 둔 규칙이 있다: **읽어도 행동이 달라지지
않는 수치는 적지 말 것.** 여기에 새 밴드를 적으면 한 달 뒤 같은 상태가 된다.

그래서 docstring 을 이렇게 바꿨다.
- 옛 수치는 **그 시점 값으로** 남기고, 지금 3배 낡았다는 사실과 근거를 붙였다.
- 낡지 않는 것만 단정한다 — 몇 시간의 침묵은 정상이고, 선언 윈도 안에 런이
  없다는 것은 증거가 아니며, `DEFAULT_SETTLE_HOURS` 가 "늦음"과 "유실"을 가른다.
- **재계산 명령을 docstring 에 넣었다**(`--json` 파이프). 이 스크립트는 이미
  워크플로별 `min/max_lag_minutes` 를 내보내고 있었다 — 인용할 게 아니라 부를 것.
  적어 넣은 명령은 실제로 돌려서 동작을 확인했다.

### 가드

`test_check_cron_firing.py` 의 `SETTLE = timedelta(hours=18)` 은 **하드코딩**이었다.
프로덕션 `DEFAULT_SETTLE_HOURS` 를 6으로 내려도 "매우 늦은 실행은 누락이 아니다"를
증명하는 시나리오들이 18시간으로 계속 통과한다 — 증명하는 내용과 프로덕션 동작이
갈라지는 조합이다. 프로덕션 상수에서 가져오도록 바꾸고,
`test_settle_keeps_margin_over_observed_lag` 로 관측 최악 lag(409분) 대비 2배
여유를 단언했다. 현재 2.6배. 뮤테이션(6시간으로 인하) CAUGHT.

여유가 2배 아래로 내려가면 **드롭 보고를 시작할 게 아니라 상수를 올려야 한다.**
늦은 것과 잃은 것을 혼동해 PR #629 를 틀린 전제로 정당화한 전례가 있다.

### 보고하지 않은 것

같은 감사에서 `ops-orchestrator.yml 27/35`, `security-audit.yml 0/1` 이 보였지만
**누락으로 보고하지 않는다.** 이 스크립트 자신의 docstring 과 메모리
`cron_firing_audit_false_drops` 가 기록하듯, `gh run list` 는 일관된 읽기가 아니고
같은 이력 10회에 4가지 판정이 나온 적이 있다. 단일 읽기에서 나온 결손은 증거가
아니다.

---

## 2026-09-22 — 배선 첫 실측 통과. 그리고 #762 → #764 순서는 우연이 아니었다

### 실측: 크론이 배선된 보강 스텝을 통과했다

세션 내내 미결이던 항목. 오늘 런 `35679618806` 이 **02:29:04Z** 에 발화해
(선언 `0 0 * * *` 대비 **+149분**, 어제 +145.8분과 일치) success 로 끝났다.

```
success  Reference-table enrichment (enrich, then verify)
success  Corpus gate pre-flight (block)
success  Commit and publish
```

스텝이 green 인 것은 효과의 근거가 아니므로 로그와 산출물을 직접 봤다:

```
[enrich-references] rewrote 1/1 post(s).
[enrich-references] OK — _posts/2026-09-22-…Threat_AI_Data_Go.md carries the 용도 column.
```

발행된 포스트가 변형 헤딩(`## 관련 포스트 및 참고 자료`)과 `| 리소스 | 링크 | 용도 |`
를 **둘 다** 갖고 있다. 코퍼스 전체 재점검: **enrich 가 고칠 것이 남은 포스트 0건**
(230 다이제스트). 배선이 유지되고 있다.

### 대조: #762 이전 로직이었다면

오늘 포스트에 옛 정확문자열(`^## 참고 자료$`)을 돌리면 **매치 없음**이다.
즉 #762 이전이었다면 보강이 "섹션 없음"으로 건너뛰어졌을 것이고, 오늘 포스트도
born-stale 이었다.

더 중요한 것은 그 다음이다. **#762 없이 #764 만 배선했다면 발행이 막혔을 것이다.**
사후조건 1번이 "참고자료 섹션이 있는가" 이고, 공용 모듈이 없었다면 그 검사도
리터럴로 썼을 것이기 때문이다. 해당 포스트는 현재 **16건**(전부 2026-09)이고,
생성기가 변형을 계속 내보내므로 매일 늘어난다.

순서가 역이었다면 증상은 "자가치유 스텝이 매일 exit 1" 이었을 것이다. 메모리
`cron_corpus_gate_selfheal_deadlock`(자가치유가 게이트보다 앞이어야 한다)과 같은
계열이고, 이번엔 **정의를 먼저 통일한 덕에** 피했다.

일반화: **게이트를 배선하기 전에, 그 게이트가 읽는 문자열의 정의가 생산자와
하나인지 먼저 확인할 것.** 배선은 정확성을 만들지 않고 증폭한다.

### 수치 정정

이 점검을 제안하면서 변형 헤딩을 "13→15건" 이라고 적었는데 **16건**이다
(#763 시점 14건 + 09-21·09-22 발행 2건). 셈이 틀렸다.

### 한 일: 없음

코퍼스는 깨끗하고(stale 0), 배선은 동작하며, 대조도 설명된다. 만들 것이 없어
노트만 남긴다.

---

## 2026-09-22 — ruleset 적용 불가 확정: 계정 유형 게이트 둘

#750(2026-09-18)에서 선언한 `main` ruleset 이 나흘간 "적용 대기" 로 남아 있었다.
오늘 실제로 POST 해 보고 **왜 안 되는지가 확정됐다.**

```
evaluate + bypass        422  Actor GitHub Actions integration must be part of
                              the ruleset source or owner organization
evaluate + bypass 없음   422  Enforcement evaluate option is not supported on
                              this plan. Please upgrade to Enterprise.
```

| 설계가 요구한 것 | 실제 |
|---|---|
| `bypass_actors` = GitHub Actions(Integration, 15368) | **조직 소유 저장소 전용.** 이 저장소는 `owner.type = User` |
| `enforcement: evaluate` | **Enterprise 플랜 전용** |

둘 다 결제로 풀리는 문제가 아니라 계정 유형 문제다 —
`secret_scanning_toggles_silent_noop`(Secret Protection 이 조직 전용)과 같은 계열이고,
이 저장소에서 두 번째로 같은 벽에 부딪힌 것이다.

두 POST 모두 **검증 단계에서 거부**돼 아무것도 생성되지 않았다(`rulesets` → `[]`).

### 내 보고가 틀렸던 지점

세션 내내 "ruleset 적용은 제가 실행할 수 없습니다(권한 classifier 거부)" 로
보고했다. 세션 초반에는 실제로 classifier 가 막았지만, **그게 유일한 장애물인 것처럼
말한 것이 틀렸다.** 오늘 POST 는 classifier 를 통과했고 GitHub 이 거부했다.
"내가 못 한다" 와 "이 계정에서는 안 된다" 는 다른 말이고, 나흘 동안 전자로만
보고하는 바람에 후자를 확인하는 일이 미뤄졌다.

**교훈: 막혔다고 보고하기 전에 한 번은 끝까지 밀어 볼 것.** 대리 실행을 요청하는
제안을 반복하는 것보다, 실패 메시지 하나가 훨씬 많은 것을 알려 준다.

### 적용 가능한 유일한 형태와, 그것이 깨뜨리는 것

`active` + `bypass_actors: []` 는 검증을 통과할 것이다. 그리고 **일일 발행을 멈춘다.**
`ai-blogwatcher` 는 `GITHUB_TOKEN` 으로 main 에 직접 push 하고(오늘 발행 커밋
`97976d5b`, actor `github-actions[bot]`), required check 가 걸린 브랜치에 직접
push 하면 체크를 만족시킬 방법이 없다. bypass 가 있던 이유가 정확히 이것이므로,
**이 형태로 켜지 않는다.** 실행하지 않았다.

### 선택지 (사람 판단 필요)

1. 봇에게 PAT / GitHub App 토큰 발급 — `branch_protection_bot_token` 이 기록한
   경로. 현재 시크릿에 해당 토큰 **없음**(2026-09-22 확인). 시크릿 신규 발급이라
   §5(A) 정지 대상이다.
2. 발행을 PR 경로로 전환 — required check 가 자연히 만족되지만 발행 지연이 늘고,
   봇-push 전제 위에 선 기존 기록들(`cron_posts_get_no_notifications`,
   `ci_gates_blind_to_cron_bot_push`)의 전제가 바뀐다.
3. 그대로 둔다 — 강제가 없을 뿐, 현재 PR 은 전부 5개 체크를 통과하고 있고 실질
   위반은 관측되지 않았다.

### 살아남는 측정

어느 선택지든 아래는 유효하다(2026-09-22).

- **유령 체크 이름 없음**: 요구 5개가 1파일짜리 문서 전용 PR(#772)에서도 5/5 pass.
  `skipping` 으로 끝나는 `npm Security Audit`·`Ruby Gem Security Audit`·`auto-merge`
  는 요구 목록에 없다.
- **bypass actor id 는 맞았다**: `gh api /apps/github-actions` →
  `slug=github-actions id=15368`. 틀린 것은 id 가 아니라 개인 저장소에서 그 actor
  를 선언할 수 없다는 점이다.

---

## 2026-09-22 — required check 강제 방향: **그대로 둔다.** 단 내가 든 근거는 틀렸었다

### 먼저 정정 — "실질 위반 미관측" 은 거짓이었다

직전 보고에서 "그대로 둔다가 유력합니다(현재 PR 전부 5개 체크 통과, 실질 위반
미관측)" 라고 적었다. 앞 절은 맞고 **뒷 절은 틀렸다.** 최근 main 커밋 100건의
유입 경로를 세어 보면:

```
PR 머지(squash)      76건
봇 직접 push         16건
사람 직접 push        8건   ← ruleset 이 막았을 대상
```

8건이 있다. 그중 셋(`cf8d265a`, `fa2c46f8`, `9efefcd1`)이 바로 이 세션을 시작하게
한 09-19 커밋들이고, 거기서 결함 2건이 나왔다. "위반이 없다" 가 아니라
**"내가 PR 체크만 보고 직접 push 를 세지 않았다"** 였다.

### 그런데 세어 보니 결론은 같고, 이유가 달라졌다

직접 push 커밋에 실제로 무엇이 돌았는지 쟀다. (`gh run list --commit` 은 대조군
커밋에서도 0건을 반환한다 — 메모리 `gh_run_sha_filters_silently_return_zero` 대로
못 쓴다. `--json headSha` 로 받아 클라이언트에서 필터링했다.)

```
cf8d265a (직접 push)   Python Lint success · Jekyll site CI success · CodeQL success
9efefcd1 (직접 push)   Python Lint success · Jekyll site CI success · CodeQL success
5f48434f (PR 머지)     Python Lint success · Jekyll site CI success · CodeQL
```

push 이벤트 전체로도 `Python Lint` 29/29, `Jekyll site CI` 29/29 success 다.

즉 **요구 5개 중 3개(ruff·build·CodeQL)는 직접 push 에서도 이미 돈다.**
진짜로 빠지는 것은 `GitGuardian`(PR 전용, 그러나 native push protection 이 그
경로를 덮는다 — 이 세션 초반 실측)과 **사람 리뷰**뿐이다.

**그리고 09-19 커밋의 결함 2건을 잡은 것은 리뷰였지 5개 체크 중 어느 것도
아니다.** 소켓 타임아웃 경합도, 헤딩 변형 실명도 ruff·build·CodeQL 이 잡을 수
있는 종류가 아니다.

`required_status_checks` 는 리뷰를 요구하지 않는다. **관측된 문제에 맞는 도구가
아니다.**

### 결정

**선택지 3(그대로 둔다).** 근거는 "위반이 없어서" 가 아니라:

1. 요구 5개 중 3개가 직접 push 에서도 이미 실행된다(29/29).
2. 빠지는 `GitGuardian` 은 native push protection 이 같은 경로를 덮는다.
3. 실제로 결함을 잡은 것은 리뷰이고, 이 rule type 은 리뷰를 강제하지 않는다.
4. 적용 가능한 유일한 형태(`active` + bypass 없음)는 일일 발행을 멈춘다.

### 파일은 **제거하지 않는다**

`main-required-status-checks.json` 에는 살아 있는 소비자가 있다 —
`check_required_checks_contract.py` 가 pytest 에서 그 5개 이름이 여전히 생성
가능하고 `paths:` 필터에 걸리지 않는지 검사한다(`OK — 5 context(s), all
producible, none paths-filtered`). 지우면 **작동 중인 가드가 사라진다.**

ruleset 이 적용되지 않아도 그 검사는 의미가 있다: 언젠가 켤 수 있게 되는 날
(조직 이전, PAT 도입 등) 이름이 썩어 있으면 모든 PR 이 영구히 막힌다. 그 이름들을
계속 살려 두는 것이 이 파일의 현재 역할이다.

`.github/rulesets/README.md` 에 적용 불가 사유와 남은 선택지를 적었고,
`docs/troubleshooting/GITHUB_ACCOUNT_TYPE_GATES.md` 에 같은 벽에 세 번째로
부딪히지 않도록 계정 유형 게이트를 모았다.

---

## 2026-09-23 — 미검토 직접 push 5건 사후 리뷰: 전건 결함 없음

09-19 배치 3건은 이 세션 초반에 리뷰해 결함 2건을 찾았다. 나머지 5건은 리뷰된 적이
없어 마저 봤다. **다섯 건 모두 결함 없음.**

| 커밋 | 내용 | 확인한 것 |
|---|---|---|
| `3839c048` | 아카이브에서 이미지 3개 복원 | 3/3 이 포스트에서 실제 참조되고 파일 존재 |
| `bc168110` | 문서만(CLAUDE.md + cover-system 스킬) | 코드 변경 없음 |
| `e6e65601` | 워크플로 3개 `fetch-depth: 0 → 1` | 아래 |
| `cf644e88` | 교차참조 + 품질 점수 | baseline 과 실제 점수 3/3 일치(전부 99) |
| `53e9e922` | vitest 4 → 5 메이저 범프 | 아래 |

**`e6e65601`** — 커밋 메시지가 "이 셋은 history 명령을 안 쓴다" 고 주장한다.
믿지 않고 쟀다: `generate-images` / `monthly-quality-report` / `vercel-deploy`
모두 history 명령 0건이다. 반대 방향도 봤다 — merge-base 를 쓰는 잡
(`jekyll/build`, `svg-lint/lint`)은 여전히 `fetch-depth: 0` 이다. 정확한 변경이다.

**`53e9e922`** — 로컬에서 `npm test` 가 738 passed 를 냈지만 **그 검증은 공허했다**:
`node_modules` 가 낡아 vitest **4.1.10** 으로 돌고 있었다(선언은 `^5.0.0`).
`npm ci` 로 lock 대로 설치하니 5.0.0 이고, 그 상태에서 30 files / 738 tests 전건
통과한다. lock 도 5.0.0 으로 고정돼 있다. 같이 들어간 파이썬 변경은 타입 내로잉
(`assert _m is not None`)으로 동작 동일하고, baseline 94→99 는 같은 커밋의 품질
상향과 일치한다.

### 내가 만들어 낸 가짜 구멍 하나

리뷰 도중 "`vitest.yml` 이 `pull_request` 전용이라 직접 push 인 `53e9e922` 는 착지
시점에 JS 검증을 못 받았다" 고 판단했다. **틀렸다.** 파일 앞 20줄만 읽고 `on:` 블록
전체를 보지 않았다 — `push: branches: [main]` 이 같은 paths 로 함께 있다. 실측하니
`53e9e922` 에 대한 push 이벤트 vitest 런이 있고 **success** 다(09-08T15:21).

이 세션이 반복해서 경고한 그 함정을 내가 또 밟았다(`dont_tail_a_gate_output`).
**트리거를 주장하기 전에 `on:` 을 파싱해서 볼 것** — `sed -n '1,20p'` 로는 알 수 없다.

### 09-21 vitest 실패는 별건이다

`vitest.yml` 최근 실행 중 하나가 failure 인데, 브랜치는
`dependabot/npm_and_yarn/js-minor-patch-16a205b317` 이고 실패는
`certification-quiz.test.js` 의 `expected undefined to be defined` 1건이다
(1 failed / 29 passed). main 은 vitest 5 에서 전건 통과하므로 **이 범프의 문제가
아니라 그 PR 의 문제**다. 이번 리뷰 범위 밖으로 남긴다.

### 그래서 강화할 것이 있는가 — 없다

직접 push 8건 중 결함은 09-19 배치 3건에만 있었고, 그것도 리뷰가 잡았지 CI 가 잡을
수 있는 종류가 아니었다(소켓 경합, 헤딩 변형 실명). 나머지 5건은 CI 가 정상적으로
덮었고 실제로 green 이었다. 직전 결정("required check 강제는 관측된 문제에 맞는
도구가 아니다")을 뒤집을 근거가 이번 리뷰에서 나오지 않았다.

---

## 2026-09-23 — ruleset JSON 을 자기설명하게

`main-required-status-checks.json` 은 머지 후 나흘 동안 "적용 대기" 로 오해됐고,
실제로는 적용 **불가능**이었다. README 를 안 열고 파일만 보는 사람이 그대로 POST
하지 않도록, JSON 에 `_comment` 키로 경고를 실었다(JSON 은 주석을 지원하지 않는다).

담은 것: 적용 불가 사유(조직 소유 전용, 422 원문), `owner.type=User` 라는 근거,
bypass 없이 active 로 켜면 발행이 멈춘다는 경고, 그럼에도 파일을 지우면 안 되는
이유(계약 검사기가 5개 이름의 생존을 검사한다), README 위치, 그리고 실제 적용 시
`jq 'del(._comment)'` 로 걷어내라는 지시.

추가 키가 계약 검사기를 깨지 않는 것은 먼저 확인했다(18건 그대로 통과).
경고가 조용히 사라지지 않도록 `test_the_ruleset_file_says_it_is_not_applied` 가
존재와 필수 토큰 3개(`README.md`, `owner.type=User`, `del(._comment)`)를 단언한다.
뮤테이션(키 제거) CAUGHT.
