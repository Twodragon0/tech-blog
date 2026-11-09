# PR·이슈·운영 검증 우선순위 점검 (2026-11-09)

## 범위와 판정 기준

GitHub의 열린 PR 13개, 열린 이슈 3개와 최근 Actions 결과를 조회했다.
중복 #756을 2026-11-09 10:28 UTC에 종료해 열린 PR은 12개로 줄었다.
검토 기준 main은 `786e1ad8`이며, 수치는 조회 시점의 스냅샷이다.
기본 작업 폴더의 기존 미커밋 변경은 보존하고 별도 worktree에서 수정했다.
아래의 병합·재실행 항목은 실행 순서 제안이며, 완료 상태를 뜻하지 않는다.

우선순위는 실제 보안 권고(P1), 검증 결과를 오판하는 경로(P1),
개발·운영 차단(P2), 중복·문서 최신화(P3) 순으로 정했다.
체크가 녹색이어도 감사 자체가 건너뛰어졌거나 권한 때문에 측정하지 못했다면
정상 동작의 증거로 쓰지 않는다.

## P1: Ruby 보안 수정과 감사 신호

### 이슈 #801: addressable 업데이트

- [이슈 #801](https://github.com/Twodragon0/tech-blog/issues/801)의 과거 CI에는
  `addressable 2.9.0` 관련 경고가 있다. [PR #800](https://github.com/Twodragon0/tech-blog/pull/800)은
  csv·sass-embedded 업데이트이므로 이 취약점을 해결하지 않는다.
- 이번 변경은 `Gemfile.lock`의 addressable만 **2.9.0 → 2.9.2**로 갱신했다.
  다른 gem 버전은 변경하지 않았다.
- 최신 로컬 ruby-advisory-db `7e90cbd88d767c9281acefbb8854c80e0cad6060`,
  bundler-audit 0.9.3으로 원본 lockfile을 임시 폴더에서 검사해 **7건**을 재현했다.
  과거 CI 보고 건수와 현재 DB 검사 건수는 별도 관측값이다.
- 수정 lockfile의 `bundle audit check --update`는 **No vulnerabilities found**,
  전체 Jekyll 빌드도 성공했다. 이 결과는 로컬 수정본의 증거다.
  원격 main의 #801을 아직 해결 완료로 닫지 않는다.
- 병합 후 **main에서 Security Audit을 실행**해 실제 기준 브랜치 결과를 확인하고
  기존 자동 reconcile이 #801을 닫는지 검증한다. PR 브랜치의 결과만으로
  main의 해결을 주장하지 않는다.

원본 권고의 예:
[경로 정규화 DoS](https://github.com/sporkmonger/addressable/security/advisories/GHSA-qq38-m9mg-xjj5),
[경로 정규화 결과 불일치](https://github.com/sporkmonger/addressable/security/advisories/GHSA-8gmh-2hhj-2hv9).
이 저장소에서의 실제 악용·침해가 확인됐다는 뜻은 아니다.

### 감사 실행 실패를 clean으로 처리하는 경로

기존 workflow는 npm 명령 실패를 무시하고, Ruby 감사 로그에
`Vulnerabilities found!`가 없으면 `vulnerable=false`를 기록했다.
따라서 네트워크·권고 DB 갱신 실패·깨진 보고서도 취약점 없음으로 읽힐 수 있다.
이 경우 기존 보안 이슈까지 잘못 닫을 수 있어 의존성 수정과 별도로 보완한다.

필요한 계약은 다음과 같다.

- 정상 검사 결과의 발견 사항은 기존 advisory 이슈 경로로 보고한다.
- 도구 실행·보고서 파싱 실패는 job 실패이며 clean 판정을 내보내지 않는다.
- 실패한 검사 후 reconcile은 실행하지 않아 기존 이슈 상태를 보존한다.
- PR·feature branch 검사에서는 저장소 공통 보안 이슈를 변경하지 않는다.
  기본 브랜치에서 확인한 결과만 이슈를 열고 닫는 근거로 사용한다.
- 완료한 감사와 발견 사항 0건을 구분하고, workflow 변경 자체도 감사 대상으로 삼는다.
- fake CLI와 임시 파일로 정상·발견·오류를 검증하며 실제 취약점 API나 Secret은 쓰지 않는다.

## P1: #804의 미해결 Sentry 권한

[운영 이슈 #804](https://github.com/Twodragon0/tech-blog/issues/804)는 부분 복구 상태다.
[Ops 실행 42561838613](https://github.com/Twodragon0/tech-blog/actions/runs/42561838613)의
job 결론은 success지만 보고서 내용은 **P1**이다.

| 검사 | 현재 근거 | 판정 |
|---|---|---|
| Ruff/lint | lint-and-types OK | 과거 포맷 실패는 현재 재현되지 않음 |
| main Actions | recent failed runs: 0 | 조회한 최근 구간은 정상 |
| Vercel API | `Skipped (VERCEL_TOKEN not set)` | API 상태 미측정; 정상으로 판정하지 않음 |
| Sentry issues API | HTTP 403 | 미해결 P1 |

[Sentry 실행 42598432118](https://github.com/Twodragon0/tech-blog/actions/runs/42598432118)도
project API 접근은 성공했지만 issues API는 HTTP 403이었다.
CSP 보고서는 이를 **MEASURED NOTHING**으로 명시한다. 따라서 녹색 job만으로
이슈 #804를 닫거나 CSP 이벤트 0건을 주장할 수 없다.
Sentry의 event 읽기 권한과 org/project 범위를 별도 확인한 뒤 같은 쿼리의
HTTP 200·응답 형식·미해결 이벤트를 검증해야 한다. 이번 점검은 Secret을 변경하지 않았다.

## 전체 PR 처리 순서

| 순위 | PR | 확인 결과 | 다음 처리 |
|---|---|---|---|
| P2 | [#817](https://github.com/Twodragon0/tech-blog/pull/817) age 리허설 | CI 통과, mergeable | 리뷰 후 병합 후보. 일반 CI의 실제 age 검사는 도구 미제공 시 skip; 로컬 실제 암호화 증거와 구분 |
| P2 | [#798](https://github.com/Twodragon0/tech-blog/pull/798) Actions | 기능 체크 통과, auto-merge 실패 | `enablePullRequestAutoMerge`가 required protection rules 부재로 실패. 체크를 완화하지 말고 수동 병합 검토 또는 별도 보호 규칙 설계 |
| P2 | [#783](https://github.com/Twodragon0/tech-blog/pull/783) Ruff 0.16.9 | build 실패 | CI requirement·BlogWatcher requirement·workflow 4개 핀을 한 버전으로 맞춘 통합 수정 필요 |
| P2 | [#778](https://github.com/Twodragon0/tech-blog/pull/778) Ruff 0.16.8 통합 | 선언 2곳·핀 4곳을 함께 변경 | 통합 방식은 적절. 최신 main/#798 변경과 합쳐 재검증한 뒤 #783/#759 대체 여부 결정 |
| P2 | [#759](https://github.com/Twodragon0/tech-blog/pull/759) Ruff 0.16.8 | build 실패, 겹치는 수정 | 통합 수정 CI 통과 전에는 해결로 닫지 않음 |
| P2 | [#761](https://github.com/Twodragon0/tech-blog/pull/761) NumPy | 충돌, DIRTY | 현재 requirements-visual.txt 기준으로 재생성·시각 도구 검증 |
| P2 | [#800](https://github.com/Twodragon0/tech-blog/pull/800) Ruby minor/patch | build 통과, auto-merge 실패 | addressable 보안 수정과 역할 구분. lockfile 갱신 후 감사·빌드 재확인 |
| P3 | [#779](https://github.com/Twodragon0/tech-blog/pull/779) window error 가드 | CI 통과 | jsdom major 업데이트 전 테스트 가드 검토 |
| P3 | [#816](https://github.com/Twodragon0/tech-blog/pull/816) jsdom 31 | Vitest·build 통과, major | 파싱 완료 시점·CSS·canvas 변경의 실제 사용 영향 리뷰 후 병합 |
| P3 | [#782](https://github.com/Twodragon0/tech-blog/pull/782) fonttools | build 통과, auto-merge 실패 | 폰트 산출물 영향과 최종 체크 재확인 |
| P3 | [#760](https://github.com/Twodragon0/tech-blog/pull/760) CairoSVG | build 통과 | 중복 #756 대신 유지, 렌더링 회귀 확인 후 병합 후보 |
| P3 완료 | [#756](https://github.com/Twodragon0/tech-blog/pull/756) CairoSVG | #760과 diff 완전 동일 | 중복 종료 완료, #760 유지, 브랜치는 삭제하지 않음 |
| P2 보류 | [#585](https://github.com/Twodragon0/tech-blog/pull/585) 방화벽 백업 | Secret 대기, 오래된 브랜치 | VERCEL_TOKEN·프로젝트 접근 확정 및 최신 main 재검증 전 cron 복원 보류 |

#756/#760의 diff SHA-256은 모두
`f58e269bcd59724caa411b42e04108204bab1db5334f2a4408801e2df12a315a`이다.
다른 PR은 제목 유사성만으로 닫지 않는다. 특히 Ruff PR은 변경 파일·핀 범위가 달라
대체 구현의 검증이 먼저다. `auto-merge` 성공도 실제 병합 완료와 동일하지 않으며,
각 PR의 OPEN/CLOSED/MERGED 상태를 따로 확인한다.

## 게시·RSS와 품질 이슈

- 운영 RSS `https://tech.2twodragon.com/feed.xml`과 백업 RSS
  `https://twodragon0.github.io/tech-blog/feed.xml`은 HTTP 200·XML 파싱 성공이었다.
  두 피드 모두 item 50건, 최신 글은 **2026-11-09**, item link의 비 HTTPS 주소는 0건이다.
  백업 링크에는 `/tech-blog/posts/...`가 포함됐다.
  각 피드의 최신 게시 URL도 HTTP 200·제목·canonical 태그 존재를 확인했다.
- [자동 발행 실행 42557984975](https://github.com/Twodragon0/tech-blog/actions/runs/42557984975)는
  발행·백업 빌드·배포가 성공했다. 현재 관측으로는 발행 중단이 재현되지 않는다.
- [품질 이슈 #799](https://github.com/Twodragon0/tech-blog/issues/799)는 11월 1일 생성된
  당시 보고서다. 당시의 “11월 포스트 0개”를 현재 상태로 인용하지 않는다.
  포맷 점수·표·체크리스트 숫자만 올리는 보완 대신 실제 내용·출처·게시 공백을 점검한다.
- 기존 백업 프로젝트 검토안의 실제 프로젝트·버킷·키 보관자 확정은 계속 보류다.
  PR·CI 개선을 클라우드 생성·결제·IAM·복구 키 변경 승인으로 확장하지 않았다.

## 완료 조건과 되돌리기

보안 수정의 완료 조건은 최종 HEAD의 CI 성공, 리뷰, 병합 후 main의 실제 감사 0건이다.
job 성공과 발견 사항 0건, 검증 skip을 별도로 보고한다.
문제 발생 시 보안 수정 커밋과 workflow 보완 커밋을 각각 revert할 수 있다.
취약 버전으로 되돌리는 경우 보안 이슈는 유지하고 사유·노출 범위를 재평가한다.
작업 폴더·브랜치·운영 Secret·클라우드 리소스의 일괄 삭제는 수행하지 않았다.

원격 반영은 별도 차단 상태다. `fix/ops-priority-audit-20261109` 전송 시도는
호스트 전역 `agent-guard`의 PreToolUse 훅에서 거부됐다.
이전 PR용 브랜치·커밋 한정 예외를 다른 브랜치로 확대하지 않았다.
따라서 로컬 검증·커밋과 원격 PR·CI 실행을 구분한다.

## 최종 로컬 검증

| 항목 | 결과 |
|---|---|
| 보안 수정 커밋 | `cad567d8`: addressable 2.9.2, 최신 DB 검사 0건 |
| 감사 보호 커밋 | `25fd2a3f`: 실패 시 verdict 미발행, 기본 브랜치 이슈 갱신 제한, 선행 필터 실패 전파 |
| 전체 pytest | **6,498 passed, 9 skipped**, 기존 폰트 경고 1건 |
| Ruff | CI와 같은 0.16.7, scripts 전체 lint·484개 파일 format check 통과 |
| Mypy | 새 오프라인 테스트 모듈 검사 통과 |
| Actionlint·diff | 변경 workflow 정적 검사·공백 검사 통과 |
| Jekyll | 전체 사이트 빌드 통과 |
| 공개 서비스 | 운영·백업 RSS 및 각 최신 게시물 HTTP 200 |

추가 리뷰에서 찾은 선행 `check-changes` 실패·취소·건너뜀의 요약 오판도 수정했다.
실제 workflow shell을 실행하는 회귀 테스트가 수정 전 실패하고 수정 후 통과했으며,
변경 파일 탐지가 성공했을 때만 정상적인 감사 건너뜀을 허용한다.
별도 읽기 전용 최종 리뷰에서 해당 차단 문제가 해소됐음을 확인했다.
위 pytest의 환경 의존 skip은 실제 실행 성공으로 계산하지 않았다.
