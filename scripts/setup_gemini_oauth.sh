#!/bin/bash
# Gemini OAuth 2.0 설정 스크립트
# Google Cloud 서비스 계정을 사용하여 OAuth 2.0 인증을 설정합니다.

set -e

# ============================================
# 사용자 설정 필요
# ============================================
# 아래 값을 실제 프로젝트 ID와 서비스 계정으로 변경하세요
# Google Cloud Console에서 확인 가능합니다.
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT="your-service-account@your-project-id.iam.gserviceaccount.com"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
KEY_FILE="$PROJECT_ROOT/gemini-service-key.json"

echo "============================================================"
echo "🔐 Gemini OAuth 2.0 설정"
echo "============================================================"
echo ""
echo "프로젝트 ID: $PROJECT_ID"
echo "서비스 계정: $SERVICE_ACCOUNT"
echo ""
echo "⚠️  주의: 스크립트 상단의 PROJECT_ID와 SERVICE_ACCOUNT를 실제 값으로 변경하세요!"
echo ""

# gcloud CLI 확인
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI가 설치되어 있지 않습니다."
    echo "   설치: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI 확인 완료"
echo ""

# 프로젝트 설정
echo "📝 Google Cloud 프로젝트 설정 중..."
gcloud config set project "$PROJECT_ID"
echo "✅ 프로젝트 설정 완료: $PROJECT_ID"
echo ""

# 서비스 계정 키 다운로드
echo "🔑 서비스 계정 키 다운로드 중..."
if [ -f "$KEY_FILE" ]; then
    echo "⚠️  키 파일이 이미 존재합니다: $KEY_FILE"
    read -p "덮어쓰시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 취소되었습니다."
        exit 1
    fi
fi

gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SERVICE_ACCOUNT" \
    --project="$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo "✅ 서비스 계정 키 다운로드 완료: $KEY_FILE"
else
    echo "❌ 서비스 계정 키 다운로드 실패"
    exit 1
fi

# .gitignore에 추가
GITIGNORE_FILE="$PROJECT_ROOT/.gitignore"
if [ -f "$GITIGNORE_FILE" ]; then
    if ! grep -q "gemini-service-key.json" "$GITIGNORE_FILE"; then
        echo "" >> "$GITIGNORE_FILE"
        echo "# Gemini OAuth service account key" >> "$GITIGNORE_FILE"
        echo "gemini-service-key.json" >> "$GITIGNORE_FILE"
        echo "✅ .gitignore에 키 파일 추가됨"
    fi
fi

# 환경 변수 설정 안내
echo ""
echo "============================================================"
echo "📝 환경 변수 설정"
echo "============================================================"
echo ""
echo "다음 명령어를 실행하거나 .env 파일에 추가하세요:"
echo ""
echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$KEY_FILE\""
echo "export GOOGLE_CLOUD_PROJECT=\"$PROJECT_ID\""
echo "export USE_GEMINI_OAUTH=\"true\""
echo ""
echo "또는 .env 파일에 추가:"
echo "GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE"
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"
echo "USE_GEMINI_OAUTH=true"
echo ""

# Python 패키지 설치 안내
echo "============================================================"
echo "📦 Python 패키지 설치"
echo "============================================================"
echo ""
echo "OAuth 2.0을 사용하려면 다음 패키지가 필요합니다:"
echo ""
echo "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-generativeai"
echo ""
echo "또는 requirements.txt에 추가:"
echo "google-auth>=2.23.0"
echo "google-auth-oauthlib>=1.1.0"
echo "google-auth-httplib2>=0.1.1"
echo "google-generativeai>=0.3.0"
echo ""

echo "============================================================"
echo "✅ 설정 완료!"
echo "============================================================"
echo ""
echo "다음 단계:"
echo "1. 환경 변수 설정 (위 명령어 실행)"
echo "2. Python 패키지 설치"
echo "3. 스크립트 실행: python3 scripts/generate_enhanced_audio.py"
echo ""
