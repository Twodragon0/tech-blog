# Sentry 워크플로우 문제 해결 가이드

## 🔍 현재 발생한 문제

### 에러 메시지
```
error: Project not found. Ensure that you configured the correct project and organization.
```

### 원인 분석
이 에러는 다음 중 하나일 수 있습니다:
1. **조직 이름 불일치**: `SENTRY_ORG` 값이 실제 Sentry 조직 이름과 다름
2. **프로젝트 이름 불일치**: `SENTRY_PROJECT` 값이 실제 Sentry 프로젝트 이름과 다름
3. **Token 권한 부족**: Token에 해당 프로젝트에 대한 권한이 없음

## ✅ 해결 방법

### 1. Sentry 대시보드에서 정확한 정보 확인

1. **Sentry 대시보드 접속**
   - https://sentry.io 접속
   - 로그인

2. **조직 이름 확인**
   - 상단 왼쪽에 표시된 조직 이름 확인
   - URL에서도 확인 가능: `https://sentry.io/organizations/[조직이름]/`

3. **프로젝트 이름 확인**
   - 프로젝트 선택 후 URL 확인
   - URL 형식: `https://sentry.io/organizations/[조직이름]/projects/[프로젝트이름]/`

### 2. 워크플로우 파일 수정

`.github/workflows/sentry-release.yml` 파일에서 다음 값들을 확인하고 수정:

```yaml
env:
  SENTRY_ORG: [실제 조직 이름]      # 예: twodragon
  SENTRY_PROJECT: [실제 프로젝트 이름]  # 예: tech-blog
```

### 3. Token 권한 확인

1. **Sentry 대시보드** → **Settings** → **Account** → **Auth Tokens**
2. Token 클릭하여 권한 확인
3. 다음 권한이 있는지 확인:
   - ✅ `project:releases` (필수)
   - ✅ `project:read` (권장 - 프로젝트 정보 조회용)

### 4. 프로젝트 접근 권한 확인

1. **Sentry 대시보드** → **Settings** → **Projects** → **tech-blog**
2. **Team Access** 확인
3. Token을 발급한 계정이 프로젝트에 접근 권한이 있는지 확인

## 🧪 테스트 방법

### 로컬에서 테스트 (선택사항)

```bash
# Sentry CLI 설치 (로컬 테스트용)
npm install -g @sentry/cli

# 프로젝트 목록 확인
sentry-cli projects list --org [조직이름]

# Release 생성 테스트
sentry-cli releases new [버전] --org [조직이름] --project [프로젝트이름]
```

### GitHub Actions에서 테스트

1. 워크플로우 파일 수정 후 커밋
2. 워크플로우 수동 실행
3. 로그에서 디버그 정보 확인

## 📋 체크리스트

- [ ] Sentry 대시보드에서 조직 이름 확인
- [ ] Sentry 대시보드에서 프로젝트 이름 확인
- [ ] 워크플로우 파일의 `SENTRY_ORG` 값 확인
- [ ] 워크플로우 파일의 `SENTRY_PROJECT` 값 확인
- [ ] Token 권한 확인 (`project:releases`, `project:read`)
- [ ] 프로젝트 접근 권한 확인
- [ ] 워크플로우 재실행 및 로그 확인

## 🔗 참고 자료

- [Sentry CLI 문서](https://docs.sentry.io/product/cli/)
- [Sentry Auth Tokens](https://docs.sentry.io/api/auth/)
- [GitHub Actions Sentry 통합](https://github.com/getsentry/action-release)
