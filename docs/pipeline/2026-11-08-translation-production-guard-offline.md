# 운영 장부 보호: 기존 DB 확인과 영속 유지보수 차단

상태: 운영용 API의 오프라인 구현. 호스트의 production 디렉터리·원장·launchd·Secret·정기 실행은 변경하지 않는다. 모델 API와 실제 재부팅을 실행하지 않는다. 저장·복구 런북은 별도 [PR #812](https://github.com/Twodragon0/tech-blog/pull/812)로 제안했다.

## 왜 별도 운영 진입점인가

기존 `BudgetLedger`는 fixture와 명시적 초기 구성에 필요한 신규 DB 생성을 지원한다. 이 동작을 운영 호출자에 그대로 사용하면 경로 누락을 빈 장부로 오인할 수 있다. `ProductionBudgetLedger`는 기존 DB와 기존 flock을 요구하고, 운영 batch 전에 유지보수 상태를 확인한다. fixture의 기존 생성 동작은 바꾸지 않는다.

실제 운영 호출자는 반드시 이 보호 API를 사용해야 한다. 다른 코드가 일반 `BudgetLedger`나 직접 SQL로 우회하는 것을 파일 권한 이상의 보안 경계로 막지는 않는다. 실제 transport나 운영 workflow는 이번 구현에서 연결하지 않는다.

## API와 실패 경계

| API | 동작 | 실패 시 |
|---|---|---|
| `check_ready()` | 기존 flock 아래 read-only DB의 무결성·스키마·policy와 차단 상태 확인 | run history·예약·파일 초기화 없이 중단 |
| `batch(run_id)` | 동일 flock을 보유하는 strict batch, DB를 만드는 연결 모드 금지 | 첫 예약·호출 전에 중단 |
| `enter_maintenance(operation_id, reason_code)` | 기존 flock 아래 영속 marker 기록 | busy이면 marker를 바꾸지 않음 |
| `clear_maintenance(operation_id)` | marker ID 일치와 DB 준비 상태를 확인한 뒤 명시적으로 해제 | 검증 실패·ID 불일치이면 차단 유지 |

일반 `BudgetLedger`를 `require_existing=True`로 사용하는 경우 신규 DB 생성만 차단한다. 운영의 유지보수 보호까지 적용하려면 `ProductionBudgetLedger`를 사용한다. 최초 bootstrap과 정책 migration은 별도 승인 절차이며 이 API가 DB를 새로 만들도록 우회하지 않는다.

DB·lock이 없거나 DB가 빈 파일/손상/잘못된 스키마/다른 policy라면 실패한다. flock 획득 뒤에도 상태를 검사하고 strict SQLite 연결은 파일이 사라진 경우 새 DB를 만들지 않는다. `check_ready()`는 본 검사이지만 검사 직후의 독립 실호출을 허용하는 토큰이 아니다. 실제 예약·호출은 보호 batch의 잠금을 보유한 상태에서 수행해야 한다.

## 유지보수 marker

marker는 canonical DB 옆의 `budget.sqlite.maintenance.json`이다. 파일명과 위치는 장부 경로에서 결정하며 임시 runner 디렉터리에 두지 않는다. marker에 만료 시각·자동 삭제·UTC 날짜 전환에 따른 해제를 넣지 않는다. 새 프로세스도 동일 경로를 읽으므로 재시작 후에도 차단한다. 실제 OS 재부팅과 운영 디스크 전원 손실 내구성은 별도 시험이다.

내용은 버전·안전한 작업 ID·허용된 reason code로 제한한다. reason은 `restore`, `policy_migration`, `storage_incident`, `planned_maintenance`다. 원문·자유형 사고 설명·API 키·provider 응답은 기록하지 않는다. marker가 손상됐거나 읽을 수 없거나 예상하지 않은 파일 형태라면 정상으로 추정하지 않고 차단한다.

생성·해제는 기존 batch와 같은 flock으로 직렬화한다. 실행 중 batch가 있다면 유지보수 전환은 busy로 실패한다. **실행 중인 batch를 강제 중단하는 긴급 정지 기능은 아니다.** 기존 작업 종료/usage 확인 후 다시 시도한다. 진입은 DB가 손상·누락됐어도 기존 lock을 확보할 수 있으면 사고 차단을 남길 수 있어야 하지만, 해제는 건강한 기존 DB와 policy 확인을 요구한다.

marker 생성은 비공개 파일과 fsync·디렉터리 동기화를 사용한다. 기존 marker를 덮어쓰거나 lock 파일을 삭제·교체해 전환하지 않는다. 해제에도 fsync와 디렉터리 동기화를 적용한다. 일반 파일시스템의 신뢰된 단일 호스트라는 전제이며 별도 hosted runner에 차단 상태를 전파하는 분산 서비스는 아니다.

## 예시: 임시 fixture에서만 실행

아래는 이미 별도 bootstrap된 임시 장부를 대상으로 하는 API 예시다. 운영 경로 생성이나 production 활성화 명령이 아니다.

```python
from pathlib import Path
from scripts.news.translation_production import ProductionBudgetLedger
ledger = ProductionBudgetLedger(Path("/tmp/rehearsal/budget.sqlite"), daily_limit_microusd=1000, batch_limit_microusd=800)
ledger.check_ready()
ledger.enter_maintenance("restore-drill-01", "restore")
# 이 상태에서는 새 protected batch와 check_ready가 실패한다.
ledger.clear_maintenance("restore-drill-01")
```

[구현 API](../../scripts/news/translation_production.py)를 참고한다. 복구 담당자는 해제 전에 외부 사용량·누락 예약·run/attempt 이력·게시 tracker 대조를 완료해야 한다. 메서드는 외부 provider의 청구 내역이나 공개 RSS 상태를 대신 확인하지 않는다.

## 검증과 남은 운영 연결

테스트는 임시 DB와 가짜 시도 counter만 사용한다. missing DB·empty/corrupt DB·policy 불일치·marker·재시작 차단·busy 전환·명시적 해제·기존 잠금 inode 보존을 검증한다. T6 fixture와 기존 장부 회귀도 함께 확인한다.

이번 구현은 운영 진입점 보호를 제공하며 자동 bootstrap, 백업/복구 도구, 가격/token 산정, 실제 사용량 정산, Secret 전달, launchd 등록을 추가하지 않는다. 실제 운영 진입점이 보호 API를 사용하고 marker와 DB가 영속 경로에 놓였는지 확인한 뒤에만 운영 활성화를 검토한다.

## I/O 장애의 한계

해제 중 marker 삭제 후 디렉터리 fsync가 실패하면 기존 marker의 재게시를 시도한다. 재게시까지 실패하는 이중 I/O 장애에서는 marker가 없는 상태가 남을 수 있으므로 무조건 영속 차단된다고 보장하지 않는다. 이 경우 실행자 전체를 운영 계층에서 중지하고 파일시스템·marker·원장 상태를 확인할 때까지 재개하지 않는다. API의 오류를 성공으로 처리하거나 새 객체를 만들어 재시도하는 것은 복구 절차가 아니다. 단일 로컬 파일시스템의 신뢰된 호출자라는 전제와 실제 전원 손실 미검증도 유지한다.

## 로컬 검증 기록

운영 보호 30개·기존 장부 44개·T6 회귀 9개, 집중 검사 총 83개가 통과했다. 변경 Python 3개 파일의 Ruff·format·Mypy를 통과했고, 별도 읽기 전용 리뷰에서 확인한 이중 I/O 장애의 best-effort 한계를 위에 명시했다. 실제 운영 DB·Secret·모델 API·OS 재부팅은 사용하지 않았다. 전체 commit hook 검증과 커밋 SHA는 완료 보고에 기록한다.

## T6 종단 연결

T6 검증 명령의 `--require-existing-ledger`는 이미 준비된 **임시 fixture 장부**에만 보호 API를 적용하는 옵션이다. Python 호출에서는 `require_existing_ledger=True`를 명시한다. 이 경우 `ProductionBudgetLedger.batch()`의 같은 잠금 아래 DB와 marker를 확인하며, 실패해도 기본 `BudgetLedger` 생성 경로로 돌아가지 않는다. fixture 입력·가짜 transport·콘텐츠 gate는 그대로 사용한다.

보고서는 기본 경로를 `ledger_policy=fixture_bootstrap`, 기존 장부 경로를 `ledger_policy=existing_only`로 구분한다. missing DB·유지보수·손상·policy 불일치가 차단되면 `status=failed`, `fixture_requests=0`, `live_calls=0`인 안전한 보고서만 남기고 후보를 쓰지 않는다. 출력 디렉터리는 실행마다 새로 지정해야 하며 운영 장부를 이 검증 명령에 전달하지 않는다.

```bash
python scripts/validate_translation_pipeline.py \
  --fixture scripts/tests/fixtures/translation-validation.json \
  --output /tmp/guarded-fixture-check-01 \
  --ledger /tmp/rehearsal/budget.sqlite \
  --run-id guarded-fixture-01 --require-existing-ledger
```

[검증 명령 구현](../../scripts/validate_translation_pipeline.py)을 참고한다. 기본 fixture 초기 구성 경로는 이전 workflow와의 호환을 위해 유지하며 운영 bootstrap 승인 절차를 대신하지 않는다.

수동 `Translation Offline Validation` workflow는 Secret 없이 CLI 회귀 테스트를 실행하고, 별도 runner.temp 경로에 fixture 장부를 준비한 뒤 같은 장부를 보호 모드로 다시 검증한다. 준비 단계와 보호 단계의 정상 CLI는 각각 가짜 요청 3건을 처리한다. `translation-offline-report`에는 보호 모드의 `report.json`만 올린다. 초기 구성 실패의 진단도 보존하도록 `translation-bootstrap-report`에 준비 단계의 안전한 보고서를 별도로 올린다. 후보·DB·원문 검수 자료는 두 artifact 모두에 넣지 않는다. hosted runner의 임시 장부를 운영 일일 예산 저장소로 간주하지 않는다.

실제 CLI를 새 프로세스로 실행하는 종단 테스트는 missing DB 무생성, 기존 장부 성공, 유지보수 후 새 프로세스의 요청 0회 차단, 해제 ID 확인, 명시적 해제 뒤 재실행과 기존 비용·잠금 inode 보존을 검증한다. 실제 provider Secret·API·production 경로·배포는 사용하지 않는다.

T6 연결 후 집중 검사: runner 20개 + 운영 보호 30개 + 기존 원장 44개, 총 94개 통과. 별도 읽기 전용 검토에서 확인한 bootstrap 실패 보고서 누락도 별도 safe report artifact로 보완했다.
