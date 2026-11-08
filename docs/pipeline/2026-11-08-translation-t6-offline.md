# T6: Secret 없는 운영 연결 검증과 비용 장부

상태: 오프라인 fixture 검증. 실제 모델 API 호출·Secret 등록·정기 번역 활성화·운영 글 게시·배포는 수행하지 않는다. PR #810은 CI 통과 후 병합됐으며 이 작업은 그 이후 별도 브랜치다.

## 먼저 잠근 계약

구현 모듈이 없는 상태에서 새 테스트를 수집해 실패하는 것을 확인한 뒤 비용 장부와 검증 진입점을 구현했다. 기존 T1~T5의 입력/출력 계약, 한국어·숫자·CVE·URL 검증, 출처 카드·통계·품질 검사를 약화하지 않는다. 새 패키지는 추가하지 않는다.

## 일일 비용과 동시 실행

`translation_budget.py`는 SQLite 영속 장부와 POSIX 파일 잠금을 사용한다. 금액은 부동소수점 대신 정수 micro-USD다(1 USD = 1,000,000). 각 batch가 비차단 배타 잠금을 전체 context 동안 보유하므로 **같은 장부 경로를 공유하는 로컬 프로세스**의 batch는 하나만 실행된다. 잠금 획득 실패는 대기·동시 실행 대신 안전한 오류다.

호출 전 `reserve`가 최대 비용을 원자적으로 예약한다. UTC 예약 날짜의 일일 총액과 batch 총액을 모두 검사하며 거부 시 호출하지 않는다. 확인된 실제 비용만 `settle`로 예약 이하 금액에 정산한다. 사용량이 불명확하거나 예외·프로세스 종료가 발생하면 예약액을 유지한다. 자동 환불·예약 TTL·매일 장부 삭제는 없다. 자정 이후 정산해도 원래 예약일에 귀속된다. 실행 ID는 장부 전체에서 재사용하지 않고 시도 ID는 동일 실행 안에서 재사용하지 않는다.

프로세스 종료 시 운영체제가 잠금을 해제하지만 SQLite에 예약한 비용은 남는다. 손상되거나 정책이 일치하지 않는 장부는 비용 0으로 초기화하지 않고 중단한다. 장부와 잠금 파일은 비공개로 보관하고 경로를 바꾸거나 파일을 삭제해 한도를 우회하지 않는다. 동일 파일을 별칭/하드 링크로 연결하거나 여러 경로에서 실행하지 않는다.

이 잠금은 네트워크 분산 잠금이 아니다. 서로 다른 GitHub hosted runner와 임시 파일시스템 사이에는 일일 예산을 공유하지 못한다. 운영 활성화에는 고정된 단일 실행 호스트의 영속 저장소 또는 원자적 예약을 제공하는 별도 공유 서비스가 필요하다. 현재 workflow concurrency 역시 이 검증 workflow의 실행만 직렬화한다.

## Secret 없는 검증 진입점

`validate_translation_pipeline.py`는 live 옵션·제공자 선택·기본 HTTP transport를 제공하지 않는다. 저장소의 고정 JSON fixture에서 원문과 사전 검수 한국어를 읽고 T2의 가짜 응답 → T4 → T5 → 실제 tech-blog 렌더러를 연결한다. 환경의 모델 API 키를 제공자에 전달하거나 사용하지 않으며 legacy AI 모드는 `none`으로 제한한 뒤 이전 값을 복원한다.

가짜 transport도 각 시도 전에 장부를 예약하고 확인된 가짜 비용으로 정산한다. 시도당 예약 1,000·정산 500 micro-USD는 **테스트용 수치**다. 실제 모델 가격이나 실제 사용량이 아니며 운영용 장부와 섞지 않는다. 캐시와 장부는 서로 다르다. 검증 실행의 캐시는 프로세스 내부이며 장부는 재시작 후에도 남는다.

입력은 100 KB·기사 1~10개·고정 필드로 제한하고 중복 URL을 거부한다. 생성한 원문 카드와 통계를 검증하고 기존 품질 gate 목표 80을 적용한다. 품질 gate의 self-heal이 검수된 후보를 바꾸면 자동 수용하지 않고 검수를 요구하며 중단한다. URL 재검사만으로 제목·요약의 사실 보존을 증명할 수 없기 때문이다. 내용이 유지된 후보의 출처·통계를 다시 검사한다. 모든 입력 검증에 성공하더라도 fixture 검증만으로 의미적 번역 품질·실제 제공자·운영 발행 전체가 검증되는 것은 아니다.

산출물 디렉터리와 장부 경로는 checkout 밖에 있어야 하며 기존 산출물을 덮어쓰지 않는다. 후보 Markdown은 파일 0600·디렉터리 0700으로 생성한다. 실패 시 후보 파일을 제거하고 안전한 상태 report를 남긴다. T5 번역 실패의 마스킹 검수 자료는 별도 비공개 하위 디렉터리에 남는다. 성공해도 production `_posts`, 이미지, 게시 URL tracker, publish manifest, Git 원격을 변경하지 않는다. report는 `offline_fixture`, `live_calls=0`을 명시한다.

실행 예시(현재 checkout에서 실행):

```bash
python scripts/validate_translation_pipeline.py \
  --fixture scripts/tests/fixtures/translation-validation.json \
  --output /tmp/t6-validation-run-001 \
  --ledger /tmp/offline-translation-budget.sqlite \
  --run-id offline-run-001
```

[검증 코드](../../scripts/validate_translation_pipeline.py)를 참고한다. output 경로와 run ID는 실행마다 새 값이어야 한다. 재시작 검증 시 장부 경로는 유지하고 새로운 run ID를 사용한다. 운영용 예산 장부를 이 명령에 전달하지 않는다.

## 별도 수동 workflow

`translation-validation.yml`은 `workflow_dispatch`만 제공하며 일정·push/PR 자동 실행·임의 입력을 추가하지 않는다. 권한은 `contents: read`, checkout 인증 보존은 끈다. 기존 스크립트 의존성만 설치하고 고정 fixture를 검증한다. 제공자 Secret을 전달하지 않으며 보고서 JSON만 7일 artifact로 올린다. 원문 후보·SQLite·검수 디렉터리는 업로드하지 않는다. workflow 전체 timeout은 5분이다.

runner.temp의 장부는 이 오프라인 job만 위한 임시 장부다. 다음 hosted runner에서 이전 일일 사용량을 복원한다는 보장은 없다. 운영용 영속 장부·Secret 주입·실제 사용량 정산·token/가격 snapshot·전체 batch deadline·endpoint/redirect/응답 크기 제한은 여전히 후속 작업이다. 현재 명령이 과금 없이 동작하는 이유는 가짜 transport뿐이며 일반적인 dry-run이 무료이기 때문이 아니다.

## 검증과 복구 기준

회귀 테스트는 UTC 자정, batch/일일 예산, 재시작과 불명확 비용 유지, 중복 실행/시도 거부, 정산 상한·중복 정산, 프로세스 간 배타 잠금과 종료 후 해제, 손상 장부 중단을 확인한다. 검증 모드 테스트는 네트워크를 차단하고 실제 한국어 후보 생성·품질 gate, 키 미사용·보정 중 번역 변경 거부, 예산 부족 시 0회 가짜 호출, 실패 후보 제거, checkout 출력 및 덮어쓰기 거부, workflow의 Secret·게시 권한 부재를 검사한다.

실패 시 새 실행으로 무작정 재시도하지 않는다. report와 원장 잔액을 대조하고, 불명확 비용은 유지한 상태로 원인을 해결한다. 손상 장부는 비공개 백업과 SQLite 검사 후 복구하며 빈 DB로 자동 교체하지 않는다. 검증 workflow가 실패해도 기존 운영 발행 workflow의 검사나 Secret 경계를 변경하지 않는다. 실제 운영 중단·키 회전·게시 복구 절차는 [운영 준비 문서](2026-11-08-translation-operations-readiness.md)를 따른다.

공통 config 모듈은 import 시 환경변수를 읽을 수 있다. 검증 모드가 보장하는 경계는 키를 읽는 모든 라이브러리를 제거하는 것이 아니라 환경 키가 fake provider 요청에 사용되거나 report에 노출되지 않고 실호출 경로가 없다는 점이다. workflow는 모델 Secret을 전달하지 않는다.

## 이번 구현의 완료 증거

- 예산 44개·T6 9개, 집중 테스트 총 53개 통과. 네트워크 차단 상태에서 재시작 후 잔액 유지와 초과 시 가짜 호출 0회를 확인했다.
- 실제 CLI fixture 실행: `status=validated`, `live_calls=0`, 가짜 요청 3회, 본문 기사 3개, 품질 점수 88/100. 임시 상태 경로는 `/private/tmp/t6-validation-evidence-final-20261108`이다.
- 변경 Python의 Ruff·format·Mypy와 workflow Action SHA 고정 검사를 통과했다.
- 별도 읽기 전용 리뷰 후 품질 보정의 번역 변경을 거부하는 회귀 테스트를 추가했다. 예산의 로컬 동시성/비용 경계도 리뷰했다.
- 원격 Actions 실행·운영 모델 호출·Secret 접근·정기 일정 변경은 수행하지 않았다. 전체 pytest 결과와 로컬 커밋은 작업 완료 보고에 기록한다.
