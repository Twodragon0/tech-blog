# Gemini OAuth 2.0 빠른 시작 가이드

Google Cloud 서비스 계정을 사용하여 즉시 시작하는 가이드입니다.

## ⚡ 3분 안에 시작하기

### 1. 서비스 계정 키 다운로드

```bash
cd /path/to/tech-blog
./scripts/setup_gemini_oauth.sh
```

### 2. Python 패키지 설치

```bash
pip install -r scripts/requirements.txt
```

### 3. 환경 변수 설정

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gemini-service-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export USE_GEMINI_OAUTH="true"
```

### 4. 실행!

```bash
python3 scripts/generate_enhanced_audio.py
```

## ✅ 확인 사항

스크립트 실행 시 다음이 표시되면 성공:

```
🔑 사용 가능한 API:
  OAuth 2.0: ✅
    서비스 계정: your-service-account@your-project-id.iam.gserviceaccount.com
    프로젝트 ID: your-project-id
🎯 OAuth 2.0 우선 전략: Gemini OAuth 2.0 API로 대본 생성 시도...
✅ OAuth 2.0 인증 완료 (서비스 계정 사용)
```

## 🔧 문제 해결

### 키 파일을 찾을 수 없음

```bash
# 키 파일 위치 확인
ls -la gemini-service-key.json

# 절대 경로로 설정
export GOOGLE_APPLICATION_CREDENTIALS="/full/path/to/gemini-service-key.json"
```

### Python 패키지 오류

```bash
# 패키지 재설치
pip install --upgrade google-auth google-generativeai
```

### 권한 오류

Google Cloud Console에서 서비스 계정 권한 확인:
- IAM & Admin > Service Accounts
- 사용 중인 서비스 계정 선택
- 권한 탭에서 `Vertex AI User` 또는 `Generative Language User` 확인

## 📚 더 자세한 정보

- [상세 설정 가이드](./GEMINI_OAUTH_SETUP.md)
- [OAuth 통합 가이드](./GEMINI_OAUTH_INTEGRATION.md)
- [Gemini AI Pro 가이드](./GEMINI_AI_PRO_GUIDE.md)

---

**마지막 업데이트**: 2026-01-08
