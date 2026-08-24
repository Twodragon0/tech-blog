# Vercel 환경 변수 설정 가이드

tech-blog 프로젝트에 필요한 Vercel 환경 변수 설정 가이드입니다.

## 런타임 env 계약 (2026-08-24 실측)

`api/`의 서버리스 함수가 읽는 환경 변수 전체다. 이 표는 손으로 관리하지 않는다 —
`scripts/check_runtime_env_contract.py`가 `api/**/*.js`의 `process.env.*`를
스캔해서 선언 누락·고아 선언을 CI에서 차단하고, `--vercel`로 실제 프로비저닝
여부까지 확인한다.

```bash
# 선언 동기화만 (자격증명 불필요, CI가 도는 것과 동일)
python3 scripts/check_runtime_env_contract.py

# Vercel에 실제로 있는지까지 (vercel CLI 로그인 필요, 이름만 조회)
python3 scripts/check_runtime_env_contract.py --vercel
```

| 변수 | 분류 | 상태 (2026-08-24) | 부재 시 |
|---|---|---|---|
| `GA4_API_SECRET` | REQUIRED | ❌ **미설정** | `api/vitals.js`가 모든 web_vitals 비콘을 폐기. 엔드포인트는 그래도 204를 반환하므로 **수집이 정상인 것처럼 보인다** |
| `DEEPSEEK_API_KEY` | REQUIRED | ✅ Production | 챗봇 위젯 오류 |
| `SENTRY_DSN` | OPTIONAL | ✅ Production | 서버측 오류 리포팅 없음, 기능은 동작 |
| `GA4_MEASUREMENT_ID` / `SITE_ORIGIN` / `DEEPSEEK_MODEL` / `DEBUG` / `SEARCH_*` / `RATELIMIT_*` | OPTIONAL | 미설정 | 코드에 기본값 있음 |
| `USE_UPSTASH_RATELIMIT` / `UPSTASH_REDIS_REST_*` | OPTIONAL | 미설정 | **의도된 상태**. in-memory 레이트리미터는 서버리스에서 인스턴스별로 동작하고 코드가 시작 시 그걸 경고한다. 선택된 trade-off이며 누락된 자격증명이 아니다 |
| `NODE_ENV` / `VERCEL_ENV` | PLATFORM | 런타임 주입 | — |

프로젝트에 `REDIS_URL`, `POSTGRES_URL`, `DATABASE_URL`, `PRISMA_DATABASE_URL`,
`BLOB_READ_WRITE_TOKEN`이 있지만 **`api/`의 어떤 코드도 읽지 않는다** — Vercel
스토리지 연동이 만든 것이다. 결함은 아니지만, `REDIS_URL`이 있다고 레이트리밋이
Redis를 쓰는 것은 아니다(위 표의 `USE_UPSTASH_RATELIMIT` 참조).

### `GA4_API_SECRET` 등록 체크리스트

`web_vitals` 수집은 이 값 없이는 **0건**이다. PR #558·#586이 gtag 배치 유실을
없애려고 퍼스트파티 비콘으로 옮겼지만, 시크릿이 없어 그 파이프라인은 아직 아무것도
수집하지 않았다. 근거: `vercel env ls production`에 이름이 없음(2026-08-24).

1. **GA4에서 값 생성**
   Google Analytics → **Admin** → **Data streams** → 웹 스트림 선택 →
   **Measurement Protocol API secrets** → **Create**.
   생성된 secret value를 복사한다. Measurement ID는 코드에 기본값
   `G-B29150XJ73`으로 있으므로 따로 등록하지 않아도 된다.

2. **Vercel에 등록** — 대시보드 또는 CLI 중 하나로.

   ```bash
   vercel env add GA4_API_SECRET production
   # 프롬프트에 1단계에서 복사한 값 붙여넣기
   ```

   Production만으로 충분하다. Preview 배포에서 vitals를 수집할 이유가 없고,
   같은 GA4 속성에 프리뷰 트래픽이 섞이면 데이터가 오염된다.

3. **재배포** — 환경 변수는 빌드 시점에 주입되므로 **기존 배포에는 적용되지
   않는다.** Vercel 대시보드에서 최신 Production 배포를 Redeploy 하거나, 아무
   커밋이나 main에 올린다.

4. **검증** — 세 단계를 순서대로. 앞 단계를 건너뛰면 실패 원인을 구분할 수 없다.

   ```bash
   # (a) 등록 자체 확인 — 이름만 조회, 값은 노출되지 않는다
   python3 scripts/check_runtime_env_contract.py --vercel
   # 기대: [runtime-env] OK — ... all 2 REQUIRED present in Vercel.
   ```

   (b) **전송 확인**: DevTools → Network → `vitals` 필터 → 탭을 닫거나 내부
   링크 클릭. `/api/vitals`로 POST 1건, status 204, metric 최대 3개.
   204는 시크릿이 있어도 없어도 같으므로 **이것만으로는 수집을 증명하지
   못한다.**

   (c) **수집 확인**: GA4 → Realtime → `web_vitals` 이벤트. LCP/CLS는 상호작용
   없이도 올라오고, INP는 독자가 상호작용해야 나타난다. 여기서 이벤트가 보이면
   비로소 파이프라인이 살아 있다.

5. **회귀 방지** — 값을 로테이션하거나 삭제하면 다시 조용히 0건이 된다.
   `--vercel` 체크를 주기적으로 돌리는 것이 유일한 감시 수단이다. CI에는 걸 수
   없다(`VERCEL_TOKEN` 미등록, PR #585가 그 프로비저닝 대기 중).

배경: `notes/ga4-web-vitals-delivery-loss.md`(왜 gtag를 버렸나),
`notes/ga4-web-vitals-reporting.md`(이벤트 계약·리포트 스펙),
`notes/ci-skip-campaign-2026-08.md`(런타임 자격증명이 왜 감사 사각지대였나).

## DeepSeek API 키 설정

### 방법 1: Vercel 대시보드에서 설정 (권장)

1. [Vercel 대시보드](https://vercel.com/dashboard) 접속
2. `tech-blog` 프로젝트 선택
3. **Settings** → **Environment Variables** 이동
4. 다음 변수 추가:
   - **Key**: `DEEPSEEK_API_KEY`
   - **Value**: [DeepSeek Platform](https://platform.deepseek.com)에서 발급받은 API 키
   - **Environment**: 
     - ✅ Production
     - ✅ Preview  
     - ✅ Development
5. **Save** 클릭

### 방법 2: Vercel CLI 사용

```bash
cd /path/to/tech-blog  # 실제 프로젝트 경로로 교체 필요

# Production 환경
vercel env add DEEPSEEK_API_KEY production
# 프롬프트에 DeepSeek API 키 입력 (sk-로 시작)

# Preview 환경
vercel env add DEEPSEEK_API_KEY preview
# 프롬프트에 DeepSeek API 키 입력 (sk-로 시작)

# Development 환경
vercel env add DEEPSEEK_API_KEY development
# 프롬프트에 DeepSeek API 키 입력 (sk-로 시작)
```

### 확인

환경 변수가 제대로 설정되었는지 확인:

```bash
vercel env ls
```

다음과 같이 표시됩니다 (2026-08-24 실측):

```
DEEPSEEK_API_KEY    Encrypted    Production
```

이 문서는 이전에 `Development, Preview, Production`이라고 적고 있었으나 실제
등록은 Production 하나다. 챗봇을 프리뷰에서 시험할 일이 있으면 그때 추가하면
되고, 없다면 Production만으로 충분하다.

## 참고사항

- **보안**: API 키는 Vercel에서 암호화되어 저장됩니다
- **동기화**: online-course 프로젝트와 동일한 DeepSeek API 키를 사용합니다
- **재배포**: 환경 변수 추가 후 자동으로 재배포되거나, 수동으로 재배포가 필요할 수 있습니다

## 문제 해결

### 환경 변수가 적용되지 않는 경우

1. **재배포 확인**: 환경 변수 추가 후 프로젝트가 재배포되었는지 확인
2. **환경 확인**: Production, Preview, Development 모두 설정되었는지 확인
3. **로컬 테스트**: 로컬에서 테스트하려면 `.env.local` 파일에 추가:
   ```bash
   DEEPSEEK_API_KEY=sk-your-deepseek-api-key
   ```
   **주의**: `.env.local` 파일은 절대 git에 커밋하지 마세요!

### API 오류가 발생하는 경우

- **503 오류**: API 키가 설정되지 않았거나 잘못된 경우
- **429 오류**: Rate limit 초과 (잠시 후 재시도)
- **401 오류**: API 키가 유효하지 않은 경우 (키 확인 필요)
