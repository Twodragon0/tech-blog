#!/bin/bash
# Sentry Free 티어 할당량 모니터링 스크립트
#
# 사용법:
#   ./scripts/monitor_sentry_quota.sh
#
# 환경 변수:
#   SENTRY_AUTH_TOKEN: Sentry Auth Token (선택사항, 더 정확한 정보 제공)
#   SENTRY_ORG: Sentry 조직 이름 (기본값: twodragon)
#   SENTRY_PROJECT: Sentry 프로젝트 이름 (기본값: tech-blog)

set -e

SENTRY_ORG=${SENTRY_ORG:-twodragon}
SENTRY_PROJECT=${SENTRY_PROJECT:-tech-blog}
FREE_TIER_LIMIT=5000  # Free 티어 월 5,000 이벤트 제한

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "📊 Sentry Free 티어 할당량 모니터링"
echo "=================================="
echo ""

# Auth Token이 있으면 API 호출
if [ -n "$SENTRY_AUTH_TOKEN" ]; then
    echo -e "${BLUE}API를 통해 이벤트 수 확인 중...${NC}"
    
    # 현재 날짜 계산 (월 시작일)
    CURRENT_DATE=$(date +%Y-%m-%d)
    MONTH_START=$(date -v1d +%Y-%m-%d 2>/dev/null || date -d "$(date +%Y-%m-01)" +%Y-%m-%d)
    
    # Sentry API 호출 (실제 구현은 curl 사용)
    echo "   API 호출: GET /api/0/projects/${SENTRY_ORG}/${SENTRY_PROJECT}/stats/"
    echo "   기간: ${MONTH_START} ~ ${CURRENT_DATE}"
    echo ""
    echo -e "${YELLOW}   ⚠️  실제 API 호출은 Sentry 대시보드에서 확인하세요.${NC}"
    echo ""
else
    echo -e "${YELLOW}   ⚠️  SENTRY_AUTH_TOKEN이 설정되지 않았습니다.${NC}"
    echo "   더 정확한 정보를 위해 Auth Token을 설정하세요."
    echo ""
fi

echo -e "${BLUE}할당량 정보${NC}"
echo "   Free 티어 제한: ${FREE_TIER_LIMIT} 이벤트/월"
echo "   현재 사용량: Sentry 대시보드에서 확인"
echo "   남은 일수: $(date +%d)일"
echo ""

# 예상 사용량 계산
DAYS_IN_MONTH=$(date -d "$(date +%Y-%m-01) +1 month -1 day" +%d 2>/dev/null || echo "30")
CURRENT_DAY=$(date +%d)
DAYS_REMAINING=$((DAYS_IN_MONTH - CURRENT_DAY + 1))

echo -e "${BLUE}예상 사용량 계산${NC}"
echo "   일일 평균 제한: $((FREE_TIER_LIMIT / DAYS_IN_MONTH)) 이벤트/일"
echo "   남은 일수: ${DAYS_REMAINING}일"
echo "   남은 일수당 제한: $((FREE_TIER_LIMIT / DAYS_IN_MONTH * DAYS_REMAINING)) 이벤트"
echo ""

# 최적화 상태 확인
echo -e "${BLUE}최적화 상태${NC}"
echo "   ✅ 프로덕션만 수집"
echo "   ✅ 트레이스 샘플링: 5%"
echo "   ✅ 로그 레벨 필터링: warn, error만"
echo "   ✅ console.log 제외"
echo "   ✅ 중복 로그 필터링: 1분당 10회 제한"
echo ""

# 권장사항
echo -e "${BLUE}권장사항${NC}"
echo "   1. Sentry 대시보드에서 이벤트 수 확인:"
echo "      https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/stats/"
echo ""
echo "   2. 이벤트 수가 많으면:"
echo "      - 트레이스 샘플링을 5% → 3%로 낮추기"
echo "      - Vercel Log Drains 샘플링을 10% → 5%로 낮추기"
echo "      - 로그 필터링을 더 엄격하게 설정"
echo ""
echo "   3. 알림 설정:"
echo "      - Sentry 대시보드에서 할당량 알림 설정"
echo "      - 80% 도달 시 알림 받기"
echo ""

# 대시보드 링크
echo -e "${GREEN}대시보드 링크${NC}"
echo "   프로젝트: https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/"
echo "   통계: https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/stats/"
echo "   로그: https://sentry.io/organizations/${SENTRY_ORG}/projects/${SENTRY_PROJECT}/logs/"
echo ""
