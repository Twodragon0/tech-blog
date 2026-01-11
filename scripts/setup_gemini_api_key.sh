#!/bin/bash
# Gemini API Key 설정 스크립트
# GitHub Secrets와 로컬 환경 변수에 Gemini API Key를 설정합니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 기본값 (보안: 실제 키는 GitHub Secrets에 저장하고, 여기서는 플레이스홀더 사용)
# 실제 사용 시에는 --api-key 옵션으로 실제 키를 제공하거나 GitHub Secrets에서 가져와야 합니다.
DEFAULT_API_KEY="your-gemini-api-key"
DEFAULT_PROJECT_ID="your-project-id"

echo "============================================================"
echo "🔑 Gemini API Key 설정"
echo "============================================================"
echo ""

# 사용법 출력
usage() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --api-key KEY          설정할 Gemini API Key"
    echo "  --project-id ID         설정할 Google Cloud 프로젝트 ID"
    echo "  --github                GitHub Secrets에만 설정"
    echo "  --local                 로컬 환경 변수에만 설정"
    echo "  --both                  GitHub Secrets와 로컬 환경 변수 모두 설정 (기본값)"
    echo "  --default               기본값 사용 (플레이스홀더, 실제 키는 --api-key로 제공 필요)"
    echo "  --help                  이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 --api-key YOUR_KEY --both"
    echo "  $0 --default --github"
    echo "  $0 --api-key YOUR_KEY --local"
    echo ""
}

# GitHub CLI 확인
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        echo -e "${RED}❌ GitHub CLI (gh)가 설치되어 있지 않습니다.${NC}"
        echo ""
        echo "설치 방법:"
        echo "  macOS: brew install gh"
        echo "  Linux: https://cli.github.com/manual/installation"
        echo ""
        echo "설치 후 다음 명령어로 로그인:"
        echo "  gh auth login"
        echo ""
        return 1
    fi
    
    # GitHub CLI 인증 확인
    if ! gh auth status &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI에 로그인되어 있지 않습니다.${NC}"
        echo ""
        echo "다음 명령어로 로그인하세요:"
        echo "  gh auth login"
        echo ""
        return 1
    fi
    
    return 0
}

# GitHub Secrets 설정
set_github_secret() {
    local key_name=$1
    local key_value=$2
    
    if [ -z "$key_value" ]; then
        echo -e "${RED}❌ API Key 값이 비어있습니다.${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📝 GitHub Secrets에 ${key_name} 설정 중...${NC}"
    
    # GitHub CLI로 Secret 설정
    if echo -n "$key_value" | gh secret set "$key_name" --repo "$(gh repo view --json nameWithOwner -q .nameWithOwner)"; then
        echo -e "${GREEN}✅ GitHub Secret 설정 완료: ${key_name}${NC}"
        return 0
    else
        echo -e "${RED}❌ GitHub Secret 설정 실패: ${key_name}${NC}"
        return 1
    fi
}

# 로컬 환경 변수 설정
set_local_env() {
    local key_name=$1
    local key_value=$2
    local shell_rc=""
    
    # Shell 확인
    if [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    else
        shell_rc="$HOME/.profile"
    fi
    
    echo -e "${BLUE}📝 로컬 환경 변수 설정 중...${NC}"
    echo ""
    echo "다음 명령어를 실행하거나 ${shell_rc}에 추가하세요:"
    echo ""
    echo -e "${GREEN}export ${key_name}='${key_value}'${NC}"
    echo ""
    
    # .env 파일 생성/업데이트 (프로젝트 루트)
    ENV_FILE="$PROJECT_ROOT/.env"
    if [ -f "$ENV_FILE" ]; then
        # 기존 값이 있으면 업데이트, 없으면 추가
        if grep -q "^${key_name}=" "$ENV_FILE"; then
            # macOS와 Linux 호환성을 위한 sed 사용
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s|^${key_name}=.*|${key_name}=${key_value}|" "$ENV_FILE"
            else
                sed -i "s|^${key_name}=.*|${key_name}=${key_value}|" "$ENV_FILE"
            fi
            echo -e "${GREEN}✅ .env 파일 업데이트 완료: ${key_name}${NC}"
        else
            echo "${key_name}=${key_value}" >> "$ENV_FILE"
            echo -e "${GREEN}✅ .env 파일에 추가 완료: ${key_name}${NC}"
        fi
    else
        echo "${key_name}=${key_value}" > "$ENV_FILE"
        echo -e "${GREEN}✅ .env 파일 생성 완료: ${key_name}${NC}"
    fi
    
    # .gitignore에 .env 추가 (없는 경우)
    GITIGNORE_FILE="$PROJECT_ROOT/.gitignore"
    if [ -f "$GITIGNORE_FILE" ] && ! grep -q "^\.env$" "$GITIGNORE_FILE"; then
        echo "" >> "$GITIGNORE_FILE"
        echo "# Environment variables" >> "$GITIGNORE_FILE"
        echo ".env" >> "$GITIGNORE_FILE"
        echo -e "${GREEN}✅ .gitignore에 .env 추가됨${NC}"
    fi
    
    echo ""
    echo "현재 세션에서 사용하려면:"
    echo -e "${GREEN}export ${key_name}='${key_value}'${NC}"
    echo ""
}

# 메인 함수
main() {
    local api_key=""
    local project_id=""
    local target="both"  # both, github, local
    local use_default=false
    
    # 인자 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            --api-key)
                api_key="$2"
                shift 2
                ;;
            --project-id)
                project_id="$2"
                shift 2
                ;;
            --github)
                target="github"
                shift
                ;;
            --local)
                target="local"
                shift
                ;;
            --both)
                target="both"
                shift
                ;;
            --default)
                use_default=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}❌ 알 수 없는 옵션: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done
    
    # 기본값 사용
    if [ "$use_default" = true ]; then
        if [ -z "$api_key" ]; then
            api_key="$DEFAULT_API_KEY"
        fi
        if [ -z "$project_id" ]; then
            project_id="$DEFAULT_PROJECT_ID"
        fi
        echo -e "${YELLOW}⚠️  기본값 사용:${NC}"
        echo "  API Key: ${api_key:0:20}..."
        echo "  Project ID: $project_id"
        echo ""
    fi
    
    # API Key 입력 요청
    if [ -z "$api_key" ]; then
        echo -e "${BLUE}📝 Gemini API Key를 입력하세요:${NC}"
        echo -e "${YELLOW}(기본값 사용: ${DEFAULT_API_KEY})${NC}"
        read -p "API Key (Enter로 기본값 사용): " input_key
        api_key="${input_key:-$DEFAULT_API_KEY}"
        echo ""
    fi
    
    # Project ID 입력 요청
    if [ -z "$project_id" ]; then
        echo -e "${BLUE}📝 Google Cloud 프로젝트 ID를 입력하세요:${NC}"
        echo -e "${YELLOW}(기본값 사용: ${DEFAULT_PROJECT_ID})${NC}"
        read -p "Project ID (Enter로 기본값 사용): " input_id
        project_id="${input_id:-$DEFAULT_PROJECT_ID}"
        echo ""
    fi
    
    # 설정 요약
    echo "============================================================"
    echo "📋 설정 요약"
    echo "============================================================"
    echo "API Key: ${api_key:0:20}..."
    echo "Project ID: $project_id"
    echo "대상: $target"
    echo ""
    
    # GitHub Secrets 설정
    if [ "$target" = "github" ] || [ "$target" = "both" ]; then
        if check_gh_cli; then
            set_github_secret "GEMINI_API_KEY" "$api_key"
            if [ -n "$project_id" ]; then
                set_github_secret "GOOGLE_CLOUD_PROJECT" "$project_id"
            fi
        else
            echo -e "${YELLOW}⚠️  GitHub Secrets 설정을 건너뜁니다.${NC}"
        fi
        echo ""
    fi
    
    # 로컬 환경 변수 설정
    if [ "$target" = "local" ] || [ "$target" = "both" ]; then
        set_local_env "GEMINI_API_KEY" "$api_key"
        if [ -n "$project_id" ]; then
            set_local_env "GOOGLE_CLOUD_PROJECT" "$project_id"
        fi
    fi
    
    echo "============================================================"
    echo -e "${GREEN}✅ 설정 완료!${NC}"
    echo "============================================================"
    echo ""
    echo "다음 단계:"
    if [ "$target" = "github" ] || [ "$target" = "both" ]; then
        echo "  1. GitHub Actions에서 Secret 확인:"
        echo "     Settings → Secrets and variables → Actions"
    fi
    if [ "$target" = "local" ] || [ "$target" = "both" ]; then
        echo "  2. 로컬 환경 변수 로드:"
        echo "     source ~/.zshrc  # 또는 ~/.bashrc"
        echo "     또는: export GEMINI_API_KEY='$api_key'"
    fi
    echo "  3. 스크립트 실행:"
    echo "     python3 scripts/generate_enhanced_audio.py"
    echo ""
}

# 스크립트 실행
main "$@"
