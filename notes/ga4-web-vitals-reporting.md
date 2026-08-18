# GA4 `web_vitals` — 측정기준 등록과 보고서 설계

PR #554 (`48192d4b`) 이후 LCP·INP·CLS는 모두 하나의 GA4 이벤트 `web_vitals`로
전송된다. 이 문서는 GA4 관리 화면에서 해야 하는 등록 작업과, 등록 후 만들 수 있는
탐색 보고서 구성을 코드 기준으로 정리한다.

측정 ID: `G-B29150XJ73` (`_config.yml:27`)

---

## 1. 이벤트 계약 (코드 기준)

전송 지점은 한 곳이다 — `assets/js/performance-monitor.js:67-76` 의 `sendVital()`.

| 파라미터 | 타입 | 값 | 비고 |
|---|---|---|---|
| `metric_name` | string | `LCP` \| `INP` \| `CLS` | |
| `metric_value` | number | LCP·INP는 정수 ms, CLS는 소수 4자리 | 단위가 지표마다 다름 |
| `metric_rating` | string | `good` \| `needs-improvement` \| `poor` | |
| `metric_cause` | string | 최대 100자 | **CLS에만 붙는다** (`performance-monitor.js:74`) |

임계값은 `rate(value, good, poor)` (`performance-monitor.js:78-82`) 로 계산되며
Core Web Vitals 공식 기준과 동일하다.

| 지표 | good | needs-improvement | poor |
|---|---|---|---|
| LCP | ≤ 2500ms | ≤ 4000ms | > 4000ms |
| INP | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS | ≤ 0.1 | ≤ 0.25 | > 0.25 |

전송 시점은 페이지 hide (`visibilitychange` → hidden, `pagehide` 백스톱).
`beforeunload`는 모바일·bfcache에서 신뢰할 수 없어 쓰지 않는다
(`performance-monitor.js:84-90`).

**측정되지 않은 값은 보내지 않는다.** LCP 엔트리가 없거나 INP 상호작용이 0건이면
이벤트 자체를 생략한다 — 0을 보내면 만점처럼 보이기 때문
(`performance-monitor.js:112-115`, `192-195`).

---

## 2. GA4 관리 화면 등록 (관리자 작업, 1회)

`관리 → 데이터 표시 → 맞춤 정의`

### 2-1. 맞춤 측정기준 (이벤트 범위) — 3개

| 측정기준 이름 | 범위 | 이벤트 매개변수 |
|---|---|---|
| Metric Name | 이벤트 | `metric_name` |
| Metric Rating | 이벤트 | `metric_rating` |
| Metric Cause | 이벤트 | `metric_cause` |

### 2-2. 맞춤 측정항목 — 1개

| 측정항목 이름 | 범위 | 이벤트 매개변수 | 측정 단위 |
|---|---|---|---|
| Metric Value | 이벤트 | `metric_value` | 표준 |

`metric_value`는 숫자이므로 **측정기준이 아니라 측정항목**으로 등록해야 평균·백분위
계산이 가능하다. 측정기준으로 잘못 등록하면 값이 문자열 버킷이 되어 집계가 안 된다.

**단위 주의**: LCP·INP는 ms, CLS는 0~1 사이 소수다. 하나의 측정항목에 섞여 들어오므로
보고서에서 `metric_name`으로 반드시 분리해야 한다. 단위를 "밀리초"로 지정하면 CLS가
0.05ms처럼 표시되므로 **"표준"으로 두는 편이 안전하다.**

> 등록 후 데이터가 보고서에 나타나기까지 최대 24~48시간 걸린다. 실시간 보고서에서는
> 등록 전에도 이벤트 매개변수를 바로 볼 수 있다.

---

## 3. 실시간 검증 절차

`보고서 → 실시간` 에서 확인하되, **그냥 페이지를 열기만 하면 아무것도 안 보인다.**
두 가지 게이트가 있다.

1. **GA는 지연 로드된다.** 첫 상호작용(pointermove/scroll/keydown/touchstart/click)
   또는 10~12초 유휴 폴백에서야 gtag가 로드된다 (`head-runtime.js:186-205`).
2. **vitals는 페이지 hide에서 flush된다.** 페이지를 보고 있는 동안에는 전송되지 않는다.

검증 순서:

1. `https://tech.2twodragon.com/` 접속 (시크릿 창 권장 — SW/HTML 캐시 회피)
2. 스크롤 몇 번 + 링크 한두 개 클릭 (INP 상호작용 생성 + GA 로드 트리거)
3. **다른 탭으로 전환**하거나 탭을 닫는다 ← 이때 flush
4. GA4 실시간 → `이벤트 이름`에서 `web_vitals` 확인
5. `web_vitals` 클릭 → 매개변수에서 `metric_name`이 `LCP`/`INP`/`CLS`로 들어오는지 확인

기대 결과: 한 세션에서 최대 3건(LCP·INP·CLS). INP는 상호작용이 있어야만 나온다.

---

## 4. 탐색 보고서 구성

`탐색 → 빈 보고서` 에서 만든다. 세그먼트는 전부 공통으로
**이벤트 이름 = `web_vitals`** 필터를 건다.

### 보고서 A — 지표 × 등급 분포 (건강도 한눈에)

| 항목 | 설정 |
|---|---|
| 기법 | 자유 형식 |
| 행 | `Metric Name` |
| 열 | `Metric Rating` |
| 값 | `이벤트 수` |
| 셀 유형 | 히트맵 |

읽는 법: 각 행에서 `good` 비율이 75% 이상이면 그 지표는 CWV를 통과한다
(CWV 판정 기준이 p75이므로).

### 보고서 B — 페이지별 p75

| 항목 | 설정 |
|---|---|
| 기법 | 자유 형식 |
| 행 | `페이지 경로 및 화면 클래스` |
| 열 | `Metric Name` |
| 값 | `Metric Value` (요약: **백분위수 → 75%**) |
| 필터 | `이벤트 수` ≥ 30 |

**필터가 핵심이다.** 표본 5건짜리 페이지의 p75는 노이즈다. 최소 표본을 걸지 않으면
"최악의 페이지" 상위권이 전부 트래픽 없는 페이지로 채워진다.

GA4 자유 형식의 값 요약에는 백분위수가 있지만 p75가 없는 경우가 있다 — 그때는
`평균` 대신 **`최댓값`과 `평균`을 나란히** 두고 격차로 판단하거나, 보고서 A의
`poor` 비율을 페이지별로 쪼개는 방식이 더 정직하다.

### 보고서 C — CLS 원인 상위 목록

| 항목 | 설정 |
|---|---|
| 기법 | 자유 형식 |
| 행 | `Metric Cause` |
| 값 | `이벤트 수`, `Metric Value` (평균) |
| 필터 | `Metric Name` 정확히 일치 `CLS` |

`metric_cause`는 CLS에만 있으므로 필터를 빼면 `(not set)` 행이 대부분을 차지한다.
값 형식은 `Image: <src>` / `Ad: <src|class>` / `Card: <class>` / `Script insertion` /
`<TAG>#<id>.<class>` (`analyzeCLSCause`, `performance-monitor.js:218`).

---

## 5. 데이터 해석 시 반드시 알아야 할 편향

> **2026-08-18 갱신**: 아래 1~4는 실측 결과 **과소평가였다.** 이보다 훨씬 큰 유실
> 경로(gtag의 5초 배치 타이머)가 따로 있다. 탭을 닫거나 사이트 내 다른 글로
> 이동하면 `web_vitals`가 **전량 유실된다.** 측정 근거와 폴백 설계는
> `notes/ga4-web-vitals-delivery-loss.md`. 아래 절은 그중 작은 쪽(경로 A)만
> 다룬다.

이 데이터는 **모든 방문자를 대표하지 않는다.** 낙관적으로 치우친다.

1. **상호작용 없이 10초 안에 떠난 세션은 통째로 빠진다.** GA가 로드되기 전이라
   `__track`이 이벤트를 `__gaPending` 버퍼에 넣은 채 페이지가 사라진다
   (`head-runtime.js:132-142`). 봇·바운스 제거가 원래 의도지만, **페이지가 느려서
   떠난 진짜 사용자도 같이 제거된다.** 즉 최악의 LCP가 데이터에 안 잡힌다.
2. **gtag 로드 중 페이지를 떠나면 유실된다.** 상호작용으로 로드가 시작됐지만
   `onload`(=`__gaReady`) 전에 hide되면 그 세션의 vitals는 버퍼에 남아 사라진다.
3. **INP는 상호작용한 세션만 집계된다.** 정의상 그렇고, 편향이라기보다 특성이다.
4. **Vercel Speed Insights와 숫자가 다르다.** Speed Insights는 10% 샘플링이고
   이쪽은 (위 편향을 제외한) 전수라 서로 대조용으로만 쓴다.

따라서 이 대시보드는 **절대 수치의 정답이 아니라 배포 전후 추세 비교용**이다.
절대 판정은 CrUX(Search Console → Core Web Vitals)를 기준으로 삼는다.

---

## 관련 문서

- `assets/js/performance-monitor.js` — 유일한 전송 지점
- `assets/js/head-runtime.js` — `__track` 버퍼와 GA 지연 로드
- `tests/js/performance-monitor.test.js` — 이벤트 계약 회귀 테스트
