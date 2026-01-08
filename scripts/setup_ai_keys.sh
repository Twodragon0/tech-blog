#!/bin/bash
# AI API 키 설정 스크립트

echo "=========================================="
echo "AI API 키 설정"
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

# Claude API 키 입력
read -p "Claude API 키를 입력하세요 (없으면 Enter): " CLAUDE_KEY
if [ ! -z "$CLAUDE_KEY" ]; then
    # 기존 설정 제거
    sed -i.bak '/^export CLAUDE_API_KEY=/d' "$SHELL_RC" 2>/dev/null || true
    # 새 설정 추가
    echo "export CLAUDE_API_KEY=\"$CLAUDE_KEY\"" >> "$SHELL_RC"
    echo "✓ Claude API 키 설정 완료"
else
    echo "Claude API 키를 건너뜁니다."
fi

# Gemini API 키 입력
read -p "Gemini API 키를 입력하세요 (없으면 Enter): " GEMINI_KEY
if [ ! -z "$GEMINI_KEY" ]; then
    # 기존 설정 제거
    sed -i.bak '/^export GEMINI_API_KEY=/d' "$SHELL_RC" 2>/dev/null || true
    # 새 설정 추가
    echo "export GEMINI_API_KEY=\"$GEMINI_KEY\"" >> "$SHELL_RC"
    echo "✓ Gemini API 키 설정 완료"
else
    echo "Gemini API 키를 건너뜁니다."
fi

echo ""
echo "=========================================="
echo "설정 완료!"
echo "=========================================="
echo ""
echo "다음 명령어를 실행하여 환경 변수를 로드하세요:"
echo "  source $SHELL_RC"
echo ""
echo "또는 새 터미널을 열면 자동으로 적용됩니다."
echo ""
