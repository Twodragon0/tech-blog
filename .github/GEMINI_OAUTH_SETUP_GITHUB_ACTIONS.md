# GitHub Actions에서 Gemini OAuth 2.0 설정 가이드

GitHub Actions에서 Gemini OAuth 2.0을 사용하여 보이스 생성을 최적화하는 방법을 안내합니다.

## 🎯 개요

Gemini OAuth 2.0을 사용하면:
- ✅ API Key보다 안전한 인증
- ✅ 토큰 자동 갱신
- ✅ 비용 절감 가능
- ✅ 세밀한 권한 관리

## 📋 사전 요구사항

1. Google Cloud 프로젝트 생성
2. Gemini API 활성화
3. 서비스 계정 생성 및 키 다운로드

## 🔧 설정 단계

### 1. Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. 프로젝트 ID 확인 (예: `my-gemini-project-123456`)

### 2. Gemini API 활성화

```bash
# gcloud CLI 사용 (선택적)
gcloud services enable generativelanguage.googleapis.com --project=YOUR_PROJECT_ID
```

또는 Google Cloud Console에서:
1. **APIs & Services** → **Library**
2. "Generative Language API" 검색
3. **Enable** 클릭

### 3. 서비스 계정 생성

```bash
# gcloud CLI 사용
gcloud iam service-accounts create gemini-service \
    --display-name="Gemini Service Account" \
    --project=YOUR_PROJECT_ID

# 서비스 계정에 Gemini API 사용 권한 부여
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:gemini-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

또는 Google Cloud Console에서:
1. **IAM & Admin** → **Service Accounts**
2. **Create Service Account** 클릭
3. 이름: `gemini-service`
4. 역할: `AI Platform User` 또는 `Vertex AI User`
5. **Done** 클릭

### 4. 서비스 계정 키 생성

```bash
# gcloud CLI 사용
gcloud iam service-accounts keys create gemini-service-key.json \
    --iam-account=gemini-service@YOUR_PROJECT_ID.iam.gserviceaccount.com \
    --project=YOUR_PROJECT_ID
```

또는 Google Cloud Console에서:
1. 생성한 서비스 계정 클릭
2. **Keys** 탭 → **Add Key** → **Create new key**
3. **JSON** 선택 → **Create**
4. JSON 파일이 자동으로 다운로드됨

### 5. GitHub Secrets 설정

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**

2. 다음 Secrets 추가:

   #### 필수 Secrets
   
   **`GEMINI_SERVICE_ACCOUNT_KEY`**
   - 다운로드한 JSON 파일 전체 내용을 복사
   - GitHub Secret으로 저장
   - 예시:
     ```json
     {
       "type": "service_account",
       "project_id": "my-gemini-project-123456",
       "private_key_id": "...",
       "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
       "client_email": "gemini-service@my-gemini-project-123456.iam.gserviceaccount.com",
       ...
     }
     ```
   
   **`GOOGLE_CLOUD_PROJECT`**
   - 프로젝트 ID 값만 저장
   - 예시: `my-gemini-project-123456`

   #### 선택적 Secrets (OAuth 2.0 실패 시 폴백)
   
   **`GEMINI_API_KEY`** (선택)
   - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급
   - OAuth 2.0 실패 시 API Key로 폴백

   **`DEEPSEEK_API_KEY`** (선택)
   - [DeepSeek Platform](https://platform.deepseek.com)에서 발급
   - Gemini 실패 시 DeepSeek으로 폴백

### 6. 워크플로우 확인

워크플로우는 이미 업데이트되어 있습니다 (`.github/workflows/ai-video-gen.yml`).

다음 환경 변수가 자동으로 설정됩니다:
- `GOOGLE_APPLICATION_CREDENTIALS`: 서비스 계정 키 파일 경로
- `GOOGLE_CLOUD_PROJECT`: 프로젝트 ID
- `USE_GEMINI_OAUTH`: `true` (서비스 계정 키가 있는 경우)

## 🚀 사용 방법

### 워크플로우 실행

1. GitHub 저장소 → **Actions** 탭
2. **Generate AI Video Lecture** 워크플로우 선택
3. **Run workflow** 클릭
4. (선택) 특정 포스트 파일명 입력
5. **Run workflow** 실행

### API 선택 전략

워크플로우는 다음 순서로 API를 선택합니다:

1. **Gemini OAuth 2.0** (서비스 계정 키가 있는 경우) ⭐
2. **Gemini API Key** (OAuth 실패 시)
3. **DeepSeek API** (Gemini 실패 시)

## 🔍 검증

### 로컬 테스트

```bash
# 환경 변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gemini-service-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export USE_GEMINI_OAUTH="true"

# 테스트 실행
python3 scripts/generate_enhanced_audio.py
```

### GitHub Actions 로그 확인

워크플로우 실행 후 로그에서 다음을 확인:

```
🔑 사용 가능한 API:
  ✅ ElevenLabs: 설정됨
  ✅ DeepSeek: 설정됨
  ✅ Gemini (OAuth 2.0): 설정됨 ⭐
    프로젝트 ID: your-project-id

🎯 API 선택 전략:
  ⭐ Gemini OAuth 2.0 우선 (서비스 계정 사용)
```

## 🐛 문제 해결

### OAuth 2.0 인증 실패

**증상:**
```
❌ OAuth 2.0 인증 실패: ...
```

**해결 방법:**
1. 서비스 계정 키 형식 확인 (JSON 전체 내용)
2. 프로젝트 ID 확인 (`GOOGLE_CLOUD_PROJECT`)
3. Gemini API 활성화 확인
4. 서비스 계정 권한 확인 (`roles/aiplatform.user`)

### 폴백 동작 확인

OAuth 2.0 실패 시 자동으로 다음 순서로 폴백:
1. Gemini API Key (설정된 경우)
2. DeepSeek API (설정된 경우)

### 비용 모니터링

워크플로우 실행 후 로그에서 사용량 통계 확인:

```
📊 API 사용량 통계
============================================================

GEMINI:
  요청 수: 1
  총 토큰: 1500
  Prompt 토큰: 1000
  Completion 토큰: 500
  에러 수: 0
```

## 💡 최적화 팁

### 1. 캐싱 활용

동일한 포스트는 캐시에서 재사용:
- 캐시 유효기간: 7일
- 비용 절감 효과: 동일 포스트 재처리 시 API 호출 없음

### 2. API 선택 전략

환경 변수로 전략 조정:

```yaml
env:
  PREFER_GEMINI: 'true'  # Gemini 우선
  USE_GEMINI_FOR_SCRIPT: 'true'  # Gemini로 대본 생성
  USE_DEEPSEEK_FOR_SCRIPT: 'true'  # DeepSeek 폴백
  USE_GEMINI_FOR_IMPROVEMENT: 'true'  # Gemini로 개선
```

### 3. 비용 관리

- OAuth 2.0 사용 시 비용 절감 가능
- 캐싱으로 중복 호출 방지
- 사용량 통계로 모니터링

## 📚 관련 문서

- [Gemini OAuth 2.0 통합 가이드](../scripts/GEMINI_OAUTH_INTEGRATION.md)
- [개선된 오디오 생성 가이드](../scripts/README_ENHANCED_AUDIO.md)
- [보이스 생성 통합 상태 점검](../VOICE_GENERATION_AUDIT.md)
- [GitHub Secrets 관리 가이드](./SECRETS_MANAGEMENT.md)

## ⚠️ 보안 주의사항

1. **서비스 계정 키 보호**
   - 절대 Git에 커밋하지 않음
   - GitHub Secrets에만 저장
   - 정기적 로테이션 (90일마다 권장)

2. **최소 권한 원칙**
   - 서비스 계정에 필요한 최소 권한만 부여
   - `roles/aiplatform.user` 권한만 사용

3. **감사 로그**
   - Google Cloud Console에서 API 사용 로그 확인
   - 비정상 사용 패턴 모니터링

---

**마지막 업데이트**: 2026-01-10
