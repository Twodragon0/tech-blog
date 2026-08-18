# `web_vitals` 전송 유실 — 실측과 폴백 설계

**요약: 조사 대상이었던 `__gaPending` 유실은 실재하지만 작은 쪽이었다. 훨씬 큰
유실은 gtag의 5초 배치 타이머에 있다. 현재 `web_vitals`는 독자가 탭을 백그라운드로
두고 5초 이상 살려둔 경우에만 GA4에 도달한다. 탭을 닫거나 사이트 내 다른 글로
이동하면 전량 유실된다.**

측정 하네스: `scripts/dev/measure_ga_pending_loss.mjs` (Playwright)
측정 대상: `https://tech.2twodragon.com/` (프로덕션, 2026-08-18)

---

## 1. 유실 경로는 두 개다

### 경로 A — `__gaPending` (원래 조사 대상)

상호작용 없이 10~12초 유휴 폴백 전에 떠나면 gtag가 아예 로드되지 않는다.
`__track`은 이벤트를 `__gaPending`에 넣고, 페이지와 함께 사라진다.

| 시나리오 | gtag 요청 | `__gaReady` | 결과 |
|---|---|---|---|
| 무상호작용 3초 후 이탈 | ✗ | false | `web_vitals` 버퍼에 갇힘 |
| 무상호작용 8초 후 이탈 | ✗ | false | `web_vitals` 버퍼에 갇힘 |
| 무상호작용 13초 후 이탈 | ✓ | true | 유휴 폴백 발동, 버퍼 비워짐 |

### 경로 B — gtag 5초 배치 타이머 (조사 범위 밖, 훨씬 크다)

gtag가 정상 로드돼 `__gaReady === true` 인 상태에서도, `dataLayer`에 push된
이벤트는 **즉시 전송되지 않는다.** 약 5초 뒤 배치로 나간다.

push → 네트워크 요청까지의 지연 (n=4):

```
run 1: 5005ms   run 2: 5004ms   run 3: 5003ms   run 4: 5004ms
```

편차 2ms — 우연이 아니라 고정 상수다.

vitals는 페이지 hide에서 push되므로, **hide 후 5초 안에 페이지가 죽으면 큐에 있던
이벤트가 함께 죽는다.**

| hide 후 이탈까지 | 전송된 `web_vitals` |
|---|---|
| 0ms | 0 / 3 |
| 500ms | 0 / 3 |
| 2000ms | 0 / 3 |
| 5000ms | 2 / 3 |
| 10000ms | 3 / 3 |
| 15000ms | 3 / 3 |

0 → 3 의 단조 증가가 5초 경계에 정확히 걸린다.

### 이게 계측 아티팩트가 아니라는 대조군

"페이지가 사라지는 중이라 요청을 못 잡은 것 아니냐"를 배제하기 위해, **같은
`visibilitychange` 핸들러에서** 우리가 제어하는 URL로 `navigator.sendBeacon`을
함께 쏘고 둘 다 CDP로 관측했다.

| hide 후 이탈까지 | 대조군 sendBeacon 포착 | gtag `web_vitals` 포착 |
|---|---|---|
| 0ms | 1 | 0 / 3 |
| 500ms | 1 | 0 / 3 |
| 2000ms | 1 | 0 / 3 |

teardown 중에도 포착 경로는 멀쩡하다. gtag가 실제로 안 보낸 것이다.
**동시에 이 대조군은 `sendBeacon`이 hide 시점에 확실히 동작한다는 것도 증명한다** —
즉 폴백 전송 수단으로 쓸 수 있다.

---

## 2. 클라이언트 측 우회는 전부 실패

배치 타이머를 클라이언트에서 무력화할 수 있는지 확인했다. 이벤트 push 직후 이탈,
전송 여부:

| 시도 | 전송 |
|---|---|
| 평범한 gtag 이벤트 (기준선) | 0 |
| `transport_type: 'beacon'` | 0 |
| 이벤트 + 즉시 flusher push 하나 더 | 0 |
| `event_callback` 지정 | 0 |

**1줄 수정으로 끝나는 길은 없다.** 별도 전송 수단이 필요하다.

---

## 3. 실무적 함의

- 사이트 내 링크 클릭은 전부 full unload다(SPA 아님). **글 → 글 이동은 유실.**
- 탭 닫기도 **유실**.
- 탭 전환 후 5초 이상 방치해야 **전송**.

즉 현재 GA4의 `web_vitals` 데이터는 "탭을 바꾸고 안 돌아온 독자" 표본에 가깝다.
`notes/ga4-web-vitals-reporting.md` §5에 적은 편향 설명은 경로 A만 반영한 것이라
과소평가였다. 실제 편향은 그보다 훨씬 크다.

**부수 효과 하나**: 지난 검증 절차에서 안내한 "스크롤 → 탭 전환 → Realtime 확인"은
공교롭게도 유일하게 동작하는 경로다. **Realtime에서 이벤트가 보인다고 해서 실제
트래픽에서 수집되고 있다는 뜻이 아니다.**

---

## 4. 폴백 설계 후보

### 옵션 1 — 첫 상호작용 직후 LCP만 조기 전송 (부분 해결, 인프라 없음)

LCP는 첫 상호작용 시점에 확정된다. hide까지 기다릴 이유가 없으므로 상호작용 직후
보내면 배치 타이머 5초가 페이지 생존 중에 소진된다.

- 비용 0, 코드 변경 작음
- **CLS·INP는 정의상 끝까지 누적되므로 해결 못 함** — 3개 중 1개만 복구
- 경로 A(무상호작용)는 여전히 유실 (상호작용이 전제)

### 옵션 2 — 클라이언트에서 `/g/collect`로 직접 sendBeacon

gtag가 쓰는 것과 같은 엔드포인트로 우리가 직접 beacon을 쏜다.

- api_secret 불필요, CSP `connect-src`에 `https://*.google-analytics.com` 이미 허용됨
- **페이로드 형식이 비공식·무문서**다. 구글이 바꾸면 조용히 깨지고, 깨진 걸 알아챌
  방법이 없다
- 광고 차단기에 gtag와 똑같이 막힘 → 편향 일부만 해소

### 옵션 3 — 퍼스트파티 엔드포인트 + 서버측 Measurement Protocol (권장)

hide에서 `navigator.sendBeacon('/api/vitals', …)` → Vercel 함수가 GA4 MP로 전달.

- **대조군에서 이미 동작이 실증됨** (gap=0에서 1/1 포착)
- `api_secret`은 Vercel env에 남아 클라이언트에 노출되지 않음
- 퍼스트파티라 광고 차단기 우회 → 경로 A·B 둘 다, 그리고 차단기 편향까지 해소
- CSP `connect-src 'self'` 이미 허용됨. `api/` 서버리스 함수 패턴도 이미 있음
  (`api/chat.js`, `api/search.js`)
- 비용: 세션당 함수 호출 1회. 계산량은 무시할 수준이나 **Vercel 호출 수 한도는
  확인 필요**
- 구현 난점: MP 이벤트를 기존 세션에 붙이려면 `_ga` 쿠키의 client_id 와
  `_ga_<container>` 쿠키의 session_id 를 파싱해 함께 보내야 한다. 안 하면 별도
  세션으로 집계돼 페이지별 조인이 깨진다

### 옵션 4 — 현상 유지 + 한계 문서화

경로 A만 적어둔 현재 문서를 경로 B까지 포함하도록 고치고, GA4 수치는 추세용으로만
쓰며 절대 판정은 CrUX로 한다. 코드 변경 없음.

---

## 5. 결정 — 옵션 3 채택 (구현 완료)

세 지표를 모두 복구하는 유일한 안이고, 전송 수단은 이미 실측으로 검증됐다.
옵션 2는 무문서 의존이라 조용히 깨질 위험이 크고, 옵션 1은 3분의 1만 해결한다.

### ⚠️ 배포 전 필수 — `GA4_API_SECRET`

**이 환경변수가 없으면 `/api/vitals`는 모든 리포트를 버린다.** gtag 경로는
제거됐으므로, 시크릿 없이 배포하면 수집이 "일부"에서 **"전무"로 나빠진다.**
반드시 배포 전에 설정할 것.

1. GA4 → 관리 → 데이터 스트림 → 해당 스트림 → **Measurement Protocol API 비밀번호**
   → 만들기
2. Vercel → Project Settings → Environment Variables → `GA4_API_SECRET` 추가
   (Production + Preview)
3. 재배포

설정 전에는 함수가 `[vitals] GA4_API_SECRET is not set; dropping report` 경고만
남기고 204를 반환한다 (독자에게는 영향 없음).

### 구성 요소

| 파일 | 역할 |
|---|---|
| `assets/js/performance-monitor.js` | hide에서 3개 지표를 모아 `/api/vitals`로 beacon 1건 |
| `api/vitals.js` | 검증 후 GA4 Measurement Protocol로 전달 |
| `tests/js/api-vitals.test.js` | 엔드포인트 회귀 테스트 27건 |
| `vercel.json` | `api/vitals.js` maxDuration 5s |

전송 페이로드(압축 형태): `{"p":"/posts/foo/","m":[{"n":"LCP","v":1200,"r":"good"}]}`
— `c`(원인)는 CLS에만 붙는다.

### 공개 엔드포인트라서 건 방어

인증 없는 POST 엔드포인트이므로 이벤트 주입 통로가 되지 않도록:

- **POST 전용**, 그 외 405
- **동일 출처 검증** — `Origin`/`Referer`가 사이트 호스트 또는 `*.vercel.app`이 아니면
  드롭. 둘 다 없으면 드롭
- **엄격한 검증** — 지표명·등급 allow-list, 값 범위, 지표 중복 금지, 최대 3건,
  본문 2KB 상한, `metric_cause` 제어문자 제거 + 100자
- **Rate limiting** — 기존 `api/lib/ratelimit.js` 재사용
- `api_secret`은 응답·로그에 절대 포함하지 않음 (회귀 테스트로 고정)

### 알려진 한계 — `cid_source`

`_ga` 쿠키가 없는 방문자(= GA가 한 번도 안 돈, 바로 이 엔드포인트가 구하려는 세션)는
Measurement Protocol이 요구하는 `client_id`를 만들어 낼 수밖에 없다. 합성 id는
GA4에서 **새 사용자로 집계되어 사용자 수를 부풀린다.**

그래서 모든 이벤트에 `cid_source` 파라미터를 붙인다 (`ga_cookie` | `synthetic`).
사용자 수 지표를 볼 때는 `cid_source = ga_cookie`로 필터링해야 하며, 이 값을
맞춤 측정기준으로 등록해 두는 것을 권장한다. 지표 분포(LCP/INP/CLS 값 자체)는
양쪽 모두 유효하다.

### 비용

세션당 함수 호출 1회, maxDuration 5s. 연산량은 무시할 수준이나 **Vercel 플랜의
함수 호출 한도는 트래픽 증가 시 확인이 필요하다** — 현재 트래픽 기준으로는
측정하지 않았다.

---

## 재현

```bash
node scripts/dev/measure_ga_pending_loss.mjs https://tech.2twodragon.com/ --runs 2
```

`--runs 2` 기준 약 3분. GA collect 요청은 네트워크 계층에서 abort되므로 프로덕션
속성에 합성 이벤트가 들어가지 않는다.

**주의**: 하네스의 hide 직후 대기 시간이 5초보다 짧으면 배치 타이머가 돌기 전이라
`vitalsSent=0`이 나온다. 이건 유실이 아니라 계측 오류다 — 초기 측정에서 실제로
이 함정에 빠졌다.
