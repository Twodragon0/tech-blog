# GitHub Secrets 관리 가이드

이 문서는 GitHub Actions와 Vercel에서 사용하는 Secrets를 안전하게 관리하는 방법을 제공합니다.

## 필수 Secrets

### Sentry 관련
- `SENTRY_AUTH_TOKEN`: Sentry 인증 토큰
  - 생성 방법: Sentry 대시보드 → Settings → Account → Auth Tokens
  - 권한: `project:releases` (최소 권한)
  - 사용처: `.github/workflows/sentry-release.yml`, `.github/workflows/vercel-deploy.yml`

### Vercel 관련
- Vercel 대시보드에서 직접 관리 (GitHub Integration 사용 시 자동 동기화)
  - 환경 변수는 Vercel 대시보드에서 설정

### SNS 공유 관련
- `TWITTER_API_KEY`: Twitter/X API Key
- `TWITTER_API_SECRET`: Twitter/X API Secret
- `TWITTER_ACCESS_TOKEN`: Twitter/X Access Token
- `TWITTER_ACCESS_SECRET`: Twitter/X Access Secret
- `FACEBOOK_PAGE_ID`: Facebook Page ID
- `FACEBOOK_ACCESS_TOKEN`: Facebook Access Token
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn Access Token
- `LINKEDIN_PERSON_ID`: LinkedIn Person ID

## Secrets 설정 방법

### GitHub Secrets 설정
1. GitHub 저장소 접속
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** 클릭
4. Name과 Value 입력 후 저장

### Vercel 환경 변수 설정
1. Vercel 대시보드 접속
2. 프로젝트 선택 → **Settings** → **Environment Variables**
3. 환경별 변수 추가:
   - **Production**: 프로덕션 전용
   - **Preview**: 프리뷰 배포용
   - **Development**: 로컬 개발용

## 보안 모범 사례

### 1. 최소 권한 원칙
- 각 Secret은 필요한 최소 권한만 부여
- Sentry Auth Token: `project:releases` 권한만
- GitHub Actions: 필요한 권한만 부여

### 2. 환경별 분리
- 프로덕션과 개발 환경의 Secrets 분리
- 테스트용 토큰과 프로덕션 토큰 분리

### 3. 정기적 로테이션
- 90일마다 Secrets 로테이션 권장
- 유출 의심 시 즉시 재생성

### 4. 접근 제어
- Secrets 접근 권한을 최소한의 인원에게만 부여
- 감사 로그 정기 확인

## Secrets 검증

### GitHub Actions에서 Secrets 확인
```yaml
- name: Verify Secrets
  run: |
    if [ -z "${{ secrets.SENTRY_AUTH_TOKEN }}" ]; then
      echo "❌ SENTRY_AUTH_TOKEN is not set"
      exit 1
    fi
    echo "✅ Secrets verified"
```

### Vercel 환경 변수 확인
```bash
# Vercel CLI 사용
vercel env ls
```

## 문제 해결

### Secret이 설정되지 않은 경우
1. GitHub Secrets 확인: Settings → Secrets and variables → Actions
2. 워크플로우에서 Secret 참조 확인
3. Secret 이름 오타 확인

### 권한 오류
1. Sentry Auth Token 권한 확인
2. GitHub Actions 권한 설정 확인
3. Vercel 프로젝트 권한 확인

## 참고 자료

- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Sentry Auth Tokens](https://docs.sentry.io/api/auth/)
