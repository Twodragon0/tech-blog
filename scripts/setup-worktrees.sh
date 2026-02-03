#!/bin/bash
# Git Worktree 병렬 세션 관리 스크립트
# 여러 Claude 세션을 동시에 실행하기 위한 작업 트리 생성/관리 도구
#
# Usage:
#   bash scripts/setup-worktrees.sh setup    # 워크트리 생성
#   bash scripts/setup-worktrees.sh cleanup  # 워크트리 삭제
#   bash scripts/setup-worktrees.sh status   # 워크트리 상태 확인
#   bash scripts/setup-worktrees.sh aliases  # .zshrc에 추가할 alias 출력

set -euo pipefail

# ===========================
# Configuration
# ===========================
REPO_ROOT="/Users/yong/Desktop/tech-blog"
WORKTREE_BASE="$HOME/worktrees"
PROJECT="tech-blog"

# Worktree 정의: name:branch:description
WORKTREES=(
  "a:work-a:Content writing and post updates"
  "b:work-b:Script development and tooling"
  "c:work-c:Feature development and testing"
  "d:work-d:Analytics and read-only analysis"
)

# ===========================
# Colors
# ===========================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ===========================
# Helper Functions
# ===========================
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

# ===========================
# Setup Function
# ===========================
setup() {
  log_info "Setting up worktrees for $PROJECT..."

  # 워크트리 디렉토리 생성
  if [[ ! -d "$WORKTREE_BASE" ]]; then
    mkdir -p "$WORKTREE_BASE"
    log_success "Created worktree base directory: $WORKTREE_BASE"
  fi

  cd "$REPO_ROOT"

  # 각 워크트리 생성
  for wt_config in "${WORKTREES[@]}"; do
    IFS=':' read -r name branch description <<< "$wt_config"
    worktree_path="$WORKTREE_BASE/${PROJECT}-${name}"

    # 이미 존재하는지 확인
    if [[ -d "$worktree_path" ]]; then
      log_warn "Worktree already exists: $worktree_path (skipping)"
      continue
    fi

    log_info "Creating worktree: $name ($description)"

    # 브랜치가 존재하는지 확인
    if git show-ref --verify --quiet "refs/heads/$branch"; then
      log_info "Branch $branch already exists, using it"
      git worktree add "$worktree_path" "$branch"
    else
      log_info "Creating new branch: $branch"
      git worktree add -b "$branch" "$worktree_path" main
    fi

    log_success "Created: $worktree_path"
  done

  echo ""
  log_success "All worktrees created successfully!"
  echo ""
  log_info "Next steps:"
  echo "  1. Run: bash scripts/setup-worktrees.sh aliases"
  echo "  2. Copy the alias commands to your ~/.zshrc"
  echo "  3. Run: source ~/.zshrc"
  echo "  4. Use: za, zb, zc, zd, zm to switch between worktrees"
}

# ===========================
# Cleanup Function
# ===========================
cleanup() {
  log_warn "Cleaning up all worktrees..."

  cd "$REPO_ROOT"

  for wt_config in "${WORKTREES[@]}"; do
    IFS=':' read -r name branch description <<< "$wt_config"
    worktree_path="$WORKTREE_BASE/${PROJECT}-${name}"

    if [[ -d "$worktree_path" ]]; then
      log_info "Removing worktree: $worktree_path"
      git worktree remove "$worktree_path" --force 2>/dev/null || true
      log_success "Removed: $worktree_path"
    else
      log_warn "Worktree not found: $worktree_path (skipping)"
    fi

    # 브랜치 삭제 여부 확인
    if git show-ref --verify --quiet "refs/heads/$branch"; then
      read -p "Delete branch $branch? (y/N): " confirm
      if [[ "$confirm" =~ ^[Yy]$ ]]; then
        git branch -D "$branch" 2>/dev/null || true
        log_success "Deleted branch: $branch"
      else
        log_info "Kept branch: $branch"
      fi
    fi
  done

  echo ""
  log_success "Cleanup completed!"
}

# ===========================
# Status Function
# ===========================
status() {
  log_info "Worktree status for $PROJECT:"
  echo ""

  cd "$REPO_ROOT"
  git worktree list

  echo ""
  log_info "Configured worktrees:"
  for wt_config in "${WORKTREES[@]}"; do
    IFS=':' read -r name branch description <<< "$wt_config"
    worktree_path="$WORKTREE_BASE/${PROJECT}-${name}"

    if [[ -d "$worktree_path" ]]; then
      echo -e "  ${GREEN}✓${NC} $name: $worktree_path ($description)"
    else
      echo -e "  ${RED}✗${NC} $name: $worktree_path ($description)"
    fi
  done
}

# ===========================
# Aliases Function
# ===========================
aliases() {
  log_info "Copy these aliases to your ~/.zshrc:"
  echo ""
  echo "# ============================="
  echo "# Tech Blog Worktree Aliases"
  echo "# ============================="

  for wt_config in "${WORKTREES[@]}"; do
    IFS=':' read -r name branch description <<< "$wt_config"
    worktree_path="$WORKTREE_BASE/${PROJECT}-${name}"
    echo "alias z${name}='cd $worktree_path && claude'  # $description"
  done

  echo "alias zm='cd $REPO_ROOT && claude'  # Main worktree"
  echo ""

  log_info "After adding to ~/.zshrc, run: source ~/.zshrc"
  echo ""
  log_info "Usage examples:"
  echo "  za  # Work on content (worktree a)"
  echo "  zb  # Work on scripts (worktree b)"
  echo "  zc  # Work on features (worktree c)"
  echo "  zd  # Analytics only (worktree d)"
  echo "  zm  # Main branch"
}

# ===========================
# Help Function
# ===========================
show_help() {
  cat << EOF
Git Worktree 병렬 세션 관리 스크립트

여러 Claude 세션을 동시에 실행하기 위한 작업 트리 생성/관리 도구

Usage:
  bash scripts/setup-worktrees.sh <command>

Commands:
  setup     워크트리 생성 (a, b, c, d)
  cleanup   모든 워크트리 삭제
  status    워크트리 상태 확인
  aliases   .zshrc에 추가할 alias 명령어 출력
  help      이 도움말 출력

Worktrees:
  a (work-a): Content writing and post updates
  b (work-b): Script development and tooling
  c (work-c): Feature development and testing
  d (work-d): Analytics and read-only analysis

Examples:
  # 1. 워크트리 생성
  bash scripts/setup-worktrees.sh setup

  # 2. Alias 확인
  bash scripts/setup-worktrees.sh aliases

  # 3. ~/.zshrc에 alias 추가 후 적용
  source ~/.zshrc

  # 4. 이제 za, zb, zc, zd, zm 명령어로 빠르게 이동 가능!

EOF
}

# ===========================
# Main
# ===========================
main() {
  case "${1:-help}" in
    setup)
      setup
      ;;
    cleanup)
      cleanup
      ;;
    status)
      status
      ;;
    aliases)
      aliases
      ;;
    help|--help|-h)
      show_help
      ;;
    *)
      log_error "Unknown command: $1"
      echo ""
      show_help
      exit 1
      ;;
  esac
}

main "$@"
