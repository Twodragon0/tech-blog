#!/bin/bash
# AI 기반 포스팅 개선 스크립트 실행 (1시간)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/ai_improvement_log.txt"

cd "$PROJECT_ROOT"

# 환경 변수 확인
if [ -z "$CLAUDE_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "경고: AI API 키가 설정되지 않았습니다."
    echo "기본 템플릿 기반으로 개선이 진행됩니다."
    echo ""
    echo "API 키를 설정하려면:"
    echo "  ./scripts/setup_ai_keys.sh"
    echo ""
    read -p "계속하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "=========================================="
echo "AI 기반 포스팅 개선 프로세스 시작"
echo "실행 시간: 1시간"
echo "로그 파일: $LOG_FILE"
echo "=========================================="
echo ""

# 로그 파일 초기화
echo "[$(date '+%Y-%m-%d %H:%M:%S')] AI 기반 포스팅 개선 프로세스 시작" > "$LOG_FILE"

# Python 스크립트 실행
python3 "$SCRIPT_DIR/ai_improve_posts.py" >> "$LOG_FILE" 2>&1

echo ""
echo "=========================================="
echo "AI 기반 포스팅 개선 프로세스 완료"
echo "로그 파일 확인: tail -f $LOG_FILE"
echo "=========================================="
