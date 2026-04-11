# Sentry Allowed Domains 설정 가이드

Sentry DSN은 클라이언트 측 코드에 노출되므로, 허용 도메인을 제한하여 DSN 남용을 방지해야 합니다.

## 1. Allowed Domains 설정

**경로:** Sentry > Settings > Projects > [프로젝트 선택] > Client Keys (DSN) > Configure

**Allowed Domains에 추가할 도메인:**

```
tech.2twodragon.com
www.tech.2twodragon.com
twodragon0.github.io
```

빈 칸으로 두면 모든 도메인에서 이벤트를 전송할 수 있으므로, 반드시 운영/백업 도메인만 등록합니다.

## 2. Inbound Data Filters 활성화

**경로:** Settings > Projects > [프로젝트 선택] > Inbound Filters

다음 필터를 활성화합니다:

- **Filter out known web crawlers** - 봇/크롤러의 불필요한 에러 이벤트 차단
- **Filter out browser extensions** - 브라우저 확장 프로그램에서 발생하는 에러 제외
- **Legacy browsers** - 지원하지 않는 구형 브라우저 이벤트 필터링

## 3. Rate Limits 설정

**경로:** Settings > Projects > [프로젝트 선택] > Client Keys (DSN) > Configure > Rate Limit

Free Tier 한도(5K 이벤트/월)를 초과하지 않도록 프로젝트 수준 rate limit을 설정합니다:

| 설정 | 권장 값 |
|------|---------|
| Rate limit window | 60 seconds |
| Max events per window | 10 |

이 설정으로 분당 최대 10건의 이벤트만 수신하여, 급증(spike) 상황에서도 월간 한도를 보호합니다.

## 참고

- `_config.yml:191`과 `vercel.json:44`에 DSN이 설정되어 있습니다.
- DSN 자체는 공개되어도 이벤트 전송만 가능하므로 데이터 유출 위험은 없지만, 쿼터 남용 방지를 위해 위 설정을 적용합니다.
