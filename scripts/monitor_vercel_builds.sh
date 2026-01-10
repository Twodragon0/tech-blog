#!/bin/bash
# Vercel 빌드 성능 모니터링 스크립트

set -e

echo "📊 Vercel 빌드 성능 모니터링"
echo "============================"
echo ""

if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI가 설치되어 있지 않습니다."
    echo "설치: npm i -g vercel"
    exit 1
fi

echo "🔍 최근 배포 확인 중..."
echo ""

# 최근 배포 목록 가져오기
DEPLOYMENTS=$(vercel ls --json 2>/dev/null | head -5)

if [ -z "$DEPLOYMENTS" ]; then
    echo "⚠️  배포 정보를 가져올 수 없습니다."
    echo "Vercel에 로그인하세요: vercel login"
    exit 1
fi

echo "최근 배포:"
vercel ls --limit 5
echo ""

echo "📈 빌드 메트릭:"
echo "  - 빌드 시간: 목표 < 2분"
echo "  - 동시 빌드 수: Pro 플랜 기준 최대 12개"
echo "  - 배포 성공률: 목표 > 99%"
echo ""

echo "🔗 유용한 명령어:"
echo "  - 실시간 로그: vercel logs --follow"
echo "  - 배포 상세 정보: vercel inspect [URL]"
echo "  - 환경 변수 확인: vercel env ls"
echo ""

echo "✅ 모니터링 완료"
