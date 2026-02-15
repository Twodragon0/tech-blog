#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 인증 스크립트
Access Token을 얻기 위한 OAuth 플로우를 실행합니다.
"""

import os
import sys
import json
import requests
from urllib.parse import urlencode, parse_qs, urlparse
from pathlib import Path

# 프로젝트 루트 디렉토리
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


# .env 파일에서 환경 변수 로드
def load_env_file():
    """Load environment variables from .env file"""
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def get_authorization_url():
    """Generate LinkedIn OAuth authorization URL"""
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    redirect_uri = os.environ.get(
        "LINKEDIN_REDIRECT_URI", "http://localhost:8000/auth/linkedin/callback"
    )

    if not client_id:
        print("❌ ERROR: LINKEDIN_CLIENT_ID가 설정되지 않았습니다.")
        print("   scripts/setup_linkedin_keys.sh를 실행하여 설정하세요.")
        sys.exit(1)

    # LinkedIn OAuth 2.0 스코프 (최신 버전)
    # openid: OpenID Connect 인증
    # profile: 기본 프로필 정보
    # email: 이메일 주소
    # w_member_social: 게시물 작성 권한
    scopes = ["openid", "profile", "email", "w_member_social"]

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": "random_state_string",  # CSRF 방지
        "scope": " ".join(scopes),
    }

    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    return auth_url


def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token"""
    client_id = os.environ.get("LINKEDIN_CLIENT_ID")
    client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
    redirect_uri = os.environ.get(
        "LINKEDIN_REDIRECT_URI", "http://localhost:8000/auth/linkedin/callback"
    )

    if not all([client_id, client_secret]):
        print("❌ ERROR: LinkedIn 인증 정보가 설정되지 않았습니다.")
        sys.exit(1)

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"

    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(token_url, data=data, timeout=15)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ ERROR: 토큰 교환 실패 - {response.status_code}")
        print(f"   응답: {response.text}")
        sys.exit(1)


def get_user_profile(access_token):
    """Get LinkedIn user profile information using OpenID Connect"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # OpenID Connect를 사용한 프로필 정보 가져오기
    try:
        # userinfo 엔드포인트 사용
        profile_url = "https://api.linkedin.com/v2/userinfo"
        response = requests.get(profile_url, headers=headers, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            # Fallback: 기존 v2/me 엔드포인트 시도
            profile_url = "https://api.linkedin.com/v2/me"
            response = requests.get(profile_url, headers=headers, timeout=15)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  프로필 정보를 가져올 수 없습니다: {response.status_code}")
                print(f"   응답: {response.text}")
                return None
    except Exception as e:
        print(f"⚠️  프로필 정보 조회 중 오류: {e}")
        return None


def save_tokens(access_token, refresh_token=None, person_id=None):
    """Save tokens to .env file"""
    env_file = PROJECT_ROOT / ".env"

    # .env 파일 읽기
    env_lines = []
    if env_file.exists():
        with open(env_file, "r") as f:
            env_lines = f.readlines()

    # 기존 토큰 업데이트 또는 추가
    updated = False
    new_lines = []

    for line in env_lines:
        if line.startswith("LINKEDIN_ACCESS_TOKEN="):
            new_lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}\n")
            updated = True
        elif line.startswith("LINKEDIN_REFRESH_TOKEN="):
            if refresh_token:
                new_lines.append(f"LINKEDIN_REFRESH_TOKEN={refresh_token}\n")
            updated = True
        elif line.startswith("LINKEDIN_PERSON_ID="):
            if person_id:
                new_lines.append(f"LINKEDIN_PERSON_ID={person_id}\n")
            updated = True
        else:
            new_lines.append(line)

    # 새로 추가해야 하는 경우
    if not updated:
        new_lines.append(f"\n# LinkedIn OAuth Tokens (자동 생성)\n")
        new_lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}\n")
        if refresh_token:
            new_lines.append(f"LINKEDIN_REFRESH_TOKEN={refresh_token}\n")
        if person_id:
            new_lines.append(f"LINKEDIN_PERSON_ID={person_id}\n")

    # .env 파일 쓰기
    with open(env_file, "w") as f:
        f.writelines(new_lines)

    print(f"✓ 토큰이 {env_file}에 저장되었습니다.")


def main():
    load_env_file()

    print("=" * 50)
    print("LinkedIn OAuth 2.0 인증")
    print("=" * 50)
    print()

    # Step 1: Authorization URL 생성
    auth_url = get_authorization_url()

    print("1단계: 다음 URL을 브라우저에서 열어주세요:")
    print()
    print(auth_url)
    print()
    print("2단계: LinkedIn에 로그인하고 권한을 승인하세요.")
    print("3단계: 리다이렉트된 URL에서 'code' 파라미터를 복사하세요.")
    print()
    print("예시:")
    print("  http://localhost:8000/auth/linkedin/callback?code=AQT...&state=...")
    print("  ↑ 이 부분을 복사: AQT...")
    print()

    # Step 2: Authorization code 입력
    authorization_code = input("Authorization code를 입력하세요: ").strip()

    if not authorization_code:
        print("❌ ERROR: Authorization code가 필요합니다.")
        sys.exit(1)

    # Step 3: Access Token 교환
    print()
    print("Access Token을 요청하는 중...")
    token_data = exchange_code_for_token(authorization_code)

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in", 0)

    if not access_token:
        print("❌ ERROR: Access Token을 받을 수 없었습니다.")
        sys.exit(1)

    print(f"✓ Access Token을 받았습니다. (만료 시간: {expires_in}초)")

    # Step 4: 사용자 프로필 정보 가져오기
    print()
    print("사용자 프로필 정보를 가져오는 중...")
    profile = get_user_profile(access_token)

    person_id = None
    if profile:
        # OpenID Connect 응답에서는 'sub' 필드가 Person ID
        # 기존 API 응답에서는 'id' 필드가 Person ID
        person_id = profile.get("sub") or profile.get("id")

        # 이름 정보 추출 (OpenID Connect vs 기존 API)
        first_name = profile.get("given_name") or profile.get("localizedFirstName", "")
        last_name = profile.get("family_name") or profile.get("localizedLastName", "")
        full_name = f"{first_name} {last_name}".strip()

        print(f"✓ 프로필 정보를 가져왔습니다.")
        if full_name:
            print(f"  이름: {full_name}")
        if profile.get("email"):
            print(f"  이메일: {profile.get('email')}")
        print(f"  Person ID: {person_id}")

    # Step 5: 토큰 저장
    print()
    save_tokens(access_token, refresh_token, person_id)

    print()
    print("=" * 50)
    print("✅ 인증 완료!")
    print("=" * 50)
    print()
    print("이제 share_sns.py 스크립트를 사용하여 LinkedIn에 포스팅할 수 있습니다.")
    print()
    print("사용 예시:")
    print("  python scripts/share_sns.py _posts/2026-01-08-example.md")
    print()


if __name__ == "__main__":
    main()
