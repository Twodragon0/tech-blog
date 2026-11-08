# 번역 비용 원장: 암호화 외부 백업과 복구키 보관 계획

상태: **설계 제안, 미활성화**. 작성·공식 문서 확인일: 2026-11-08.
이 설계 문서는 운영 버킷 생성, 운영 snapshot 암호화·업로드, 운영 키 생성·배포, IAM 변경을 수행하지 않는다.
Google 자격 증명이나 운영 원장을 읽어 적용 상태를 확인한 문서도 아니다.

## 1. 보관 목적과 보장 경계

Mac의 디스크와 함께 소실되지 않는 암호화 사본을 마련하고, 별도 장치에서 복구 가능성을 확인한다.
업로드 성공만으로 복구 가능성을 선언하지 않는다. 마지막 검증된 외부 사본의 시각과 복호화 시험 결과를 함께 남긴다.
마지막 **검증 완료된 외부 사본**은 실제 복구 가능 시점의 근거다. 그 사본의 나이와 허용 가능한 데이터 손실의 목표인 RPO를 구분한다. 외부 RPO 목표와 측정 방식을 승인하기 전에는 로컬 백업 주기나 예정된 업로드 주기만으로 달성을 선언하지 않는다.
현재 외부 사본과 키 보관을 만들지 않았으므로 달성한 RPO·RTO·전원 장애 복구 성공을 주장하지 않는다.

client-side encryption은 저장 서비스에 보내기 전 암호화하는 선택이다.
본 설계에서는 SQLite와 manifest를 묶은 tar를 age로 암호화하고 GCS에는 암호문만 보낸다.
서버 측 기본 암호화나 CMEK만으로 이 설계를 대체했다고 간주하지 않는다.
[공식: GCS client-side encryption](https://docs.cloud.google.com/storage/docs/encryption/client-side-keys)

## 2. 외부 저장소의 구체적 제안

| 항목 | 제안값 | 현재 상태 |
|---|---|---|
| 프로젝트 | 운영 호스트와 분리된 백업 전용 프로젝트 | 프로젝트·번호 미확정 |
| 버킷 | `twodragon-techblog-ledger-backups-<PROJECT_NUMBER>` | 이름 예약·생성하지 않음 |
| 리전 | 서울 `asia-northeast3` | 미설정 |
| 클래스 | STANDARD | 미설정 |
| 공개 접근 | 비공개, public access prevention, uniform bucket-level access | 적용 전 확인 필요 |
| live 사본 수명 | 생성 후 30일 삭제 lifecycle 제안 | 미설정 |
| soft delete | 삭제 후 7일 보관 제안 | 미설정 |
| Bucket Lock | 기본 도입하지 않음 | 잠금 작업 금지 |

`<PROJECT_NUMBER>`는 실제 값이 아닌 자리표시자다. 전 세계 이름 충돌과 조직 정책을 승인 시점에 확인한다.
미디어 저장용 버킷이 존재한다고 가정하거나 재사용하지 않는다. 이름에 비밀이나 개인 식별 정보를 넣지 않는다.
서울은 GCS의 `asia-northeast3` 리전이다. 지역 내 중복성과 호스트 외부 사본은 같은 개념이 아니다.
[공식: GCS locations](https://docs.cloud.google.com/storage/docs/locations)

객체 이름은 다음 한 형식으로 고정한다. `<UTC>`와 `<fingerprint>`도 실제 값이 아닌 자리표시자다.

```text
tech-blog/translation-ledger/twodragon-3/production/v1/<UTC>/<fingerprint>/snapshot.tar.age
```

`<UTC>`는 예를 들어 승인된 구현이 생성하는 UTC 시각, `<fingerprint>`는 검증된 manifest의 accounting fingerprint다.
암호문 이름은 키 회전 때 재사용하지 않는다. 새 UTC 경로로 생성하고 기존 generation을 덮어쓰지 않는다.
경로·크기·업로드 시각은 GCS 운영자에게 보일 수 있다. 원장 행이나 비밀을 객체 메타데이터로 복사하지 않는다.

## 3. 신원과 권한 분리

| 주체 | 계획된 권한·자료 | 금지하는 결합 |
|---|---|---|
| Mac 업로더 | 전용 버킷의 `roles/storage.objectCreator`, age 공개 recipient 파일 | 객체 읽기·삭제·덮어쓰기, age 개인키 |
| 외부 검증자 | 별도 신원의 `roles/storage.objectViewer`, 승인된 객체 readback | Mac 업로더와 같은 인증 수단 |
| 복구키 보관자 | 암호화된 age identity 보관본과 인출 절차 | Mac 또는 GitHub Secrets에 개인키 저장 |
| 백업 관리자 | 버킷·보존·IAM 변경을 검토하는 별도 관리자 | 업로더에 관리자 권한 부여 |

Object Creator는 객체 생성 역할이며 객체 내용 읽기·삭제·덮어쓰기를 허용하지 않는다.
Object Viewer는 객체·메타데이터 조회와 목록 권한을 제공한다. 정확한 최소 범위와 부가 권한은 승인 시 다시 확인한다.
업로드 방식이 추가 권한을 요구하면 업로더 권한을 넓히는 대신 업로드 구현을 재검토한다.
[공식: Storage IAM roles](https://docs.cloud.google.com/iam/docs/roles-permissions/storage)

클라우드 로그인에는 MFA를 적용하고 관리자·break-glass 신원은 일반 업로더와 분리할 계획이다.
이 MFA는 age 파일 복호화 조건이 아니다. 클라우드 접근 권한, 암호문 소유, 복호화 개인키는 서로 다른 경계다.
break-glass 절차와 백업 프로젝트의 접근 회복 수단을 호스트와 독립적으로 보관한다.
현재 인증 방식, 보관자, MFA 등록, break-glass 테스트는 미확정이며 변경하지 않았다.

## 4. age recipient와 identity의 보관

Mac에는 **공개 recipient 파일만** 배포한다. 개인 identity, 복호화 passphrase, password-manager 복구코드를 두지 않는다.
공개 파일도 무결성이 필요하다. 승인한 recipient 지문·버전과 실제 파일을 대조해 공격자 키로의 교체를 감지한다.
GitHub Secrets·워크플로 환경·저장소·Paseo 세션 로그에 age 개인키를 넣지 않는다.

age의 `-R`은 공개 recipient 목록, `-i`는 복호화 identity 파일을 받는다.
여러 recipient는 **각 수신자가 단독으로 복호화 가능한 OR 관계**다. 2-of-2 분할키나 MFA가 아니다.
passphrase로 암호화된 identity 파일을 사용할 수 있다는 점과 실제 보관 정책은 구분한다.
[공식: age CLI recipient·identity·다중 수신자](https://github.com/FiloSottile/age/blob/main/README.md)

계획은 primary 복구용과 escrow 복구용의 독립 recipient를 사용하는 것이다. 실제 키는 생성하지 않았다.
각 identity의 암호화된 보관본은 다음 두 독립 위치에 두고, 인출 시험을 따로 수행한다.

1. 호스트 밖의 MFA 보호 password manager: 암호화 identity와 승인된 보관자 접근 절차.
2. 별도 물리 장소의 암호화된 오프라인 USB: 암호화 identity와 인출 기록.

두 사본은 같은 디스크·클라우드 프로젝트·동기화 계정의 단일 장애에 묶지 않는다.
USB 해제 수단과 identity passphrase를 USB 또는 암호문과 함께 평문으로 두지 않는다.
password manager의 비상 복구 수단도 Mac에만 보관하지 않는다. 실제 제품·보관자·장소는 활성화 전에 지정한다.
두 보관본의 존재·복호화 가능성은 현재 미확인이다. 단순 복사 성공을 인출 시험으로 기록하지 않는다.

아래 이름은 실제 vault·매체가 아닌 배치 제안이다. 실제 계정과 보관자를 지정한 뒤 인출 시험으로 확정한다.

| 자료 | 제안 위치·논리 이름 | 인출 규칙 |
|---|---|---|
| 공개 recipient 목록 | Mac `~/.config/tech-blog/translation/offsite/recipients.txt` | 승인 지문·버전만 비교, 파일 0600 |
| primary 암호화 identity | off-host vault `TechBlog/Ledger/primary/v1` + 암호화 USB `ledger-primary-v1` | vault의 별도 secret field에 passphrase, 인출 기록 |
| escrow 암호화 identity | 별도 보관자 vault `TechBlog/Ledger/escrow/v1` + 다른 장소의 암호화 USB `ledger-escrow-v1` | primary 계정 잠금 시에도 독립 인출 가능하게 설계 |
| 오프라인 passphrase·vault 비상 복구 수단 | USB와 다른 장소의 봉인 보관물 `ledger-key-recovery-v1` | 해당 보관자만 개봉, 사용자·일시·key version 기록 |

vault의 secret field는 암호화된 vault 안의 값이지 파일 옆 평문 문서가 아니다. 봉인 보관물에 들어갈 실제 값은 이 문서·Git·채팅에 기록하지 않는다. cloud 계정 복구 코드와 암호화 키 인출 수단도 서로 혼동하지 않는다.

## 5. 로컬 snapshot에서 암호화 사본까지

1. 기존 flock을 공유하는 backup 도구로 새 private snapshot을 만든다. 실행 중 SQLite 파일을 임의 복사하지 않는다.
2. 성공한 snapshot의 `budget.sqlite`와 `manifest.json`만 목록화한다. 원장·lock·marker 원본 경로를 tar 대상으로 지정하지 않는다.
3. snapshot manifest의 파일 크기·SHA-256·schema·policy·accounting fingerprint 검증을 완료한다.
4. 임시 작업 디렉터리는 호스트의 승인된 로컬 위치에 0700으로 만들고 파일은 0600으로 제한한다.
5. 두 파일을 상대 경로로만 tar에 넣고 공개 recipient 파일로 age 암호화한다.
6. 출력 암호문을 새 이름으로 생성하고 종료 상태·파일 크기·암호문 SHA-256을 기록한다.
7. 평문 tar가 필요하면 0700 작업 영역에만 만들고 검증 후 보존 정책에 따라 정리한다. 평문은 업로드하지 않는다.

완료 manifest가 없는 부분 snapshot은 백업 대상으로 선택하지 않는다. tar에 symlink·절대경로·상위경로를 허용하지 않는다.
이 런북은 실제 암호화 명령을 실행하지 않았다. 구현 시 사용 age 버전과 공개 recipient 배포·고정 방식을 검토한다.
age는 수신자 암호화 도구이며 생성 주체에 대한 별도 서명 증명을 제공한다고 가정하지 않는다.
암호문 해시는 손상 검사용이다. 공격자가 파일과 해시를 함께 바꿀 수 있는 저장 위치만으로 진위를 증명하지 않는다.

## 6. 생성 전용 업로드와 외부 검증

1. 업로더는 승인된 이름의 암호문만 전송하고, JSON API 기준 `ifGenerationMatch=0`을 요청한다.
2. 같은 live 객체가 이미 있으면 412 응답을 충돌로 기록한다. precondition을 제거해 재시도하지 않는다.
3. 응답의 bucket·object·generation·크기와 로컬 암호문 SHA-256을 외부 검증 기록에 연결한다.
4. 응답이 유실되면 업로더는 읽기 권한이 없으므로 성공을 추정하지 않고 검증자에게 확인을 요청한다.
5. 별도 검증자가 그 generation을 지정해 readback하고 암호문 SHA-256을 대조한다.
6. 승인된 off-host 복구 환경에서 복호화·manifest·전체 SQLite 검증까지 통과한 사본만 verified로 표시한다.

generation-match 0은 같은 이름의 live 객체가 없는 경우에만 쓰기를 허용한다.
noncurrent 또는 soft-deleted 사본의 영구 부재까지 뜻하지 않으므로 이름·generation 기록을 함께 사용한다.
[공식: request preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions)

검증자에게 업로드·삭제 권한을 묶지 않는다. 검증 과정의 임시 복호화 권한은 보관자 절차에 따라 따로 인출한다.
호스트가 암호문을 만들고 전송했다는 기록만으로 off-host restore proof를 대체하지 않는다.
최초 활성화 시 각 recipient의 인출 시험을 별도로 진행하고 실패한 recipient는 준비 완료로 표시하지 않는다.

## 7. 보존·비용·경보

제안은 live 객체를 30일 경과 후 lifecycle로 삭제하고, 삭제된 객체를 soft delete로 7일 더 보존하는 것이다.
lifecycle은 비동기이므로 정확히 30일째 삭제·37일째 영구 제거를 보장하지 않는다. 별도 retention hold가 있으면 더 길어질 수 있다.
soft-deleted 사본의 저장 비용도 고려한다. 삭제 후 정책 변경을 모든 기존 사본에 소급되는 보장으로 읽지 않는다.
[공식: lifecycle](https://docs.cloud.google.com/storage/docs/lifecycle), [공식: soft delete](https://docs.cloud.google.com/storage/docs/soft-delete)

이 30일은 lifecycle 제안이지 최소 30일 보존을 강제하는 잠긴 retention 정책이 아니다.
관리자 권한 탈취까지 포함한 WORM 요구는 별도 설계·승인이 필요하다. 생성 전용 업로더만으로 관리자 삭제를 막지는 못한다.
Bucket Lock은 잠그면 retention 기간을 줄이거나 제거할 수 없는 비가역 동작이므로 기본 도입하지 않는다.
[공식: Bucket Lock](https://docs.cloud.google.com/storage/docs/bucket-lock)

STANDARD 저장량 외에 요청·readback 전송·복원·soft-delete 잔여 저장량을 비용에 포함한다.
현재 지역·청구 계정의 실제 단가는 확인하지 않았으며 USD 금액을 제시하지 않는다.
예산 알림과 업로드량 경보는 제안일 뿐 서비스의 하드 지출 상한이 아니다. 비용 초과 시 적용할 운영 중지 절차를 따로 승인한다.
[공식: Storage pricing](https://cloud.google.com/storage/pricing)

## 8. 키 회전·분실·유출

회전은 cloud IAM 토큰 회전과 별도로 관리한다. 새 recipient를 승인하고 off-host 인출·복호화 시험 후 신규 암호문부터 적용한다.
오래된 암호문은 기존 키를 요구할 수 있다. public recipient 목록을 수정해도 이미 저장된 age 파일의 접근이 철회되지는 않는다.
다음 순서는 age 수신자 동작을 바탕으로 한 이 운영 설계의 정책이며, 자동 키 폐기 기능이라는 뜻은 아니다.

1. primary 또는 escrow 변경 시 새 공개 recipient 버전을 승인하고 Mac의 공개 파일만 교체한다.
2. 필요한 과거 사본은 off-host에서 복호화하고 새 recipient로 다시 암호화해 새 객체 이름으로 검증 업로드한다.
3. 구 recipient 암호문·다운로드 사본·quarantine·soft-deleted generation의 목록과 만료를 확인한다.
4. **모든 구 암호문 사본과 soft-delete 기간이 끝날 때까지** 해당 구 개인키를 안전하게 보관한다.
5. 보존 종료·복구 필요성·법적 보존 여부를 재검토한 후 보관자가 키 폐기를 승인하고 기록한다.

키 유출 시 새 암호문 보호를 위해 recipient를 교체해도 유출된 구 암호문을 다시 비밀로 만들 수는 없다.
개인키 분실은 GCS 관리자나 MFA로 우회할 수 없다. 남은 독립 recipient와 보관본이 모두 없으면 암호문은 복구 불가로 처리한다.
기존 키를 조기 폐기하거나 새 키로 복호화할 수 있다고 추정해 백업 검증을 통과시키지 않는다.

## 9. 복원 인출과 현재 도구의 한계

1. 별도 신원으로 선택한 객체 generation·검증 기록·암호문 해시를 확보한다. 운영 Mac에서 키를 인출하지 않는다.
2. off-host의 격리된 0700 오프라인 작업 영역에서 승인된 암호화 identity를 인출하고 복호화한다.
3. tar 항목이 상대경로의 승인된 두 regular 파일뿐인지 확인한 후 안전하게 추출한다.
4. 복호화된 manifest의 SHA-256·크기·엄격한 schema와 SQLite 전체 integrity·policy·회계 기록을 검증한다.
5. 실제 복원 전 일치하는 maintenance operation ID와 기존 flock, 정상 current DB를 확인한다.
6. 현재 restore 도구는 **현재 모든 accounting records와 정확히 같은 상태**의 snapshot만 허용한다.
7. restore 후에도 maintenance는 유지한다. 별도 건강 검사와 승인된 clear 절차 전까지 번역을 재개하지 않는다.

과거 snapshot이 정상이어도 그 이후 비용이 있다면 현재 도구로 되돌리지 않는다. 누락·손상된 current DB도 복원 허용 조건이 아니다.
그 경우 기존 보존 증거와 공급자 사용량 등을 대조하는 별도 검토된 회계 조정·복구 절차가 필요하며, 이 문서는 override를 제공하지 않는다.
복호화 시험 성공과 운영 원장 복원 허용은 다른 판정이다. 시험을 위해 실제 원장·marker·키 보관 위치를 변경하지 않는다.

## 10. 활성화 전 필수 확인

- [ ] 실제 프로젝트 번호, 전용 버킷 이름 가용성, 리전·비공개 정책과 책임자를 승인했다.
- [ ] 업로더·검증자·관리자 신원과 최소 권한, MFA·break-glass 접근을 시험했다.
- [ ] primary·escrow의 공개 recipient 지문과 두 독립 암호화 개인키 보관본을 확인했다.
- [ ] 각 보관본 인출과 off-host 복호화·전체 SQLite 검증에 성공했다.
- [ ] 30일 lifecycle·7일 soft-delete 비용과 키 회전 보존 기간, 비용 알림 책임자를 승인했다.
- [ ] 업로드 generation·암호문 hash·manifest fingerprint·restore proof 기록을 호스트 밖에 보존할 위치를 정했다.
- [ ] 현행 EXACT-state 복원 제약과 current 손상 시 별도 복구가 필요함을 담당자가 이해했다.

이 항목이 확인되기 전 상태는 미활성화다. 문서 작성만으로 외부 백업이나 키 보관이 구성됐다고 보고하지 않는다.

## 임시 암호화와 실제 대상의 사전 점검

[age fixture 검증과 사전 점검 기록](../pipeline/2026-11-08-translation-age-offsite-preflight.md)에서 임시 키의 왕복·거부 시험과 기존 Cloud 계정·프로젝트·버킷·로컬 경로·1Password CLI 메타데이터를 구분했다. 실제 프로젝트·보관자·운영 키와 외부 사본은 아직 확정·배포하지 않았다.
