# LinkedIn API 연동 가이드

## 📋 개요

이 가이드는 **OAuth 2.0 방식**으로 LinkedIn API를 사용하여 블로그 포스트를 자동으로 공유하는 방법을 설명합니다.

> **⚠️ 중요**: LinkedIn API는 OAuth 2.0 방식만 지원합니다. API key는 사용하지 않으며, Client ID/Secret과 Access Token만 사용합니다.

## 🔐 OAuth 2.0 인증 설정

> **⚠️ 중요**: LinkedIn API는 OAuth 2.0 방식만 지원합니다. API key는 사용하지 않습니다.

### 1. LinkedIn Developer Portal에서 앱 생성

1. [LinkedIn Developer Portal](https://www.linkedin.com/developers/) 접속
2. 앱 생성 (자세한 내용은 `LINKEDIN_APP_CREATION_GUIDE.md` 참조)
3. 다음 OAuth 2.0 인증 정보 확인:
   - **Client ID**: OAuth 2.0 클라이언트 식별자
   - **Client Secret**: OAuth 2.0 클라이언트 비밀키
   - **Redirect URI**: OAuth 2.0 콜백 URL

### 2. 환경 변수 설정

#### 방법 1: 자동 설정 스크립트 사용 (권장)

```bash
./scripts/setup_linkedin_keys.sh
```

스크립트 실행 시 다음 정보를 입력하세요:
- LinkedIn Client ID
- LinkedIn Client Secret
- Redirect URI (기본값: `http://localhost:8000/auth/linkedin/callback`)

#### 방법 2: 수동 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8000/auth/linkedin/callback
```

### 3. LinkedIn Developer Portal에서 Redirect URI 등록

1. LinkedIn Developer Portal → 앱 선택 → "Auth" 탭
2. "Authorized redirect URLs for your app" 섹션에 다음 URL 추가:
   ```
   http://localhost:8000/auth/linkedin/callback
   ```
3. "Update" 클릭하여 저장

## 🔑 OAuth 인증 (Access Token 획득)

### 1. OAuth 인증 스크립트 실행

```bash
python scripts/linkedin_oauth.py
```

### 2. 인증 프로세스

1. **Authorization URL 생성**
   - 스크립트가 LinkedIn 인증 URL을 생성합니다
   - 이 URL을 브라우저에서 엽니다

2. **LinkedIn 로그인 및 권한 승인**
   - LinkedIn 계정으로 로그인
   - 앱이 요청하는 권한을 검토하고 승인
   - 필요한 권한 (OAuth 2.0 OpenID Connect):
     - `openid`: OpenID Connect 인증
     - `profile`: 기본 프로필 정보
     - `email`: 이메일 주소
     - `w_member_social`: 게시물 작성 권한

3. **Authorization Code 복사**
   - 리다이렉트된 URL에서 `code` 파라미터 값을 복사
   - 예시: `http://localhost:8000/auth/linkedin/callback?code=AQT...&state=...`
   - `AQT...` 부분을 복사

4. **Access Token 획득**
   - 스크립트에 Authorization Code 입력
   - Access Token이 자동으로 `.env` 파일에 저장됩니다

### 3. 인증 완료 확인

`.env` 파일에 다음 항목이 추가되었는지 확인:

```bash
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_PERSON_ID=your_person_id_here
```

## 📝 블로그 포스트 공유

### 기본 사용법

```bash
python scripts/share_sns.py _posts/2026-01-08-example.md
```

### 포스트 파일 경로 지정

```bash
# 전체 경로
python scripts/share_sns.py /path/to/_posts/2026-01-08-example.md

# 상대 경로
python scripts/share_sns.py _posts/2026-01-08-example.md

# 파일명만 (자동 검색)
python scripts/share_sns.py 2026-01-08-example.md
```

### 공유 메시지 형식

LinkedIn에 공유되는 메시지는 다음과 같은 형식입니다:

```
🚀 새로운 기술 블로그 포스트를 공유합니다!

📝 [포스트 제목]

[포스트 요약 (최대 300자)]

이 글에서는 실무에서 바로 적용할 수 있는 내용을 다룹니다.

👉 전체 글 읽기: [포스트 URL]

[태그 해시태그]

#DevSecOps #CloudSecurity #AWS #Kubernetes #TechBlog
```

## 🔒 보안 모범 사례

### 1. OAuth 2.0 인증 정보 관리

- ✅ `.env` 파일은 절대 Git에 커밋하지 마세요
- ✅ `.gitignore`에 `.env` 파일이 포함되어 있는지 확인
- ✅ Client Secret은 안전하게 보관 (OAuth 2.0 클라이언트 비밀키)
- ✅ Access Token은 정기적으로 갱신 (일반적으로 60일 유효)
- ✅ **API key는 사용하지 않음**: OAuth 2.0 방식만 사용

### 2. Access Token 갱신

Access Token은 만료될 수 있습니다. 만료 시:

1. `linkedin_oauth.py` 스크립트를 다시 실행
2. 새로운 Authorization Code로 Access Token 갱신
3. 또는 Refresh Token을 사용하여 자동 갱신 (구현 예정)

### 3. 권한 최소화

- 필요한 최소한의 권한만 요청
- `w_member_social` 권한은 포스팅이 필요한 경우에만 사용

## 🐛 문제 해결

### 문제 1: "Client ID가 설정되지 않았습니다"

**해결 방법:**
```bash
# 환경 변수 확인
echo $LINKEDIN_CLIENT_ID

# .env 파일 확인
cat .env | grep LINKEDIN_CLIENT_ID

# 설정 스크립트 재실행
./scripts/setup_linkedin_keys.sh
```

### 문제 2: "Invalid redirect_uri"

**원인:** LinkedIn Developer Portal에 등록된 Redirect URI와 일치하지 않음

**해결 방법:**
1. LinkedIn Developer Portal → 앱 → Auth 탭 확인
2. "Authorized redirect URLs"에 정확한 URL이 등록되어 있는지 확인
3. `.env` 파일의 `LINKEDIN_REDIRECT_URI` 값과 일치하는지 확인

### 문제 3: "Access Token이 만료되었습니다"

**해결 방법:**
```bash
# OAuth 인증 스크립트 재실행
python scripts/linkedin_oauth.py
```

### 문제 4: "403 Forbidden" 또는 "401 Unauthorized"

**원인:**
- Access Token이 만료됨 (OAuth 2.0 토큰 만료)
- 필요한 OAuth 스코프 권한이 없음
- API Rate Limit 초과

**해결 방법:**
1. OAuth 2.0 인증 재실행하여 Access Token 갱신
2. LinkedIn Developer Portal에서 앱 권한(OAuth 스코프) 확인
3. API 호출 빈도 확인 (Rate Limit: 분당 100회)
4. **API key는 사용하지 않음**: OAuth 2.0 Access Token만 사용

## 📚 참고 자료

- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
- [LinkedIn API 문서](https://docs.microsoft.com/en-us/linkedin/)
- [OAuth 2.0 가이드](https://oauth.net/2/)
- [LinkedIn 앱 생성 가이드](../LINKEDIN_APP_CREATION_GUIDE.md)

## ✅ 체크리스트

LinkedIn 연동을 완료하기 위한 체크리스트:

- [ ] LinkedIn Developer Portal에서 앱 생성 완료
- [ ] 회사 페이지 검증 완료 (Enterprise 개발자)
- [ ] Client ID와 Client Secret 확인
- [ ] Redirect URI를 LinkedIn Developer Portal에 등록
- [ ] `.env` 파일에 인증 정보 설정
- [ ] OAuth 인증 완료 (Access Token 획득)
- [ ] 테스트 포스트 공유 성공
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있는지 확인

---

**Last Updated**: 2026-01-08  
**Maintainer**: DevSecOps Team
