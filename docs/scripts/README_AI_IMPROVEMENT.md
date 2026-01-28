# AI 기반 포스팅 자동 개선 시스템

Claude, Gemini, Cursor를 활용하여 포스팅을 지능적으로 개선하는 시스템입니다.

## 🚀 빠른 시작

### 0. 의존성 설치

```bash
pip3 install -r scripts/requirements.txt
```

또는:

```bash
pip3 install requests certifi
```

### 1. API 키 설정

```bash
# API 키 설정 스크립트 실행
./scripts/setup_ai_keys.sh
```

또는 수동으로 환경 변수 설정:

```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export CLAUDE_API_KEY="your-claude-api-key"
export GEMINI_API_KEY="your-gemini-api-key"

# 환경 변수 로드
source ~/.zshrc  # 또는 source ~/.bashrc
```

### 2. 즉시 실행 (1시간)

```bash
cd ~/Desktop/tech-blog
./scripts/run_ai_improvement.sh
```

### 3. 백그라운드 실행

```bash
cd ~/Desktop/tech-blog
./scripts/start_ai_background.sh
```

### 4. 로그 확인

```bash
tail -f ai_improvement_log.txt
```

## 📋 AI 도구 활용 순서

스크립트는 다음 순서로 AI 도구를 활용합니다:

1. **Claude API** (1순위)
   - 가장 고품질의 콘텐츠 생성
   - Anthropic Claude 3.5 Sonnet 사용
   - API 키 필요: `CLAUDE_API_KEY`

2. **Gemini API** (2순위)
   - Claude 실패 시 사용
   - Google Gemini Pro 사용
   - API 키 필요: `GEMINI_API_KEY`

3. **Cursor 분석** (3순위)
   - API 키 없이도 작동
   - 파일 구조 분석 기반 개선
   - 유사 포스팅 참고

## 🔧 API 키 발급 방법

### Claude API 키

1. [Anthropic Console](https://console.anthropic.com/) 접속
2. 계정 생성 또는 로그인
3. API Keys 메뉴에서 새 키 생성
4. 생성된 키를 환경 변수에 설정

### Gemini API 키

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. Google 계정으로 로그인
3. API 키 생성
4. 생성된 키를 환경 변수에 설정

## 📊 개선 기준

다음 조건을 만족하는 포스팅이 자동으로 개선됩니다:

- 본문이 1500자 미만인 포스팅
- "서론" 또는 "1." 섹션이 없는 포스팅
- 원본 링크만 있고 본문이 거의 없는 포스팅

## ✨ 개선 내용

AI는 다음을 수행합니다:

1. **제목과 excerpt 분석**: 포스팅의 주제와 목적 파악
2. **카테고리별 맞춤 콘텐츠**: 보안/클라우드/DevSecOps별 특화
3. **구조화된 본문 생성**:
   - 서론: 배경 및 목적
   - 개요: 주요 개념
   - 핵심 내용: 상세 설명
   - 실전 적용: 구체적인 설정 방법
   - 모범 사례: 보안 및 운영 모범 사례
   - 문제 해결: 일반적인 문제 및 해결
   - 결론: 요약 및 마무리
4. **코드 예제 포함**: 실용적인 코드 및 설정 예시
5. **보안 강조**: 보안 모범 사례 자동 포함

## 🎯 프롬프트 엔지니어링

AI에게 전달되는 프롬프트는 다음과 같은 요구사항을 포함합니다:

- 실무 중심의 구체적인 내용
- 코드 예제와 설정 예시
- 보안 모범 사례 강조
- 단계별 가이드 제공
- 문제 해결 섹션 포함
- 마크다운 형식
- 한글 작성

## 📝 로그 파일

모든 작업은 `ai_improvement_log.txt`에 기록됩니다:

```bash
# 실시간 로그 확인
tail -f ai_improvement_log.txt

# 최근 50줄 확인
tail -n 50 ai_improvement_log.txt

# 특정 포스팅 검색
grep "포스팅명" ai_improvement_log.txt
```

## ⚙️ 고급 설정

### 실행 시간 변경

`ai_improve_posts.py` 파일에서 `RUN_DURATION` 변수 수정:

```python
RUN_DURATION = 7200  # 2시간으로 변경
```

### API 모델 변경

Claude 모델 변경:

```python
data = {
    "model": "claude-3-opus-20240229",  # 다른 모델로 변경
    ...
}
```

Gemini 모델 변경:

```python
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
```

### Rate Limit 조정

API 호출 간 대기 시간 조정:

```python
time.sleep(2)  # 2초 대기 (필요시 조정)
```

## 🔍 문제 해결

### API 키가 인식되지 않는 경우

```bash
# 환경 변수 확인
echo $CLAUDE_API_KEY
echo $GEMINI_API_KEY

# 수동으로 설정
export CLAUDE_API_KEY="your-key"
export GEMINI_API_KEY="your-key"

# 스크립트 실행
./scripts/run_ai_improvement.sh
```

### API 호출 실패

1. **인터넷 연결 확인**
2. **API 키 유효성 확인**
3. **Rate Limit 확인**: 너무 빠른 호출 시 대기 시간 증가
4. **로그 확인**: `ai_improvement_log.txt`에서 오류 메시지 확인

### 개선 품질이 낮은 경우

1. **프롬프트 수정**: `ai_improve_posts.py`의 프롬프트 개선
2. **템플릿 수정**: 카테고리별 템플릿 함수 수정
3. **수동 검토**: AI 생성 내용은 기본 템플릿이므로 수동 개선 필요할 수 있음

## 📈 성능 최적화

### 병렬 처리

여러 포스팅을 동시에 개선하려면:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(improve_post_with_ai, post) 
              for post in posts_to_improve]
```

### 캐싱

이미 개선된 포스팅은 스킵:

```python
# 개선된 포스팅 마킹
if post_info['body_length'] > 2000:
    continue  # 이미 충분히 긴 포스팅은 스킵
```

## 🔐 보안 주의사항

1. **API 키 보호**: API 키를 Git에 커밋하지 마세요
2. **환경 변수 사용**: 하드코딩 대신 환경 변수 사용
3. **로그 파일**: 로그 파일에 민감한 정보가 포함되지 않도록 주의

## 📚 참고 자료

- [Claude API 문서](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Gemini API 문서](https://ai.google.dev/docs)
- [Cursor 문서](https://cursor.sh/docs)

## 💡 팁

1. **점진적 개선**: 한 번에 모든 포스팅을 개선하지 말고, 소수씩 개선 후 검토
2. **수동 검토**: AI 생성 내용은 항상 수동으로 검토하고 필요시 수정
3. **원본 보존**: 원본 포스트 링크는 항상 유지하여 원본 내용 확인 가능
4. **정기 실행**: cron이나 systemd를 사용하여 정기적으로 실행

## 🎉 완료!

이제 AI 기반 포스팅 개선 시스템이 준비되었습니다. 스크립트를 실행하면 Claude, Gemini, Cursor를 활용하여 포스팅이 지속적으로 개선됩니다!
