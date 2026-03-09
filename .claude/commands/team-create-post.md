# Team: 블로그 포스트 생성 (Multi-Agent)

멀티 에이전트 팀을 활용하여 고품질 블로그 포스트를 생성합니다.

## 팀 구성

| Agent | Role | Model |
|-------|------|-------|
| researcher | 주제 조사, 최신 트렌드 수집 | sonnet |
| writer | 포스트 초안 작성 | haiku |
| executor | 파일 생성, front matter 구성 | sonnet |
| qa-tester | 최종 검증 (링크, 이미지, 보안) | sonnet |

## 실행 워크플로우

### Phase 1: 사용자 입력 수집
AskUserQuestion으로 다음 정보를 수집:
- 포스트 주제/제목 (Korean)
- 카테고리: security, devsecops, devops, cloud, kubernetes, finops, incident
- 태그 (콤마 구분)
- 깊이 수준: 개요(overview), 심화(deep-dive), 실습(hands-on)

### Phase 2: 조사 (researcher agent, 병렬)
Task(subagent_type="oh-my-claudecode:researcher", model="sonnet") 실행:
- 주제 관련 최신 자료 조사 (WebSearch)
- 기존 블로그 포스트와의 중복 확인
- 핵심 포인트 5-10개 도출
- 참고 자료 목록 작성

동시에 Task(subagent_type="oh-my-claudecode:explore", model="haiku") 실행:
- _posts/ 디렉토리에서 관련 기존 포스트 탐색
- 기존 포스트의 스타일/구조 패턴 분석
- 카테고리별 포스트 수 확인

### Phase 3: 초안 작성 (writer agent)
Task(subagent_type="oh-my-claudecode:writer", model="haiku") 실행:
- Phase 2 조사 결과를 기반으로 포스트 초안 작성
- 기존 포스트 스타일에 맞춰 작성
- 코드 블록에 언어 태그 포함
- 10줄 이상 코드는 설명으로 대체

### Phase 4: 파일 생성 (executor agent)
Task(subagent_type="oh-my-claudecode:executor", model="sonnet") 실행:
- 파일명 생성: YYYY-MM-DD-English_Title.md
- Front matter 구성 (CLAUDE.md 규칙 준수)
- _posts/ 디렉토리에 파일 작성
- 이미지 경로 설정: /assets/images/YYYY-MM-DD-English_Title.svg

### Phase 5: 검증 (qa-tester agent)
Task(subagent_type="oh-my-claudecode:qa-tester", model="sonnet") 실행:
- python3 scripts/check_posts.py 로 포스트 검증
- Front matter 완전성 확인
- 파일명 규칙 준수 확인
- 보안 검증 (하드코딩된 비밀 없음)
- 코드 블록 언어 태그 확인

### Phase 6: 결과 보고
사용자에게 다음 정보 제공:
- 생성된 파일 경로
- 포스트 요약 (제목, 카테고리, 태그)
- 검증 결과
- 다음 단계 안내:
  * `python3 scripts/generate_post_images.py --post <filename>` 로 이미지 생성
  * `/validate-post` 로 추가 검증
  * 내용 검토 후 커밋

## 비용 최적화
- researcher만 sonnet 사용 (WebSearch 필요)
- writer는 haiku (초안 작성은 가벼운 모델로 충분)
- executor는 sonnet (파일 작업 정확성)
- qa-tester는 sonnet (검증 정확성)

## 참고
- CLAUDE.md의 Post Writing Rules 준수
- FAQ 섹션 절대 추가하지 않음
- 파일명/이미지명 영문만 사용
