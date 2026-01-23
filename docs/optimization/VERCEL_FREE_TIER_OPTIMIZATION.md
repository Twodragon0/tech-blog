# Vercel 프리티어 최적화 가이드

tech-blog 프로젝트의 DeepSeek 채팅 위젯이 Vercel 프리티어 제한 내에서 최적화되었습니다.

## 적용된 최적화

### 1. 실행 시간 최적화

- **타임아웃**: 8초로 설정 (프리티어 안전 마진)
- **함수 최대 실행 시간**: 10초 (`vercel.json`에 설정)
- **빠른 실패**: 입력 검증 및 Rate limiting을 먼저 수행

```javascript
// api/chat.js
const CONFIG = {
  TIMEOUT_MS: 8000, // 8초 타임아웃
};
```

### 2. 메모리 최적화

- **함수 메모리**: 1024MB로 제한 (`vercel.json`)
- **Rate Limiter**: 간단한 Map 기반 구현 (메모리 효율적)
- **자동 정리**: 오래된 Rate limit 레코드 자동 삭제

### 3. Rate Limiting

- **세션당 최대 요청**: 10회/분
- **윈도우**: 60초
- **메모리 기반**: 프리티어용 간단한 구현
- **프로덕션 권장**: Redis 또는 Vercel KV 사용

```javascript
// 세션당 10회/분 제한
RATE_LIMIT: {
  MAX_REQUESTS: 10,
  WINDOW_MS: 60000,
}
```

### 4. 로깅 최적화

- **프로덕션**: 최소한의 로그만 기록
- **개발 환경**: 상세 로그 활성화
- **실행 시간 모니터링**: 5초 이상인 경우만 로깅

### 5. 응답 크기 최적화

- **최대 토큰 수**: 2000 → 1500으로 감소
- **메시지 길이 제한**: 2000자
- **불필요한 데이터 제거**: 최소한의 응답만 반환

## Vercel 프리티어 제한

### Hobby (무료) 플랜

- ✅ **실행 시간**: 최대 10초 (설정됨)
- ✅ **메모리**: 1024MB (설정됨)
- ✅ **함수 호출**: 무제한
- ⚠️ **동시 실행**: 제한 있음 (Rate limiting으로 완화)

### Pro 플랜 (업그레이드 시)

- 실행 시간: 최대 60초
- 메모리: 최대 3008MB
- 더 많은 동시 실행

## 모니터링

### 로그 확인

```bash
# 스크립트 사용
./scripts/check-vercel-logs.sh

# 또는 직접
vercel logs https://tech.2twodragon.com
vercel logs https://tech.2twodragon.com --json
```

### 배포 확인

```bash
vercel ls
vercel inspect https://tech.2twodragon.com
```

### 환경 변수 확인

```bash
vercel env ls
```

## 성능 모니터링

### 주요 메트릭

1. **실행 시간**: 평균 2-5초 (DeepSeek API 응답 시간에 따라 다름)
2. **메모리 사용량**: 평균 50-100MB
3. **에러율**: Rate limiting 및 타임아웃 모니터링

### 경고 기준

- ⚠️ 실행 시간 > 7초: 타임아웃 위험
- ⚠️ 메모리 사용량 > 800MB: 메모리 부족 위험
- ⚠️ Rate limit 초과 빈번: Rate limit 조정 필요

## 문제 해결

### 타임아웃 오류

**증상**: 504 Gateway Timeout

**해결책**:
1. 타임아웃 시간 확인 (현재 8초)
2. DeepSeek API 응답 시간 확인
3. 필요시 `max_tokens` 더 줄이기

### Rate Limit 오류

**증상**: 429 Too Many Requests

**해결책**:
1. Rate limit 설정 확인 (현재 10회/분)
2. 사용자에게 대기 시간 안내
3. 필요시 Redis 기반 Rate limiting으로 업그레이드

### 메모리 부족

**증상**: 함수 크래시

**해결책**:
1. Rate limit 저장소 크기 확인
2. 불필요한 로그 제거
3. 메모리 사용량 모니터링

## 업그레이드 권장사항

프로덕션 환경에서 더 나은 성능을 원한다면:

1. **Vercel Pro 플랜**: 더 긴 실행 시간 및 메모리
2. **Vercel KV**: Redis 기반 Rate limiting
3. **로깅 서비스**: Vercel Analytics 또는 외부 서비스
4. **모니터링**: Sentry, Datadog 등

## 비용 최적화

### 현재 설정

- ✅ 타임아웃 최소화로 불필요한 실행 시간 방지
- ✅ Rate limiting으로 API 호출 수 제한
- ✅ 로깅 최소화로 스토리지 비용 절감
- ✅ 메모리 제한으로 리소스 사용 최적화

### 예상 비용

- **Vercel**: 무료 (Hobby 플랜)
- **DeepSeek API**: 사용량 기반 (프리티어 최적화로 비용 절감)

## 참고 자료

- [Vercel Functions 제한사항](https://vercel.com/docs/functions/limitations)
- [Vercel 프리티어 가이드](https://vercel.com/docs/limits)
- [DeepSeek API 문서](https://platform.deepseek.com/api-docs/)
