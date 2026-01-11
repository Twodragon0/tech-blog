# Gemini API 설정 가이드

Gemini API를 설정하고 사용하는 방법을 안내합니다.

## 🚀 빠른 설정 (3단계)

### 1단계: OAuth 2.0 설정 (권장) ⭐

```bash
# 스크립트 디렉토리로 이동
cd scripts

# OAuth 2.0 설정 스크립트 실행
./setup_gemini_oauth.sh
```

**설정 전 확인사항:**
- Google Cloud 프로젝트 생성 완료
- 서비스 계정 생성 완료
- Gemini API 활성화 완료

자세한 내용: [Gemini OAuth 2.0 설정 가이드](./GEMINI_OAUTH_SETUP.md)

### 2단계: API Key 설정 (선택, 폴백용)

OAuth 2.0 실패 시 폴백으로 사용됩니다.

#### 옵션 A: 기본값 사용

```bash
# 기본값 사용 (GitHub Secrets + 로컬 환경 변수)
./setup_gemini_api_key.sh --default --both
```

#### 옵션 B: 커스텀 키 사용

```bash
# 커스텀 API Key 사용
./setup_gemini_api_key.sh --api-key YOUR_KEY --both

# 또는 GitHub Secrets에만 설정
./setup_gemini_api_key.sh --api-key YOUR_KEY --github

# 또는 로컬 환경 변수에만 설정
./setup_gemini_api_key.sh --api-key YOUR_KEY --local
```

**참고:**
- `--both`: GitHub Secrets와 로컬 환경 변수 모두 설정
- `--github`: GitHub Secrets에만 설정
- `--local`: 로컬 환경 변수에만 설정

자세한 내용: [Gemini API Key 설정 가이드](./SETUP_GEMINI_API_KEY.md)

### 3단계: 테스트 실행

```bash
# 프로젝트 루트로 이동
cd ..

# 최신 포스트로 테스트
python3 scripts/generate_enhanced_audio.py

# 또는 특정 포스트 지정
python3 scripts/generate_enhanced_audio.py _posts/2026-01-10-example.md
```

**예상 출력:**
```
🎯 API 선택 전략 (우선순위):
  1️⃣ Gemini OAuth 2.0 (우선) ⭐
  2️⃣ Gemini API Key (폴백)
  3️⃣ DeepSeek API (폴백)

📝 Gemini OAuth 2.0 API로 대본 생성 중...
✅ Gemini OAuth 2.0 API로 대본 생성 완료
🎤 ElevenLabs API로 음성 생성 중...
✅ 음성 생성 완료
```

## 📋 설정 요약

### 우선순위

워크플로우와 스크립트는 다음 순서로 API를 사용합니다:

1. **Gemini OAuth 2.0** (서비스 계정) ⭐ 최우선
2. **Gemini API Key** (폴백)
3. **DeepSeek API** (폴백)

### 필요한 Secrets

#### 필수
- `ELEVENLABS_API_KEY`: ElevenLabs API Key
- `ELEVENLABS_VOICE_ID`: ElevenLabs Voice ID

#### 선택 (최소 하나)
- `GEMINI_SERVICE_ACCOUNT_KEY`: OAuth 2.0 서비스 계정 키 (권장) ⭐
- `GEMINI_API_KEY`: Gemini API Key (폴백)
- `DEEPSEEK_API_KEY`: DeepSeek API Key (폴백)

## 💡 권장 설정

### 프로덕션 환경 (GitHub Actions)

```bash
cd scripts

# 1. OAuth 2.0 설정 (비용 절감, 보안 강화)
./setup_gemini_oauth.sh
# → GitHub Secrets에 GEMINI_SERVICE_ACCOUNT_KEY 설정 필요

# 2. API Key 폴백 설정 (선택, OAuth 실패 시 사용)
./setup_gemini_api_key.sh --default --github
# 또는
./setup_gemini_api_key.sh --api-key YOUR_KEY --github
```

### 개발 환경 (로컬)

```bash
cd scripts

# 로컬 환경 변수만 설정
./setup_gemini_api_key.sh --default --local
# 또는
./setup_gemini_api_key.sh --api-key YOUR_KEY --local
```

### 완전한 설정 (OAuth + API Key)

```bash
cd scripts

# 1. OAuth 2.0 설정
./setup_gemini_oauth.sh

# 2. API Key 폴백 설정
./setup_gemini_api_key.sh --default --both
```

## 🔍 확인 방법

### 설정 확인

#### GitHub Secrets 확인

```bash
# GitHub CLI 사용
gh secret list

# 또는 GitHub 웹에서
# Settings → Secrets and variables → Actions
```

확인할 Secrets:
- `GEMINI_SERVICE_ACCOUNT_KEY` (OAuth 2.0)
- `GEMINI_API_KEY` (폴백)
- `GOOGLE_CLOUD_PROJECT` (OAuth 2.0)

#### 로컬 환경 변수 확인

```bash
# .env 파일 확인
cat .env

# 환경 변수 로드 후 확인
source .env  # 또는 source ~/.zshrc
echo $GEMINI_API_KEY
echo $GOOGLE_CLOUD_PROJECT
```

### 실행 확인

```bash
# 스크립트 실행
cd ..
python3 scripts/generate_enhanced_audio.py

# 로그에서 API 선택 확인
tail -f video_generation_log.txt | grep -E "(🎯|✅|❌)"
```

**성공 시 예상 로그:**
```
🎯 OAuth 2.0 우선 전략: Gemini OAuth 2.0 API로 대본 생성 시도...
📝 Gemini OAuth 2.0 API로 대본 생성 중...
✅ Gemini OAuth 2.0 API로 대본 생성 완료 (1234자)
🎤 ElevenLabs API로 음성 생성 중...
✅ 음성 생성 완료: output/example_audio.mp3
```

**폴백 시 예상 로그:**
```
🎯 OAuth 2.0 우선 전략: Gemini OAuth 2.0 API로 대본 생성 시도...
❌ OAuth 2.0 실패, Gemini API 키로 대본 생성 시도...
📝 Gemini AI Pro로 대본 생성 중...
✅ Gemini AI Pro로 대본 생성 완료 (1234자)
```

## 📚 관련 문서

- [Gemini OAuth 2.0 설정 가이드](./GEMINI_OAUTH_SETUP.md)
- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)
- [GitHub Secrets 관리 가이드](../.github/SECRETS_MANAGEMENT.md)

---

**마지막 업데이트**: 2026-01-10
