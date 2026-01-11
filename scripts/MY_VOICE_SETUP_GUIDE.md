# 내 목소리로 강의 영상 만들기 가이드

## 🎯 목표
ElevenLabs를 사용하여 자신의 목소리로 블로그 포스팅을 강의 영상으로 변환하기

## 📋 무료 플랜에서 가능한 방법

### ⚠️ 중요: 무료 플랜 제한사항
- **Voice Cloning 불가**: Instant Voice Clone과 Professional Voice Clone은 유료 플랜(Starter $5/월 이상)에서만 사용 가능
- **Voice Design 사용 가능**: 텍스트 프롬프트로 새로운 목소리 생성 가능
- **월 10,000자 제한**: Text to Speech 사용량 제한

## 🚀 단계별 설정 가이드

### 1단계: ElevenLabs에서 Voice 생성

#### 방법 A: Voice Design 사용 (무료 플랜 권장) ⭐

1. [ElevenLabs Creative Platform](https://elevenlabs.io/app)에 로그인
2. 왼쪽 메뉴에서 **"Voices"** 클릭
3. **"Add a new voice"** 버튼 클릭
4. **"Voice Design"** 선택
5. 텍스트 프롬프트 입력:
   ```
   한국어를 구사하는 남성 강의 목소리, 차분하고 명확한 톤, 약간 낮은 음성, 전문적이고 신뢰감 있는 말투
   ```
   또는
   ```
   한국어를 구사하는 여성 강의 목소리, 친근하고 밝은 톤, 명확한 발음, 자연스러운 구어체
   ```
6. **"Generate"** 클릭하여 Voice 생성 (약 1분 소요)
7. 생성된 Voice를 테스트해보고 마음에 들면 사용

#### 방법 B: Voice Remixing 사용 (무료 플랜, Alpha 기능)

1. **"Voices"** 메뉴로 이동
2. 기존 Voice 선택
3. **"Voice Remixing"** 옵션 사용
4. 텍스트 프롬프트로 Voice 변환

### 2단계: Voice ID 확인

1. 생성한 Voice를 클릭하여 상세 페이지로 이동
2. URL에서 Voice ID 확인 (예: `https://elevenlabs.io/app/voices/21m00Tcm4TlvDq8ikWAM`)
   - Voice ID는 URL의 마지막 부분입니다
3. 또는 Voice 설정에서 Voice ID 복사

### 3단계: API로 Voice 목록 조회 (선택사항)

스크립트를 사용하여 사용 가능한 모든 Voice 목록을 조회할 수 있습니다:

```bash
# 환경 변수 설정
export ELEVENLABS_API_KEY='your-api-key-here'

# Voice 목록 조회
python3 scripts/generate_audio.py --list-voices
```

출력 예시:
```
🔍 ElevenLabs Voice 목록 조회 중...
✅ 5개의 Voice를 찾았습니다.

📋 사용 가능한 Voice 목록:
============================================================

🎤 Voice: My Lecture Voice
   ID: 21m00Tcm4TlvDq8ikWAM
   카테고리: generated
   설명: Voice Design으로 생성된 강의용 목소리

💡 Voice ID를 환경 변수에 설정하세요:
   export ELEVENLABS_VOICE_ID='21m00Tcm4TlvDq8ikWAM'
```

### 4단계: 환경 변수 설정

로컬에서 사용하는 경우:
```bash
export ELEVENLABS_API_KEY='your-api-key-here'
export ELEVENLABS_VOICE_ID='your-voice-id-here'
export DEEPSEEK_API_KEY='your-deepseek-key-here'
```

GitHub Actions에서 사용하는 경우:
1. GitHub 저장소 → Settings → Secrets and variables → Actions
2. 다음 Secrets 추가:
   - `ELEVENLABS_API_KEY`
   - `ELEVENLABS_VOICE_ID`
   - `DEEPSEEK_API_KEY`

### 5단계: 오디오 생성 테스트

```bash
# 최신 포스트로 오디오 생성
python3 scripts/generate_audio.py

# 특정 포스트로 오디오 생성
python3 scripts/generate_audio.py _posts/2026-01-10-example.md
```

## 💡 Voice Design 프롬프트 작성 팁

### 좋은 프롬프트 예시

1. **차분한 강의 목소리**:
   ```
   한국어를 구사하는 남성 강의 목소리, 차분하고 명확한 톤, 약간 낮은 음성, 전문적이고 신뢰감 있는 말투, 자연스러운 속도
   ```

2. **친근한 강의 목소리**:
   ```
   한국어를 구사하는 여성 강의 목소리, 친근하고 밝은 톤, 명확한 발음, 자연스러운 구어체, 약간 빠른 속도
   ```

3. **전문가 목소리**:
   ```
   한국어를 구사하는 전문가 목소리, 신뢰감 있고 전문적인 톤, 명확하고 정확한 발음, 중간 속도
   ```

### 프롬프트 작성 시 포함할 요소

- **언어**: "한국어를 구사하는"
- **성별**: "남성" 또는 "여성" (선택사항)
- **톤**: "차분한", "밝은", "전문적인" 등
- **속도**: "자연스러운 속도", "약간 빠른 속도" 등
- **용도**: "강의 목소리", "내레이션 목소리" 등

## 🔄 유료 플랜으로 업그레이드 시 (선택사항)

### Starter 플랜 ($5/월)
- ✅ Instant Voice Clone 사용 가능
- ✅ 10초 오디오로 목소리 클론
- ✅ 월 30,000자 제한

### Creator 플랜 ($22/월)
- ✅ Professional Voice Clone 사용 가능
- ✅ 30분 오디오로 고품질 목소리 클론
- ✅ 월 100,000자 제한
- ✅ 192 kbps 고품질 오디오

**Voice Cloning 사용 방법:**
1. **Voices** 메뉴 → **"Add a new voice"**
2. **"Instant Voice Clone"** 또는 **"Professional Voice Clone"** 선택
3. 깨끗한 오디오 샘플 업로드 (노이즈 없는 환경, 명확한 발음)
4. Voice 생성 완료 후 Voice ID 확인

## 📝 API 권한 설정

API 키 생성 시 다음 권한이 필요합니다:

| 권한 항목 | 설정 | 이유 |
|---------|------|------|
| **Text to Speech** | ✅ **Access** | 필수 - 텍스트를 음성으로 변환 |
| **Voices** | ✅ **Read** | Voice 목록 조회 시 필요 |
| **Voice Generation** | ❌ **No Access** | Voice는 웹 UI에서 생성 |

## ⚠️ 주의사항

1. **무료 플랜 제한**: 월 10,000자 제한이 있으므로 긴 포스트는 요약 후 사용
2. **Voice ID 보안**: Voice ID는 민감 정보가 아니지만, API 키는 절대 공개하지 마세요
3. **비용 관리**: 사용량은 [ElevenLabs Usage 페이지](https://elevenlabs.io/app/usage)에서 확인 가능
4. **Voice 품질**: Voice Design은 Voice Cloning보다 품질이 낮을 수 있지만, 무료로 사용 가능

## 🔗 관련 링크

- [ElevenLabs Creative Platform](https://elevenlabs.io/app)
- [ElevenLabs API 문서](https://elevenlabs.io/docs)
- [Voice Design 가이드](https://elevenlabs.io/docs/voice-design)
- [플랫폼 선택 가이드](./ELEVENLABS_PLATFORM_GUIDE.md)

## 🆘 문제 해결

### Voice 목록이 조회되지 않는 경우
- API 키에 "Voices: Read" 권한이 있는지 확인
- API 키 형식이 올바른지 확인 (`sk_`로 시작해야 함)

### Voice ID를 찾을 수 없는 경우
- Voice 상세 페이지의 URL에서 확인
- `--list-voices` 옵션으로 API로 조회

### 오디오 생성이 실패하는 경우
- Voice ID가 올바른지 확인
- API 키에 "Text to Speech: Access" 권한이 있는지 확인
- 월 사용량 제한을 초과하지 않았는지 확인
