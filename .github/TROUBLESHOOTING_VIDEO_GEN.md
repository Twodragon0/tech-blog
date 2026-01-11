# 비디오 생성 워크플로우 문제 해결 가이드

## 🔍 일반적인 오류 및 해결 방법

### 1. DeepSeek API 401 Unauthorized 오류

**증상:**
```
[ERROR] ❌ DeepSeek API 요청 실패: 401 Client Error: Unauthorized
```

**원인:**
- API 키가 잘못되었거나 만료됨
- API 키 형식이 올바르지 않음
- API 키가 GitHub Secrets에 올바르게 설정되지 않음

**해결 방법:**

#### 1단계: DeepSeek API 키 확인
1. [DeepSeek Platform](https://platform.deepseek.com) 접속
2. 로그인 후 **API Keys** 메뉴로 이동
3. 기존 API 키 확인 또는 새 API 키 생성

#### 2단계: API 키 형식 확인
- 올바른 형식: `sk-`로 시작하는 문자열
- 예시: `sk-1234567890abcdef...`

#### 3단계: GitHub Secrets 업데이트
```bash
# GitHub CLI 사용
cd "/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"
gh secret set DEEPSEEK_API_KEY --body "your-new-api-key-here"

# 확인
gh secret list | grep -i deepseek
```

#### 4단계: 로컬 테스트
```bash
# 환경 변수 설정
export DEEPSEEK_API_KEY='your-api-key-here'
export ELEVENLABS_API_KEY='your-elevenlabs-key'
export ELEVENLABS_VOICE_ID='your-voice-id'

# 테스트 실행
python3 scripts/generate_audio.py
```

### 2. ElevenLabs API 오류

**증상:**
```
[ERROR] ❌ ElevenLabs API 요청 실패: 401/403
```

**해결 방법:**
1. [ElevenLabs Creative Platform](https://elevenlabs.io/app) 접속
2. **Developers** → **API Keys** 확인
3. API 키 권한 확인: **Text to Speech (Access)** 활성화
4. 사용량 확인: [Usage 페이지](https://elevenlabs.io/app/usage)
   - 무료 티어: 월 10,000자 제한

```bash
# GitHub Secrets 업데이트
gh secret set ELEVENLABS_API_KEY --body "your-new-api-key"
gh secret set ELEVENLABS_VOICE_ID --body "your-voice-id"
```

### 3. 스크립트 파일을 찾을 수 없음

**증상:**
```
python3: can't open file 'scripts/generate_audio.py': [Errno 2] No such file or directory
```

**해결 방법:**
```bash
# 스크립트 파일 커밋 확인
git status scripts/generate_audio.py

# 파일이 없다면 추가
git add scripts/generate_audio.py
git commit -m "feat: Add audio generation script"
git push origin main
```

### 4. Python 패키지 설치 오류

**증상:**
```
ModuleNotFoundError: No module named 'frontmatter'
```

**해결 방법:**
워크플로우에서 자동으로 설치되지만, 로컬에서 테스트할 때:
```bash
pip3 install -r scripts/requirements.txt
```

### 5. 포스트 파일을 찾을 수 없음

**증상:**
```
[ERROR] ❌ 포스트 파일을 찾을 수 없습니다
```

**해결 방법:**
- 워크플로우 실행 시 `post_file` 파라미터에 정확한 파일명 입력
- 파일명 형식: `2026-01-10-example-post.md`
- `_posts/` 디렉토리에 파일이 있는지 확인

## 🔧 디버깅 방법

### 1. 로그 확인
```bash
# GitHub Actions 로그
gh run view <run-id> --log

# 로컬 로그
tail -f video_generation_log.txt
```

### 2. API 키 검증
```bash
# DeepSeek API 테스트
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}],"max_tokens":10}'

# ElevenLabs API 테스트
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### 3. 환경 변수 확인
워크플로우에서 환경 변수가 올바르게 전달되는지 확인:
```yaml
env:
  DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
  ELEVENLABS_VOICE_ID: ${{ secrets.ELEVENLABS_VOICE_ID }}
```

## 📊 성공적인 실행 확인

워크플로우가 성공적으로 실행되면:
1. ✅ **오디오 파일 생성**: `output/*_audio.mp3`
2. ✅ **비디오 파일 생성**: `output/*_video.mp4`
3. ✅ **아티팩트 업로드**: GitHub Actions에서 다운로드 가능
4. ✅ **로그에 성공 메시지**: "✅ 오디오 생성 완료"

## 🔗 관련 문서

- [Secrets Management](./SECRETS_MANAGEMENT.md)
- [ElevenLabs Setup](./ELEVENLABS_SETUP.md)
- [Workflow Test Guide](./WORKFLOW_TEST_GUIDE.md)
- [Cost Management](./COST_MANAGEMENT.md)

## 💡 예방 조치

1. **정기적인 API 키 확인**: 월 1회 API 키 유효성 확인
2. **사용량 모니터링**: 
   - DeepSeek: [Platform Dashboard](https://platform.deepseek.com)
   - ElevenLabs: [Usage Page](https://elevenlabs.io/app/usage)
3. **로컬 테스트 우선**: GitHub Actions 실행 전 로컬에서 테스트
4. **크레딧 제한 설정**: 예상치 못한 사용 방지
