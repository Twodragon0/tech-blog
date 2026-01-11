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
cd /path/to/tech-blog  # 실제 프로젝트 경로로 교체 필요

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

## 🎤 ElevenLabs API 설정

### GitHub CLI로 설정 (권장)

```bash
cd /path/to/tech-blog  # 실제 프로젝트 경로로 교체 필요

# API Key 설정
gh secret set ELEVENLABS_API_KEY --body "your-api-key-here"

# Voice ID 설정 (ElevenLabs 대시보드에서 확인)
gh secret set ELEVENLABS_VOICE_ID --body "your-voice-id-here"

# 확인
gh secret list | grep -i elevenlabs
```

### 웹 인터페이스로 설정

1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. Name: `ELEVENLABS_API_KEY` 또는 `ELEVENLABS_VOICE_ID`
4. Secret 값 입력 후 저장

> 💡 **참고**: 
> - API Key는 ElevenLabs Creative Platform → Developers → API Keys에서 생성
> - Voice ID는 Voices 메뉴에서 확인
> - 자세한 내용은 [ELEVENLABS_SETUP.md](./ELEVENLABS_SETUP.md) 참고

## 🐛 문제 해결

### Secret이 보이지 않는 경우
- Secret 이름이 정확한지 확인 (대소문자 구분)
- 저장소 Settings → Secrets and variables → Actions에서 확인

### 워크플로우가 실패하는 경우
- Secret이 올바르게 설정되었는지 확인
- Token/Key 값이 정확한지 확인
- 권한 확인:
  - Sentry: `project:releases`
  - ElevenLabs: Text to Speech (Access)

### ElevenLabs 관련 오류
- API Key 형식 확인: `sk_`로 시작해야 함
- Voice ID 형식 확인: UUID 형식
- 사용량 확인: [ElevenLabs Usage](https://elevenlabs.io/app/usage)
- 무료 티어 제한: 월 10,000자
