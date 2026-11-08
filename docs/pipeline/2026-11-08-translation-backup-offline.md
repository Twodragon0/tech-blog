# 번역 장부의 잠금 연동 백업·검증 복구 도구

상태: 임시 합성 DB를 이용한 오프라인 구현·시험. 실제 production 장부·유지보수 상태·launchd·Secret·정기 일정·모델 API는 변경하지 않는다. PR #813은 ShellCheck 다운로드 정상화 후 모든 CI를 확인하고 병합했다.

## 구현 경계

[LedgerBackup API](../../scripts/news/translation_backup.py)와 [CLI](../../scripts/manage_translation_ledger.py)는 `ProductionBudgetLedger`의 **기존 flock** 아래 동작한다. `BudgetLedger.batch()`를 백업 용도로 호출하지 않으므로 snapshot 때문에 run history가 늘지 않는다. 원본 DB는 read-only URI로 열고 SQLite Backup API를 사용하며, 모든 연결은 명시적으로 닫는다. 같은 파일시스템의 신뢰된 단일 호스트라는 전제를 유지한다.

snapshot은 새 디렉터리의 `budget.sqlite`와 마지막에 쓰는 `manifest.json`으로 구성한다. DB·manifest의 파일은 0600, 디렉터리는 0700을 사용한다. 완료되지 않은 파일은 정상 snapshot으로 취급하지 않으며 기존 snapshot을 덮어쓰지 않는다. manifest에는 버전·스키마·승인 policy·UTC 생성 시각·SHA-256·크기·집계·accounting fingerprint를 보존한다. fingerprint는 run·reservation·policy의 내용과 미정산 예약을 포함한다. 원문·API 키·provider 응답은 저장하지 않는다.

검증은 파일 checksum뿐 아니라 DB integrity·FK·schema·policy 및 실제 accounting 내용까지 확인한다. manifest는 무조건 신뢰하지 않고 크기·필드·형식을 검사한다. checksum은 우발 손상 탐지 자료이며 신뢰된 저장소·소유자·접근 통제를 대신하지 않는다. 파일·디렉터리 fsync는 수행하지만 실제 전원 손실 내구성은 별도 시험이다.

## 백업

기존 DB와 lock이 없으면 초기화하지 않고 거부한다. batch가 같은 flock을 보유하고 있으면 백업도 busy로 거부한다. snapshot 출력 경로는 source DB·lock·maintenance 파일을 가리키거나 덮어쓸 수 없다. CLI는 장부와 snapshot이 checkout 안에 놓이는 것도 거부한다.

아래는 **이미 별도로 준비한 임시 fixture** 전용 예시다. 1000/800 micro-USD는 운영 상한이 아니라 예시 장부와 정확히 일치해야 하는 합성 설정이다.

```bash
python scripts/manage_translation_ledger.py backup \
  --ledger /tmp/ledger-rehearsal/budget.sqlite \
  --snapshot-dir /tmp/ledger-rehearsal/snapshot-01 \
  --daily-limit-microusd 1000 --batch-limit-microusd 800
```

[CLI 구현](../../scripts/manage_translation_ledger.py)을 참고한다. snapshot 디렉터리는 새 이름이어야 하며, 마지막 manifest 완료와 DB 검증이 확인된 snapshot만 보존·전송한다. 이 명령에는 retention·암호화 외부 전송·정기 실행·없는 장부 bootstrap 기능이 없다.

## 복구의 안전한 첫 범위

복구는 일치하는 **기존 maintenance operation ID**를 요구한다. marker를 생성하거나 해제하는 암묵적 동작은 없다. snapshot과 현재 DB가 각각 유효해야 하며 run·reservation·policy accounting이 정확히 같아야 한다. 확인 가능한 비용·실행 이력을 바꾸지 않는 검증 복원만 자동 적용한다.

과거 snapshot에서 예약·실행이 사라지거나 금액이 달라지는 경우를 거부한다. 현재 DB가 누락·손상돼 최신 비용을 대조할 수 없는 경우도 거부한다. `--force`나 확인 생략 옵션은 없다. 이것은 모든 재해를 자동으로 되돌리는 기능이 아니다. 손상 원장 복구·과거 snapshot 이후의 누락 비용 병합에는 별도 검토된 reconciliation/migration과 외부 사용량 대조가 필요하다. [운영 런북](../runbooks/translation-ledger-storage-backup-recovery.md)의 사고 보존·재개 기준을 따른다.

검증 후 staging을 활성 DB와 같은 파일시스템에 만들고 SQLite 연결을 모두 닫은 뒤 DB만 원자적으로 교체한다. 기존 DB와 필요한 사고 자료를 보존하며 기존 flock inode와 maintenance를 유지한다. 완료 뒤에도 API 호출은 계속 차단되며 운영자의 비용·ID·게시 이력 대조 없이 자동 재개하지 않는다.

아래 예시는 `restore-rehearsal-01`로 maintenance가 이미 진입돼 있고 snapshot 이후 accounting 변화가 없는 임시 DB만 대상으로 한다.

```bash
python scripts/manage_translation_ledger.py restore \
  --ledger /tmp/ledger-rehearsal/budget.sqlite \
  --snapshot-dir /tmp/ledger-rehearsal/snapshot-01 \
  --daily-limit-microusd 1000 --batch-limit-microusd 800 \
  --operation-id restore-rehearsal-01
```

[복구 API](../../scripts/news/translation_backup.py)를 참고한다. 잘못된 operation ID, marker 부재/손상, policy 불일치, checksum 손상, 오래된 accounting은 active DB를 바꾸기 전에 중단한다. 실패 보고가 있었다면 staging/사고 자료와 유지보수 상태를 확인하고 무작정 재시도하거나 marker를 지우지 않는다. 실제 적용 후 발생한 I/O 오류는 별도 운영 격리가 필요한 상태이며 실패가 항상 “변경 없음”을 뜻하지는 않는다.

## 검증 계획과 운영 미적용 항목

임시 DB에서 미정산 예약 보존·run history 불변·checksum/manifest 검증·복구 후 예산 상한·기존 flock inode·maintenance 유지·프로세스 간 상호 배타를 확인한다. stale snapshot, 손상 파일, 원장 누락, policy/ID 불일치, 덮어쓰기, 교체 전 I/O 실패도 거부해야 한다. CLI는 별도 새 프로세스로 성공·실패를 검증한다.

실제 SSD 장애·전원 손실·오프호스트 복원·복원 키 보관·외부 암호화 저장소·스케줄·retention은 검증 범위 밖이다. 운영 진입점이 보호 API를 사용하고 장부/marker가 영속 경로에 놓였는지 먼저 확인한다. DB와 lock을 미디어 Move·SSD 정리 정책에 넣지 않는다.

## 형식 근거

- [SQLite Backup API](https://www.sqlite.org/backup.html)
- [SQLite 파일 손상 방지](https://www.sqlite.org/howtocorrupt.html)
- [Python sqlite3.Connection.backup](https://docs.python.org/3.11/library/sqlite3.html#sqlite3.Connection.backup)

## 이번 구현의 확인 결과

- 백업 API 22개·실제 CLI 6개, 집중 테스트 총 28개 통과. 변경 Python 4개 파일의 Ruff·format·Mypy와 문서 예제·상대 링크를 검사했다.
- 테스트를 먼저 실패시킨 뒤 CLI의 dangling symlink 검사 우회와 새 상위 디렉터리의 fsync 누락을 수정했다. 별도 읽기 전용 리뷰에서 회계 기록 손실이나 stale snapshot 허용 결함은 발견하지 못했다.
- 임시 CLI 리허설에서 백업·복구를 성공했고 실행 1건·예약 2건·미정산 1건·합성 비용 500 micro-USD를 유지했다. snapshot SHA-256·기존 lock inode가 보존됐고 복구 후에도 유지보수 차단이 남았다.
- 리허설 보고서는 `ledger-backup-tool-rehearsal-sjebvk2g/rehearsal-report.json`에 생성했다. 임시 경로의 장기 보존은 보장하지 않는다. 모델 호출은 0회이며 실제 power-loss·운영 원장·외부 복원은 시험하지 않았다.
- 전체 commit hook 결과와 로컬 커밋은 작업 완료 보고에 기록한다.
