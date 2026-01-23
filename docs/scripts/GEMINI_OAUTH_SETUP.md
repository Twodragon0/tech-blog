# Gemini OAuth 2.0 설정 가이드

Google Cloud 서비스 계정을 사용하여 OAuth 2.0 인증을 설정하는 가이드입니다.

## 🎯 개요

- **프로젝트 ID**: `your-project-id` (실제 프로젝트 ID로 변경)
- **서비스 계정**: `your-service-account@your-project-id.iam.gserviceaccount.com` (실제 서비스 계정으로 변경)
- **인증 방식**: Google Cloud 서비스 계정 OAuth 2.0

## 🚀 빠른 시작

### 1단계: 서비스 계정 키 다운로드

```bash
# 자동 설정 스크립트 실행
./scripts/setup_gemini_oauth.sh
```

또는 수동으로:

```bash
# gcloud CLI로 키 다운로드
# 실제 서비스 계정과 프로젝트 ID로 변경하세요
gcloud iam service-accounts keys create gemini-service-key.json \
    --iam-account=your-service-account@your-project-id.iam.gserviceaccount.com \
    --project=your-project-id
```

### 2단계: Python 패키지 설치

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-generativeai
```

또는 `requirements.txt`에 추가:

```
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-generativeai>=0.3.0
```

### 3단계: 환경 변수 설정

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gemini-service-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export USE_GEMINI_OAUTH="true"
```

또는 `.env` 파일에 추가:

```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gemini-service-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
USE_GEMINI_OAUTH=true
```

> **참고**: `.env.example` 파일을 참조하여 실제 값으로 변경하세요.

### 4단계: 스크립트 실행

```bash
python3 scripts/generate_enhanced_audio.py
```

## 📋 상세 설정

### 서비스 계정 키 파일 위치

키 파일은 프로젝트 루트에 저장하는 것을 권장합니다:

```
tech-blog/
├── gemini-service-key.json  # 서비스 계정 키
├── .gitignore               # 키 파일 제외됨
└── scripts/
    └── generate_enhanced_audio.py
```

### 환경 변수 상세

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `GOOGLE_APPLICATION_CREDENTIALS` | 서비스 계정 키 파일 경로 | `/path/to/gemini-service-key.json` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud 프로젝트 ID | `your-project-id` |
| `USE_GEMINI_OAUTH` | OAuth 2.0 사용 여부 | `true` |

### .gitignore 설정

`.gitignore` 파일에 다음을 추가하여 키 파일이 Git에 커밋되지 않도록 합니다:

```
# Gemini OAuth service account key
gemini-service-key.json
```

## 🔒 보안 고려사항

### 1. 키 파일 보안

- ✅ 키 파일은 절대 Git에 커밋하지 않음
- ✅ `.gitignore`에 추가됨
- ✅ 로컬에서만 사용
- ✅ 필요시 권한 제한: `chmod 600 gemini-service-key.json`

### 2. 환경 변수 관리

- ✅ 프로덕션에서는 환경 변수로 관리
- ✅ GitHub Secrets에 추가 (CI/CD 사용 시)
- ✅ 로컬 `.env` 파일은 Git에 커밋하지 않음

### 3. 서비스 계정 권한

현재 서비스 계정에 필요한 권한:
- `roles/aiplatform.user`: Vertex AI 사용 권한
- `roles/generativelanguage.user`: Gemini API 사용 권한

## 🧪 테스트

### OAuth 2.0 인증 테스트

```bash
# 환경 변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gemini-service-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export USE_GEMINI_OAUTH="true"

# 스크립트 실행
python3 scripts/generate_enhanced_audio.py
```

### 인증 확인

스크립트 실행 시 다음 메시지가 표시되면 성공:

```
🔑 사용 가능한 API:
  OAuth 2.0: ✅
    서비스 계정: your-service-account@your-project-id.iam.gserviceaccount.com
    프로젝트 ID: your-project-id
    자격 증명 파일: /path/to/gemini-service-key.json
```

## 🔄 API 선택 우선순위

OAuth 2.0이 활성화되면 다음 우선순위로 API를 선택합니다:

1. **OAuth 2.0** (우선) ⭐
2. Gemini API Key (폴백)
3. DeepSeek API (폴백)

## 🐛 문제 해결

### 오류: "GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다"

**해결 방법:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gemini-service-key.json"
```

### 오류: "서비스 계정 키 파일을 찾을 수 없습니다"

**해결 방법:**
1. 키 파일 경로 확인
2. 파일 존재 여부 확인: `ls -la gemini-service-key.json`
3. 절대 경로 사용 권장

### 오류: "google.auth 모듈을 찾을 수 없습니다"

**해결 방법:**
```bash
pip install google-auth google-generativeai
```

### 오류: "권한이 없습니다"

**해결 방법:**
1. 서비스 계정에 필요한 권한 확인
2. Google Cloud Console에서 권한 확인:
   - IAM & Admin > Service Accounts
   - 사용 중인 서비스 계정 선택
   - 권한 탭 확인
3. 필요한 권한:
   - `roles/aiplatform.user`: Vertex AI 사용 권한
   - `roles/generativelanguage.user`: Gemini API 사용 권한

## 📊 OAuth 2.0 vs API Key 비교

| 항목 | OAuth 2.0 | API Key |
|------|-----------|---------|
| 보안 | ✅ 높음 (토큰 자동 갱신) | ⚠️ 중간 |
| 관리 | 복잡 (서비스 계정 필요) | 간단 |
| 권한 | 세밀한 권한 관리 | 전체 권한 |
| 감사 | ✅ 지원 | ❌ 미지원 |
| 권장 사용 | 프로덕션 | 개발/테스트 |

## 🔗 관련 문서

- [Gemini OAuth 통합 가이드](./GEMINI_OAUTH_INTEGRATION.md)
- [Gemini AI Pro 활용 가이드](./GEMINI_AI_PRO_GUIDE.md)
- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)
- [Google Cloud 인증 가이드](https://cloud.google.com/docs/authentication)

## ⚠️ 주의사항

1. **키 파일 보안**: 서비스 계정 키는 민감 정보입니다. 절대 공개하지 마세요.
2. **권한 관리**: 최소 권한 원칙을 따르세요.
3. **비용 모니터링**: OAuth 2.0 사용 시에도 비용이 발생합니다.
4. **토큰 갱신**: 서비스 계정은 자동으로 토큰을 갱신합니다.

---

**마지막 업데이트**: 2026-01-08
