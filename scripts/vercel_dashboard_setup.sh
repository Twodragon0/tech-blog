#!/bin/bash
# Vercel 대시보드 설정 가이드 스크립트
# 이 스크립트는 설정 가이드를 출력하고, Vercel CLI로 현재 설정을 확인합니다.

set -e

echo "🚀 Vercel 배포 최적화 설정 가이드"
echo "=================================="
echo ""

echo "📋 1단계: Vercel 대시보드에서 On-Demand Concurrent Builds 활성화"
echo "------------------------------------------------------------"
echo ""
echo "다음 단계를 따라주세요:"
echo ""
echo "1. Vercel 대시보드 접속: https://vercel.com/dashboard"
echo "2. 프로젝트 선택: tech-blog"
echo "3. Settings → Build & Development Settings 이동"
echo "4. 'On-Demand Concurrent Builds' 섹션 찾기"
echo "5. 'Run all builds immediately' 옵션 선택"
echo "6. Save 클릭"
echo ""
echo "✅ 이 설정으로 빌드 대기 시간이 제거되고 최대 40% 빌드 속도 향상"
echo ""

echo "📊 2단계: 현재 Vercel 설정 확인"
echo "--------------------------------"
echo ""

if command -v vercel &> /dev/null; then
    echo "Vercel CLI가 설치되어 있습니다. 설정을 확인합니다..."
    echo ""
    
    # 프로젝트 정보 확인
    echo "현재 프로젝트 정보:"
    vercel ls 2>/dev/null || echo "⚠️  프로젝트 정보를 가져올 수 없습니다. Vercel에 로그인하세요: vercel login"
    echo ""
    
    # 환경 변수 확인
    echo "환경 변수 확인:"
    vercel env ls 2>/dev/null || echo "⚠️  환경 변수를 확인할 수 없습니다."
    echo ""
else
    echo "⚠️  Vercel CLI가 설치되어 있지 않습니다."
    echo "설치 방법: npm i -g vercel"
    echo ""
fi

echo "📈 3단계: 빌드 성능 모니터링"
echo "----------------------------"
echo ""
echo "빌드 로그 확인 명령어:"
echo "  vercel logs --follow"
echo ""
echo "특정 배포 확인:"
echo "  vercel inspect [DEPLOYMENT_URL]"
echo ""
echo "배포 목록 확인:"
echo "  vercel ls"
echo ""

echo "✅ 설정 완료!"
echo ""
echo "다음 배포부터 최적화된 빌드 설정이 적용됩니다."
