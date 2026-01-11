# Gemini CLI 및 OAuth 2.0 통합 가이드

Gemini CLI와 OAuth 2.0을 활용하여 더 안전하고 효율적인 인증 및 사용 방안을 제시합니다.

## 🎯 개요

### 현재 상태
- ✅ Gemini CLI: `improve_post_summary.py`에서 사용 중
- ✅ OAuth 2.0: LinkedIn API에만 사용 중
- ⚠️ Gemini API: API 키 방식만 사용 중

### 개선 방안
1. **Gemini CLI 통합**: 오디오/영상 생성 스크립트에 Gemini CLI 통합
2. **OAuth 2.0 인증**: Google Cloud OAuth 2.0으로 API 키 대체
3. **서비스 계정**: 서버 환경에서 서비스 계정 사용
4. **하이브리드 방식**: CLI와 API를 상황에 맞게 선택

## 🔐 OAuth 2.0 인증 방식

### 방식 1: Google Cloud OAuth 2.0 (권장)

Google Cloud 서비스 계정을 사용하여 OAuth 2.0 인증을 구현합니다.

#### 장점
- ✅ API 키보다 안전 (토큰 자동 갱신)
- ✅ 서비스 계정 기반 (사용자 개입 불필요)
- ✅ 세밀한 권한 관리
- ✅ 감사 로그 지원

#### 설정 방법

1. **Google Cloud 프로젝트 생성**
   ```bash
   # Google Cloud Console에서 프로젝트 생성
   # https://console.cloud.google.com/
   ```

2. **서비스 계정 생성**
   ```bash
   # gcloud CLI 설치 (선택사항)
   gcloud iam service-accounts create gemini-service \
       --display-name="Gemini Service Account"
   
   # 서비스 계정 키 생성
   gcloud iam service-accounts keys create ~/gemini-service-key.json \
       --iam-account=gemini-service@PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Gemini API 활성화**
   ```bash
   gcloud services enable generativelanguage.googleapis.com
   ```

4. **환경 변수 설정**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="~/gemini-service-key.json"
   export GEMINI_PROJECT_ID="your-project-id"
   ```

#### 코드 통합

```python
from google.auth import default
from google.auth.transport.requests import Request
import google.generativeai as genai

def get_gemini_client_with_oauth():
    """OAuth 2.0을 사용하여 Gemini 클라이언트 생성"""
    # 서비스 계정 자격 증명 사용
    credentials, project = default()
    
    # Gemini API 클라이언트 초기화
    genai.configure(credentials=credentials)
    
    return genai.GenerativeModel('gemini-1.5-pro')
```

### 방식 2: 사용자 OAuth 2.0 (개인 사용)

개인 Google 계정으로 OAuth 2.0 인증을 구현합니다.

#### 장점
- ✅ 개인 계정 사용
- ✅ 사용자 동의 기반
- ✅ 토큰 자동 갱신

#### 설정 방법

1. **OAuth 2.0 클라이언트 ID 생성**
   ```bash
   # Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성
   # https://console.cloud.google.com/apis/credentials
   ```

2. **인증 스크립트 생성**
   ```python
   # scripts/gemini_oauth.py
   from google_auth_oauthlib.flow import InstalledAppFlow
   from google.auth.transport.requests import Request
   import pickle
   import os
   
   SCOPES = ['https://www.googleapis.com/auth/generative-language']
   
   def authenticate_gemini():
       """OAuth 2.0 인증 플로우"""
       creds = None
       
       # 기존 토큰 확인
       if os.path.exists('token.pickle'):
           with open('token.pickle', 'rb') as token:
               creds = pickle.load(token)
       
       # 토큰이 없거나 만료된 경우 재인증
       if not creds or not creds.valid:
           if creds and creds.expired and creds.refresh_token:
               creds.refresh(Request())
           else:
               flow = InstalledAppFlow.from_client_secrets_file(
                   'credentials.json', SCOPES)
               creds = flow.run_local_server(port=0)
           
           # 토큰 저장
           with open('token.pickle', 'wb') as token:
               pickle.dump(creds, token)
       
       return creds
   ```

## 🛠️ Gemini CLI 통합

### 현재 사용 중인 곳
- `improve_post_summary.py`: 요약 개선
- `check_images.py`: 이미지 생성 명령어 생성

### 통합 방안

#### 1. 오디오 생성 스크립트에 Gemini CLI 통합

```python
# scripts/generate_enhanced_audio.py에 추가

import subprocess
from pathlib import Path

def generate_script_with_gemini_cli(text: str, post_title: str = "") -> Optional[str]:
    """
    Gemini CLI를 사용하여 대본 생성
    API 호출 대신 CLI 사용 (더 간단하고 안전)
    """
    prompt = f"""다음 보안 기술 블로그 내용을 5분 내외의 자연스러운 강의 대본으로 요약해줘.

제목: {post_title}

블로그 내용:
{text[:50000]}

요구사항:
- 구어체로 작성
- 핵심 내용 명확하게 전달
- 5분 내외 분량 (약 800-1000자)
- 한국어로 작성"""
    
    try:
        log_message("📝 Gemini CLI로 대본 생성 중...")
        
        result = subprocess.run(
            ['gemini', prompt],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT
        )
        
        if result.returncode == 0:
            script = result.stdout.strip()
            
            # 대본 길이 검증
            if len(script) > MAX_SCRIPT_LENGTH:
                log_message(f"⚠️ 생성된 대본이 너무 깁니다 ({len(script)}자). 처음 {MAX_SCRIPT_LENGTH}자만 사용합니다.", "WARNING")
                script = script[:MAX_SCRIPT_LENGTH]
            
            log_message(f"✅ Gemini CLI로 대본 생성 완료 ({len(script)}자)")
            return script
        else:
            log_message(f"❌ Gemini CLI 오류: {result.stderr}", "ERROR")
            return None
            
    except FileNotFoundError:
        log_message("❌ Gemini CLI를 찾을 수 없습니다. 설치: npm install -g @google/gemini-cli", "ERROR")
        return None
    except subprocess.TimeoutExpired:
        log_message("❌ Gemini CLI 타임아웃", "ERROR")
        return None
    except Exception as e:
        log_message(f"❌ Gemini CLI 오류: {str(e)}", "ERROR")
        return None
```

#### 2. 환경 변수로 CLI/API 선택

```python
# CLI 우선, 실패 시 API 사용
USE_GEMINI_CLI = os.getenv("USE_GEMINI_CLI", "true").lower() == "true"

def generate_script_with_gemini(text: str, post_title: str = "") -> Optional[str]:
    """Gemini CLI 또는 API를 사용하여 대본 생성"""
    
    # CLI 우선 사용
    if USE_GEMINI_CLI:
        script = generate_script_with_gemini_cli(text, post_title)
        if script:
            return script
        log_message("⚠️ Gemini CLI 실패, API로 폴백...", "WARNING")
    
    # API 사용 (기존 코드)
    return generate_script_with_gemini_api(text, post_title)
```

## 🔄 하이브리드 전략

### 전략 1: CLI 우선 (권장)

```bash
# 환경 변수 설정
export USE_GEMINI_CLI='true'
export GEMINI_API_KEY='your-key'  # 폴백용
```

**특징:**
- ✅ CLI 우선 사용 (간단하고 안전)
- ✅ API 폴백 (CLI 실패 시)
- ✅ OAuth 2.0 지원 (CLI 설정)

### 전략 2: API 우선

```bash
# 환경 변수 설정
export USE_GEMINI_CLI='false'
export GEMINI_API_KEY='your-key'
```

**특징:**
- ✅ API 직접 사용 (더 세밀한 제어)
- ✅ OAuth 2.0 지원 (서비스 계정)
- ✅ CLI는 보조 도구로 사용

### 전략 3: 작업별 선택

```python
# 대본 생성: API 사용 (고급 기능)
# 요약 개선: CLI 사용 (간단)
# 이미지 생성: CLI 사용 (명령어 생성)

def generate_script(text: str, post_title: str = "") -> Optional[str]:
    # API 사용 (고급 프롬프트, Safety Settings)
    return generate_script_with_gemini_api(text, post_title)

def improve_summary(summary: str) -> Optional[str]:
    # CLI 사용 (간단한 작업)
    return improve_summary_with_gemini_cli(summary)
```

## 📋 구현 단계

### 1단계: Gemini CLI 통합 (즉시 가능)

```bash
# 1. Gemini CLI 설치 확인
npm install -g @google/gemini-cli

# 2. 환경 변수 설정
export USE_GEMINI_CLI='true'
export GEMINI_API_KEY='your-key'  # 폴백용

# 3. 스크립트 실행
python3 scripts/generate_enhanced_audio.py
```

### 2단계: OAuth 2.0 인증 추가 (중기)

```bash
# 1. Google Cloud 프로젝트 생성
# 2. 서비스 계정 생성
# 3. 서비스 계정 키 다운로드
# 4. 환경 변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="~/gemini-service-key.json"

# 5. 스크립트 수정하여 OAuth 2.0 사용
```

### 3단계: 완전 통합 (장기)

```bash
# 모든 Gemini 작업을 OAuth 2.0 + CLI/API 하이브리드로 통합
# - 대본 생성: OAuth 2.0 API
# - 요약 개선: OAuth 2.0 CLI
# - 이미지 생성: OAuth 2.0 CLI
```

## 🔒 보안 고려사항

### API 키 vs OAuth 2.0

| 방식 | 보안 | 관리 | 권장 사용 |
|------|------|------|----------|
| API 키 | ⚠️ 중간 | 간단 | 개발/테스트 |
| OAuth 2.0 | ✅ 높음 | 복잡 | 프로덕션 |

### 권장 사항

1. **개발 환경**: API 키 사용 (간단)
2. **프로덕션**: OAuth 2.0 사용 (안전)
3. **하이브리드**: CLI는 OAuth 2.0, API는 API 키 (유연성)

## 💡 활용 예시

### 예시 1: Gemini CLI로 대본 생성

```bash
# 직접 사용
gemini "다음 블로그 내용을 강의 대본으로 변환해주세요: [내용]"

# 스크립트 통합
python3 scripts/generate_enhanced_audio.py --use-cli
```

### 예시 2: OAuth 2.0으로 안전한 인증

```python
# 서비스 계정 사용
from google.auth import default
import google.generativeai as genai

credentials, project = default()
genai.configure(credentials=credentials)
model = genai.GenerativeModel('gemini-1.5-pro')
```

### 예시 3: 하이브리드 사용

```python
# CLI로 간단한 작업
subprocess.run(['gemini', '요약 개선: ...'])

# API로 고급 작업
response = model.generate_content('고급 프롬프트...')
```

## 🔗 관련 문서

- [Gemini CLI 공식 문서](https://github.com/google-gemini/gemini-cli)
- [Google Cloud OAuth 2.0 가이드](https://cloud.google.com/docs/authentication)
- [Gemini API 문서](https://ai.google.dev/docs)
- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)
- [Gemini AI Pro 활용 가이드](./GEMINI_AI_PRO_GUIDE.md)

## ⚠️ 주의사항

1. **CLI 설치**: `npm install -g @google/gemini-cli` 필요
2. **OAuth 2.0 설정**: Google Cloud 프로젝트 필요
3. **토큰 관리**: OAuth 2.0 토큰은 안전하게 보관
4. **Rate Limit**: CLI와 API 모두 Rate Limit 확인

## 🚀 빠른 시작

### CLI 통합 (5분)

```bash
# 1. Gemini CLI 설치
npm install -g @google/gemini-cli

# 2. API 키 설정 (CLI용)
export GEMINI_API_KEY='your-key'

# 3. 환경 변수 설정
export USE_GEMINI_CLI='true'

# 4. 스크립트 실행
python3 scripts/generate_enhanced_audio.py
```

### OAuth 2.0 통합 (30분)

```bash
# 1. Google Cloud 프로젝트 생성
# 2. 서비스 계정 생성 및 키 다운로드
# 3. 환경 변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="~/gemini-service-key.json"

# 4. 스크립트 수정 (OAuth 2.0 코드 추가)
# 5. 스크립트 실행
python3 scripts/generate_enhanced_audio.py
```

---

**마지막 업데이트**: 2026-01-08
