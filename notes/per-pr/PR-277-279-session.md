# Session Summary: PR #277 ~ #279 & Production Issues (2026-04-21 ~ 2026-04-22)

**Date:** 2026-04-21 ~ 2026-04-22  
**Lead:** Writer Agent (a0339dbce5efae8fc)  
**Branch:** `feat/digest-quality-gate` (current)  
**Context:** Multiple PR handling, production diagnostics, digest image regeneration (72 SVGs)

---

## 1. PR 처리 이력

| PR | Branch | Status | Files | Notes |
|---|--------|--------|-------|-------|
| #275 | docs/notes-pr-254-272 | OPEN | - | PR #254-272 session record + ROCm cell fix; 조사 대상이었으나 본 세션에서 merge 미실행 |
| #276 | feat/digest-quality-gate | CLOSED (obsolete) | 1 | `digest_quality_report` pre-publish gate; PR #274와 중복 기능, 다른 구현 방식 충돌 (`check_file()` vs `_run_digest_quality_gate()`) → **close 권고** |
| #277 | fix/entity-cleanup-09-17-and-05-30 | **MERGED** | 8 | Vercel preview=false 복원 + 2025-10-31 HTML entity 파일명 정리; 2개 redirect 추가 |
| #278 | fix/adsense-403-graceful-fallback | OPEN | 1 | AdSense 403 graceful fallback (5초 타임아웃 후 슬롯 숨김) |
| #279 | feat/regenerate-images-card-signal-map | OPEN | 72 | 72개 digest SVG 재생성 (Jan 23 ~ Apr 20, 2026) |

**PR #277 Merge Details:**
- Commit: `a36eadc5` (`fix(deploy): enable Vercel preview builds...`)
- 8 파일 변경, redirect 2개 추가 (`_redirects` 업데이트)
- Vercel preview deployment 빨간불 해결 (deployment 객체 0ms errored 상태 원인 → preview=true 복원)

---

## 2. 로컬 브랜치 (Push 미실행)

| Branch | Status | Commits | Purpose |
|--------|--------|---------|---------|
| `fix/entity-cleanup-09-17-and-05-30` | Local only | 6 | 2025-09-17 ampquot 정리 + 2025-05-30 고아 이미지 삭제 + HTML entity pre-commit hook 구현 (테스트 60개 추가, 총 855개) |

**상태:** Push 대기 중. PR #277 머지 후 생성 권장.

---

## 3. Production 이슈 진단

### 3.1 CSP 오류 (sentry-cdn.com)
**증상:**  
- Browser 콘솔: `bundle.min.js.map` 차단 (CSP violation)
- 원인: `https://browser.sentry-cdn.com/` → browser.sentry-cdn.com, cdn.jsdelivr.net 필요

**진단 결과:**  
- Origin/main에 이미 fix 존재 (commit `0f3bb6d8`, PR #267: CSP sentry source map, AdSense empty gap, OG preload warning, severity blockquote cleanup)
- Production 배포가 stale (이전 커밋 기반)
- **해결:** PR #277 머지 → Vercel 재배포 예상

### 3.2 AdSense 403 오류 (ca-pub-6788271437088974)
**증상:**  
- AdSense 슬롯 로드 실패 (403 Forbidden)
- 원인: Google 서버측 이슈 (계정/도메인 승인 상태 불명확)

**진단 결과:**  
- 코드 side에서 fix 불가능 (Google 정책 이슈)
- **현재 대응:** PR #278 (graceful fallback) — 5초 타임아웃 후 슬롯 숨김
- **추천:** 사용자가 Google AdSense 대시보드에서 계정/도메인 승인 상태 확인 필수

**PR #278 Details:**
- 파일: `_includes/adsense-slot.html`
- 변경: timeout 5초 후 슬롯 display:none
- 1개 파일, 최소 변경

---

## 4. 이미지 재생성 (PR #279)

### 4.1 개요
- **도구:** `scripts/regenerate_generator_digest_svgs.py`
- **포맷:** card-signal-map (scripts/news/svg_generator.py::generate_card_signal_svg)
- **범위:** 72개 digest SVG (2026-01-23 ~ 2026-04-20)

### 4.2 재생성 범위 상세

| Period | Date Range | Count | Details |
|--------|------------|-------|---------|
| Jan | 01-23 ~ 01-31 | 9 | 2026-01-23 to 31 |
| Feb | 02-01 ~ 02-28 | 28 | 2026-02 전체 |
| Mar | 03-01 ~ 03-31 | 29 | 2026-03 전체 |
| Apr (partial) | 04-02~05, 09~14, 20 | 13 | 2026-04-02/03/04/05, 09/10/11/12/13/14, 20 |
| **Total** | | **72** | |

### 4.3 레퍼런스 제외 (건드린 안 함)
- `2026-04-06/07/08` (32-39KB legacy diverse format, reference)
- `2026-04-15/16/17/18/19` (card-signal-map reference, 이미 재생성됨)

### 4.4 배치 전략
- 5개씩 15배치 ralph loop 위임
- 각 배치: 1개 커밋 (atomic, 1개 범위)
- 예: "feat(images): regenerate 2026-01-23 to 2026-01-27 digest SVGs to card-signal-map format"

### 4.5 현재 상태
- **최신 머지:** `82e434f9` (2026-04-14 to 04-20)
- **PR #279 상태:** OPEN, 15 atomic 커밋 완료

---

## 5. 주요 학습 & 발견 사항

### 5.1 Vercel Preview=false 빨간불 원인
**발견:**  
- `preview: false` 설정 시 deployment 객체는 등록되지만 response code 0ms로 errored 처리
- GitHub check가 red로 표시됨 (false positive)

**해결:**  
- `preview: true` 복원
- PR #277에서 수정됨

### 5.2 HTML Entity 이중 인코딩 잔재
**발견:**  
- 과거 파일명에 `amplsquo`, `amprsquo`, `ampquot`, `ampamp` 패턴 존재
- 원인: smart quote → `&lsquo;` → `&amp;lsquo;` (이중 인코딩) → 파일명 잔재

**현재 대응:**  
- Pre-commit hook 구현 (로컬 브랜치: `fix/entity-cleanup-09-17-and-05-30`)
- 테스트 60개 추가, 총 855개
- 향후 재발 방지

### 5.3 Gemini CLI 환경 제약
**발견:**  
- Gemini CLI OAuth: cloudcode-pa API only 지원
- `GEMINI_API_KEY` 플레이스홀더만 가능 (실제 키 설정 불가)

**대안:**  
- AI 생성 필요 시 Claude API 또는 Claude CLI 사용

### 5.4 Agent 브랜치 오염 위험
**발견:**  
- 백그라운드 에이전트가 의도와 다른 브랜치에 커밋할 수 있음
- 사례: `fix/entity-cleanup-09-17-and-05-30` 브랜치에 hook 커밋 섞임

**권장사항:**  
- 에이전트 프롬프트에 "브랜치 X에 커밋" 명시
- 세션 시작 시 checkout 단계 강제

---

## 6. 남은 작업 & 인수인계

### 6.1 PR 머지 대기
- [ ] PR #278 머지 (AdSense 403 fallback)
- [ ] PR #279 머지 (72개 digest SVG)
- [ ] PR #276 close (obsolete)

### 6.2 로컬 작업
- [ ] `fix/entity-cleanup-09-17-and-05-30` push (6 커밋)
- [ ] PR 생성 (HTML entity pre-commit hook)
- [ ] 로컬 테스트: `pytest scripts/tests/` 통과 확인

### 6.3 추가 작업 (별도 전략 필요)
- [ ] Non-digest 포스트 46개 이미지 재생성
  - 현재: 카드-신호맵 포맷 72개만 완료
  - 필요: diverse 포맷, 기타 SVG 재생성

### 6.4 사용자 수동 작업
- [ ] Google AdSense 대시보드 확인 (계정/도메인 승인 상태)
- [ ] Production 배포 상태 모니터링 (PR #277 머지 후)

---

## 7. 주요 통계

| 항목 | 수치 | 비고 |
|------|------|------|
| PR 처리 | 4 | #275(조사), #276(close), #277(merge), #278/279(pending) |
| 파일 변경 | 8 + 72 + 1 | PR #277(8), PR #279(72 SVG), PR #278(1) |
| 로컬 커밋 | 6 | `fix/entity-cleanup-09-17-and-05-30` |
| 테스트 추가 | 60 | HTML entity pre-commit hook |
| 이미지 재생성 | 72 | Card-signal-map format (Jan 23 ~ Apr 20) |
| 배치 수 | 15 | 5개씩 atomic 커밋 |

---

## 8. 참고 커밋

| Commit | Message | Branch |
|--------|---------|--------|
| `a36eadc5` | fix(deploy): enable Vercel preview builds and clean HTML entity remnants (#277) | main |
| `82e434f9` | feat(images): regenerate 2026-04-14 to 2026-04-20 digest SVGs to card-signal-map format | feat/regenerate-images-card-signal-map |
| `0f3bb6d8` | fix: CSP sentry source map, AdSense empty gap, OG preload warning (#267) | main |

---

## Next Actions

1. **즉시 처리 (오늘)**
   - PR #278, #279 머지 (검증 후)
   - PR #277 Vercel 배포 모니터링

2. **이번 주 내**
   - `fix/entity-cleanup-09-17-and-05-30` push + PR 생성
   - PR #276 close 처리
   - AdSense 계정 상태 Google 대시보드 확인 (사용자)

3. **차주 이후**
   - Non-digest 포스트 46개 이미지 재생성 전략 수립
   - 기술 부채 정리 (pre-commit hook 통합, entity cleanup 자동화)

---

**Session completed by:** Writer Agent  
**File path:** `/Users/yong/Desktop/personal/tech-blog/notes/per-pr/PR-277-279-session.md`
