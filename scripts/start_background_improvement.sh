#!/bin/bash
# 백그라운드에서 포스팅 개선 프로세스 시작

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/improvement.log"
PID_FILE="$PROJECT_ROOT/improvement.pid"

cd "$PROJECT_ROOT"

# 이미 실행 중인 프로세스 확인
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "이미 실행 중인 프로세스가 있습니다. (PID: $OLD_PID)"
        echo "중지하려면: kill $OLD_PID"
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

echo "백그라운드에서 포스팅 개선 프로세스 시작..."
echo "로그 파일: $LOG_FILE"
echo "PID 파일: $PID_FILE"

# 백그라운드 실행
nohup python3 "$SCRIPT_DIR/smart_improve_posts.py" > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# PID 저장
echo $NEW_PID > "$PID_FILE"

echo "프로세스 시작됨 (PID: $NEW_PID)"
echo "로그 확인: tail -f $LOG_FILE"
echo "프로세스 확인: ps -p $NEW_PID"
echo "중지: kill $NEW_PID"
