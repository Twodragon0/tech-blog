#!/bin/bash
# LinkedIn API 키 설정 스크립트

echo "=========================================="
echo "LinkedIn API 키 설정"
echo "=========================================="
echo ""

# 현재 셸 확인
CURRENT_SHELL=$(basename "$SHELL")
SHELL_RC=""

if [ "$CURRENT_SHELL" = "zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ "$CURRENT_SHELL" = "bash" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

echo "현재 셸: $CURRENT_SHELL"
echo "설정 파일: $SHELL_RC"
echo ""

# .env 파일 경로
ENV_FILE="$(dirname "$0")/../.env"

# .env 파일이 없으면 .env.example에서 복사
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$(dirname "$0")/../.env.example" ]; then
        cp "$(dirname "$0")/../.env.example" "$ENV_FILE"
        echo "✓ .env 파일을 생성했습니다."
    else
        touch "$ENV_FILE"
        echo "✓ 새 .env 파일을 생성했습니다."
    fi
fi

# LinkedIn Client ID 입력
read -p "LinkedIn Client ID를 입력하세요: " CLIENT_ID
if [ ! -z "$CLIENT_ID" ]; then
    # .env 파일 업데이트
    if grep -q "^LINKEDIN_CLIENT_ID=" "$ENV_FILE"; then
        # macOS와 Linux 호환성을 위한 sed 명령어
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^LINKEDIN_CLIENT_ID=.*|LINKEDIN_CLIENT_ID=$CLIENT_ID|" "$ENV_FILE"
        else
            sed -i "s|^LINKEDIN_CLIENT_ID=.*|LINKEDIN_CLIENT_ID=$CLIENT_ID|" "$ENV_FILE"
        fi
    else
        echo "LINKEDIN_CLIENT_ID=$CLIENT_ID" >> "$ENV_FILE"
    fi
    
    # 셸 RC 파일에도 추가 (선택적)
    sed -i.bak '/^export LINKEDIN_CLIENT_ID=/d' "$SHELL_RC" 2>/dev/null || true
    echo "export LINKEDIN_CLIENT_ID=\"$CLIENT_ID\"" >> "$SHELL_RC"
    echo "✓ LinkedIn Client ID 설정 완료"
else
    echo "⚠️  Client ID를 입력하지 않았습니다."
fi

# LinkedIn Client Secret 입력
read -p "LinkedIn Client Secret을 입력하세요: " CLIENT_SECRET
if [ ! -z "$CLIENT_SECRET" ]; then
    # .env 파일 업데이트
    if grep -q "^LINKEDIN_CLIENT_SECRET=" "$ENV_FILE"; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^LINKEDIN_CLIENT_SECRET=.*|LINKEDIN_CLIENT_SECRET=$CLIENT_SECRET|" "$ENV_FILE"
        else
            sed -i "s|^LINKEDIN_CLIENT_SECRET=.*|LINKEDIN_CLIENT_SECRET=$CLIENT_SECRET|" "$ENV_FILE"
        fi
    else
        echo "LINKEDIN_CLIENT_SECRET=$CLIENT_SECRET" >> "$ENV_FILE"
    fi
    
    # 셸 RC 파일에도 추가 (선택적)
    sed -i.bak '/^export LINKEDIN_CLIENT_SECRET=/d' "$SHELL_RC" 2>/dev/null || true
    echo "export LINKEDIN_CLIENT_SECRET=\"$CLIENT_SECRET\"" >> "$SHELL_RC"
    echo "✓ LinkedIn Client Secret 설정 완료"
else
    echo "⚠️  Client Secret을 입력하지 않았습니다."
fi

# Redirect URI 입력
read -p "LinkedIn Redirect URI를 입력하세요 (기본값: http://localhost:8000/auth/linkedin/callback): " REDIRECT_URI
REDIRECT_URI=${REDIRECT_URI:-http://localhost:8000/auth/linkedin/callback}

if grep -q "^LINKEDIN_REDIRECT_URI=" "$ENV_FILE"; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^LINKEDIN_REDIRECT_URI=.*|LINKEDIN_REDIRECT_URI=$REDIRECT_URI|" "$ENV_FILE"
    else
        sed -i "s|^LINKEDIN_REDIRECT_URI=.*|LINKEDIN_REDIRECT_URI=$REDIRECT_URI|" "$ENV_FILE"
    fi
else
    echo "LINKEDIN_REDIRECT_URI=$REDIRECT_URI" >> "$ENV_FILE"
fi
echo "✓ Redirect URI 설정 완료"

echo ""
echo "=========================================="
echo "설정 완료!"
echo "=========================================="
echo ""
echo "⚠️  보안 주의사항:"
echo "  - .env 파일은 절대 Git에 커밋하지 마세요!"
echo "  - Client Secret은 안전하게 보관하세요."
echo ""
echo "다음 단계:"
echo "  1. LinkedIn Developer Portal에서 Redirect URI를 등록하세요:"
echo "     $REDIRECT_URI"
echo "  2. OAuth 인증을 위해 다음 스크립트를 실행하세요:"
echo "     python scripts/linkedin_oauth.py"
echo ""
echo "환경 변수를 로드하려면:"
echo "  source $SHELL_RC"
echo "  또는"
echo "  export \$(cat $ENV_FILE | xargs)"
echo ""
