# Sentry 모니터링 전용 자격 전환 런북

최종 점검: 2026-11-12 KST. 이 문서는 전환 준비 절차이며 Secret·권한·운영 변수는 변경하지 않았다.

## 현재 차단 조건

[main Healthcheck 43047061832](https://github.com/Twodragon0/tech-blog/actions/runs/43047061832)은
2026-11-12 00:18 KST(2026-11-11 15:18 UTC)에 project 검사에서 `token_ok=true`를
기록했지만 issues API HTTP 403, `issues_ok=false`로 실패했다.
프로젝트 API 성공은 issues 접근 성공이 아니다.

저장소 메타데이터에는 `SENTRY_MONITOR_AUTH_TOKEN` Secret과 `SENTRY_MONITOR_MODE` 변수가 없다.
현재는 기본 shared 모드이며 기존 공유 자격도 issues API 접근에 실패한다.
이 실행 환경에는 Sentry 전용 도구·브라우저와 로컬 Sentry 환경 자격이 없다.
토큰 원문을 읽지 않았고, 실제 주체·personal/integration 유형·활성/만료 상태·scope 목록·
팀 역할·대상 조직/블로그 프로젝트 접근은 미확인이다.

## 최소 권한과 필요한 메타데이터

- [Project 조회 API](https://docs.sentry.io/api/projects/retrieve-a-project/)의 읽기 scope: `project:read`.
- [Organization Issues API](https://docs.sentry.io/api/events/list-an-organizations-issues/)의 읽기 scope: `event:read`.
- 쓰기·관리·릴리스 권한은 모니터링에 추가하지 않는다.
- 토큰 scope 외에 해당 주체의 의도한 조직·팀·블로그 프로젝트 접근도 확인한다.
  scope와 쿼리의 프로젝트 필터만으로 주체의 프로젝트 격리가 보장되지는 않는다.

전환 담당자는 토큰 문자열을 제외한 다음 메타데이터를 확인해야 한다:
주체 식별, 토큰 유형, 활성/만료 상태, scope 이름 목록, 전용 자격 여부,
조직·팀 역할과 대상 프로젝트 접근. 기존 공유 토큰의 실제 메타데이터가 확인되기 전에는
403의 원인을 특정 scope 누락으로 단정하지 않는다.

## 전환 순서

1. 승인된 담당자가 위 메타데이터와 읽기 권한을 확인하고 전용 자격을 준비한다.
2. 전용 자격을 Actions Secret `SENTRY_MONITOR_AUTH_TOKEN`에 먼저 등록한다.
   토큰을 명령 인수·로그·문서·채팅에 복사하지 않는다.
   기존 `SENTRY_AUTH_TOKEN`과 릴리스·배포 소비 경로는 유지한다.
3. 동시 모니터링 실행을 식별한 뒤 Actions 변수 `SENTRY_MONITOR_MODE=dedicated`로 전환한다.
   기존 실행은 시작 시점의 설정을 사용할 수 있으므로 새 실행과 구분한다.
4. main의 Sentry Healthcheck를 실행해 project와 issues 두 endpoint의 HTTP 200과
   유효 응답, `issues_ok=true`를 확인한다. `limit=1` 표본을 전체 이슈 수로 표현하지 않는다.
5. Ops와 Production Monitoring에서 Sentry가 실제 측정됐는지 확인한다.
   부분 페이지·401/403·JSON 오류·누락 자격은 정상이나 0건으로 판정하지 않는다.
6. 공유 자격을 사용하는 릴리스·배포 경로가 유지되는지 확인한다.
   운영 접근 증거를 확보하고 [#804](https://github.com/Twodragon0/tech-blog/issues/804)의
   다른 미해결 항목까지 검증한 뒤 종료를 판단한다.

전용 모드의 Secret이 누락되면 shared 자격으로 자동 fallback하지 않고 실패한다.
Secret 등록을 끝내기 전에 전환 변수를 먼저 바꾸지 않는다.

## 실패 시 복구

1. HTTP 상태·endpoint 종류·시각·실행 URL만 기록한다. 응답 원문이나 토큰은 공개하지 않는다.
2. Actions 변수만 `shared`로 되돌리고 새 실행부터 반영되는지 확인한다.
   진행 중인 dedicated 실행은 별도 식별하여 취소 또는 완료 판정한다.
3. shared도 현재 HTTP 403이므로 이 조치는 **구성 복귀이며 정상 복구가 아니다**.
   미측정 경고와 #804를 유지하고 접근 권한 진단을 계속한다.
4. 기존 릴리스 공유 토큰을 회전·삭제하지 않는다. 전용 토큰이 노출됐다면
   전용 토큰만 폐기·재발급하는 승인된 자격 복구 절차를 따른다.
5. 프로젝트 필터 제거·검사 생략·코드 revert로 성공을 만들어 권한 문제를 숨기지 않는다.

오프라인 계약 검사 통과는 운영 자격의 접근 성공을 입증하지 않는다.
