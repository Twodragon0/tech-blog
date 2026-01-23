# DeepSeek API 최적화 가이드

## 개요

챗봇 API 엔드포인트(`/api/chat`)가 비용 최적화, 효율성, 보안성 측면에서 최적화되었습니다.

## 주요 개선 사항

### 1. 비용 최적화

#### Context Caching 활용
- **자동 캐싱**: DeepSeek API는 자동으로 Context Caching을 수행합니다.
- **시스템 메시지 재사용**: 일관된 시스템 메시지를 사용하여 캐시 히트율 향상
- **대화 컨텍스트 유지**: 최근 10개 메시지를 유지하여 캐시 효율성 향상
- **캐시 히트율 모니터링**: `prompt_cache_hit_tokens`, `prompt_cache_miss_tokens` 추적
- **비용 절감**: 캐시 히트 시 최대 90% 비용 절감

#### Off-Peak 시간대 활용
- **할인 시간대**: UTC 16:30-00:30 (한국 시간 기준: 다음날 01:30-09:30)
- **할인율**: DeepSeek-R1 모델 75% 할인, DeepSeek-V3 모델 50% 할인
- **자동 감지**: 서버에서 시간대를 자동으로 감지하여 로깅

#### 토큰 사용량 최적화
- **모니터링**: Prompt tokens, Completion tokens, Cache hit rate 추적
- **응답 품질 균형**: `max_tokens`를 1500으로 증가 (비용 최적화는 Context Caching으로 보완)
- **대화 히스토리 제한**: 최대 10개 메시지 유지 (캐시 효율성 고려)

### 2. 효율성 개선

#### 대화 컨텍스트 유지
- **세션 기반 대화**: 사용자 세션별로 대화 히스토리 유지
- **자동 전송**: 프론트엔드에서 최근 대화 히스토리를 자동으로 전송
- **Context Caching 활용**: 이전 대화를 재사용하여 응답 시간 단축

#### 응답 시간 최적화
- **타임아웃 설정**: Pro 플랜 55초, Hobby 플랜 9초
- **에러 처리**: 타임아웃, 네트워크 오류 등 다양한 에러 상황 처리
- **로깅**: 실행 시간 및 토큰 사용량 모니터링

### 3. 보안성 강화

#### 입력 검증 강화
- **위험 패턴 감지**: XSS, JavaScript injection, CSS injection 등 다양한 공격 패턴 감지
- **대화 히스토리 검증**: 전송된 대화 히스토리도 검증 및 정제
- **길이 제한**: 메시지 최소/최대 길이 검증

#### Rate Limiting 개선
- **세션 기반 제한**: 세션당 1분에 최대 15개 요청 (비용 최적화를 위해 증가)
- **메모리 관리**: 오래된 레코드 자동 정리
- **익명 사용자 처리**: 세션 ID가 없는 경우에도 제한 적용

#### XSS 방지 강화
- **입력 정제**: HTML 태그, JavaScript, 위험한 패턴 제거
- **응답 정제**: AI 응답도 동일한 정제 과정 적용
- **제어 문자 제거**: 보안 위험을 줄이기 위한 추가 필터링

## 사용 방법

### API 요청 형식

```json
{
  "message": "질문 내용",
  "sessionId": "세션 ID (선택사항)",
  "conversationHistory": [
    {"role": "user", "content": "이전 질문"},
    {"role": "assistant", "content": "이전 답변"}
  ]
}
```

### 환경 변수 설정

```bash
# 필수
DEEPSEEK_API_KEY=sk-your-api-key

# 선택 (기본값: deepseek-chat)
DEEPSEEK_MODEL=deepseek-chat  # 또는 deepseek-v3
```

### 모델 선택

- **deepseek-chat**: 일반 작업용 (기본값, 비용 효율적)
- **deepseek-v3**: 고급 작업용 (더 높은 성능, 비용 증가)

## 비용 모니터링

### 개발 환경에서 모니터링

개발 환경에서는 API 응답에 사용량 정보가 포함됩니다:

```json
{
  "response": "답변 내용",
  "sessionId": "세션 ID",
  "provider": "deepseek",
  "usage": {
    "promptTokens": 150,
    "completionTokens": 200,
    "cacheHitTokens": 100,
    "cacheMissTokens": 50,
    "cacheHitRate": "66.7%",
    "isOffPeak": true
  }
}
```

### 프로덕션 로깅

프로덕션 환경에서는 서버 로그에서 다음 정보를 확인할 수 있습니다:

```
[Chat API] Execution time: 2345ms
[Chat API] Token usage - Prompt: 150 (Cache hit: 100, Miss: 50), Completion: 200, Cache hit rate: 66.7%
[Chat API] Off-peak hours (UTC 18:00) - 50-75% discount applied
```

## 최적화 팁

### 1. Context Caching 최대화

- **일관된 시스템 메시지 사용**: 시스템 메시지를 변경하지 않으면 캐시 히트율 향상
- **대화 컨텍스트 유지**: 이전 대화를 유지하면 캐시 효율성 향상
- **반복적인 질문 패턴**: 유사한 질문 패턴을 사용하면 캐시 활용도 증가

### 2. Off-Peak 시간대 활용

- **비급한 작업**: Off-peak 시간대에 처리하면 비용 절감
- **배치 작업**: 여러 요청을 Off-peak 시간대에 모아서 처리

### 3. 모델 선택

- **일반 질문**: `deepseek-chat` 사용 (비용 효율적)
- **복잡한 작업**: `deepseek-v3` 사용 (더 높은 성능)

## 보안 고려사항

### API 키 보안

- **환경 변수 사용**: API 키는 절대 코드에 하드코딩하지 않음
- **Vercel Secrets**: Vercel 환경 변수에 안전하게 저장
- **로깅 제한**: 프로덕션에서는 민감 정보 로깅 최소화

### 입력 검증

- **서버 측 검증**: 클라이언트 검증만으로는 충분하지 않음
- **XSS 방지**: 모든 입력과 출력을 정제
- **Rate Limiting**: 무차별 대입 공격 방지

### CORS 설정

- **허용된 Origin만**: 실제 도메인만 허용
- **개발 환경**: 로컬 개발 시에만 localhost 허용

## 성능 지표

### 예상 성능

- **평균 응답 시간**: 2-5초 (DeepSeek API 응답 시간에 따라 다름)
- **캐시 히트율**: 50-80% (대화 컨텍스트 유지 시)
- **비용 절감**: 캐시 히트 시 최대 90% 절감

### 모니터링

- **실행 시간**: 5초 이상인 경우 로깅
- **토큰 사용량**: 개발 환경에서 상세 로깅
- **에러율**: 다양한 에러 상황 추적

## 문제 해결

### 캐시 히트율이 낮은 경우

1. **시스템 메시지 확인**: 일관된 시스템 메시지 사용 확인
2. **대화 컨텍스트 확인**: 이전 대화가 올바르게 전송되는지 확인
3. **질문 패턴 확인**: 완전히 다른 질문만 하면 캐시 효율성 감소

### 비용이 높은 경우

1. **Off-peak 시간대 활용**: 가능한 경우 Off-peak 시간대에 요청
2. **모델 선택**: `deepseek-chat` 사용 (기본값)
3. **토큰 사용량 확인**: 개발 환경에서 사용량 모니터링

### 보안 문제

1. **입력 검증**: 위험한 패턴이 감지되면 요청 거부
2. **Rate Limiting**: 과도한 요청은 자동으로 제한
3. **CORS 설정**: 허용되지 않은 Origin에서의 요청 거부

## 참고 자료

- [DeepSeek API 문서](https://api-docs.deepseek.com/)
- [DeepSeek Context Caching 가이드](https://api-docs.deepseek.com/guides/kv_cache)
- [DeepSeek 가격 정보](https://platform.deepseek.com/pricing)
