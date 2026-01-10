#!/bin/bash
# Sentry 설정 스크립트
# 
# 사용법:
#   ./scripts/setup-sentry.sh [sentry-dsn]
#
# 예시:
#   ./scripts/setup-sentry.sh https://xxxxx@xxxxx.ingest.sentry.io/xxxxx

set -e

TECH_BLOG_DIR="/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"
SENTRY_DSN="${1}"

cd "$TECH_BLOG_DIR"

echo "🔧 Sentry 설정 중..."
echo ""

if [ -z "$SENTRY_DSN" ]; then
    echo "❌ DSN이 제공되지 않았습니다."
    echo ""
    echo "사용법:"
    echo "  ./scripts/setup-sentry.sh https://xxxxx@xxxxx.ingest.sentry.io/xxxxx"
    echo ""
    echo "DSN 확인 방법:"
    echo "  1. https://sentry.io 접속"
    echo "  2. 프로젝트 선택 → Settings → Client Keys (DSN)"
    echo "  3. DSN 복사"
    exit 1
fi

# DSN 형식 검증
if [[ ! "$SENTRY_DSN" =~ ^https://[a-zA-Z0-9]+@[a-zA-Z0-9.]+\.ingest\.sentry\.io/[0-9]+$ ]]; then
    echo "⚠️  DSN 형식이 올바르지 않습니다."
    echo "   예상 형식: https://xxxxx@xxxxx.ingest.sentry.io/xxxxx"
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ DSN 확인: ${SENTRY_DSN:0:30}..."
echo ""

# Vercel 환경 변수 추가
echo "📝 Vercel 환경 변수 추가 중..."
echo ""

# Production
echo "$SENTRY_DSN" | vercel env add SENTRY_DSN production 2>&1 | grep -v "Enter" || true

# Preview
echo "$SENTRY_DSN" | vercel env add SENTRY_DSN preview 2>&1 | grep -v "Enter" || true

# Development
echo "$SENTRY_DSN" | vercel env add SENTRY_DSN development 2>&1 | grep -v "Enter" || true

echo ""
echo "✅ Sentry 설정 완료!"
echo ""
echo "다음 단계:"
echo "  1. _includes/sentry.html 파일에서 SENTRY_DSN 변수 설정"
echo "  2. Sentry SDK 최신 버전 확인 및 업데이트"
echo "  3. 배포 후 Sentry 대시보드에서 이벤트 수신 확인"
echo ""
echo "Sentry 대시보드: https://sentry.io"
