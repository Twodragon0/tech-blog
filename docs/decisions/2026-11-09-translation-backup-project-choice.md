# 번역 원장 외부 백업: 기존 프로젝트와 전용 프로젝트 선택

작성일: 2026-11-09. 상태: **조건부 설계 권고, 대상 미선택·미배포**.
이 결정서는 프로젝트·계정·버킷 생성, 결제 연결, IAM 변경, 키 생성·복사·인출을 승인하거나 수행하지 않는다.
공식 동작은 작성 시 문서를 확인했고 실제 계정 관측은 아래의 **11월 8일 기록**에만 의존한다.

## 1. 먼저 결정할 결과

**B: 전용 백업 프로젝트를 승인 후 구성하는 방안을 권고한다.**
백업 리소스의 변경·비용·권한 검토를 일반 워크로드와 구분하기 쉽기 때문이다.
이 권고는 새 프로젝트를 이미 만들 수 있거나, 청구 계정에 연결할 권한이 확인됐다는 의미가 아니다.
현재 Go 판정은 양쪽 모두 보류다. 프로젝트, 버킷, vault, primary·escrow 보관자와 인출 시험이 확정되지 않았다.
A의 제한적 시험은 명시한 조건을 모두 충족하고 종료·이전 기한을 승인한 경우에만 예외로 검토한다.

## 2. 이미 관측한 사실과 아직 모르는 것

| 항목 | 2026-11-08에 기록한 사실 | 이번 결정에 쓰는 한계 |
|---|---|---|
| 기본 프로젝트 | project ID·number 조회 성공, ACTIVE | 11월 9일 현재 상태나 백업 승인 증거 아님 |
| 해당 프로젝트의 버킷 | 조회 범위 내 목록 0개 | 다른 프로젝트·비가시 리소스의 부재 아님 |
| 이름 필터 전용 후보 | 지정 필터에서 프로젝트 0개 | 전용 프로젝트가 전혀 없다는 결론 아님 |
| 활성 CLI 계정 | 활성 계정 1개 | 생성·결제·객체 쓰기 권한 증거 아님 |
| password manager | CLI account list 0개 | GUI 계정·vault 부재 증거 아님 |
| 운영 원장·policy·recipient | 제안 경로에 없음 | 실제 활성화·복호화 준비 미완료 |
| 프로젝트·vault·보관자 | 미선정·미검증 | 현재 기본값을 자동 채택할 수 없음 |

실제 식별자·계정 이메일·project number는 이 공개 문서에 기록하지 않는다.
[11월 8일 관측 범위](../pipeline/2026-11-08-translation-age-offsite-preflight.md)를 참조한다.
이번 문서 작성 중 실제 Google·vault 메타데이터를 다시 조회하지 않았다.

## 3. 프로젝트와 버킷이 나누는 경계

프로젝트는 API·권한·비용을 조직하는 단위이며 그 안에 버킷 같은 서비스 리소스가 속한다.
별도 버킷은 객체 경로·수명·버킷 IAM을 나눌 수 있지만 같은 프로젝트의 변경·삭제·상속 정책 경계를 공유한다.
[공식: Resource hierarchy](https://docs.cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy), [프로젝트 특성](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)

버킷에 작은 allow 역할을 주어도 상위 프로젝트·폴더·조직에서 상속된 넓은 allow 권한을 축소하지 못한다.
전용 프로젝트도 같은 폴더·조직의 권한을 상속하므로 관리자·그룹 구성원을 함께 검토해야 한다.
[공식: IAM 상속과 effective allow 정책](https://docs.cloud.google.com/iam/docs/resource-hierarchy-access-control)

같은 계정·관리자가 두 프로젝트를 제어하거나 같은 조직 정책에 묶이면 공통 장애·침해 경로가 남는다.
프로젝트별 Owner가 서로 다르면 한쪽 Owner 권한만으로 다른 프로젝트를 자동 제어하는 것은 아니다.
동일 인물의 두 Owner 권한이나 조직 관리자 권한이 함께 탈취되는 상황은 별도로 평가한다.
따라서 B도 완전히 독립된 재해·보안 경계라고 표현하지 않는다.

Cloud Billing 연결은 IAM 부모 관계가 아니다. 같은 billing account가 객체 읽기 권한을 자동 부여하지 않는다.
다만 공유된 결제·결제 관리자 문제는 두 프로젝트의 이용 가능성에 영향을 주는 공통 운영 위험이다.
프로젝트 생성, 결제 연결, 비용 조회는 필요한 권한이 다르므로 실제 권한 검증과 담당자 승인이 필요하다.
[공식: Cloud Billing 권한과 결제 연결](https://docs.cloud.google.com/billing/docs/how-to/billing-access)

## 4. 선택지 비교

| 기준 | A: 현재 기본 프로젝트 + 전용 버킷 | B: 새 전용 백업 프로젝트 |
|---|---|---|
| 노출 범위 | 기존 서비스·상속 관리자와 같은 프로젝트 경계 | 일반 워크로드의 프로젝트별 변경과 분리 가능 |
| 정책 | 기존 프로젝트 정책·로그 설정과 충돌 검토 | 백업 목적 정책을 별도 검토, 상위 상속은 여전히 존재 |
| IAM | 버킷 범위 최소 권한 가능, 상위 넓은 역할 주의 | 프로젝트·버킷 역할을 백업 목적으로 구분 가능 |
| 비용 가시성 | 전용 버킷·레이블과 비용 분류 필요 | 프로젝트 단위 추적·책임 구분이 상대적으로 명확 |
| 준비 권한 | 기존 프로젝트의 버킷·IAM 변경 승인 필요 | 프로젝트 생성·부모 위치·결제 연결 승인도 필요 |
| 복구 운영 | 기존 서비스의 장애 대응과 담당자가 섞일 위험 | 별도 복구 담당·연락 경로 설계가 쉬우나 준비 부담 증가 |
| 키 보관 | off-host 독립 보관이 필수 | 프로젝트 분리와 관계없이 같은 요구 |
| 현재 확인 | ACTIVE·빈 버킷 목록이라는 과거 관측만 있음 | 실재·가용 이름·권한·결제 미확인 |

두 선택지 모두 미디어 버킷 재사용을 전제하지 않고 백업 전용 비공개 버킷을 설계한다.
이 비교는 비용 절감액이나 가용성 수치를 제시하지 않는다. 실제 요금·청구 조건은 별도 확인 대상이다.

## 5. 양쪽에 공통인 보안·보존 요구

- 업로더는 버킷 범위 `roles/storage.objectCreator`, 검증자는 별도 `roles/storage.objectViewer` 신원을 계획한다.
- Creator는 생성만 가능하고 내용 읽기·삭제·덮어쓰기를 허용하지 않는다. 상속된 다른 역할도 함께 대조한다.
- Mac에는 승인한 age 공개 recipient만 두고 운영 private identity·복호화 passphrase는 두지 않는다.
- 클라우드 로그인·MFA·break-glass와 age primary·escrow 보관을 서로 다른 복구 경로로 관리한다.
[공식: GCS 역할](https://docs.cloud.google.com/iam/docs/roles-permissions/storage)

UBLA는 ACL 대신 IAM으로 객체 접근을 관리한다. PAP는 공개 노출 방지 계층이며 서명 URL 공유까지 막는 장치는 아니다.
서명 URL을 새로 발급하는 방식으로 검증자 분리를 우회하지 않는다.
[공식: UBLA](https://docs.cloud.google.com/storage/docs/uniform-bucket-level-access), [PAP의 적용 범위](https://docs.cloud.google.com/storage/docs/public-access-prevention)

제안은 서울 STANDARD, live 사본 30일 lifecycle 삭제·soft delete 7일이며 모두 미설정이다.
보존·soft delete·Bucket Lock은 프로젝트·계정 삭제나 자격 증명 상실까지 해결하는 만능 경계가 아니다.
프로젝트 삭제에는 별도 복원 절차와 시간 제한이 있다. 이를 유일한 백업 복구 수단으로 의존하지 않는다.
[공식: 프로젝트 삭제·복원](https://docs.cloud.google.com/resource-manager/docs/delete-restore-projects), [soft delete](https://docs.cloud.google.com/storage/docs/soft-delete)

잠긴 retention 정책은 줄이거나 제거할 수 없는 비가역 변경이므로 기본 적용하지 않는다.
별도의 WORM 요구가 생기면 잔여 보존·삭제·청구 책임을 검토해 다시 결정한다.
[공식: Bucket Lock](https://docs.cloud.google.com/storage/docs/bucket-lock)

암호문이 모두 삭제되면 off-host 개인키만으로 원장을 복구할 수 없다.
반대로 암호문을 보유해도 유효한 recipient의 개인키와 인출 수단을 모두 잃으면 복호화할 수 없다.
키와 암호문을 각각 독립적으로 보관·검증해야 한다.

## 6. A의 제한적 시험 Go / No-Go

A는 B 준비를 생략하는 영구 기본값이 아니다. 아래 조건 중 하나라도 미충족이면 No-Go다.

- [ ] 기존 프로젝트 소유자가 백업 시험·비용·보존 책임을 명시적으로 승인했다.
- [ ] 상위 상속 역할, 기존 공개 정책과 로그·수명 설정을 검토했고 허용 가능한 범위를 기록했다.
- [ ] 우선 합성 데이터·임시 키로 시험하며 운영 평문·운영 private key를 업로드하거나 Mac에 반입하지 않는다.
- [ ] 업로더·검증자 분리, generation precondition, hash·off-host 복호화 증거를 확보한다.
- [ ] 시작일·종료일·데이터량 한도·B 이전 담당자를 확정한다. 종료일 없는 시험은 승인하지 않는다.
- [ ] 운영 원장 암호문으로 전환하려면 B와 동일한 운영 키 보관·복구 조건을 별도 승인한다.

실패 시 새 업로드를 중지하고 증거를 보존한다. 기존 프로젝트 전체를 삭제하거나 IAM을 일괄 초기화하지 않는다.
시험 종료 때 데이터 보존·soft delete·키 보존 의무를 대조해 해당 시험 리소스만 후속 정리한다.
이 문서에서는 리소스 삭제나 권한 회수를 실행하지 않는다.

## 7. B의 조건부 Go / No-Go

B의 권고는 다음 승인과 시험을 통과한 뒤 실행 단계로 전환한다.

- [ ] 프로젝트 소유·폴더/조직 위치·상속 관리자와 독립 복구 담당자를 결정한다.
- [ ] 생성 권한과 결제 연결 권한·실제 비용 조회 권한을 각각 확인한다.
- [ ] 전용 버킷 이름 가용성·서울 지역·UBLA·PAP·보존 설정을 검토한다.
- [ ] 기존 일반 워크로드 서비스 계정에 백업 읽기·삭제 권한이 자동 포함되지 않는지 확인한다.
- [ ] 두 독립 키 보관 위치와 primary·escrow 각각의 인출·복호화 시험을 완료한다.
- [ ] generation 지정 readback·완전한 snapshot audit와 외부 증거 보존을 완료한다.

버킷 이름 제안 `twodragon-techblog-ledger-backups-<PROJECT_NUMBER>`는 미생성 placeholder다.
B 준비 실패 시 A로 자동 fallback하지 않는다. 실패 단계·원인을 남기고 승인된 경로를 다시 선택한다.

## 8. 비용 통제와 실행 작업 단위

프로젝트 분리만으로 지출 상한이 생기지 않는다. 제안하는 alerts-only budget은 알림이며 사용·청구를 자동 차단하지 않는다.
현재 공식 문서는 일부 서비스의 spend-cap budget도 구분하지만 이 GCS 구성·계정에서 지원·적용됐는지는 검증하지 않았다.
하드 상한으로 간주하지 말고 경보 수신·중지 결정·보존 의무를 운영 절차로 정한다.
[공식: budgets와 alerts-only 한계](https://docs.cloud.google.com/billing/docs/how-to/budgets)

| 단위 | 다음 승인·실행 범위 | 완료 증거 | Go 조건 |
|---|---|---|---|
| W1 | A/B와 책임자·시험 기한 결정 | 승인된 선택·범위 기록 | 미확정이면 중지 |
| W2 | 실제 프로젝트·부모 IAM·결제 권한 확인 | 식별자 비공개 대조표·역할 검토 | 필요한 권한·소유 확인 |
| W3 | 승인된 버킷·역할·보존 구성 | 설정 diff·복구/비용 책임 기록 | 별도 변경 승인 |
| W4 | off-host 키 보관·인출 | 각 recipient 시험·독립 보관 증거 | 실제 키는 Git 밖에서 관리 |
| W5 | 합성 암호문 업로드·검증 | generation·hash·복호화 audit | 실패 시 운영 데이터 금지 |
| W6 | 승인된 운영 경로 연결 | 마지막 검증 사본·RPO 목표·경보 시험 | 조용한 fallback 없음 |

W3~W6은 새 유료 리소스·IAM·키 작업을 포함할 수 있어 이 문서만으로 실행하지 않는다.
계정 생성이나 관리자 권한 확대를 편의상 먼저 수행하지 않는다. 새 Cloud Billing account 생성도 기본 요구가 아니다.

## 9. A에서 B로의 이전과 되돌림

1. B의 승인·권한·정책·키 보관 조건을 먼저 충족하고 A의 신규 업로드를 잠시 중지한다.
2. 이전할 객체의 bucket·name·generation·암호문 hash·key version·보존 상태를 비공개 목록으로 고정한다.
3. destination에는 새 이름과 generation-match 0을 적용하고 source generation도 고정해 복사한다.
4. 412나 불명확한 응답에서 조건을 제거하거나 기존 객체를 덮어쓰지 않는다.
5. 별도 검증자가 B의 해당 generation을 readback하고 암호문 hash·복호화·manifest·SQLite audit를 대조한다.
6. B가 검증된 뒤에만 다음 업로드 목적지를 전환하고 마지막 검증 시각·감시 경로를 갱신한다.
7. A는 검증·보존 종료 전 삭제하지 않는다. B 검증 실패 시 A를 보존하고 승인된 기존 경로로만 재개한다.
[공식: source/destination preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions)

키도 바꾸면 새 recipient로 재암호화한 별도 객체를 검증한다. 기존 ciphertext의 키가 자동 교체된다고 가정하지 않는다.
구 개인키는 모든 구 암호문·다운로드·quarantine·soft-deleted 사본의 보존이 끝날 때까지 안전하게 유지한다.
이전 실패의 되돌림은 목적지 전환을 취소하는 절차이며 프로젝트 삭제·정책 약화·과거 원장 덮어쓰기가 아니다.

## 10. 복원 도구와 최종 미결 사항

현재 restore 도구는 정상 current DB와 모든 accounting records가 정확히 같은 snapshot만 허용한다.
stale snapshot, missing/corrupt current DB는 의도적으로 거부한다. 이는 일반적인 재해 복구 override 도구가 아니다.
과거 비용이 누락된 상태는 별도 검토된 회계 조정·복구 절차가 필요하며 프로젝트 선택으로 이 제약이 사라지지 않는다.

미결: 실제 프로젝트·버킷, 상속 IAM·결제 범위, vault·primary/escrow 보관자, 독립 연락·복구 수단, 시험 종료일, RPO 목표.
승인 전 결론은 **B 권고·양쪽 미활성화**다. 이후 구성·키·외부 복구 증거는 [암호화 외부 백업 런북](../runbooks/translation-ledger-encrypted-offsite-backup.md)에 따라 별도로 수집한다.
