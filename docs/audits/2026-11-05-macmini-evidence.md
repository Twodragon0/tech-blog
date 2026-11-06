# Mac mini 읽기 전용 증거 수집

수집일: 2026-11-05 KST. 이 기록은 순간 상태이며 재부팅이나 PR 생성 실험을 수행한 결과가 아니다.

| 확인 | 관측 | 입증하지 못하는 것 |
|---|---|---|
| 하드웨어 식별 | hw.model=Mac16,10 | 모델 추론 성능과 소비전력 |
| pmset | sleep=0, womp=1, autorestart=1 | 전원 장애 후 무인 복구 |
| FileVault | On | 콜드 부팅 무인 잠금 해제 |
| supportsauthrestart | true | 실제 인증 재시작 성공 |
| last reboot | 11월 4일 23:22 부팅 기록 | 재부팅 주체와 잠금 해제 방식 |
| uptime | 수집 당시 약 11시간 20분 | 24/7 가용성 SLA |
| launchctl | Paseo, ytdl-webhook PID 존재 | 앱 health 또는 재부팅 직후 자동 복구 |
| queue/watchdog | PID 없이 최근 종료 코드 0 | 영구 실행 여부, 큐 처리 성공 |
| worktree | 현재 main 체크아웃 1개 | 과거 worktree 실행 이력 |
| PR 조회 | 최근 PR 15개, Paseo 검색 0개, agent 검색 20개 조회 | Paseo를 통한 생성과 실행 주체의 인과관계 |

PR 조회는 `gh pr list --repo Twodragon0/tech-blog --state all`에 제한과 검색 조건을 붙여 수행했다. agent 검색은 본문 등에 매칭되어 Dependabot PR도 포함한다. 관련 PR이 존재하지 않는다는 결론도, Paseo 자동화 실증이 완료됐다는 결론도 내릴 수 없다. 실제 PR URL과 Paseo 세션 ID, worktree 경로, head SHA를 연결하는 추가 증거가 필요하다.

## core.bare 임시 진단 종료 결정

- `git config --get core.bare` 결과 false.
- 훅이 지정한 `~/.claude/core-bare-watch.log`와 `.state`가 발견되지 않았다. 전이 0건이 입증된 것은 아니다.
- 과거 원인 후보와 관찰 목적은 삭제 전 스크립트 및 Git 이력에 남아 있다.
- 관찰 기한이 지난 상태에서 근거 없이 계속 갱신하는 대신 관찰을 종료한다. `.claude/hooks/core-bare-watch.sh`, settings 연결, 진단 만료 레지스트리 항목을 함께 제거했다.
- Git 구성은 변경하지 않았다. 이는 원인 해결 선언이 아니다. 증상이 재현되면 해당 시점 config와 실행 주체를 확보한 뒤 기한을 가진 관찰을 다시 설계한다.

## 추가 실증이 필요한 항목

1. 동일 작업의 Paseo 세션, worktree, PR, SHA, CI 로그 연결.
2. 현장 복구 수단을 확보한 유지보수 창에서 인증 재시작 후 원격 접속과 앱 health 확인.
3. 전원 복귀 시험은 정상 재시작과 따로 검증.

자격 증명, 상세 내부 네트워크 주소, 원문 세션 로그는 이 문서에 저장하지 않았다.

## 2026-11-06 추가 확인

Paseo 저장 세션 `35177e97-3930-4687-874b-5c2f60214210`과 검토 세션 `65210c18-6b1b-4cb4-be2a-e20c995ce17d`의 cwd가 `~/.paseo/worktrees/2vejhm97/claudesec-ci-guards`로 일치했다. 해당 디렉터리의 브랜치는 `test/ci-regression-guards`, HEAD는 `5b2620b3c6e59ddd56a7aae6a0ec26dd5ce72062`다. GitHub PR [claudesec #596](https://github.com/Twodragon0/claudesec/pull/596)의 headRefName과 headRefOid가 모두 일치했다.

따라서 **저장 세션 → 작업 디렉터리 → 브랜치/SHA → PR**의 연결은 확인됐다. 다만 저장 메타데이터와 현재 Git 상태의 대조이므로 어느 세션의 어느 명령이 PR을 생성했는지까지 입증하는 실행 추적은 아니다. tech-blog 저장소의 자동 PR 실증으로 일반화하지 않는다.

`Mac mini Worktree Test` 세션 메타데이터는 남아 있지만 해당 디렉터리는 존재하지 않았다. PR #591은 확인되나 현재 파일 기반 SHA 대조를 수행할 수 없으므로 같은 수준의 연결 증거로 채택하지 않았다. 다른 저장소의 코드나 자격 증명은 복사하지 않았다.

## 2026-11-06 새로 재현한 Git 환경 누출

linked worktree에서 pre-commit이 pytest를 실행할 때 Git의 hook-local 환경을 그대로 상속했다. 테스트의 fixture Git 명령이 실제 worktree를 대상으로 동작해 임시 `seed` 커밋 두 개(`de431bda`, `7176fdb7`)와 합성 인덱스 경로가 나타났고, 공유 core.bare도 true로 바뀌었다. main의 HEAD는 유지됐다. 관찰 후 core.bare=false로 복원하고, 증거 브랜치를 보존한 뒤 작업 브랜치는 mixed reset으로 복구했다. 생성된 글과 데이터는 삭제하지 않았다.

이는 현재 경로에서 재현한 원인이다. 9월의 원래 사건도 같은 원인이었다고 확정하지 않는다. 단순 관찰 훅을 다시 설치하는 대신 pytest 실행 시 Git-local 환경을 격리하는 원인 수정을 진행한다.
