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
