#!/bin/bash
# 1시간 동안 포스팅 개선 스크립트 실행

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/improvement_log.txt"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "포스팅 개선 프로세스 시작"
echo "실행 시간: 1시간"
echo "로그 파일: $LOG_FILE"
echo "=========================================="
echo ""

# 로그 파일 초기화
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 포스팅 개선 프로세스 시작" > "$LOG_FILE"

# Python 스크립트 실행
python3 "$SCRIPT_DIR/smart_improve_posts.py" >> "$LOG_FILE" 2>&1

echo ""
echo "=========================================="
echo "포스팅 개선 프로세스 완료"
echo "로그 파일 확인: tail -f $LOG_FILE"
echo "=========================================="
