# 빠른 설정 가이드

## 🔑 GitHub Secrets에 Token 추가하기

### 방법 1: GitHub 웹 인터페이스 (권장)

1. **저장소 페이지 접속**
   - https://github.com/Twodragon0/tech-blog 접속

2. **Settings 메뉴**
   - 저장소 상단의 **Settings** 탭 클릭

3. **Secrets 메뉴**
   - 왼쪽 사이드바: **Secrets and variables** → **Actions**

4. **새 Secret 추가**
   - **New repository secret** 버튼 클릭
   - **Name**: `SENTRY_AUTH_TOKEN` (정확히 입력)
   - **Secret**: `[발급받은 Token 값 입력]` (예: `sntryu_...`)
   - **Add secret** 클릭
   
   > 💡 **참고**: Token 값은 Sentry 대시보드에서 발급받은 값을 입력하세요.

### 방법 2: GitHub CLI 사용

```bash
cd "/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"

# Secret 추가
gh secret set SENTRY_AUTH_TOKEN \
  --body "[발급받은 Token 값]"

# 확인
gh secret list
```

## ✅ 확인 방법

### GitHub CLI로 확인
```bash
gh secret list
```

### 워크플로우 테스트
```bash
# 테스트 워크플로우 실행
gh workflow run "Test Sentry Release"

# 실행 상태 확인
gh run list --workflow="Test Sentry Release" --limit 1

# 로그 확인
gh run view <run-id> --log
```

## 🐛 문제 해결

### Secret이 보이지 않는 경우
- Secret 이름이 정확한지 확인: `SENTRY_AUTH_TOKEN` (대소문자 구분)
- 저장소 Settings → Secrets and variables → Actions에서 확인

### 워크플로우가 실패하는 경우
- Secret이 올바르게 설정되었는지 확인
- Token 값이 정확한지 확인
- Token 권한 확인: `project:releases`
