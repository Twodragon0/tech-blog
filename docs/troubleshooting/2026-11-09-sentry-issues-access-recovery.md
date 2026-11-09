# Sentry issues API 403: 확인 범위와 복구 조건

## 관측과 미확인 사항

2026-11-09 최초 점검의 [Sentry Healthcheck 실행 42598432118](https://github.com/Twodragon0/tech-blog/actions/runs/42598432118)은
project API 검사를 통과한 뒤 issues API에서 HTTP 403을 기록했다.
job 자체는 success였지만 CSP 보고서는 측정하지 못했다고 명시했다.
[운영 이슈 #804](https://github.com/Twodragon0/tech-blog/issues/804)의 Sentry 항목은
해결 완료로 닫을 수 없다.

이어 기존 workflow를 읽기 전용으로 실행한
[실행 42623064807](https://github.com/Twodragon0/tech-blog/actions/runs/42623064807)에서도
2026-11-09 13:10 UTC에 issues API HTTP 403과 CSP **MEASURED NOTHING**이 재현됐다.
이 실행도 기존 코드에서 success로 끝났으므로, 현재 접근 복구의 증거로 쓰지 않는다.
아래의 수정 코드는 이 실행에 아직 반영되지 않았다.

GitHub Secret 이름 메타데이터에서 `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT`는
존재하며 마지막 변경 시점은 2026-01-11이다. 이는 값·유효 범위·만료·권한의 증거가 아니다.
점검 환경의 세 환경 변수는 모두 비어 있어 같은 토큰으로 실시간 재검증할 수 없었다.
Secret 값, 인증 파일, 실제 조직·프로젝트 식별자는 읽거나 문서에 복사하지 않았다.
토큰 재발급·범위 확대·GitHub Secret 변경도 수행하지 않았다.

403만으로 특정 scope가 빠졌다고 단정하지 않는다. 필요한 이벤트 읽기 권한,
토큰 소유자의 조직·팀·프로젝트 접근, 토큰 유형과 대상 범위를 함께 확인해야 한다.
project API 성공은 해당 프로젝트의 issues API 권한까지 증명하지 않는다.

## 공식 API 계약

[Organization Issues API](https://docs.sentry.io/api/events/list-an-organizations-issues/)는
`project` 필터에 **ID와 slug를 모두 허용**한다. 따라서 현재의 slug 사용을
403의 원인으로 지목하거나 숫자 ID로 바꾸면 해결된다고 주장하지 않는다.
필터를 생략하거나 `-1`을 지정하면 접근 가능한 모든 프로젝트를 조회하므로
기존 선택 프로젝트 필터를 유지한다.

같은 문서는 `event:read`, `event:write`, `event:admin` 중 하나를 요구한다.
읽기 전용 모니터링에는 `event:read`가 최소 필요 권한이며, 쓰기·관리 권한을
추가할 이유는 없다. 검색은 `query=is:unresolved`를 명시한다.
[Project Issues API](https://docs.sentry.io/api/events/list-a-projects-issues/)는 deprecated이므로
이를 권한 오류 우회 경로로 추가하지 않았다.

## 코드에서 복구한 부분

- Ops 쿼리는 선택 프로젝트와 `query=is:unresolved`를 명시하고 최대 100건을 요청한다.
  이 숫자는 첫 페이지 관측값이며 전체 미해결 이슈 수를 보증하지 않는다.
- HTTP 오류·깨진 JSON·이슈 목록이 아닌 응답은 P1·미측정으로 판정한다.
  인증 응답 원문·토큰·설정 식별자는 오류 요약에 넣지 않는다.
- Healthcheck는 issues API가 200이며 JSON object의 배열을 반환해야 성공한다.
  401·403이나 200의 잘못된 응답은 job을 실패시키며 `issues_ok=true`를 내보내지 않는다.
- CSP 볼륨 보조 보고서는 기존의 미측정 표시를 유지한다. project API를 확인했다면
  issues 접근 검사 실패 뒤에도 진단 보고서를 실행하지만 실패한 job을 성공으로 바꾸지 않는다.
- fake HTTP·curl fixture만으로 성공·403·응답 오류를 검증했다.
  이 오프라인 통과를 실제 운영 토큰의 복구 증거로 계산하지 않는다.

## 실제 접근 복구 절차

1. Sentry 관리 화면에서 현재 모니터링 토큰의 유형·소유자·만료 상태를 확인한다.
   토큰 문자열을 채팅·로그·이슈에 붙이지 않는다.
2. 읽기 전용 `event:read`와 의도한 조직·팀·프로젝트 접근이 있는지 확인한다.
   GitHub의 org/project 설정이 블로그용 대상과 일치하는지도 관리 화면에서 대조한다.
   현재 증거만으로 어떤 항목이 빠졌는지는 미확정이다.
3. 기존 권한이 충분하다면 재발급 전에 대상·역할 불일치를 수정할 방안을 검토한다.
   권한·토큰·Secret 변경이 필요하면 대상과 최소 변경 범위를 명시해 별도 승인 후 수행한다.
4. 코드 병합 후 기본 브랜치에서 `Sentry Healthcheck`를 실행한다.
   project API 200, issues API 200·배열 응답, `issues_ok=true`를 모두 확인한다.
   `limit=1`의 샘플 결과를 전체 이벤트 0건으로 표현하지 않는다.
5. Ops Orchestrator의 multi-agent 점검을 실행해 Sentry의 P1이 없어졌는지 확인한다.
   lint·GitHub Actions·Vercel은 각각 별도 증거로 판정한다. Vercel Secret이 없어 건너뛰었다면
   API 상태를 정상으로 판정하지 않는다.
6. #804의 나머지 미해결 항목까지 검증한 뒤에만 이슈 종료 여부를 결정한다.
   이번 작업에서는 이슈를 닫거나 외부 알림을 전송하지 않았다.

## 실패와 되돌리기

403이 계속되면 API 응답 본문을 공개하지 말고 상태 코드·검사한 endpoint 종류·시각만 기록한다.
검증을 녹색으로 만들기 위해 검사나 선택 프로젝트 필터를 제거하지 않는다.
Secret을 변경한 작업은 승인한 관리자가 이전 유효 버전으로 복원하거나 별도 회전 절차를 따른다.
코드 회귀는 이 변경 커밋을 revert할 수 있지만, 이전 코드가 성공으로 표시했던
403은 여전히 실제 접근 성공을 뜻하지 않으므로 #804를 열린 상태로 유지한다.
