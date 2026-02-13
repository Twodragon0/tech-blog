#!/bin/bash
# Sentry Auth Token을 GitHub Secrets에 업데이트하는 스크립트
# 사용법: 
#   1. ./scripts/update-sentry-token.sh <SENTRY_AUTH_TOKEN>
#   2. ./scripts/update-sentry-token.sh (자동으로 .env에서 읽기 시도)

set -e

# 인자가 없으면 .env 파일에서 자동으로 읽기 시도
if [ -z "$1" ]; then
    if [ -f .env ]; then
        SENTRY_TOKEN=$(grep -E "^SENTRY_AUTH_TOKEN=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" | xargs)
        if [ -n "$SENTRY_TOKEN" ]; then
            echo "✅ .env 파일에서 SENTRY_AUTH_TOKEN 발견"
            SENTRY_AUTH_TOKEN="$SENTRY_TOKEN"
        else
            echo "❌ .env 파일에 SENTRY_AUTH_TOKEN이 없습니다."
            echo ""
            echo "사용법: $0 <SENTRY_AUTH_TOKEN>"
            echo ""
            echo "예시:"
            echo "  $0 sntryu_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            echo "  또는"
            echo "  $0 sentry-release_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            echo ""
            echo ".env 파일에 추가하려면:"
            echo "  echo 'SENTRY_AUTH_TOKEN=your-token-here' >> .env"
            exit 1
        fi
    else
        echo "❌ .env 파일이 없습니다."
        echo ""
        echo "사용법: $0 <SENTRY_AUTH_TOKEN>"
        echo ""
        echo "예시:"
        echo "  $0 sntryu_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        exit 1
    fi
else
    SENTRY_AUTH_TOKEN="$1"
fi

# Token 형식 확인
if [[ ! "$SENTRY_AUTH_TOKEN" =~ ^(sntryu_|sentry-release) ]]; then
    echo "⚠️  경고: Token 형식이 일반적인 형식과 다릅니다"
    echo "   일반적인 형식: sntryu_... 또는 sentry-release..."
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔐 GitHub Secrets에 SENTRY_AUTH_TOKEN 업데이트 중..."
echo "$SENTRY_AUTH_TOKEN" | gh secret set SENTRY_AUTH_TOKEN

if [ $? -eq 0 ]; then
    echo "✅ SENTRY_AUTH_TOKEN이 성공적으로 업데이트되었습니다!"
    echo ""
    echo "📋 다음 단계:"
    echo "1. GitHub Actions 워크플로우가 자동으로 새 Token을 사용합니다"
    echo "2. 다음 워크플로우 실행을 확인하세요:"
    echo "   gh run list --workflow='Sentry Release' --limit 1"
    echo ""
    echo "🔍 Token 권한 확인:"
    echo "   - project:read ✅"
    echo "   - release:admin ✅"
    echo "   - organization:read ✅"
else
    echo "❌ GitHub Secrets 업데이트 실패"
    exit 1
fi
