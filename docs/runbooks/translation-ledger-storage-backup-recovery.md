# 번역 비용 원장: 운영 저장소·백업·복구 절차

상태: **운영 제안 및 임시 DB 리허설 근거 문서**. 이 문서 작성으로 호스트 디렉터리·launchd·Secret·일정·원장을 생성하거나 변경하지 않았다. 실제 API 호출과 운영 전환도 하지 않았다.

2026-11-08 읽기 전용 점검에서는 홈 볼륨 여유 공간이 약 9.9 GiB이고 `~/.local/state`가 쓰기 가능하며 `tech-blog` 하위 디렉터리는 없었다. 아래 production 원장은 **아직 생성되지 않았다**. 여유 공간은 그 시점의 관측값이며 현재 용량이나 향후 임계값 준수를 보장하지 않는다.

구현 근거는 [비용 원장](../../scripts/news/translation_budget.py), [원장 회귀 테스트](../../scripts/tests/test_translation_budget.py), [T6 오프라인 검증](../pipeline/2026-11-08-translation-t6-offline.md), [운영 준비 조건](../pipeline/2026-11-08-translation-operations-readiness.md)이다.

## 1. 실행 호스트와 저장 경계

제안 운영 방식은 **Mac mini의 단일 전용 runner**다. 모든 실행자가 같은 로컬 파일시스템의 원장과 같은 잠금 파일을 사용해야 한다. GitHub hosted runner마다 DB를 다운로드하거나 실행 종료 후 업로드하는 방식은 동시 예약과 일일 상한을 보장하지 못한다. artifact·Git·GCS 객체 동기화를 분산 잠금처럼 사용하지 않는다.

| 용도 | 제안 경로 | 관리 원칙 |
|---|---|---|
| 활성 원장 | `/Users/namyongkim/.local/state/tech-blog/translation/production/budget.sqlite` | 고정 경로, 저장소 checkout 밖 |
| 배타 잠금 | 위 경로의 `budget.sqlite.lock` | **삭제·교체 금지**, 기존 inode 유지 |
| 로컬 백업 | `/Users/namyongkim/.local/state/tech-blog/translation/backups/production/<UTC timestamp>/` | production과 형제인 backups 트리, 검증된 snapshot만 완료 표시 |
| 사고 보존본 | 같은 상태 루트의 `incidents/<incident-id>/` | 원본 DB·sidecar·해시·작업 이력, 자동 정리 제외 |
| 비밀 없는 정책 | `/Users/namyongkim/.config/tech-blog/translation/production-policy.json` | 제안 경로, 승인된 정수 상한·스키마·코드 SHA만 |
| 운영 로그 | `/Users/namyongkim/Library/Logs/tech-blog/translation/` | 제안 경로, 단계·실행 ID·오류 분류·비용 합계만 |
| 비밀 | 별도로 승인할 OS 자격 증명 저장소/주입 경로 | DB·정책 JSON·로그·백업 manifest에 키를 넣지 않음 |

경로는 역할별 제안이며 현재 설치 상태를 뜻하지 않는다. 디렉터리 0700, 파일 0600, 생성 시 `umask 077`을 적용한다. 기존 상위 홈 디렉터리의 권한을 재귀적으로 바꾸지 않는다. 소유자·실행 계정·실제 canonical 경로를 확인하고, hardlink를 만들거나 별도 DB 이름으로 상한을 우회하지 않는다. symlink를 사용한다면 구현의 `Path.resolve()` 결과와 동일한 잠금 경로로 귀결되는지 확인하되 운영 설정에는 위 canonical 경로 하나만 기록한다.

원장·잠금·현재 유효한 백업은 yt-dlp/GCS Move, 미디어 SSD 정리, 일반 workspace/tmp 정리 대상에서 제외해야 한다. “로컬 SSD 0B”는 완료 미디어의 정책이며 권위 있는 비용 원장에 적용하지 않는다. 실제 정리 규칙은 이번 작업에서 변경하지 않았다.

**처음부터 빈 DB를 `touch`하지 않는다.** 구현은 기존 빈 파일과 손상/미완성 스키마를 거부한다. 반대로 경로 자체가 없으면 새 원장을 만들 수 있다. 따라서 운영 entrypoint에는 다음 보호가 활성화 전에 필요하다.

- 정상 운영에서는 기존 DB·스키마·정책이 없으면 첫 호출 전에 중단한다.
- 최초 bootstrap은 별도의 승인된 절차와 실행 증거로만 허용한다.
- 영속 maintenance 상태가 있으면 재부팅 후에도 새 실행·API 호출을 막는다.

이 production preflight·bootstrap 승인·영속 maintenance gate는 **아직 구현·배포되지 않은 활성화 조건**이다. 지금 있는 `BudgetLedger`의 기능으로 오인하지 않는다. DB가 사라졌을 때 자동 생성하도록 두면 백업 손실이 예산 0부터 재시작하는 사고로 이어진다.

## 2. 보존해야 하는 예산 의미

금액은 정수 micro-USD이며 1 USD는 1,000,000 micro-USD다. 실제 시도 전에 최대 비용을 예약하고, 사용량이 확인된 경우에만 예약 이하 금액으로 정산한다. `actual_microusd IS NULL`인 항목은 예약 전액을 계속 사용한 것으로 집계한다. timeout·응답 분실·프로세스 종료는 자동 환불 사유가 아니다.

예약은 trusted 실행 시각을 UTC로 변환한 날짜에 귀속한다. 원문 기사 날짜를 예산 날짜로 쓰지 않는다. UTC 자정 이후 정산해도 원래 예약일의 비용이다. 실행 ID는 원장 전체에서, 시도 ID는 동일 실행 안에서 재사용하지 않는다. 일일 상한과 배치 상한은 DB policy에 저장되며 요청 설정과 정확히 일치해야 한다.

운영 상한 변경이나 스키마 upgrade는 승인된 migration 작업이다. policy mismatch를 해결하려고 DB를 삭제하거나 새 경로를 고르지 않는다. 현재 API에는 과거 실행의 불명확한 예약을 자동 재정산하는 복구 기능이 없다. 신규 batch의 `settle()`로 과거 예약을 0으로 바꾸려 하지 않는다.

## 3. 백업 일정·용량·복구 목표 — 제안값

| 항목 | 제안 | 현재 검증 범위 |
|---|---|---|
| batch 후 snapshot | 정상 batch 종료 후 15분 이내, 잠금 획득 가능할 때 | 자동화 미설치 |
| 정기 snapshot | 매일 UTC 01:00 / KST 10:00, missed run 탐지 포함 | 일정 미등록 |
| 로컬 보존 | 최근 48개 snapshot + 일별 대표 14일 | retention 미구현 |
| 로컬 용량 상한 | 전체 백업 512 MiB, 사고 보존본은 별도 승인 관리 | 현재 파일 크기·증가율 측정 필요 |
| 공간 경보 | 여유 5 GiB 미만 경보, 2 GiB 미만 신규 실호출 중지 제안 | 임계값·감시 미배포 |
| 목표 RPO | 완료 batch 기준 15분 이내 snapshot; 실제 복구점은 마지막 검증 snapshot 시각 | 진행 중 batch의 최신 예약이 백업에 없을 수 있음 |
| 기술 복원 목표 RTO | 정상 로컬 snapshot이 있으면 30분 목표 | 임시 DB의 기능 리허설만 수행 |
| 실호출 재개 RTO | 미정: 누락 비용·불명확한 사용량·중복 게시 대조가 끝날 때까지 중단 | 시간만으로 자동 재개하지 않음 |

원장 잠금을 보유한 batch가 길면 백업도 지연된다. 마지막 검증 snapshot의 나이와 지연 원인을 감시한다. retention은 새 snapshot 검증·manifest 저장 후에만 시행하고 활성 DB·잠금·사고 보존본은 삭제 대상에 넣지 않는다. 필수 보존과 용량 상한을 동시에 지키지 못하면 경보와 운영 검토로 처리하며, 공간을 만들기 위해 원장을 지우지 않는다.

같은 SSD의 백업은 실수·일부 DB 손상 복구용이다. SSD/호스트 전체 장애에는 대응하지 못한다. **암호화된 외부 보관 대상, 접근 권한, 복원 키 보관, 삭제 정책은 아직 결정·검증되지 않았다.** GCS·Time Machine·원격 백업 자격 증명이 준비돼 있다고 가정하지 않는다. 외부 사본은 검증된 완성 snapshot만 전송하며 활성 DB를 동기화하지 않는다.

## 4. 잠금과 백업의 사전 조건

1. 유지보수 담당자와 실행 계정을 확인하고 같은 원장을 쓰는 launchd·수동 CLI·CI dispatch 경로를 열거한다. 백업 실패를 해결하려고 Paseo 등 무관한 데몬을 재시작하지 않는다.
2. 현재 DB와 **기존** `budget.sqlite.lock`의 존재·소유자·권한·canonical 경로·link 수를 확인한다. 처음부터 없는 production 경로라면 백업을 중단하고 bootstrap 미완료로 기록한다.
3. 잠금은 기존 파일을 `r+b`로 열어 비차단 `LOCK_EX | LOCK_NB`로 얻는다. busy이면 정상 batch가 끝나기를 기다리도록 다음 시도를 예약하고, 잠금을 강제로 지우지 않는다. 잠금 파일이 남아 있다는 사실만으로 프로세스가 살아 있다고 판단하지 않는다.
4. 백업은 `BudgetLedger.batch()`로 수행하지 않는다. 그 메서드는 run history를 기록하므로 읽기 전용 백업 도구가 아니다.
5. SQLite 연결은 `with sqlite3.connect(...)`만으로 닫히지 않는다. `contextlib.closing` 또는 명시적 `close()`를 사용한다. DB 교체 전에는 모든 연결이 닫혀 있어야 한다.

다음 조각은 운영 자동화가 아니라 검토·리허설용 Python 예시다. 변수는 같은 유지보수 세션에서 이어서 사용한다. source는 반드시 read-only URI로 열어 파일 누락이 새 DB 생성으로 바뀌지 않게 한다. 실제 운영 실행은 위 활성화 조건을 먼저 완료해야 한다. [Python backup API](https://docs.python.org/3.11/library/sqlite3.html#sqlite3.Connection.backup)

```python
from pathlib import Path
from contextlib import closing
import fcntl, hashlib, json, os, sqlite3
from datetime import datetime, timezone
active = Path("/Users/namyongkim/.local/state/tech-blog/translation/production/budget.sqlite")
lock_path = active.with_name(active.name + ".lock")
assert active.is_file() and lock_path.is_file()
assert active.stat().st_nlink == 1
os.umask(0o077)
```

백업 디렉터리는 UTC 시각과 고유 실행 식별자를 조합해 새로 만든다. 기존 snapshot 이름을 재사용하거나 덮어쓰지 않는다. 아래 timestamp는 단독 예시이며 같은 초의 동시 요청 가능성은 `exist_ok=False`와 `O_EXCL` 실패로 처리한다.

```python
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
snapshot_dir = active.parent.parent / "backups" / "production" / stamp
snapshot_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
partial = snapshot_dir / "budget.sqlite.partial"
descriptor = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
os.close(descriptor)
```

예약 대조는 단순 총액만 보지 않고 예약 ID·실행 ID·시도 ID·UTC 날짜·최대 예약액·확정액 전체를 정렬해 비교한다. 다음 `audit_sql`은 source와 snapshot의 정확한 row 대조를 위한 것이며 원문·키를 출력하지 않는다.

```python
audit_sql = (
    "SELECT reservation_id,run_id,attempt_id,utc_day,reserved_microusd,actual_microusd "
    "FROM reservations ORDER BY reservation_id"
)
```

위 정의는 예약 이력을 읽는 쿼리다. 아래 snapshot 생성은 원장과 같은 기존 flock을 보유하는 동안 이루어진다. 원본을 raw `cp`하지 않고 SQLite Online Backup API를 사용한다. [SQLite backup 설명](https://www.sqlite.org/backup.html)

```python
with lock_path.open("r+b") as held:
    fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    lock_identity = (os.fstat(held.fileno()).st_dev, os.fstat(held.fileno()).st_ino)
    with closing(sqlite3.connect(active.as_uri() + "?mode=ro", uri=True)) as source, closing(sqlite3.connect(partial.as_uri() + "?mode=rw", uri=True)) as destination:
        destination.execute("PRAGMA synchronous=FULL")
        source.backup(destination)
        source_rows = source.execute(audit_sql).fetchall()
        source_runs = source.execute("SELECT run_id,state FROM runs ORDER BY run_id").fetchall()
        source_policy = source.execute("SELECT singleton,daily_limit_microusd,batch_limit_microusd FROM policy").fetchall()
```

이 블록이 끝나면 SQLite 연결과 잠금 descriptor가 닫힌다. 이후 writer가 다시 실행되더라도 snapshot은 앞서 잠근 시점의 상태다. 검증 시 최신 원본을 다시 읽어 snapshot과 같다고 가정하지 말고 위에서 캡처한 audit 값과 비교한다. 예외가 발생한 `.partial`은 완료 백업으로 취급하지 않는다.

`mode=ro` 열기가 hot journal 복구를 요구하며 실패하면 read/write로 몰래 재시도하거나 journal을 삭제하지 않는다. 운영 호출을 중단하고 6절의 사고 보존·복구 경로로 전환한다.

## 5. snapshot 검증과 완료 표시

검증 항목은 모두 통과해야 한다.

- `PRAGMA integrity_check`가 정확히 `ok`, `PRAGMA foreign_key_check`가 빈 결과다.
- `user_version=1`, 사용자 table이 `runs`, `reservations`, `policy` 세 개다. 열 이름·순서를 현재 코드와 대조한다. CHECK·UNIQUE·foreign key 정의도 승인된 스키마와 비교하며 새 DB를 만들어 맞추지 않는다.
- policy는 singleton 1의 한 행이며 승인된 비밀 없는 설정의 일일/배치 정수 상한과 정확히 같다. snapshot의 policy를 승인 설정 대신 사용하지 않는다.
- snapshot의 전체 reservation/run/policy rows가 백업 시 캡처한 값과 같다. 전체 예약 수, `actual IS NULL` 수, UTC 날짜별 실효 비용도 기록한다. 실효 비용은 미정산이면 예약액, 정산됐으면 확정액이다.
- SHA-256, 파일 크기, snapshot UTC 시각, 원본 경로, 코드 SHA, 스키마 버전, 정책 상한, 위 집계와 검증 결과를 비공개 manifest에 기록한다. 원문·비밀·provider 응답을 넣지 않는다.

핵심 검사 예시는 다음과 같다. 이 조각만으로 열/제약 정의와 외부 승인 정책 대조가 자동 완료되는 것은 아니다.

```python
with closing(sqlite3.connect(partial.as_uri() + "?mode=ro", uri=True)) as check:
    assert check.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
    assert check.execute("PRAGMA foreign_key_check").fetchall() == []
    assert check.execute("PRAGMA user_version").fetchone() == (1,)
    assert check.execute(audit_sql).fetchall() == source_rows
    assert check.execute("SELECT run_id,state FROM runs ORDER BY run_id").fetchall() == source_runs
    assert check.execute("SELECT singleton,daily_limit_microusd,batch_limit_microusd FROM policy").fetchall() == source_policy
```

모든 검증 후 연결을 닫고 snapshot 파일을 fsync한다. `.partial`을 같은 디렉터리의 `budget.sqlite`로 원자적으로 바꾸고 directory fsync를 수행한다. manifest도 배타 생성한 임시 파일에 기록·fsync 후 원자적 rename·directory fsync한다. 마지막에만 완료 상태를 표시한다. 기존 완료 파일을 덮는 이름은 허용하지 않는다. 이는 제안 durability 절차이며 실제 전원 손실 내구성을 시험했다는 뜻은 아니다.

```python
with partial.open("rb") as saved:
    os.fsync(saved.fileno())
snapshot = snapshot_dir / "budget.sqlite"
assert not snapshot.exists()
os.replace(partial, snapshot)
directory_fd = os.open(snapshot_dir, os.O_RDONLY)
try:
    os.fsync(directory_fd)
finally:
    os.close(directory_fd)
```

SHA-256은 닫힌 snapshot의 최종 bytes로 계산한다. manifest에 기록한 checksum은 전송 손상 탐지 자료이지 외부 공격자에 대한 진위 보증 자체는 아니다. 외부 보관에서는 별도 접근 통제·암호화·복원 키와 신뢰할 수 있는 manifest 보관이 필요하다. 검증 실패와 수동 리허설 자료는 정상 retention 목록에 섞지 않는다.

## 6. 장애 발생 시 중단과 원본 보존

**모든 신규 실호출을 먼저 차단한다.** 현재 실행·queue·수동 CLI·dispatch와 supervisor의 자동 재시작을 확인한다. 영속 maintenance 상태는 재부팅 이후에도 유지해야 한다. 단순히 프로세스 하나를 죽이거나 shell 변수를 설정하는 조치는 재개 차단을 보장하지 못한다. 이 보호가 구현되지 않은 상태에서는 운영 복원 작업을 시작하지 않는다.

1. 진행 중 호출이 있으면 종료/usage 확인까지 기다리되 응답이 불명확한 예약은 유지한다. 강제 종료가 필요했다면 시각·run/attempt ID·provider request ID의 안전한 식별 정보만 기록한다.
2. 모든 writer와 SQLite client를 닫고 같은 기존 flock을 획득한다. busy이면 복원하지 않는다. lock의 device/inode를 기록하고 작업 내내 같은 descriptor를 보유한다.
3. DB와 존재하는 `budget.sqlite-journal`, `budget.sqlite-wal`, `budget.sqlite-shm`을 사고 디렉터리에 **cold forensic copy**로 보존한다. 모든 client가 멈춘 상태에서만 복사한다. 각 파일 크기·해시·권한과 복사 시각을 기록하고 파일/디렉터리를 fsync한다. 활성 DB를 먼저 이동해 경로가 비는 틈을 만들지 않는다.
4. `os.kill`/전원 장애 후 rollback journal이 남아 있다면 원본·sidecar를 삭제하지 않는다. 보존본의 별도 작업 복사본에 파일 이름 세트를 맞춰 두고, maintenance 상태에서 SQLite read/write open으로 정상 rollback을 수행한 뒤 검사한다. 읽기 전용 백업이 실패했다는 이유만으로 DB를 새로 만들지 않는다.
5. 복구된 최신 작업 복사본이 검증되면 이를 우선 검토한다. 과거 snapshot은 아래 비용 대조가 끝나기 전까지 활성화 후보일 뿐이다.

현재 구현은 DELETE journal과 synchronous FULL을 사용하지만, 실제 발견한 sidecar는 이름만 보고 버리지 않는다. hot journal 삭제, 실행 중 DB raw copy, 열린 DB를 다른 inode로 교체하는 행위는 손상 위험이 있다. [SQLite 손상 원인과 피해야 할 조작](https://www.sqlite.org/howtocorrupt.html)

## 7. 과거 백업의 가장 큰 위험: 사라진 예약

과거 snapshot의 무결성이 정상이어도 최신 비용이 빠져 있을 수 있다. 이를 그대로 복원하면 일일 잔액과 중복 실행 이력이 과거로 돌아간다. **복원 성공은 API 재개 승인이 아니다.**

다음 정보를 UTC 날짜·run ID·attempt ID별로 대조한다.

- 현재/복구된 DB, snapshot, batch report와 안전한 실행 로그의 예약·정산 기록.
- 제공자 사용량·청구 자료·request ID. 본문이나 키를 로그에 추가하지 않는다.
- timeout·응답 분실·프로세스 종료로 사용량을 확정할 수 없는 예약 전액.
- snapshot 이후 시작한 실행 ID와 시도 ID. 비용뿐 아니라 replay 방지 이력도 보존해야 한다.
- 외부 dispatch, 후보 글, 검수 PR, publish manifest, 게시 URL tracker, 배포 SHA/RSS의 실제 상태. 이미 게시한 기사를 다시 번역하거나 재발행하지 않는다.

선택한 snapshot 시각 이후의 **누락된 모든 비용과 미정산 예약**을 복구 후보에 보존할 방법이 검증돼야 한다. 기존 API에는 과거 이력을 안전하게 병합하는 복구 migration이 없다. 필요한 경우 별도 검토 PR의 migration으로 원장 이력·policy·ID uniqueness를 보존한다. 불확실한 비용을 0으로 정산하거나 임시 새 원장에서 다시 시작하는 방법은 허용하지 않는다.

자료가 부족하면 maintenance를 유지한다. 보수적 비용 보존과 중복 방지 이력을 확정하지 못한 채 UTC 날짜가 바뀌었다는 이유로 재개하지 않는다. 자정 전환은 조사나 복구의 대체 수단이 아니다.

## 8. 검증된 후보 DB로 원자적 교체

아래는 **전체 writer 중지·영속 maintenance·기존 flock 보유·원본 보존·비용 대조 완료** 후의 순서다. 승인된 사고 기록이 없으면 실행하지 않는다.

1. 완성 snapshot 자체는 수정하지 않는다. 별도 staging DB를 활성 원장과 같은 파일시스템에 만들고, 필요한 승인 migration은 staging에만 적용한다.
2. staging DB를 read-only로 열어 5절 검증과 누락 비용/ID 대조를 다시 수행한다. policy·스키마·미정산 수·UTC 날짜별 실효 비용·파일 checksum을 확정한다.
3. **검증에 사용한 연결까지 모두 닫는다.** staging 파일을 fsync한다. 원본의 forensic copy가 완전한지 확인한다.
4. 모든 client가 멈춘 상태에서 이전 활성 sidecar를 보존 위치로 격리한다. 이전 hot journal/WAL/shm이 새 DB에 붙게 두지 않는다. 이 단계와 교체 사이에 전원이 끊겨도 maintenance는 해제되지 않아야 하며, 작업 단계 기록을 보고 사람이 전체 세트를 확인한다.
5. 기존 flock을 유지한 채 `os.replace(staged, active)`로 **DB 하나만** 원자적으로 교체한다. 활성 DB를 먼저 지우거나 이동하지 않는다. 잠금 파일은 unlink·rename·replace·재생성하지 않는다.
6. 활성 디렉터리를 fsync하고 DB 권한 0600·소유자·hardlink 수 1과 기존 lock device/inode 일치를 확인한다.
7. 같은 잠금 아래 새 활성 DB를 `mode=ro`로 열어 integrity/schema/policy/FK/예약 집계를 재확인하고 즉시 닫는다. 불일치하면 유지보수 중단 상태를 유지한다.

복원 도중 오류나 전원 장애가 나면 자동 재개하지 않는다. 새 DB와 이전 sidecar를 임의로 조합하지 말고 단계 기록·보존본·검증된 staging 상태를 확인한다. 재시도 역시 전체 writer 중지와 같은 기존 flock에서 수행한다.

## 9. 재개, launchd, 정책 변경

재개는 운영 책임자와 독립 검토자가 아래 기준을 함께 확인한 뒤 별도 기록으로 승인한다. 원격 배포·Secret·모델 호출 활성화는 이 문서의 실행 범위에 포함되지 않는다.

- DB·정책·모든 예약과 ID 이력이 대조됐으며 불명확한 사용량이 남으면 그 비용은 보수적으로 유지됐다.
- 현재 UTC 날짜만이 아니라 손실 가능성이 있는 과거 날짜도 대조했다.
- 출처·중복 게시 tracker·dispatch 재전송·이미 공개된 URL/배포 SHA를 확인했다.
- 새 실호출 전에 existing-DB preflight와 영속 maintenance gate가 실제 동작한다.
- maintenance 해제 후 처음에는 단일 검수 작업만 허용한다. 단순 예산 확인을 위해 `BudgetLedger.batch()`를 열어 run history를 오염시키지 않는다.
- 각 실행은 승인된 상한과 동일한 policy를 사용한다. cap 변경은 기존 예약을 보존하는 검토된 migration이며 경로 변경·새 빈 DB 생성으로 대체하지 않는다.

사용자 LaunchAgent는 로그인 세션에 의존한다. FileVault 부팅 잠금이나 사용자 로그인 전 실행을 보장하지 않는다. LaunchDaemon 전환은 계정·키 접근·권한·복구 책임을 따로 검토해야 한다. 이 문서에서는 launchd job을 설치·중지·재시작하지 않았고, 재부팅 후 무인 복구를 검증했다고 주장하지 않는다. 기존 [헤드리스 재부팅 복구 계획](macmini-headless-reboot-recovery.md)과 함께 운영 창을 잡는다.

## 10. 임시 리허설 증거와 활성화 체크리스트

2026-11-08의 별도 임시 DB 리허설 보고는 다음을 확인했다. 운영 production 경로와 실제 API는 사용하지 않았다.

- writer가 backup을, backup이 writer를 차단하는 상호 배타 잠금.
- `mode=ro`와 `closing`을 사용한 backup의 integrity·schema·policy·FK·예약 row 일치.
- 오래된 snapshot의 비용 500과 최신 900 micro-USD 사이에 **400 micro-USD가 누락**되는 재현.
- 최신 복원 후보에서 미정산 예약 2개와 잔여 예산 100 micro-USD 유지, 100 초과 예약 거부.
- DB 교체 후 기존 lock inode 유지, 손상 DB 거부, 원본 backup SHA-256 불변.

임시 보고 파일은 `techblog-ledger-drill-final-4jbb6yk4/drill-report.json`으로 생성됐다. 임시 경로의 장기 존재는 보장하지 않는다. 실제 power-loss, SSD 장애, 오프호스트 복원, Time Machine, 자동 일정, 운영 계정 권한/로그인 복구는 검증하지 않았다. fsync 절차와 목표 RPO/RTO는 해당 실패 시험을 대신하지 않는다.

| 책임 역할 | 활성화 전에 확정할 산출물 | 현재 상태 |
|---|---|---|
| 운영 책임자 | 실행 계정, canonical 경로, bootstrap 승인, 예산 상한 | 제안, 담당자 명시 필요 |
| runner 관리자 | 단일 호스트·모든 writer 목록, 영속 maintenance, existing-DB preflight | 미배포 |
| 백업 담당자 | 잠금 조정 자동화, snapshot/manifest 검증, retention·공간 경보 | 미구현 |
| 보안/복구 검토자 | 암호화 외부 대상·키 보관·권한·복원 리허설 | 미결정 |
| 사고 대응 담당자 | 비용·usage·예약·dispatch·게시 tracker 대조 및 승인 기록 | 절차만 작성 |

- [ ] production 디렉터리와 승인 policy는 bootstrap 작업에서만 만든다.
- [ ] missing DB·기존 빈 DB·policy mismatch가 첫 API 호출 전에 실패한다.
- [ ] maintenance가 프로세스/호스트 재시작 이후에도 유지되는 시험을 통과한다.
- [ ] 원장·backup·incident 영역을 retention과 일반 디스크 정리에서 구분한다.
- [ ] snapshot·manifest checksum과 독립 보관 위치를 확인한다.
- [ ] 오프호스트 복원과 비용 누락 대조를 실제 운영 전 별도로 시험한다.
- [ ] 복구 후 비용뿐 아니라 run/attempt replay와 중복 게시도 차단한다.
- [ ] 실호출 재개와 정기 실행 활성화는 검수 증거를 남기는 별도 변경으로 수행한다.

## 공식 근거

- [SQLite Online Backup API](https://www.sqlite.org/backup.html): 일관된 snapshot 생성 방법.
- [SQLite How To Corrupt Your Database Files](https://www.sqlite.org/howtocorrupt.html): 활성 DB 복사·hot journal 삭제·열린 DB 교체의 위험.
- [Python 3.11 sqlite3.Connection.backup](https://docs.python.org/3.11/library/sqlite3.html#sqlite3.Connection.backup): Python backup API와 연결 수명 관리의 기준.
