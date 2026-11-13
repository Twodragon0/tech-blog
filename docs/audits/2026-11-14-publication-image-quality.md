# 게시 상태와 이미지 품질 점검

기준: 2026-11-14 07:50 KST, main `7a7b81bc7f338fd37490d8798af80c91f3095fe6`.
운영 HTTP 점검과 아래 로컬 개선의 검증은 별개다. 개선분은 아직 원격 반영하지 않았다.

## 우선순위 판정

| 우선순위 | 관측 | 처리 |
|---|---|---|
| P1 발행·표시 장애 | 최근 3일 자동 발행 성공, RSS·최신 글·이미지 정상 | 장애 없음. 점검 시각은 11월 14일 09:00 예약 전이므로 당일 글 부재는 누락 아님 |
| P2 내용과 표지 일치 | 11월 13일 제목 강조와 주요 기사 카드 구성이 다르고, 웨비나가 우선 이슈로 노출 | 실제 렌더링 기사로 메타데이터 생성, 명시적 행사 홍보는 우선순위 표면에서 제외 |
| P2 이미지의 위험도 표현 | 근거 없는 HIGH/HIGH/MEDIUM 기본값과 미평가 severity 게이지 | 중립 FOCUS 기본값, 실제 severity가 없으면 게이지 생략 |
| P2 요약문 문법 | 잘린 제목 뒤 조사 연결로 SOC를을 발생 | 제목 인용과 명사 소식으로 연결하고 회귀 검사 추가 |
| P3 과거 발행 공백 | 11월 1~5일 digest 없음 | 기존 보충 초안 재검토 대상. 중복 초안·자동 보충 게시 생성하지 않음 |

11월 6~13일 digest는 연속 존재한다. 과거 공백은
`_drafts/2026-11-06-Tech_Security_Backfill_2026_10_28_11_05.md`가 이미 다루므로
추가 보충보다 원고의 출처·중복 검토가 우선이다.

## 운영 상태 증거

- [11월 13일 자동 발행](https://github.com/Twodragon0/tech-blog/actions/runs/43363815734) 성공.
- 운영·백업 RSS 모두 HTTP 200, 50항목, 최신 글 11월 13일.
- 최신 3개 글과 운영 raster 15개·백업 SVG 3개 HTTP 200.
- canonical은 운영 HTTPS URL과 일치, 백업 글은 noindex, follow.
- 344개 게시물 primary 이미지 검사 통과. 별도 본문 포함 로컬 참조 684건, 누락 0건.
  main의 기존 이미지 verifier는 frontmatter만 검사하므로 본문 참조는 따로 스캔했다.

## 개선 범위

- Webinar/Webcast/웨비나 등 명시적인 행사 접두사만 공용 필터로 판별한다.
  WebinarKit 같은 제품명은 유지하고 기사 본문을 삭제하지 않는다.
- 향후 제목·태그·description·image_alt는 실제 렌더링되는 기사 중 비홍보 항목을 따른다.
  수집 총수와 모든 원문·체크리스트는 유지한다.
- 11월 13일 제목·요약·하이라이트·대체 텍스트를 주요 기사에 맞췄다.
  BYOVD는 체크리스트에 있으므로 본문에 전혀 없다고 표현하지 않는다.
  filename·게시 date·URL·본문 바이트는 변경하지 않았다.
- 표지는 Xloader/Phishing Threat, ThreatsDay/Linux, Chrome Enterprise로 정리했다.
  SVG와 해당 글의 raster 5개만 재생성했다. 다른 과거 표지는 일괄 변경하지 않았다.
- OG 1200×630, 카드 525×295. WebP·AVIF를 유지하고 실제 표시 크기에서도 시각 검토했다.

## 통합 검증

- 회귀부터 재현: 요약문 기존 코드 5건 실패, metadata 기존 코드 3건 실패,
  이미지 기존 코드 7건 실패. 수정 후 각 집중 검사 통과.
- 두 변경 묶음 통합 전체 pytest: **6,588 passed, 23 skipped**, 기존 폰트 경고 1건.
- Jekyll 전체 빌드 성공: 22.04초. 추가 의존성 설치·유료 API 호출 없음.
- 생성 HTML의 title·description·canonical, RSS 제목·GUID, 본문 보존,
  SVG의 미확인 severity 제거, raster 5개 디코딩·크기를 확인했다.
- Ruff lint·format, 변경 helper/SEO/이미지 모듈의 mypy 검사 통과.

검증 로그: `/private/tmp/techblog-quality-pytest-20261114.log`,
`/private/tmp/techblog-quality-build-20261114.log`,
`/private/tmp/blog-quality-final-20261114.json`.

기존 기본 checkout의 사용자 수정·미추적 이미지는 보존했다.
원격 push·PR 생성·배포·새 게시물 발행은 수행하지 않았다.
