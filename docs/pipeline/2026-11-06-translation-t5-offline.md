# T5: 선택적 발행 연결의 오프라인 검증

상태: 오프라인 구현. API 호출, 유료 제공자 선택, Secret 등록, 원격 게시, 일정 변경은 수행하지 않았다.

## 변경 전 계획과 연결 지점

먼저 새 `test_translation_publication.py`를 작성하고 구현 모듈이 없어 수집에 실패하는 것을 확인했다. 이후 기존 발행기의 `main(*, translation=None)`에 선택적 Python 의존성을 추가했다. 기존 `main()`과 CLI 기본 동작은 유지하며 번역을 켜는 새 CLI 옵션이나 기본 transport는 만들지 않았다.

호출자는 `PublicationTranslation`에 T4 `execute_translation`을 묶은 executor와 기사 수 상한, 별도의 비공개 rejection 디렉터리를 명시해야 한다. 실제 제공자 연결은 승인된 후속 작업이며 이 문서는 이를 활성화하지 않는다.

## 입력과 비용 경계

- 초기 필터와 기존 중복 게시 검사를 통과한 뒤, **본문 렌더러가 받을 categorized 후보 전체**를 preflight한다. security 모드는 전체, tech-blog 모드는 기존 tech/devops/ai/cloud 범위만 처리한다.
- selected 15개만 번역하고 categorized 30개를 영어 상태로 남기는 부분 번역을 허용하지 않는다.
- 고유 기사 상한은 필수 설정이며 1~50개다. 전체 후보의 identity·timestamp·URL·중복 일관성과 상한을 검사한 **후** 첫 executor를 호출한다. 446개의 서로 다른 후보라면 상한에서 실패하며 무제한 번역하지 않는다.
- URL 또는 안정적인 source ID가 같으면 T1의 모든 원문 사실도 같아야 한다. 다른 원문이나 ID가 같은 URL로 들어오는 충돌은 재사용하지 않고 실패한다. 일치하는 중복은 첫 카테고리에 한 번만 유지한다.
- T1 요청 ID는 기존 source ID(없으면 URL)의 SHA-256이다. 입력 id, url, published_date 등 기존 메타데이터는 바꾸지 않는다. 발행 시각을 원문 발행 시각으로 대신하지 않는다.
- topic/filename 추출은 **원본 제목**을 대상으로 유지한다. 한국어 번역 때문에 slug가 바뀌지 않는다.

## 번역 결과와 렌더링

executor가 `TranslationResult(status="validated")`를 반환했다는 사실만 신뢰하지 않는다. 기사 ID, canonical URL, 한국어와 보호 사실을 T1 `validate_result`로 다시 검사한다. 렌더러가 요약의 보호 사실을 자르지 않도록 검증된 요약이 200자를 넘으면 실패한다. 검증된 제목·요약을 복제 item에 넣고 원문 snapshot은 `translation_source`, 편집 의견은 별도 `translation_editorial_note`에 보존한다. 입력 feed는 수정하지 않는다.

검증 후 item은 `TranslatedArticle` dict subclass로 전달한다. 이 타입의 frozen 결과만 `_korean_brief_summary`가 직접 읽는다. 이는 이전 전역 요약 캐시나 heuristic 재요약이 검증된 사실을 덮어쓰지 않도록 하는 경계다. 일반 JSON dict에 `translation_validated=true` 등의 필드를 넣어도 해당 타입을 위조할 수 없다. 기존 일반 item의 캐시 동작은 바꾸지 않았다.

선택적 연결은 `--use-ai none`을 요구한다. 기존 강화 경로가 Gemini/DeepSeek 등의 추가 호출 또는 fallback을 실행하게 두지 않는다. 기존 날짜·통계·문장·품질 검사와 SVG 생성은 계속 수행한다. 검사 기준을 낮추거나 테스트에서 콘텐츠 게이트를 통과하도록 가짜 결과로 바꾸지 않았다.

## 실패와 dry-run

입력·기사 수·키·제공자·출력 검증 실패 시 부분 번역 batch를 반환하지 않는다. 명시적 rejection 디렉터리에 실패 상태와 마스킹한 입력 whitelist JSON을 보존한다. 원문 길이와 보존 기사 수를 제한하고 URL의 인증 정보·query·fragment는 진단 파일에서 제거한다. 알려진 API key 패턴에는 기존 마스킹 유틸리티를 적용한다. 디렉터리 0700, 파일 0600으로 만들며 provider 예외 원문·headers·credentials는 저장하지 않는다. 따라서 이 파일은 byte-identical 원문 백업이 아니라 검수용 안전한 재현 자료다.

발행 manifest는 `failed/translation_failed`를 기록하고 종료 코드 1로 멈춘다. 이 시점에는 글·이미지·게시 URL tracker를 쓰지 않는다. 기존 수동 글도 유지한다. artifact 저장이 실패한 경우에도 성공으로 전환하지 않는다.

기존 manifest writer는 created/skipped/dry_run만 허용했으므로 이번 연결에 필요한 `failed` 상태를 추가했다. resolver는 failed를 명시적 오류로 처리하며 post_created를 켜지 않는다. 기존 skip과 created 처리는 그대로다. inline gate registry는 수정하지 않았다. 새 경계는 파일 생성 전 opt-in 입력/preflight 오류이며 기존 콘텐츠 검사와 별개다.

dry-run은 번역과 렌더링·사전 검사를 실행하고 dry_run manifest를 기록하지만 글·이미지·tracker를 쓰지 않는다. 실제 transport를 주입한 dry-run은 제공자 과금이 가능하므로 "무과금 모드"가 아니다. 이번 테스트는 fake transport뿐이다.

## 관측한 검증

- 실제 `publisher.main(translation=...)`에서 T4와 fake OpenAI transport를 연결해 임시 디렉터리에 한국어 글과 SVG를 생성했다. raster 변환/자동 커밋만 mock했다.
- selected 1개·categorized 5개 조건에서 5개를 번역하고 실제 본문에 나타난 source card 3개만 게시 tracker에 전달했다. 나머지 후보 2개는 tracker에 넣지 않았다. 본문 source URL과 통계 일관성을 확인했다. 원문 토픽 추출, 기존 품질 점수 88/100(목표 80), 정상 created manifest를 확인했다.
- 실패·충돌·상한·원문 불변·기존 파일 보존·failed manifest·dry-run·기본 미연결 동작·stale cache·위조 dict·진단 비밀 마스킹을 검증했다.
- 실제 공개 API, Secret, 발행 workflow, GitHub push, 배포, RSS 갱신은 검증하지 않았다.

## 후속 경계

T1 검사는 어휘적 보존이며 의미적 번역 충실도와 심각도 추론의 정확성을 보장하지 않는다. 기존 후속 콘텐츠 검사가 결과를 거부하면 그 실패를 유지해야 한다. 전체 배치 시간·일일 비용·T6 Secret/운영 transport 및 T7 원격 증거는 별도다.


### source-card 기반 tracker와 tech-blog 제한

선택적 연결에서는 기존 카드 검사기의 `CARD_RE`를 재사용해 생성된 본문의 quoted URL을 읽고 HTML entity를 해제한다. 검증된 후보와 연결되는 실제 source card만 tracker에 기록하며 중복 카드는 한 번만 기록한다. URL이 없거나 알 수 없거나 source card가 한 개도 없으면 글을 쓰기 전에 failed manifest와 검수 자료를 남기고 중단한다. 기본 미연결 경로는 여전히 기존 selected 기반 추적을 사용한다.

현재 tech-blog 렌더러의 일부 AI/ML·DevOps·Open Source 경로는 source card가 있다는 주석과 달리 제목·요약만 출력한다. 이 문제를 이번 작업에서 넓혀 수정하지 않았다. 해당 경로는 선택적 T5 source-card 검사를 통과하지 못하므로 실패 상태를 유지한다. tech-blog 모드 전체의 운영 준비 완료를 주장하지 않는다.

### 최종 로컬 검증

T5 테스트 23개, manifest/registry 및 T1·T2·T4를 합친 집중 검사 206개 통과. 변경 Python 6개 파일의 Ruff·format check·Mypy를 통과했다. 실제 commit hook의 전체 직렬 pytest 결과는 작업 완료 보고에 별도로 기록한다. 이번 단계는 로컬 커밋까지이며 push·제공자 호출·원격 발행은 하지 않는다.
