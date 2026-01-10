#!/bin/bash
# DeepSeek API 키를 online-course 프로젝트에서 가져와 tech-blog 프로젝트에 추가하는 스크립트
# 
# 사용법:
#   ./scripts/add-deepseek-key.sh
#
# 주의: Vercel CLI가 설치되어 있고 로그인되어 있어야 합니다.

set -e

ONLINE_COURSE_DIR="/Users/twodragon/twodragon114@gmail.com - Google Drive/내 드라이브/online-course"
TECH_BLOG_DIR="/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"

echo "🔍 online-course 프로젝트에서 DeepSeek API 키 확인 중..."

# online-course 프로젝트에서 환경 변수 확인
cd "$ONLINE_COURSE_DIR"
if ! vercel env ls 2>/dev/null | grep -q "DEEPSEEK_API_KEY"; then
    echo "❌ online-course 프로젝트에 DEEPSEEK_API_KEY가 설정되어 있지 않습니다."
    exit 1
fi

echo "✅ online-course 프로젝트에서 DEEPSEEK_API_KEY 발견"

# tech-blog 프로젝트로 이동
cd "$TECH_BLOG_DIR"

echo ""
echo "📝 tech-blog 프로젝트에 DEEPSEEK_API_KEY 추가 중..."

# Vercel 프로젝트 확인
if ! vercel project ls 2>/dev/null | grep -q "tech-blog\|tech.2twodragon.com"; then
    echo "⚠️  tech-blog Vercel 프로젝트를 찾을 수 없습니다."
    echo "   Vercel 대시보드에서 수동으로 추가해주세요:"
    echo "   1. https://vercel.com/dashboard 접속"
    echo "   2. tech-blog 프로젝트 선택"
    echo "   3. Settings → Environment Variables"
    echo "   4. DEEPSEEK_API_KEY 추가 (online-course와 동일한 값)"
    exit 1
fi

# online-course에서 환경 변수 값 가져오기 (보안상 직접 값은 표시하지 않음)
echo ""
echo "🔐 online-course 프로젝트의 DEEPSEEK_API_KEY를 tech-blog 프로젝트에 복사합니다..."
echo ""

# Vercel CLI를 사용하여 환경 변수 추가
# 주의: 실제 값은 Vercel 대시보드에서 확인하거나, vercel env pull로 가져와야 합니다
echo "💡 Vercel CLI를 사용하여 환경 변수를 추가하려면:"
echo ""
echo "   1. online-course 프로젝트에서 키 확인:"
echo "      cd \"$ONLINE_COURSE_DIR\""
echo "      vercel env pull .env.local"
echo "      # .env.local 파일에서 DEEPSEEK_API_KEY 값 확인"
echo ""
echo "   2. tech-blog 프로젝트에 키 추가:"
echo "      cd \"$TECH_BLOG_DIR\""
echo "      vercel env add DEEPSEEK_API_KEY"
echo "      # 프롬프트에 online-course의 키 값 입력"
echo "      # Environment: Production, Preview, Development 모두 선택"
echo ""
echo "또는 Vercel 대시보드에서:"
echo "   1. https://vercel.com/dashboard 접속"
echo "   2. online-course 프로젝트 → Settings → Environment Variables"
echo "   3. DEEPSEEK_API_KEY 값 복사"
echo "   4. tech-blog 프로젝트 → Settings → Environment Variables"
echo "   5. DEEPSEEK_API_KEY 추가 (복사한 값 붙여넣기)"
echo "   6. Environment: Production, Preview, Development 모두 선택"
echo ""
