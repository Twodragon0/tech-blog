# ElevenLabs API 설정 가이드

이 문서는 GitHub Actions에서 ElevenLabs API를 사용하기 위한 설정 가이드를 제공합니다.

## 🔑 필수 Secrets 설정

### 1. ELEVENLABS_API_KEY 설정

```bash
# GitHub CLI 사용 (권장)
cd "/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"
gh secret set ELEVENLABS_API_KEY --body "your-api-key-here"
```

또는 GitHub 웹 인터페이스:
1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. Name: `ELEVENLABS_API_KEY`
4. Secret: API 키 값 입력
5. **Add secret** 클릭

### 2. ELEVENLABS_VOICE_ID 설정

Voice ID는 ElevenLabs Creative Platform에서 확인할 수 있습니다:

#### 방법 1: 기존 Voice 사용
1. [ElevenLabs Creative Platform](https://elevenlabs.io/app) 접속
2. **Voices** 메뉴로 이동
3. 사용할 Voice 선택
4. Voice ID 복사 (URL 또는 설정에서 확인)

#### 방법 2: Voice Design 사용 (무료 플랜 권장) ⭐
1. **Voices** 메뉴로 이동
2. **"Add a new voice"** 클릭
3. **"Voice Design"** 선택
4. 텍스트 프롬프트 입력 (예: "한국어를 구사하는 남성 강의 목소리, 차분하고 명확한 톤")
5. 생성 완료 후 Voice ID 확인

#### 방법 3: Voice Cloning (유료 플랜 필요)
- **Instant Voice Clone**: Starter 플랜($5/월) 이상 필요
- **Professional Voice Clone**: Creator 플랜($22/월) 이상 필요

```bash
# GitHub CLI로 Voice ID 설정
gh secret set ELEVENLABS_VOICE_ID --body "your-voice-id-here"

# 예시 (실제 사용된 Voice ID)
gh secret set ELEVENLABS_VOICE_ID --body "hnRmCiCoPWAjpxiiXEwz"
```

> 💡 **참고**: Voice Design으로 생성한 Voice는 무료 플랜에서도 사용 가능합니다.

## ✅ Secrets 확인

```bash
# 모든 Secrets 목록 확인
gh secret list

# ElevenLabs 관련 Secrets만 확인
gh secret list | grep -i elevenlabs
```

## 💰 비용 관리

### 무료 티어 제한
- **월 10,000자** 제한
- 초과 시 유료 플랜 필요

### 비용 절감 방법
1. **크레딧 제한 설정**: API Key 생성 시 월간 크레딧 제한 설정
2. **포스트 요약**: 긴 포스트는 DeepSeek으로 요약 후 사용
3. **수동 실행**: 워크플로우는 `workflow_dispatch`로만 실행 (자동 실행 방지)
4. **사용량 모니터링**: [ElevenLabs Usage](https://elevenlabs.io/app/usage)에서 정기 확인

### 사용량 확인
- ElevenLabs 대시보드: **Developers** → **Usage**
- 월간 사용량 및 크레딧 잔액 확인

## 🔒 보안 모범 사례

### 1. 최소 권한 원칙
- API Key 생성 시 **Text to Speech (Access)**만 활성화
- 불필요한 권한은 모두 **No Access**로 설정

### 2. 키 관리
- API Key는 절대 Git에 커밋하지 않기
- 로그에 API Key 값이 출력되지 않도록 주의
- 정기적으로 키 로테이션 (90일마다 권장)

### 3. 크레딧 제한
- API Key 생성 시 월간 크레딧 제한 설정
- 예상 사용량보다 여유있게 설정하되, 예상치 못한 사용 방지

## 🧪 테스트

### 워크플로우 수동 실행
```bash
# 워크플로우 실행
gh workflow run "Generate AI Video Lecture" \
  --field post_file="2026-01-10-example-post.md" \
  --field video_method="ffmpeg"

# 실행 상태 확인
gh run list --workflow="Generate AI Video Lecture" --limit 1

# 로그 확인
gh run view <run-id> --log
```

### 로컬 테스트
```bash
# 환경 변수 설정
export ELEVENLABS_API_KEY='your-api-key'
export ELEVENLABS_VOICE_ID='your-voice-id'
export DEEPSEEK_API_KEY='your-deepseek-key'

# 스크립트 실행
python3 scripts/generate_audio.py
```

## 📊 모니터링

### 사용량 추적
- ElevenLabs 대시보드에서 월간 사용량 확인
- GitHub Actions 로그에서 생성된 파일 크기 확인
- 비용 초과 시 알림 설정 (ElevenLabs 대시보드)

### 문제 해결
1. **API Key 오류**: Secrets 설정 확인
2. **Voice ID 오류**: Voice ID 형식 확인 (UUID)
3. **크레딧 부족**: 사용량 확인 및 플랜 업그레이드 고려
4. **권한 오류**: API Key 권한 확인 (Text to Speech Access 필요)

## 📚 관련 문서

- [ElevenLabs Platform Guide](../scripts/ELEVENLABS_PLATFORM_GUIDE.md)
- [Secrets Management](./SECRETS_MANAGEMENT.md)
- [Quick Setup](./QUICK_SETUP.md)
