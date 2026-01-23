# Sentry Token 설정 가이드

이 문서는 Sentry Personal Token을 GitHub Secrets에 추가하는 방법을 안내합니다.

## ✅ 발급받은 Token 정보

- **Token 이름**: `sentry-release`
- **Token 값**: `sntryu_***` (GitHub Secrets에 저장됨)
- **권한**: `project:releases` ✅ (최소 권한 - 보안 강화)

> ⚠️ **보안 주의**: 실제 Token 값은 GitHub Secrets에 저장되어 있으며, 이 문서에는 포함되지 않습니다.

## 📋 GitHub Secrets 추가 방법

### 1. GitHub 저장소 접속
1. GitHub 저장소 페이지로 이동
2. **Settings** 탭 클릭

### 2. Secrets 메뉴 접근
1. 왼쪽 사이드바에서 **Secrets and variables** 클릭
2. **Actions** 선택

### 3. 새 Secret 추가
1. **New repository secret** 버튼 클릭
2. 다음 정보 입력:
   - **Name**: `SENTRY_AUTH_TOKEN`
   - **Secret**: `[발급받은 Token 값 입력]` (예: `sntryu_...`)
3. **Add secret** 버튼 클릭
   
   > 💡 **참고**: Token 값은 Sentry 대시보드에서 발급받은 값을 입력하세요.

### 4. 확인
- Secret 목록에 `SENTRY_AUTH_TOKEN`이 표시되는지 확인
- ✅ 표시되면 설정 완료!

## 🔍 사용되는 워크플로우

이 Token은 다음 워크플로우에서 사용됩니다:

1. **`.github/workflows/sentry-release.yml`**
   - GitHub Actions에서 Sentry Release 생성
   - 프로덕션 배포 시 자동 실행

2. **`.github/workflows/vercel-deploy.yml`**
   - Vercel 배포 시 Sentry Release 생성
   - 수동 실행 또는 Vercel 통합 시 실행

## 🧪 테스트 방법

### 방법 1: 수동 워크플로우 실행
1. GitHub 저장소 → **Actions** 탭
2. **Sentry Release** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. 실행 결과 확인

### 방법 2: 자동 실행 확인
1. `main` 브랜치에 푸시
2. **Actions** 탭에서 워크플로우 실행 확인
3. Sentry 대시보드에서 Release 생성 확인

## 🔒 보안 주의사항

### ✅ 권장 사항
- ✅ Token은 절대 코드에 커밋하지 않음
- ✅ GitHub Secrets에만 저장
- ✅ 최소 권한 원칙 준수 (`project:releases`만)
- ✅ 정기적 로테이션 (90일마다 권장)

### ❌ 주의사항
- ❌ Token을 공개 저장소에 노출하지 않음
- ❌ 로그에 Token이 출력되지 않도록 주의
- ❌ 불필요한 권한 부여 금지

## 📊 Sentry 대시보드 확인

### Release 확인 방법
1. [Sentry 대시보드](https://sentry.io/organizations/twodragon/projects/tech-blog/) 접속
2. **Releases** 메뉴 선택
3. 생성된 Release 확인:
   - Release 버전: `tech-blog@<commit-sha>`
   - 환경: `production`
   - 커밋 정보 자동 연결 확인

## 🐛 문제 해결

### Token이 작동하지 않는 경우
1. **Token 권한 확인**
   - Sentry 대시보드 → Settings → Auth Tokens
   - `project:releases` 권한 확인

2. **Secret 이름 확인**
   - GitHub Secrets에서 `SENTRY_AUTH_TOKEN` 정확히 확인
   - 대소문자 구분 주의

3. **워크플로우 로그 확인**
   - GitHub Actions → 워크플로우 실행 → 로그 확인
   - 에러 메시지 확인

### 권한 오류 발생 시
- Token에 `project:releases` 권한이 있는지 확인
- Sentry 프로젝트 설정에서 권한 확인

## 📝 다음 단계

1. ✅ GitHub Secrets에 Token 추가 완료
2. ⏳ 워크플로우 테스트 실행
3. ⏳ Sentry 대시보드에서 Release 확인
4. ⏳ 자동 배포 시 Release 생성 확인

## 🔗 관련 문서

- [SENTRY_VERCEL_GITHUB_INTEGRATION.md](../SENTRY_VERCEL_GITHUB_INTEGRATION.md)
- [SECRETS_MANAGEMENT.md](./SECRETS_MANAGEMENT.md)
- [SENTRY_GITHUB_FREE_TIER_OPTIMIZATION.md](../SENTRY_GITHUB_FREE_TIER_OPTIMIZATION.md)
