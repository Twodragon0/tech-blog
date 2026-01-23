# 보안 테스트 및 모니터링 빠른 시작 가이드

배포 후 보안 기능을 테스트하고 모니터링하는 빠른 가이드입니다.

## 🚀 빠른 시작

### 1. 배포 후 테스트 (5분)

```bash
# 테스트 스크립트 실행
cd scripts
./test-security.sh
```

**예상 결과**:
- ✅ 모든 테스트 통과
- Rate Limiting 작동 확인
- Bot 보호 작동 확인
- 입력 검증 작동 확인

### 2. Vercel Analytics 확인 (2분)

1. **Vercel 대시보드** 접속: https://vercel.com/dashboard
2. 프로젝트 선택 → **Analytics** 탭
3. 확인 항목:
   - Functions → `/api/chat`: 호출 수 확인
   - Functions → 에러율: 429, 403 에러 확인
   - Web Vitals: 성능 메트릭 확인

### 3. Sentry 보안 이벤트 확인 (2분)

1. **Sentry 대시보드** 접속: https://sentry.io
2. 프로젝트 선택 → **Issues** 탭
3. 필터 설정:
   ```
   tags.security = true
   ```
4. 확인 항목:
   - Rate Limit 초과 이벤트
   - Bot 차단 이벤트
   - XSS 시도 이벤트

## 📊 일일 모니터링 (1분)

```bash
# 모니터링 스크립트 실행
./scripts/monitor-security.sh

# 또는 Vercel 로그 직접 확인
vercel logs | grep -i "rate limit"
vercel logs | grep -i "bot blocked"
```

## 🔍 주요 확인 사항

### 정상 동작 확인

- ✅ Rate Limiting: 15회/분 제한 작동
- ✅ Bot 보호: Bot User-Agent 차단
- ✅ CORS 정책: 허용되지 않은 Origin 차단
- ✅ 입력 검증: XSS 패턴 차단

### 비정상 패턴 확인

- ⚠️ Rate Limit 초과 빈번: Rate Limit 조정 필요
- ⚠️ Bot 차단 빈번: 새로운 봇 패턴 확인
- ⚠️ 에러율 높음: API 응답 시간 확인

## 📚 상세 가이드

- **테스트 가이드**: `SECURITY_MONITORING_GUIDE.md`
- **보안 최적화**: `VERCEL_FIREWALL_SECURITY.md`
- **보안 정책**: `SECURITY.md`

## 🆘 문제 해결

### 테스트 실패 시

1. **API URL 확인**: `API_URL` 환경 변수 설정
2. **배포 확인**: 최신 코드가 배포되었는지 확인
3. **로그 확인**: `vercel logs`로 에러 확인

### 모니터링 데이터가 없는 경우

1. **Vercel Analytics 활성화**: Settings → Analytics 확인
2. **Sentry 설정 확인**: `_includes/sentry.html` 확인
3. **프로덕션 환경 확인**: `NODE_ENV=production` 확인

## ✅ 체크리스트

배포 후 다음을 확인하세요:

- [ ] 보안 테스트 스크립트 실행
- [ ] Vercel Analytics 함수 호출 수 확인
- [ ] Rate Limit 헤더 확인
- [ ] Bot 보호 작동 확인
- [ ] Sentry 보안 이벤트 확인
- [ ] 알림 설정 확인

---

**다음 단계**: `SECURITY_MONITORING_GUIDE.md`에서 상세 모니터링 방법 확인
