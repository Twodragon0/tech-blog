# T2 제공자 어댑터 - 오프라인 구현

## 범위

translation_provider.py는 명시적으로 선택한 Claude 또는 OpenAI, 모델, credential mapping, transport를 받아 요청을 구성한다. transport에는 기본값이 없고 네트워크 클라이언트를 만들지 않는다. 기존 enhancer·발행 경로·자동 fallback은 수정하지 않았다.

OpenAI는 Chat Completions의 JSON mode 요청을, Claude는 Messages 요청을 구성한다. 응답은 단일 정상 종료 텍스트와 JSON 객체만 허용한 뒤 T1의 ID·canonical URL·한국어·숫자·CVE·보호 용어 검사를 거친다. 원문은 별도 JSON source_data로 직렬화하며 지시문처럼 보이는 문자열도 실행하지 않는다. 이것은 모델 수준의 전체 프롬프트 주입 방어를 보장하지 않는다.

## 오류 계약

| 분류 | 예시 | retryable |
|---|---|---|
| authentication | 401, 403 | false |
| request | 400 등 기타 비정상 상태 | false |
| rate_limit | 429 | true |
| upstream | 408, 5xx | true |
| transport | builtin 및 requests의 timeout/connection 오류 | true |
| transport | 그 밖의 전송 예외 | false |
| output | 잘못된 envelope·종료 이유·JSON·T1 계약 위반 | false |

retryable은 분류 정보이며 실제 재시도는 하지 않는다. 캐시·예산·backoff는 T4, 발행 연결은 T5 이후 범위다. 오류 문자열과 request/response repr에 키·원문·응답 본문을 노출하지 않는다.

## 검증

가짜 transport와 네트워크 차단 fixture만 사용한다. 제공자별 정상 요청·단일 호출, 키 누락 전송 차단, 401/403/429/5xx, malformed JSON·추가 필드·숫자/URL/ID 변조, 잘린 응답, 안전한 오류, requests 및 builtin 예외와 잘못된 timeout 입력을 검사했다. 관련 제공자·계약 테스트 108개, Ruff check·format, Mypy가 통과했다.

실제 API 인증, 모델 가용성, JSON mode 지원, 의미적 번역 정확성은 검증하지 않았다. 새 API 키 등록이나 유료 호출은 수행하지 않았다.

## 형식 근거

- https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://platform.claude.com/docs/en/api/messages/create
- https://platform.claude.com/docs/en/api/versioning
