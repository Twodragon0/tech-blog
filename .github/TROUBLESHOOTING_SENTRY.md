# Sentry 워크플로우 문제 해결 가이드

## 🔍 일반적인 문제들

### 1. Release 생성 실패 (Command failed)

**에러 메시지 예시:**
```
Error: Command failed: /action-release/node_modules/@sentry/cli-linux-x64/bin/sentry-cli ... releases new [SHA] -p tech-blog
```

**원인 분석:**
이 에러는 다음 중 하나일 수 있습니다:
1. **Release 이미 존재**: 동일한 커밋 SHA로 이미 Release가 생성됨 (가장 흔한 원인)
2. **Token 권한 부족**: Token에 `project:releases` 권한이 없음
3. **조직/프로젝트 이름 불일치**: `SENTRY_ORG` 또는 `SENTRY_PROJECT` 값이 실제와 다름
4. **Rate Limiting**: Free 티어에서 API 호출 제한 초과
5. **네트워크/API 이슈**: Sentry API 일시적 문제

**해결 방법:**
워크플로우가 자동으로 다음을 수행합니다:
- ✅ Release 생성 전 존재 여부 확인 (중복 방지)
- ✅ API 연결 및 인증 사전 검증
- ✅ 실패 시 최종 상태 재확인 (다른 프로세스에 의해 생성되었을 수 있음)
- ✅ 상세한 에러 메시지 및 해결 방법 제시

### 2. Project not found

**에러 메시지:**
```
error: Project not found. Ensure that you configured the correct project and organization.
```

**원인 분석:**
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

## 🆕 워크플로우 개선 사항 (2026-01-11)

### 추가된 기능
1. **사전 검증 단계**
   - Token 존재 여부 확인
   - Sentry API 연결 테스트
   - 프로젝트 접근 권한 확인

2. **Release 중복 방지**
   - Release 생성 전 존재 여부 확인
   - 이미 존재하는 경우 스킵하여 불필요한 API 호출 방지

3. **향상된 에러 처리**
   - `continue-on-error: true`로 일시적 실패 허용
   - 실패 후 최종 상태 재확인
   - 상세한 에러 메시지 및 해결 방법 제시

4. **최종 상태 확인**
   - 모든 단계 완료 후 Release 존재 여부 최종 확인
   - 성공/실패 여부와 관계없이 상태 출력

### 워크플로우 실행 흐름
```
1. Checkout repository
2. Verify Sentry Configuration (API 연결 테스트)
3. Check if Release Exists (중복 확인)
4. Create Sentry Release (존재하지 않는 경우만)
5. Handle Release Creation Result (실패 시 재확인)
6. Output Release Info (최종 상태 출력)
```

## 🧪 테스트 방법

### GitHub Actions에서 테스트

1. **워크플로우 수동 실행**
   - GitHub Actions → Sentry Release → Run workflow
   - `workflow_dispatch` 트리거 사용

2. **로그 확인 포인트**
   - ✅ "Successfully connected to Sentry API" 메시지 확인
   - ✅ "Release already exists" 또는 "Release created successfully" 확인
   - ❌ 에러 발생 시 상세 메시지 확인

3. **테스트 워크플로우 사용**
   - `test-sentry-release.yml` 워크플로우 실행
   - 실제 Release 생성 없이 설정만 검증

### 로컬에서 테스트 (선택사항)

```bash
# Sentry CLI 설치 (로컬 테스트용)
npm install -g @sentry/cli

# 환경 변수 설정
export SENTRY_AUTH_TOKEN="your-token"
export SENTRY_ORG="twodragon"
export SENTRY_PROJECT="tech-blog"

# 프로젝트 목록 확인
sentry-cli projects list --org $SENTRY_ORG

# Release 생성 테스트
sentry-cli releases new [버전] --org $SENTRY_ORG --project $SENTRY_PROJECT

# Release 존재 여부 확인
sentry-cli releases info [버전] --org $SENTRY_ORG --project $SENTRY_PROJECT
```

## 📋 문제 해결 체크리스트

### 기본 설정 확인
- [ ] Sentry 대시보드에서 조직 이름 확인
- [ ] Sentry 대시보드에서 프로젝트 이름 확인
- [ ] 워크플로우 파일의 `SENTRY_ORG` 값 확인
- [ ] 워크플로우 파일의 `SENTRY_PROJECT` 값 확인
- [ ] GitHub Secrets에 `SENTRY_AUTH_TOKEN` 설정 확인

### Token 권한 확인
- [ ] Token 권한 확인 (`project:releases` 필수)
- [ ] Token 권한 확인 (`project:read` 권장)
- [ ] 프로젝트 접근 권한 확인

### 워크플로우 실행 확인
- [ ] 워크플로우 재실행 및 로그 확인
- [ ] "Verify Sentry Configuration" 단계 성공 확인
- [ ] "Check if Release Exists" 단계 결과 확인
- [ ] 최종 "Output Release Info" 단계에서 Release 상태 확인

### 에러 발생 시
- [ ] 에러 로그의 HTTP 상태 코드 확인
- [ ] 에러 메시지의 상세 내용 확인
- [ ] Sentry 대시보드에서 Release 수동 확인
- [ ] Rate limiting 여부 확인 (Free 티어)

## 🔍 디버깅 팁

### 로그에서 확인할 사항

1. **Verify Sentry Configuration 단계**
   ```
   ✅ Successfully connected to Sentry API
   ```
   - 이 메시지가 보이면 인증 및 프로젝트 접근은 정상

2. **Check if Release Exists 단계**
   ```
   ℹ️  Release [SHA] already exists
   또는
   ✅ Release [SHA] does not exist, will create new
   ```
   - 이미 존재하면 Create 단계가 스킵됨

3. **Create Sentry Release 단계**
   - 실패해도 `continue-on-error: true`로 워크플로우는 계속 진행
   - 다음 단계에서 최종 상태 재확인

4. **Handle Release Creation Result 단계**
   - 실패한 경우에만 실행
   - Release가 실제로 존재하는지 재확인
   - 존재하면 성공으로 처리

### 일반적인 해결 방법

#### 문제: "Authentication failed (HTTP 401/403)"
**해결:**
1. GitHub Secrets의 `SENTRY_AUTH_TOKEN` 확인
2. Sentry 대시보드에서 Token 재생성
3. Token에 `project:releases` 권한 확인

#### 문제: "Project not found (HTTP 404)"
**해결:**
1. Sentry 대시보드 URL에서 정확한 조직/프로젝트 이름 확인
2. 워크플로우 파일의 `SENTRY_ORG`, `SENTRY_PROJECT` 값 수정
3. 프로젝트 접근 권한 확인

#### 문제: "Release already exists"
**해결:**
- 정상 동작입니다. 워크플로우가 자동으로 스킵합니다.
- 중복 생성 시도로 인한 에러를 방지합니다.

#### 문제: Rate limiting
**해결:**
1. Free 티어의 경우 API 호출 제한 확인
2. 워크플로우 실행 빈도 줄이기
3. 불필요한 Release 생성 방지 (이미 개선됨)

## 🔗 참고 자료

- [Sentry CLI 문서](https://docs.sentry.io/product/cli/)
- [Sentry Auth Tokens](https://docs.sentry.io/api/auth/)
- [GitHub Actions Sentry 통합](https://github.com/getsentry/action-release)
- [Sentry Release API](https://docs.sentry.io/api/releases/)
