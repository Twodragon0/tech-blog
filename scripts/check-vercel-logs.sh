#!/bin/bash
# Vercel 로그 확인 스크립트
# 
# 사용법:
#   ./scripts/check-vercel-logs.sh [deployment-url]
#
# 예시:
#   ./scripts/check-vercel-logs.sh
#   ./scripts/check-vercel-logs.sh https://tech.2twodragon.com

set -e

TECH_BLOG_DIR="/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"
DEPLOYMENT_URL="${1:-https://tech.2twodragon.com}"

cd "$TECH_BLOG_DIR"

echo "🔍 Vercel 로그 확인 중..."
echo "📡 Deployment URL: $DEPLOYMENT_URL"
echo ""

# 최근 배포 정보 확인
echo "📦 최근 배포 정보:"
vercel ls 2>&1 | head -10
echo ""

# 로그 확인 (최근 배포 URL 사용)
echo "📋 최근 로그 (5분간):"
echo "   (실시간 로그를 보려면: vercel logs $DEPLOYMENT_URL)"
echo ""

# 함수 실행 통계 확인
echo "📊 함수 실행 통계 확인:"
vercel inspect "$DEPLOYMENT_URL" 2>&1 | grep -i "function\|duration\|memory" || echo "   통계 정보를 가져올 수 없습니다."
echo ""

# 환경 변수 확인
echo "🔐 환경 변수 확인:"
vercel env ls 2>&1 | grep -i "DEEPSEEK" || echo "   DEEPSEEK_API_KEY를 찾을 수 없습니다."
echo ""

echo "✅ 로그 확인 완료"
echo ""
echo "💡 추가 명령어:"
echo "   - 실시간 로그: vercel logs $DEPLOYMENT_URL"
echo "   - JSON 형식: vercel logs $DEPLOYMENT_URL --json"
echo "   - 배포 목록: vercel ls"
echo "   - 환경 변수: vercel env ls"
