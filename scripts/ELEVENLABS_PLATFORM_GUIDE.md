# ElevenLabs 플랫폼 선택 가이드

## 🎯 선택해야 할 플랫폼: **Creative Platform**

블로그 포스팅을 영상 강의로 변환하는 작업에는 **Creative Platform**을 선택해야 합니다.

## 📊 플랫폼 비교

### Creative Platform ✅ (권장)

**주요 기능:**
- ✅ **Text to Speech**: 텍스트를 음성으로 변환 (필수)
- ✅ **Image & Video (New)**: 이미지와 비디오 생성/편집
- ✅ **Voice Changer**: 음성 변조
- ✅ **Voice Isolator**: 음성 분리
- ✅ **Dubbing**: 더빙
- ✅ **Music**: 음악 생성
- ✅ **Studio**: 오디오 편집

**우리 프로젝트에 필요한 기능:**
- Text to Speech: 블로그 대본을 음성으로 변환
- Image & Video: 향후 Remotion과 통합 시 활용 가능

### Agents Platform ❌ (불필요)

**주요 기능:**
- Agents: AI 에이전트 관리
- Tools: 도구 통합
- Integrations: 외부 서비스 연동
- Outbound: 발신 전화
- Knowledge Base: 지식 베이스
- Conversations: 대화 관리
- Phone numbers: 전화번호 관리

**우리 프로젝트와의 관련성:**
- 블로그 포스팅 → 영상 변환 작업과 직접적인 관련 없음
- AI 에이전트 구축용 플랫폼

## 🚀 Creative Platform 설정 방법

### 1. 플랫폼 선택

1. [ElevenLabs](https://elevenlabs.io)에 로그인
2. "Choose your platform" 화면에서 **"Creative Platform"** 선택
3. "Continue" 클릭

### 2. API 키 발급

1. Creative Platform 대시보드 접속
2. 상단 메뉴에서 **"Developers"** 클릭
3. **"API Keys"** 메뉴 선택
4. **"Create Key"** 클릭
5. API 키 이름 지정 (예: "blog-video-generation")
6. **권한 설정** (최소 권한 원칙 적용):
   - ✅ **Text to Speech**: **Access** (필수) - 블로그 대본을 음성으로 변환
   - ⚠️ **Voices**: **Read** (선택) - Voice ID 조회 시에만 필요 (이미 Voice ID를 알고 있다면 불필요)
   - ❌ 나머지 권한: **No Access** (보안을 위해 불필요한 권한은 비활성화)
7. 필요시 월간 크레딧 제한 설정 (비용 관리)
8. **"Create"** 클릭하여 API 키 생성
9. ⚠️ **중요**: API 키는 생성 시 한 번만 표시되므로 즉시 복사하여 안전하게 보관

**권한 설정 가이드:**

| 권한 항목 | 설정 | 이유 |
|---------|------|------|
| **Text to Speech** | ✅ **Access** | 블로그 대본을 음성으로 변환하는 핵심 기능 |
| **Voices** | ⚠️ **Read** (선택) | Voice ID를 조회하거나 목록 확인 시 필요. 이미 Voice ID를 알고 있다면 불필요 |
| **Voice Generation** | ❌ **No Access** | Voice는 웹 UI에서 생성하므로 API 권한 불필요 |
| **Speech to Speech** | ❌ **No Access** | 사용하지 않음 |
| **Speech to Text** | ❌ **No Access** | 사용하지 않음 |
| **Sound Effects** | ❌ **No Access** | 사용하지 않음 |
| **Audio Isolation** | ❌ **No Access** | 사용하지 않음 |
| **Music Generation** | ❌ **No Access** | 사용하지 않음 |
| **Dubbing** | ❌ **No Access** | 사용하지 않음 |
| **ElevenLabs Agents** | ❌ **No Access** | 사용하지 않음 |
| **Projects** | ❌ **No Access** | 사용하지 않음 |
| **Audio Native** | ❌ **No Access** | 사용하지 않음 |
| **Forced Alignment** | ❌ **No Access** | 사용하지 않음 |
| **Administration** | ❌ **No Access** | 보안상 불필요한 권한 |

**보안 모범 사례:**
- 🔒 **최소 권한 원칙**: 필요한 권한만 활성화
- 💰 **크레딧 제한**: 월간 사용량 제한 설정 권장
- 🔑 **키 이름**: 용도를 명확히 하는 이름 사용 (예: "blog-video-generation")
- 📝 **키 관리**: 사용하지 않는 키는 삭제

**참고**: Developers 메뉴에는 다음 항목들이 포함되어 있습니다:
- API Keys: API 키 관리
- Webhooks: 웹훅 설정
- Usage: 사용량 확인
- Analytics: 분석 데이터
- Request Log: 요청 로그

### 3. Voice ID 확인

#### 방법 1: 기존 Voice 사용
1. **Voices** 메뉴로 이동
2. 사용할 Voice 선택
3. Voice ID 복사 (URL 또는 설정에서 확인)

#### 방법 2: Voice Design (무료 플랜 권장) ⭐
무료 플랜에서는 Voice Cloning이 불가능하지만, **Voice Design**을 사용하여 텍스트 프롬프트로 새로운 목소리를 생성할 수 있습니다.

**Voice Design 사용 방법:**
1. **Voices** 메뉴로 이동
2. **"Add a new voice"** 클릭
3. **"Voice Design"** 선택
4. 텍스트 프롬프트 입력 (예: "한국어를 구사하는 남성 강의 목소리, 차분하고 명확한 톤")
5. 생성 완료 후 Voice ID 확인

**Voice Design 프롬프트 예시:**
- "한국어를 구사하는 남성 강의 목소리, 차분하고 명확한 톤, 약간 낮은 음성"
- "한국어를 구사하는 여성 강의 목소리, 친근하고 밝은 톤, 명확한 발음"
- "한국어를 구사하는 전문가 목소리, 신뢰감 있고 전문적인 톤"

#### 방법 3: Voice Cloning (유료 플랜 필요)
**⚠️ 주의**: Voice Cloning은 무료 플랜에서 사용할 수 없습니다.
- **Instant Voice Clone**: Starter 플랜($5/월) 이상 필요 - 10초 오디오로 클론
- **Professional Voice Clone**: Creator 플랜($22/월) 이상 필요 - 30분 오디오로 고품질 클론

**Voice Cloning 사용 방법 (유료 플랜):**
1. **Voices** 메뉴로 이동
2. **"Add a new voice"** 클릭
3. **"Instant Voice Clone"** 또는 **"Professional Voice Clone"** 선택
4. 본인의 목소리 샘플 업로드
5. Voice 생성 완료 후 Voice ID 확인

#### 방법 4: API로 Voice 목록 조회
스크립트를 사용하여 사용 가능한 Voice 목록을 조회할 수 있습니다:

```bash
python3 scripts/generate_enhanced_audio.py --list-voices
```

또는 환경 변수만 설정하고 실행:

```bash
export ELEVENLABS_API_KEY='your-api-key'
python3 scripts/generate_enhanced_audio.py --list-voices
```

### 4. 환경 변수 설정

```bash
export ELEVENLABS_API_KEY='your-api-key-here'
export ELEVENLABS_VOICE_ID='your-voice-id-here'
```

또는 GitHub Secrets에 추가:
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID`

## 💡 Voice 선택 가이드

### 무료 플랜 사용자
1. **Voice Design 사용**: 텍스트 프롬프트로 원하는 목소리 생성
2. **기존 Voice 사용**: ElevenLabs에서 제공하는 프리미엄 Voice 중 선택
3. **Voice Remixing (alpha)**: 기존 Voice를 텍스트 프롬프트로 변환

### 유료 플랜 사용자
1. **Voice Cloning 권장**: 본인의 목소리로 더 자연스러운 강의 가능
2. **브랜딩**: 퍼스널 브랜딩 강화
3. **일관성**: 모든 영상에서 동일한 목소리 사용

## 📝 API 사용 예시

```python
import requests

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}

data = {
    "text": "안녕하세요, 오늘은 DevSecOps에 대해 알아보겠습니다.",
    "model_id": "eleven_multilingual_v2",  # 한국어 지원
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(url, json=data, headers=headers)
# MP3 오디오 파일 반환
```

## ⚠️ 주의사항

1. **무료 티어 제한**: 
   - 월 10,000자 제한
   - Voice Cloning 기능 불가 (Voice Design은 사용 가능)
2. **비용 관리**: 긴 포스트는 요약 후 사용 권장
3. **API 키 보안**: 절대 Git에 커밋하지 않기
4. **Voice ID 확인**: Voice 목록 조회 시 `--list-voices` 옵션 사용 가능

## 🔗 관련 링크

- [ElevenLabs Creative Platform](https://elevenlabs.io/app)
- [ElevenLabs API 문서](https://elevenlabs.io/docs)
- [Voice Cloning 가이드](https://elevenlabs.io/docs/voice-cloning)
