#!/usr/bin/env python3
"""
Gemini OAuth 2.0 인증 설정 스크립트

Google Cloud 서비스 계정을 사용하여 OAuth 2.0 인증을 설정합니다.
"""

import json
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def check_gcloud_installed() -> bool:
    """gcloud CLI가 설치되어 있는지 확인"""
    try:
        import subprocess

        result = subprocess.run(
            ["gcloud", "--version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def setup_service_account_instructions():
    """서비스 계정 설정 가이드 출력"""
    print("=" * 80)
    print("🔐 Gemini OAuth 2.0 서비스 계정 설정 가이드")
    print("=" * 80)
    print()
    print("1. Google Cloud Console에서 프로젝트 생성")
    print("   https://console.cloud.google.com/")
    print()
    print("2. 서비스 계정 생성")
    print("   - IAM & Admin > Service Accounts > Create Service Account")
    print("   - 이름: gemini-service")
    print("   - 역할: Vertex AI User")
    print()
    print("3. 서비스 계정 키 생성")
    print("   - 생성한 서비스 계정 선택 > Keys 탭 > Add Key > Create new key")
    print("   - JSON 형식 선택")
    print()
    print("4. 환경 변수 설정")
    print(
        '   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"'
    )
    print('   export GOOGLE_CLOUD_PROJECT="your-project-id"')
    print()
    print("5. Gemini API 활성화")
    print("   gcloud services enable generativelanguage.googleapis.com")
    print()
    print("=" * 80)


def setup_oauth_with_gcloud():
    """gcloud CLI를 사용하여 OAuth 2.0 설정"""
    if not check_gcloud_installed():
        print("❌ gcloud CLI가 설치되어 있지 않습니다.")
        print("   설치: https://cloud.google.com/sdk/docs/install")
        return False

    print("🔐 gcloud CLI를 사용하여 OAuth 2.0 설정 중...")
    print()

    # 프로젝트 ID 입력
    project_id = input("Google Cloud 프로젝트 ID를 입력하세요: ").strip()
    if not project_id:
        print("❌ 프로젝트 ID가 필요합니다.")
        return False

    # 서비스 계정 이름
    service_account_name = "gemini-service"

    print(f"\n📝 서비스 계정 생성 중: {service_account_name}")
    print("   (이미 존재하는 경우 무시됩니다)")

    import subprocess

    # 서비스 계정 생성
    try:
        result = subprocess.run(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "create",
                service_account_name,
                "--display-name=Gemini Service Account",
                "--project",
                project_id,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"⚠️  서비스 계정 생성 중 오류: {result.stderr}")
    except Exception as e:
        print(f"⚠️  서비스 계정 생성 중 오류: {e}")

    # 역할 부여
    print("\n🔑 역할 부여 중: roles/aiplatform.user")
    try:
        result = subprocess.run(
            [
                "gcloud",
                "projects",
                "add-iam-policy-binding",
                project_id,
                "--member",
                f"serviceAccount:{service_account_name}@{project_id}.iam.gserviceaccount.com",
                "--role",
                "roles/aiplatform.user",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ 역할 부여 완료")
        else:
            print(f"⚠️  역할 부여 중 오류: {result.stderr}")
    except Exception as e:
        print(f"⚠️  역할 부여 중 오류: {e}")

    # 서비스 계정 키 생성
    key_file = PROJECT_ROOT / f"{service_account_name}-key.json"
    print(f"\n🔑 서비스 계정 키 생성 중: {key_file}")

    try:
        result = subprocess.run(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "keys",
                "create",
                str(key_file),
                "--iam-account",
                f"{service_account_name}@{project_id}.iam.gserviceaccount.com",
                "--project",
                project_id,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"✅ 서비스 계정 키 생성 완료: {key_file}")

            # 환경 변수 설정 안내
            print("\n" + "=" * 80)
            print("📝 환경 변수 설정")
            print("=" * 80)
            print()
            print("다음 명령어를 실행하세요:")
            print()
            print(f'export GOOGLE_APPLICATION_CREDENTIALS="{key_file.absolute()}"')
            print(f'export GOOGLE_CLOUD_PROJECT="{project_id}"')
            print('export USE_GEMINI_OAUTH="true"')
            print()
            print("또는 .env 파일에 추가:")
            print(f"GOOGLE_APPLICATION_CREDENTIALS={key_file.absolute()}")
            print(f"GOOGLE_CLOUD_PROJECT={project_id}")
            print("USE_GEMINI_OAUTH=true")
            print()

            # .gitignore에 추가
            gitignore_file = PROJECT_ROOT / ".gitignore"
            if gitignore_file.exists():
                gitignore_content = gitignore_file.read_text()
                if "*-key.json" not in gitignore_content:
                    gitignore_file.write_text(
                        gitignore_content
                        + "\n# Gemini OAuth service account keys\n*-key.json\n"
                    )
                    print("✅ .gitignore에 키 파일 패턴 추가됨")

            return True
        else:
            print(f"❌ 서비스 계정 키 생성 실패: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 서비스 계정 키 생성 중 오류: {e}")
        return False


def verify_oauth_setup() -> bool:
    """OAuth 2.0 설정 확인"""
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다.")
        return False

    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.")
        return False

    credentials_file = Path(credentials_path)
    if not credentials_file.exists():
        print(f"❌ 서비스 계정 키 파일을 찾을 수 없습니다: {credentials_path}")
        return False

    # JSON 파일 유효성 확인
    try:
        with open(credentials_file, "r") as f:
            creds = json.load(f)
            if "type" not in creds or creds["type"] != "service_account":
                print("❌ 유효하지 않은 서비스 계정 키 파일입니다.")
                return False
    except json.JSONDecodeError:
        print("❌ 서비스 계정 키 파일이 유효한 JSON이 아닙니다.")
        return False

    print("✅ OAuth 2.0 설정 확인 완료")
    print(f"   프로젝트 ID: {project_id}")
    print(f"   키 파일: {credentials_path}")
    return True


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Gemini OAuth 2.0 인증 설정")
    parser.add_argument(
        "--setup", action="store_true", help="gcloud CLI를 사용하여 자동 설정"
    )
    parser.add_argument("--verify", action="store_true", help="현재 설정 확인")
    parser.add_argument(
        "--instructions", action="store_true", help="수동 설정 가이드 출력"
    )

    args = parser.parse_args()

    if args.setup:
        if setup_oauth_with_gcloud():
            print("\n✅ OAuth 2.0 설정 완료!")
        else:
            print("\n❌ OAuth 2.0 설정 실패")
            sys.exit(1)
    elif args.verify:
        if verify_oauth_setup():
            sys.exit(0)
        else:
            sys.exit(1)
    elif args.instructions:
        setup_service_account_instructions()
    else:
        print("사용법:")
        print("  python3 scripts/gemini_oauth_setup.py --setup      # 자동 설정")
        print("  python3 scripts/gemini_oauth_setup.py --verify     # 설정 확인")
        print(
            "  python3 scripts/gemini_oauth_setup.py --instructions # 수동 설정 가이드"
        )


if __name__ == "__main__":
    main()
