#!/bin/bash
# Vercel & Performance 종합 모니터링 스크립트
#
# 사용법:
#   ./scripts/monitor_vercel_builds.sh [deployment-url] [--alert-only] [--detailed]
#
# 예시:
#   ./scripts/monitor_vercel_builds.sh
#   ./scripts/monitor_vercel_builds.sh https://tech.2twodragon.com --alert-only
#   ./scripts/monitor_vercel_builds.sh https://tech.2twodragon.com --detailed

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DEPLOYMENT_URL="${1:-https://tech.2twodragon.com}"
ALERT_ONLY=false
DETAILED=false

# Parse arguments
while [[ $# -gt 1 ]]; do
    case $2 in
        --alert-only) ALERT_ONLY=true; shift ;;
        --detailed) DETAILED=true; shift ;;
        *) shift ;;
    esac
done

# Thresholds (조정 가능)
LCP_THRESHOLD=2500      # ms - Largest Contentful Paint
FID_THRESHOLD=100       # ms - First Input Delay
CLS_THRESHOLD=0.1       # - Cumulative Layout Shift
BUILD_TIME_THRESHOLD=120 # seconds

ALERT_COUNT=0
WARNINGS=()

_echo() {
    if [ "$ALERT_ONLY" = false ]; then
        echo -e "$@"
    fi
}

_alert() {
    echo -e "${RED}❌ ALERT: $1${NC}" >&2
    ALERT_COUNT=$((ALERT_COUNT + 1))
    WARNINGS+=("$1")
}

_warn() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}" >&2
}

_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

_info() {
    _echo "${BLUE}ℹ️  $1${NC}"
}

_section() {
    _echo ""
    _echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    _echo "${BLUE}$1${NC}"
    _echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    _echo ""
}

# === 0. 환경 체크 ===
_section "1. Environment Setup"

if ! command -v curl &> /dev/null; then
    _alert "curl이 설치되어 있지 않습니다."
    exit 1
fi

VERCEL_AVAILABLE=false

if ! command -v vercel &> /dev/null; then
    _warn "Vercel CLI가 설치되어 있지 않습니다. Vercel 관련 체크를 건너뜁니다."
elif [ -z "$VERCEL_TOKEN" ] && ! vercel whoami &>/dev/null; then
    _warn "Vercel에 인증되어 있지 않습니다. Vercel 관련 체크를 건너뜁니다."
else
    VERCEL_AVAILABLE=true
fi

_success "Environment checks passed"

# === 1. Site Availability (HTTP check) ===
_section "2. Site Availability"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$DEPLOYMENT_URL" 2>/dev/null || echo "000")
if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 400 ]; then
    _success "Site is accessible (HTTP $HTTP_STATUS)"
else
    _alert "Site returned HTTP $HTTP_STATUS for $DEPLOYMENT_URL"
fi

# === 1a. Vercel 배포 상태 (토큰이 있을 때만) ===
if [ "$VERCEL_AVAILABLE" = true ]; then
    _section "2a. Vercel Deployment Status"

    DEPLOYMENTS=$(VERCEL_TOKEN="${VERCEL_TOKEN}" vercel ls --json 2>/dev/null || echo "")

    if [ -z "$DEPLOYMENTS" ]; then
        _warn "배포 정보를 가져올 수 없습니다. Vercel 배포 체크를 건너뜁니다."
    else
        # 최근 배포 확인
        LATEST_DEPLOYMENT=$(echo "$DEPLOYMENTS" | jq -r '.[0] | "\(.url) - State: \(.state)"' 2>/dev/null || echo "Unable to parse deployments")
        _info "Latest deployment: $LATEST_DEPLOYMENT"

        # 배포 목록 (성공한 것만)
        _echo ""
        _echo "Recent deployments (latest 5):"
        VERCEL_TOKEN="${VERCEL_TOKEN}" vercel ls --limit 5 2>/dev/null | tail -n +2 | while read -r line; do
            if echo "$line" | grep -q "READY"; then
                echo -e "${GREEN}✓ $line${NC}"
            elif echo "$line" | grep -q "FAILED"; then
                echo -e "${RED}✗ $line${NC}"
            else
                echo "$line"
            fi
        done || true
    fi
else
    _info "Vercel CLI not available or not authenticated - skipping Vercel deployment checks"
fi

# === 2. Core Web Vitals (Lighthouse API) ===
_section "3. Core Web Vitals Analysis"

# PageSpeed Insights API를 사용할 경우
if command -v curl &> /dev/null && [ -n "$PAGESPEED_API_KEY" ]; then
    _info "Checking Core Web Vitals via PageSpeed Insights..."

    PSI_URL="https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=$DEPLOYMENT_URL&key=$PAGESPEED_API_KEY"
    PSI_RESPONSE=$(curl -s "$PSI_URL" 2>/dev/null || echo "{}")

    # CWV 메트릭 추출
    LCP=$(echo "$PSI_RESPONSE" | jq -r '.lighthouseResult.audits."largest-contentful-paint".displayValue // "N/A"' 2>/dev/null)
    FID=$(echo "$PSI_RESPONSE" | jq -r '.lighthouseResult.audits."first-input-delay".displayValue // "N/A"' 2>/dev/null)
    CLS=$(echo "$PSI_RESPONSE" | jq -r '.lighthouseResult.audits."cumulative-layout-shift".displayValue // "N/A"' 2>/dev/null)

    _echo "  LCP (Largest Contentful Paint): $LCP (목표 < 2.5s)"
    _echo "  FID (First Input Delay):         $FID (목표 < 100ms)"
    _echo "  CLS (Cumulative Layout Shift):   $CLS (목표 < 0.1)"
else
    _info "PageSpeed Insights API key not configured"
    _echo "  Set PAGESPEED_API_KEY environment variable to enable CWV monitoring"
fi

# === 3. Sentry 에러 대시보드 (선택적) ===
_section "4. Sentry Error Dashboard"

if [ -n "$SENTRY_AUTH_TOKEN" ] && [ -n "$SENTRY_ORG" ] && [ -n "$SENTRY_PROJECT" ]; then
    _info "Fetching Sentry metrics..."

    SENTRY_URL="https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/?project=$SENTRY_PROJECT&status=unresolved"
    SENTRY_RESPONSE=$(curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" "$SENTRY_URL" 2>/dev/null || echo "[]")

    ISSUE_COUNT=$(echo "$SENTRY_RESPONSE" | jq 'length // 0' 2>/dev/null)

    if [ "$ISSUE_COUNT" -gt 0 ]; then
        _warn "Found $ISSUE_COUNT unresolved Sentry issues"

        # 상위 5개 이슈 표시
        echo "$SENTRY_RESPONSE" | jq -r '.[0:5] | .[] | "\(.title) (Events: \(.stats.\"24h\"[0][1]))"' 2>/dev/null | while read -r issue; do
            echo "    - $issue"
        done
    else
        _success "No unresolved Sentry issues"
    fi
else
    _info "Sentry credentials not configured"
    _echo "  Set SENTRY_AUTH_TOKEN, SENTRY_ORG, SENTRY_PROJECT to enable error monitoring"
fi

# === 4. 빌드 성능 메트릭 ===
_section "5. Build Performance Metrics"

_echo "Target Thresholds:"
_echo "  • Build Time:      < ${BUILD_TIME_THRESHOLD}s"
_echo "  • LCP:             < ${LCP_THRESHOLD}ms"
_echo "  • FID:             < ${FID_THRESHOLD}ms"
_echo "  • CLS:             < ${CLS_THRESHOLD}"
_echo "  • Deployment Success Rate: > 99%"

# === 5. 환경 변수 상태 (마스킹) ===
_section "6. Environment Variables Status"

_echo "Required environment variables:"
ENV_VARS=(
    "VERCEL_TOKEN"
    "SENTRY_AUTH_TOKEN"
    "PAGESPEED_API_KEY"
    "DEEPSEEK_API_KEY"
)

for var in "${ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        _success "$var is set"
    else
        _warn "$var is not set"
    fi
done

# === 6. 유용한 명령어 ===
_section "7. Useful Commands"

_echo "Vercel monitoring:"
_echo "  vercel logs --follow              # Real-time logs"
_echo "  vercel inspect $DEPLOYMENT_URL    # Detailed deployment info"
_echo "  vercel env ls                     # List environment variables"
_echo "  vercel ls --limit 10              # List recent deployments"
_echo ""
_echo "Local testing:"
_echo "  npm run build                     # Build locally"
_echo "  npm test                          # Run tests"
_echo "  bundle exec jekyll serve          # Serve locally"

# === 결과 요약 ===
_section "Summary"

if [ "$ALERT_COUNT" -eq 0 ]; then
    _success "All checks passed!"
    exit 0
else
    _alert "Found $ALERT_COUNT issues"
    _echo ""
    _echo "Issues:"
    for warning in "${WARNINGS[@]}"; do
        echo "  • $warning"
    done
    exit 1
fi
