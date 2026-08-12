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
