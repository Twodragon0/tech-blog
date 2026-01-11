#!/bin/bash

# 보안 기능 테스트 스크립트
# Rate Limiting 및 Bot 보호 동작 확인

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정
API_URL="${API_URL:-https://tech.2twodragon.com/api/chat}"
SESSION_ID="test-session-$(date +%s)"

echo -e "${BLUE}=== Vercel Firewall 보안 테스트 ===${NC}\n"

# 테스트 결과 카운터
PASSED=0
FAILED=0

# 테스트 함수
test_case() {
    local name="$1"
    local expected_status="$2"
    local curl_args="$3"
    
    echo -n "테스트: $name ... "
    
    response=$(curl -s -w "\n%{http_code}" $curl_args "$API_URL" 2>/dev/null || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $http_code)"
        echo -e "  Response: $body"
        ((FAILED++))
        return 1
    fi
}

# 1. 정상 요청 테스트
echo -e "${YELLOW}1. 정상 요청 테스트${NC}"
test_case "정상 POST 요청" "200" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
    -d '{\"message\":\"안녕하세요\",\"sessionId\":\"$SESSION_ID\"}'"

# 2. Rate Limiting 테스트
echo -e "\n${YELLOW}2. Rate Limiting 테스트${NC}"
echo "  15개의 연속 요청 전송 중..."

rate_limit_triggered=false
for i in {1..16}; do
    response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H 'Content-Type: application/json' \
        -H 'Origin: https://tech.2twodragon.com' \
        -H 'User-Agent: Mozilla/5.0' \
        -d "{\"message\":\"테스트 메시지 $i\",\"sessionId\":\"$SESSION_ID\"}" \
        "$API_URL" 2>/dev/null || echo -e "\n000")
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "429" ]; then
        rate_limit_triggered=true
        echo -e "  요청 $i: ${GREEN}✓ Rate Limit 트리거됨${NC} (HTTP 429)"
        break
    else
        echo -e "  요청 $i: HTTP $http_code"
    fi
    
    # 요청 간 짧은 지연
    sleep 0.1
done

if [ "$rate_limit_triggered" = true ]; then
    echo -e "${GREEN}✓ Rate Limiting 작동 확인${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ Rate Limiting이 트리거되지 않음${NC}"
    ((FAILED++))
fi

# 3. Bot 보호 테스트
echo -e "\n${YELLOW}3. Bot 보호 테스트${NC}"

# Bot User-Agent로 요청
test_case "Bot User-Agent 차단" "403" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: curl/7.68.0' \
    -d '{\"message\":\"테스트\",\"sessionId\":\"bot-test\"}'"

# 빈 User-Agent
test_case "빈 User-Agent 차단" "403" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: ' \
    -d '{\"message\":\"테스트\",\"sessionId\":\"empty-ua-test\"}'"

# 4. CORS 정책 테스트
echo -e "\n${YELLOW}4. CORS 정책 테스트${NC}"

# 허용되지 않은 Origin
test_case "허용되지 않은 Origin 차단" "403" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://evil.com' \
    -H 'User-Agent: Mozilla/5.0' \
    -d '{\"message\":\"테스트\",\"sessionId\":\"cors-test\"}'"

# 5. 입력 검증 테스트
echo -e "\n${YELLOW}5. 입력 검증 테스트${NC}"

# XSS 시도
test_case "XSS 패턴 차단" "400" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: Mozilla/5.0' \
    -d '{\"message\":\"<script>alert(1)</script>\",\"sessionId\":\"xss-test\"}'"

# 빈 메시지
test_case "빈 메시지 거부" "400" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: Mozilla/5.0' \
    -d '{\"message\":\"\",\"sessionId\":\"empty-test\"}'"

# 메시지 길이 초과
test_case "메시지 길이 초과 거부" "400" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: Mozilla/5.0' \
    -d '{\"message\":\"'$(python3 -c "print('a' * 2001)')\",\"sessionId\":\"length-test\"}'"

# 6. 요청 크기 제한 테스트
echo -e "\n${YELLOW}6. 요청 크기 제한 테스트${NC}"

# 큰 요청 (100KB 초과)
large_payload=$(python3 -c "print('a' * 100001)")
test_case "요청 크기 초과 거부" "413" \
    "-X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: Mozilla/5.0' \
    -d '{\"message\":\"테스트\",\"conversationHistory\":[\"$large_payload\"]}'"

# 7. Rate Limit 헤더 확인
echo -e "\n${YELLOW}7. Rate Limit 헤더 확인${NC}"

response=$(curl -s -I \
    -X POST \
    -H 'Content-Type: application/json' \
    -H 'Origin: https://tech.2twodragon.com' \
    -H 'User-Agent: Mozilla/5.0' \
    -d "{\"message\":\"헤더 테스트\",\"sessionId\":\"header-test\"}" \
    "$API_URL" 2>/dev/null || echo "")

if echo "$response" | grep -q "X-RateLimit-Limit"; then
    echo -e "${GREEN}✓ Rate Limit 헤더 존재${NC}"
    echo "$response" | grep "X-RateLimit"
    ((PASSED++))
else
    echo -e "${RED}✗ Rate Limit 헤더 없음${NC}"
    ((FAILED++))
fi

# 8. Request ID 헤더 확인
echo -e "\n${YELLOW}8. Request ID 헤더 확인${NC}"

if echo "$response" | grep -q "X-Request-ID"; then
    echo -e "${GREEN}✓ Request ID 헤더 존재${NC}"
    echo "$response" | grep "X-Request-ID"
    ((PASSED++))
else
    echo -e "${RED}✗ Request ID 헤더 없음${NC}"
    ((FAILED++))
fi

# 결과 요약
echo -e "\n${BLUE}=== 테스트 결과 ===${NC}"
echo -e "통과: ${GREEN}$PASSED${NC}"
echo -e "실패: ${RED}$FAILED${NC}"
echo -e "총계: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ 모든 테스트 통과!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ 일부 테스트 실패${NC}"
    exit 1
fi
