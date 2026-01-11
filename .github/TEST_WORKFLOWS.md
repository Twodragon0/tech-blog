# 워크플로우 테스트 가이드

이 문서는 Sentry Release 워크플로우를 테스트하는 방법을 안내합니다.

## 🧪 테스트 방법

### 방법 1: 테스트 워크플로우 실행 (권장)

1. **GitHub 저장소 접속**
   - 저장소 페이지로 이동

2. **Actions 탭 열기**
   - 상단 메뉴에서 **Actions** 클릭

3. **테스트 워크플로우 선택**
   - 왼쪽 사이드바에서 **Test Sentry Release** 선택

4. **워크플로우 실행**
   - **Run workflow** 버튼 클릭
   - **Run workflow** 다시 클릭하여 확인

5. **결과 확인**
   - 워크플로우 실행이 시작되면 진행 상황 확인
   - 각 단계의 로그 확인:
     - ✅ `Verify Sentry Token`: Token 검증
     - ✅ `Verify Release Configuration`: 설정 검증
     - ✅ `Test Summary`: 테스트 요약

### 방법 2: 실제 Sentry Release 워크플로우 실행

테스트 워크플로우가 성공한 후:

1. **Sentry Release 워크플로우 선택**
   - 왼쪽 사이드바에서 **Sentry Release** 선택

2. **워크플로우 실행**
   - **Run workflow** 버튼 클릭
   - 브랜치 선택: `main`
   - **Run workflow** 다시 클릭

3. **결과 확인**
   - 워크플로우 실행 완료 대기
   - 성공 시 Sentry 대시보드에서 Release 확인

### 방법 3: 자동 실행 테스트

`main` 브랜치에 푸시하여 자동 실행:

```bash
# 테스트 커밋 생성
git commit --allow-empty -m "test: Sentry Release workflow"
git push origin main
```

## ✅ 성공 기준

### 테스트 워크플로우 성공 시
- ✅ `SENTRY_AUTH_TOKEN is set`
- ✅ `Token format is correct`
- ✅ `Successfully connected to Sentry API`
- ✅ `Configuration verified`

### Sentry Release 워크플로우 성공 시
- ✅ 워크플로우가 성공적으로 완료
- ✅ Sentry 대시보드에서 Release 확인 가능
- ✅ Release 버전: `tech-blog@<commit-sha>`
- ✅ 환경: `production`
- ✅ 커밋 정보 자동 연결

## ❌ 문제 해결

### Token 관련 오류

#### `SENTRY_AUTH_TOKEN is not set`
- **원인**: GitHub Secrets에 Token이 추가되지 않음
- **해결**: 
  1. Settings → Secrets and variables → Actions
  2. `SENTRY_AUTH_TOKEN` 추가 확인

#### `Authentication failed (HTTP 401/403)`
- **원인**: Token 권한 부족 또는 잘못된 Token
- **해결**:
  1. Sentry 대시보드에서 Token 권한 확인 (`project:releases`)
  2. Token 값이 정확한지 확인
  3. Token 재생성 후 GitHub Secrets 업데이트

#### `Project not found (HTTP 404)`
- **원인**: 조직 또는 프로젝트 이름 오류
- **해결**:
  1. 워크플로우 파일에서 확인:
     - `SENTRY_ORG: twodragon`
     - `SENTRY_PROJECT: tech-blog`
  2. Sentry 대시보드에서 정확한 이름 확인

### 워크플로우 실행 오류

#### `Workflow run failed`
- **원인**: 다양한 원인 가능
- **해결**:
  1. 워크플로우 로그 확인
  2. 각 단계별 에러 메시지 확인
  3. 위의 문제 해결 방법 참고

## 📊 Sentry 대시보드 확인

### Release 확인 방법

1. **Sentry 대시보드 접속**
   - [Sentry 프로젝트](https://sentry.io/organizations/twodragon/projects/tech-blog/) 접속

2. **Releases 메뉴**
   - 왼쪽 사이드바에서 **Releases** 클릭

3. **Release 확인**
   - 최신 Release 확인:
     - 버전: `tech-blog@<commit-sha>`
     - 환경: `production`
     - 생성 시간 확인

4. **커밋 정보 확인**
   - Release 상세 페이지에서 커밋 정보 확인
   - GitHub 커밋 링크 확인

## 🔍 로그 확인 방법

### GitHub Actions 로그

1. **Actions 탭**
   - 저장소 → **Actions** 탭

2. **워크플로우 선택**
   - 실행한 워크플로우 클릭

3. **실행 선택**
   - 최신 실행 클릭

4. **단계별 로그 확인**
   - 각 단계를 클릭하여 상세 로그 확인
   - 에러 발생 시 빨간색 표시 확인

## 📝 체크리스트

### 사전 확인
- [ ] GitHub Secrets에 `SENTRY_AUTH_TOKEN` 추가됨
- [ ] Token 권한: `project:releases` 확인
- [ ] 조직 이름: `twodragon` 확인
- [ ] 프로젝트 이름: `tech-blog` 확인

### 테스트 실행
- [ ] 테스트 워크플로우 실행 성공
- [ ] Sentry API 연결 성공
- [ ] Release 워크플로우 실행 성공
- [ ] Sentry 대시보드에서 Release 확인

### 최종 확인
- [ ] Release 버전 확인
- [ ] 환경 정보 확인
- [ ] 커밋 정보 연결 확인

## 🔗 관련 문서

- [SETUP_SENTRY_TOKEN.md](./SETUP_SENTRY_TOKEN.md)
- [SECRETS_MANAGEMENT.md](./SECRETS_MANAGEMENT.md)
- [SENTRY_VERCEL_GITHUB_INTEGRATION.md](../SENTRY_VERCEL_GITHUB_INTEGRATION.md)
