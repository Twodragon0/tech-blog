#!/bin/bash
# DeepSeek Chat API 진단 스크립트
# 
# 사용법:
#   ./scripts/diagnose-chat-api.sh
#
# 이 스크립트는 다음을 확인합니다:
# 1. Vercel 환경 변수 설정 상태
# 2. API 키 형식 검증
# 3. 최근 배포 상태
# 4. API 엔드포인트 테스트
# 5. 로그 확인

set -e

# 프로젝트 디렉토리 (실제 경로로 교체하거나 환경 변수 사용)
TECH_BLOG_DIR="${TECH_BLOG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DEPLOYMENT_URL="https://tech.2twodragon.com"
API_ENDPOINT="${DEPLOYMENT_URL}/api/chat"

cd "$TECH_BLOG_DIR"

echo "🔍 DeepSeek Chat API 진단 시작"
echo "=================================="
echo ""

# 1. Vercel CLI 설치 확인
echo "1️⃣  Vercel CLI 확인 중..."
if ! command -v vercel &> /dev/null; then
    echo "   ❌ Vercel CLI가 설치되어 있지 않습니다."
    echo "   설치: npm i -g vercel"
    exit 1
fi
echo "   ✅ Vercel CLI 설치됨"
echo ""

# 2. Vercel 로그인 상태 확인
echo "2️⃣  Vercel 로그인 상태 확인 중..."
if ! vercel whoami &> /dev/null; then
    echo "   ❌ Vercel에 로그인되어 있지 않습니다."
    echo "   로그인: vercel login"
    exit 1
fi
echo "   ✅ Vercel 로그인됨: $(vercel whoami)"
echo ""

# 3. 환경 변수 확인
echo "3️⃣  환경 변수 확인 중..."
ENV_OUTPUT=$(vercel env ls 2>&1)
if echo "$ENV_OUTPUT" | grep -q "DEEPSEEK_API_KEY"; then
    echo "   ✅ DEEPSEEK_API_KEY 발견"
    
    # 환경 변수 상세 정보
    DEEPSEEK_ENV=$(echo "$ENV_OUTPUT" | grep "DEEPSEEK_API_KEY")
    echo "   📋 환경 변수 정보:"
    echo "      $DEEPSEEK_ENV"
    
    # API 키 형식 확인 (로컬 .env 파일에서)
    if [ -f ".env.local" ]; then
        if grep -q "DEEPSEEK_API_KEY=sk-" .env.local; then
            echo "   ✅ API 키 형식 확인됨 (sk-로 시작)"
        else
            echo "   ⚠️  API 키 형식 확인 필요 (.env.local에서 sk-로 시작하는지 확인)"
        fi
    else
        echo "   💡 .env.local 파일이 없습니다. (로컬 개발용)"
    fi
else
    echo "   ❌ DEEPSEEK_API_KEY를 찾을 수 없습니다."
    echo ""
    echo "   🔧 해결 방법:"
    echo "      1. Vercel 대시보드에서 환경 변수 추가:"
    echo "         https://vercel.com/dashboard → 프로젝트 선택 → Settings → Environment Variables"
    echo ""
    echo "      2. 또는 스크립트 사용:"
    echo "         ./scripts/add-deepseek-key.sh"
    echo ""
    exit 1
fi
echo ""

# 4. 최근 배포 확인
echo "4️⃣  최근 배포 확인 중..."
DEPLOYMENTS=$(vercel ls 2>&1 | head -5)
if echo "$DEPLOYMENTS" | grep -q "tech.2twodragon.com\|tech-blog"; then
    echo "   ✅ 배포 정보 발견"
    echo "   📋 최근 배포:"
    echo "$DEPLOYMENTS" | head -3 | sed 's/^/      /'
else
    echo "   ⚠️  배포 정보를 찾을 수 없습니다."
fi
echo ""

# 5. API 엔드포인트 테스트
echo "5️⃣  API 엔드포인트 테스트 중..."
echo "   📡 엔드포인트: $API_ENDPOINT"
echo ""

# 간단한 테스트 요청
TEST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Origin: $DEPLOYMENT_URL" \
  -d '{"message":"테스트"}' \
  2>&1) || true

HTTP_CODE=$(echo "$TEST_RESPONSE" | tail -1)
RESPONSE_BODY=$(echo "$TEST_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ API 응답 성공 (HTTP $HTTP_CODE)"
    if echo "$RESPONSE_BODY" | grep -q "response"; then
        echo "   ✅ 응답 형식 정상"
        RESPONSE_TEXT=$(echo "$RESPONSE_BODY" | grep -o '"response":"[^"]*' | cut -d'"' -f4 | head -c 100)
        if [ -n "$RESPONSE_TEXT" ]; then
            echo "   📝 응답 미리보기: ${RESPONSE_TEXT}..."
        fi
    else
        echo "   ⚠️  응답 형식 확인 필요"
        echo "   응답: ${RESPONSE_BODY:0:200}..."
    fi
elif [ "$HTTP_CODE" = "503" ]; then
    echo "   ❌ API 서비스 사용 불가 (HTTP $HTTP_CODE)"
    if echo "$RESPONSE_BODY" | grep -q "API_KEY"; then
        echo "   🔍 원인: API 키 문제 가능성"
        echo "   응답: ${RESPONSE_BODY:0:200}..."
    else
        echo "   응답: ${RESPONSE_BODY:0:200}..."
    fi
elif [ "$HTTP_CODE" = "403" ]; then
    echo "   ❌ 요청 거부됨 (HTTP $HTTP_CODE)"
    echo "   🔍 원인: Origin 검증 실패 가능성"
    echo "   응답: ${RESPONSE_BODY:0:200}..."
elif [ "$HTTP_CODE" = "429" ]; then
    echo "   ⚠️  Rate Limit 초과 (HTTP $HTTP_CODE)"
    echo "   💡 잠시 후 다시 시도하세요"
else
    echo "   ⚠️  예상치 못한 응답 (HTTP $HTTP_CODE)"
    echo "   응답: ${RESPONSE_BODY:0:200}..."
fi
echo ""

# 6. 최근 로그 확인
echo "6️⃣  최근 로그 확인 중..."
echo "   📋 최근 10개 로그 항목 (Chat API 관련):"
RECENT_LOGS=$(vercel logs "$DEPLOYMENT_URL" --since 1h 2>&1 | grep -i "chat\|deepseek\|api" | tail -10 || echo "   로그를 가져올 수 없습니다.")
if [ -n "$RECENT_LOGS" ] && [ "$RECENT_LOGS" != "   로그를 가져올 수 없습니다." ]; then
    echo "$RECENT_LOGS" | sed 's/^/      /'
else
    echo "   💡 최근 1시간 내 Chat API 관련 로그가 없습니다."
    echo "   전체 로그 확인: vercel logs $DEPLOYMENT_URL --follow"
fi
echo ""

# 7. 요약 및 권장 사항
echo "=================================="
echo "📊 진단 요약"
echo "=================================="
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Chat API가 정상적으로 작동하고 있습니다!"
    echo ""
    echo "💡 다음 단계:"
    echo "   - 브라우저에서 채팅 위젯 테스트"
    echo "   - 개발자 도구(F12) → Network 탭에서 /api/chat 요청 확인"
else
    echo "⚠️  Chat API에 문제가 있을 수 있습니다."
    echo ""
    echo "🔧 권장 조치 사항:"
    echo ""
    
    if echo "$ENV_OUTPUT" | grep -q "DEEPSEEK_API_KEY"; then
        echo "   1. ✅ 환경 변수는 설정되어 있습니다."
    else
        echo "   1. ❌ 환경 변수 설정 필요:"
        echo "      - Vercel 대시보드에서 DEEPSEEK_API_KEY 추가"
        echo "      - 또는: ./scripts/add-deepseek-key.sh 실행"
    fi
    
    echo ""
    echo "   2. 📋 로그 확인:"
    echo "      vercel logs $DEPLOYMENT_URL --follow"
    echo ""
    echo "   3. 🔄 재배포:"
    echo "      git commit -m 'fix: Chat API 수정'"
    echo "      git push"
    echo ""
    echo "   4. 🌐 브라우저 콘솔 확인:"
    echo "      - 개발자 도구(F12) → Console 탭"
    echo "      - Network 탭 → /api/chat 요청 확인"
fi

echo ""
echo "✅ 진단 완료"
echo ""
