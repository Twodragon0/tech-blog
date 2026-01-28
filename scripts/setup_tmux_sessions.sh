#!/bin/bash

# tmux 세션 생성 스크립트
# tech.2twodragon.com과 edu.2twodragon.com 블로그용 세션 관리

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# tmux 설치 확인
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}❌ tmux가 설치되어 있지 않습니다.${NC}"
    echo -e "${YELLOW}다음 명령어로 설치하세요:${NC}"
    echo "  brew install tmux"
    exit 1
fi

# 디렉토리 경로 설정 (환경에 맞게 수정 필요)
TECH_BLOG_DIR="${TECH_BLOG_DIR:-$HOME/Desktop/tech-blog}"
EDU_BLOG_DIR="${EDU_BLOG_DIR:-$HOME/Desktop/online-course}"

# blog-tech 세션 생성
if tmux has-session -t blog-tech 2>/dev/null; then
    echo -e "${YELLOW}⚠️  blog-tech 세션이 이미 존재합니다.${NC}"
    echo -e "${GREEN}세션에 연결하려면: tmux attach -t blog-tech${NC}"
else
    echo -e "${GREEN}📝 blog-tech 세션 생성 중...${NC}"
    tmux new-session -d -s blog-tech -c "$TECH_BLOG_DIR"
    echo -e "${GREEN}✅ blog-tech 세션 생성 완료 (tech.2twodragon.com)${NC}"
    echo -e "${GREEN}세션에 연결하려면: tmux attach -t blog-tech${NC}"
fi

# blog-edu 세션 생성
if tmux has-session -t blog-edu 2>/dev/null; then
    echo -e "${YELLOW}⚠️  blog-edu 세션이 이미 존재합니다.${NC}"
    echo -e "${GREEN}세션에 연결하려면: tmux attach -t blog-edu${NC}"
else
    if [ ! -d "$EDU_BLOG_DIR" ]; then
        echo -e "${RED}❌ edu 블로그 디렉토리를 찾을 수 없습니다:${NC}"
        echo "  $EDU_BLOG_DIR"
        exit 1
    fi
    
    echo -e "${GREEN}📝 blog-edu 세션 생성 중...${NC}"
    tmux new-session -d -s blog-edu -c "$EDU_BLOG_DIR"
    echo -e "${GREEN}✅ blog-edu 세션 생성 완료 (edu.2twodragon.com)${NC}"
    echo -e "${GREEN}세션에 연결하려면: tmux attach -t blog-edu${NC}"
fi

echo ""
echo -e "${GREEN}📋 사용 가능한 tmux 세션:${NC}"
tmux list-sessions 2>/dev/null || echo "  (세션이 없습니다)"

echo ""
echo -e "${GREEN}💡 유용한 tmux 명령어:${NC}"
echo "  tmux attach -t blog-tech    # tech 블로그 세션 연결"
echo "  tmux attach -t blog-edu      # edu 블로그 세션 연결"
echo "  tmux list-sessions           # 모든 세션 목록 보기"
echo "  tmux kill-session -t blog-tech  # 세션 종료"
echo "  tmux kill-session -t blog-edu   # 세션 종료"
echo ""
echo -e "${GREEN}🎯 Cursor IDE에서 활용하기:${NC}"
echo "  1. Cursor 통합 터미널에서:"
echo "     tmux attach -t blog-tech"
echo "  2. Cursor에서 프로젝트 열기:"
echo "     code \"$TECH_BLOG_DIR\"  # tech 블로그"
echo "     code \"$EDU_BLOG_DIR\"   # edu 블로그"
echo "  3. Cursor 터미널 분할:"
echo "     - 터미널 1: tmux attach -t blog-tech"
echo "     - 터미널 2: tmux attach -t blog-edu"
echo ""
echo -e "${GREEN}📂 각 세션의 작업 디렉토리:${NC}"
echo "  blog-tech: $TECH_BLOG_DIR"
echo "  blog-edu:  $EDU_BLOG_DIR"
