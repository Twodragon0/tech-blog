#!/bin/bash

# 보안 모니터링 스크립트
# Vercel Analytics 및 Sentry 보안 이벤트 모니터링

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== 보안 모니터링 가이드 ===${NC}\n"

# 1. Vercel Analytics 확인
echo -e "${YELLOW}1. Vercel Analytics 확인${NC}"
echo "   Vercel 대시보드에서 다음을 확인하세요:"
echo "   - Analytics → Functions: 함수 호출 수 및 실행 시간"
echo "   - Analytics → Web Vitals: 성능 메트릭"
echo "   - Deployments → Logs: 실시간 로그 확인"
echo ""
echo "   명령어로 확인:"
echo "   ${GREEN}vercel logs --follow${NC}"
echo ""

# 2. Sentry 보안 이벤트 확인
echo -e "${YELLOW}2. Sentry 보안 이벤트 확인${NC}"
echo "   Sentry 대시보드에서 다음을 확인하세요:"
echo "   - Issues → Filters:"
echo "     * tags.security = true"
echo "     * tags.errorType = rate_limit_exceeded"
echo "     * tags.errorType = bot_blocked"
echo "     * tags.errorType = xss_attempt"
echo "   - Performance → Transactions:"
echo "     * /api/chat 엔드포인트 성능"
echo "   - Logs → Filters:"
echo "     * level = warning"
echo "     * level = error"
echo ""

# 3. Rate Limiting 통계
echo -e "${YELLOW}3. Rate Limiting 통계${NC}"
echo "   Vercel 로그에서 Rate Limit 이벤트 확인:"
echo "   ${GREEN}vercel logs | grep -i 'rate limit'${NC}"
echo ""

# 4. Bot 차단 통계
echo -e "${YELLOW}4. Bot 차단 통계${NC}"
echo "   Vercel 로그에서 Bot 차단 이벤트 확인:"
echo "   ${GREEN}vercel logs | grep -i 'bot blocked'${NC}"
echo ""

# 5. API 호출 통계
echo -e "${YELLOW}5. API 호출 통계${NC}"
echo "   Vercel Analytics에서 확인:"
echo "   - Functions → /api/chat: 호출 수, 평균 실행 시간"
echo "   - Functions → 에러율: 429, 403, 400 에러 비율"
echo ""

# 6. 보안 이벤트 알림 설정
echo -e "${YELLOW}6. 보안 이벤트 알림 설정${NC}"
echo "   Vercel:"
echo "   - Settings → Notifications → Function Errors 활성화"
echo ""
echo "   Sentry:"
echo "   - Settings → Alerts → New Alert Rule 생성:"
echo "     * 조건: tags.security = true"
echo "     * 알림: 이메일, Slack 등"
echo ""

# 7. 정기 모니터링 체크리스트
echo -e "${YELLOW}7. 정기 모니터링 체크리스트${NC}"
echo "   [ ] 일일: Vercel Analytics 함수 호출 수 확인"
echo "   [ ] 일일: Rate Limit 초과 이벤트 확인"
echo "   [ ] 주간: Bot 차단 통계 확인"
echo "   [ ] 주간: 보안 이벤트 로그 분석"
echo "   [ ] 월간: API 비용 및 사용량 분석"
echo ""

echo -e "${GREEN}모니터링 가이드 완료!${NC}"
echo ""
echo "상세 가이드는 다음 문서를 참조하세요:"
echo "  - VERCEL_FIREWALL_SECURITY.md"
echo "  - SECURITY_MONITORING_GUIDE.md"
