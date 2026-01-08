#!/bin/bash
# 의존성 설치 스크립트

echo "=========================================="
echo "의존성 설치"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: python3가 설치되어 있지 않습니다."
    exit 1
fi

echo "Python 버전: $(python3 --version)"
echo ""

# pip 확인
if ! command -v pip3 &> /dev/null; then
    echo "오류: pip3가 설치되어 있지 않습니다."
    exit 1
fi

echo "의존성 설치 중..."
pip3 install --break-system-packages -r "$SCRIPT_DIR/requirements.txt" || pip3 install --user -r "$SCRIPT_DIR/requirements.txt"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "의존성 설치 완료!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "의존성 설치 실패"
    echo "=========================================="
    exit 1
fi
