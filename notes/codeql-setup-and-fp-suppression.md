# CodeQL 설정 현황 + false-positive 처리 방침

**Status:** 확정 (2026-07-28) · owner 결정 = "현실 문서화 + dismiss 의존"
**관련:** memory `codeql-high-fp-triage-2026-07-28`, `codeql_large_diff_false_attribution`

---

## 1. 현재 설정: default setup (중요)

CodeQL은 GitHub **default setup**으로 동작한다.

```bash
gh api repos/Twodragon0/tech-blog/code-scanning/default-setup \
  --jq '{state, languages, query_suite}'
# → {"state":"configured","query_suite":"default","languages":[...]}
```

- `.github/workflows/`에 codeql-action 워크플로가 **없다** (advanced setup 아님).
- **default setup은 `.github/codeql/codeql-config.yml`을 사용하지 않는다.** query suite 선택만 가능하고 custom `paths-ignore`/`query-filters`는 무시된다.
- 따라서 `codeql-config.yml`은 현재 **dead 파일**이다. 여기에 suppression을 추가해도 **no-op**이며, "보호받고 있다"는 **착각을 유발**한다 (그래서 파일 상단에 경고 배너를 달아 둠).

## 2. FP 처리 방침 = dismiss

default setup에서 FP를 억제하는 **유일하게 실효적인** 수단은 알림 dismiss다.

```bash
gh api repos/Twodragon0/tech-blog/code-scanning/alerts/<N> -X PATCH \
  -f state=dismissed -f dismissed_reason="false positive" \
  -f dismissed_comment="<근거, ≤280자>"
```

- dismiss는 **alert fingerprint로 유지**된다 → 재분석에서 같은 FP가 떠도 자동으로 dismissed 상태가 유지된다. 플래그된 라인이 실질적으로 바뀌지 않는 한 재발하지 않는다.
- 즉 이미 dismiss한 FP는 "재발 방지"가 사실상 완료된 상태다.

## 3. 처리 완료된 FP (2026-07-28, 전건 dismiss)

env-key(예: `DEEPSEEK_API_KEY`)가 모듈에 존재하면 CodeQL이 인접 텍스트/파일 sink를
credential로 **과광범위 taint**하는 heuristic FP 패턴. 코드 수정 불필요:

| # | rule | 위치 | 근거 |
|---|------|------|------|
| #276 | py/bad-tag-filter | `scripts/dev/check_csp_inline_hashes.py:64` | first-party head.html만 파싱하는 dev/CI 게이트, sanitizer 아님 |
| #282 | py/clear-text-logging-sensitive-data | `scripts/news/content_generator.py:2591` | 로그값=공개 뉴스 제목(text[:40]), 키는 Authorization 헤더로만 |
| #283 | py/clear-text-storage-sensitive-data | `scripts/retranslate_digest.py:232` | 저장값=번역 digest 마크다운, 키는 translate() 반환값에 미포함 |

결과: **0 open high/critical** (검증: `gh api .../code-scanning/alerts?state=open`).

## 4. 향후: advanced setup 전환 (owner 결정 필요, 현재 미실행)

config 기반 `query-filters` 억제가 정말 필요해지면(예: 위 heuristic FP가 새 파일에서
빈발) advanced setup으로 전환한다:

1. Settings → Code security → CodeQL → default setup 해제.
2. `.github/workflows/codeql.yml` 추가 (github/codeql-action, SHA 핀), `config-file: ./.github/codeql/codeql-config.yml` 지정.
3. `codeql-config.yml`의 `query-filters`에 `- exclude: { id: py/clear-text-logging-sensitive-data, ... }` 형태로 경로 한정 억제 추가.

**트레이드오프:** advanced setup은 analysis 워크플로 유지보수 부담 + 스캔 트리거/스케줄 직접 관리 + 보안 포스처 변경. 현재는 dismiss만으로 충분하다고 판단하여 **전환하지 않음**.
