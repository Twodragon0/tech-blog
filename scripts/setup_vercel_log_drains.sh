#!/bin/bash
# Vercel Log Drains 설정 가이드 스크립트
#
# 사용법:
#   ./scripts/setup_vercel_log_drains.sh
#
# 이 스크립트는 Vercel Log Drains 설정을 위한 가이드를 제공합니다.

set -e

echo "🚀 Vercel Log Drains 설정 가이드"
echo "=================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Vercel Marketplace에서 Sentry 통합 설치${NC}"
echo ""
echo "   다음 단계를 따라주세요:"
echo "   1. https://vercel.com/integrations 접속"
echo "   2. 'Sentry' 검색"
echo "   3. 'Add Integration' 클릭"
echo "   4. 팀 또는 프로젝트 선택하여 설치"
echo ""
read -p "   Sentry 통합을 설치하셨나요? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}   ⚠️  Sentry 통합을 먼저 설치해주세요.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}2. Log Drain 설정${NC}"
echo ""
echo "   다음 단계를 따라주세요:"
echo "   1. Vercel 대시보드 접속: https://vercel.com/dashboard"
echo "   2. Team Settings > Drains 이동"
echo "   3. 'Add Drain' 클릭"
echo "   4. 다음 설정 입력:"
echo ""
echo "      Name: Sentry Logs"
echo "      Data Type: Logs"
echo "      Projects: tech-blog (또는 원하는 프로젝트)"
echo "      Sampling Rate: 10% (Free 티어 최적화)"
echo "      Destination: Sentry (설치한 통합 선택)"
echo ""
read -p "   Log Drain을 생성하셨나요? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}   ⚠️  Log Drain을 먼저 생성해주세요.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}3. 환경 변수 확인${NC}"
echo ""
echo "   다음 환경 변수가 설정되어 있는지 확인하세요:"
echo ""
echo "   SENTRY_DSN=https://YOUR_SENTRY_DSN@o4510686170710016.ingest.us.sentry.io/YOUR_PROJECT_ID"
echo "   SENTRY_ENVIRONMENT=production"
echo ""
echo "   Vercel CLI로 설정:"
echo "   vercel env add SENTRY_DSN production"
echo "   vercel env add SENTRY_ENVIRONMENT production"
echo ""
read -p "   환경 변수를 설정하셨나요? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}   ⚠️  환경 변수를 설정해주세요.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}4. 배포 및 검증${NC}"
echo ""
echo "   다음 단계를 따라주세요:"
echo "   1. 변경사항 커밋 및 푸시"
echo "   2. Vercel에서 자동 배포 확인"
echo "   3. Sentry 대시보드에서 로그 확인:"
echo "      https://sentry.io/organizations/twodragon/projects/tech-blog/logs/"
echo ""
echo "   테스트 로그 전송:"
echo "   - 브라우저 콘솔에서: console.warn('Test log')"
echo "   - Vercel 서버 로그 확인"
echo ""

echo -e "${GREEN}✅ 설정 완료!${NC}"
echo ""
echo "   다음 문서를 참고하세요:"
echo "   - README_SENTRY_LOGS.md"
echo "   - scripts/verify_sentry_logs.js"
echo ""
