# age fixture 검증과 외부 백업 활성화 사전 점검

점검일: 2026-11-08. PR #814는 CI 통과를 확인한 뒤 `4f77ed66`으로 병합했다. 이번 단계는 합성 fixture의 임시 키 검증과 기존 계정·프로젝트·버킷 메타데이터의 읽기 전용 확인이다. 운영 버킷·IAM·로그인·보관자·운영 키를 구성한 단계는 아니다.

## age 실행 도구의 출처

Mac의 PATH에는 age와 age-keygen이 없었다. 공식 age v1.3.2의 `darwin-arm64` 배포본을 private 임시 디렉터리에 내려받아 공식 GitHub release asset metadata의 SHA-256과 비교한 뒤 실행했다. 시스템 설치나 프로젝트 패키지 의존성은 추가하지 않았다.

| 항목 | 확인값 |
|---|---|
| 실행 버전 | `v1.3.2` |
| 배포 파일 | `age-v1.3.2-darwin-arm64.tar.gz` |
| SHA-256 | `e2020b073c44f692685a24d6abc378817eb81ffaaf49fd0531ef8565f767f2f5` |
| 사용 파일 | tar 안의 regular `age`, `age-keygen` 두 파일만 선택 |
| 설치 범위 | 임시 디렉터리, 호스트 PATH·Homebrew·Go 설정 변경 없음 |
| 공급망 검증 범위 | 공식 TLS 다운로드·GitHub metadata digest 일치; Sigsum proof 검증은 수행하지 않음 |

이는 fixture 검증을 위한 실행 출처 확인이며 운영 배포용 공급망 검토를 대체하지 않는다. [공식 age v1.3.2 릴리스](https://github.com/FiloSottile/age/releases/tag/v1.3.2), [공식 Sigsum 절차](https://github.com/FiloSottile/age/blob/main/SIGSUM.md)

## 임시 키와 합성 snapshot 검증

[age 리허설 도구](../../scripts/rehearse_translation_age.py)는 명시적으로 지정한 age·age-keygen 실행 파일만 사용한다. 호출자는 평문·identity·recipient·운영 ledger 경로를 제공할 수 없다. 자체 private TemporaryDirectory 안에서 합성 SQLite snapshot과 manifest를 tar에 묶고 native 임시 identity를 생성한다.

같은 암호문을 primary와 escrow identity가 각각 복호화해 원본 tar bytes와 snapshot 회계 기록을 대조한다. 제3의 identity와 변조된 암호문은 거부해야 한다. 이 다중 recipient는 각각 하나의 identity로 열리는 OR이며 2-of-2 비밀 분산이 아니다. 임시 identity·recipient·평문·암호문·원문 subprocess 출력은 report에 넣지 않는다. [age 공식 사용법](https://github.com/FiloSottile/age/blob/main/README.md)

예시는 운영 키가 아닌 임시 바이너리와 fixture만 사용한다. 두 실행 파일 경로는 검증한 실제 임시 경로로 지정하고, 출력 디렉터리는 새 이름을 사용한다.

```bash
python scripts/rehearse_translation_age.py \
  --age-bin /tmp/verified-age-tools/age \
  --age-keygen-bin /tmp/verified-age-tools/age-keygen \
  --output /tmp/age-fixture-rehearsal-01
```

[리허설 구현](../../scripts/rehearse_translation_age.py)을 참고한다. 결과 보고서와 오류 메시지에 키 자료가 없음을 검사하고 임시 fixture를 정리한다. 운영 private key의 분리 보관·회전·인출 증거는 이 테스트와 별개다.

## 실제 백업 대상의 읽기 전용 사전 점검

계정·프로젝트 식별자는 공개 저장소에 복사하지 않는다. 소유자가 확인할 실제 project ID·number와 읽기 전용 결과는 로컬 private 파일 `/private/tmp/techblog-offsite-preflight-20261108.json`에 기록했다(0600). 이 파일의 장기 보존은 보장하지 않는다.

| 점검 항목 | 관측 결과 | 확정 전에 남은 조건 |
|---|---|---|
| Google Cloud CLI | 설치돼 있음 | 도구 설치와 백업 권한 준비를 구분 |
| 활성 Google 계정 | 활성 계정 1개 조회됨 | 백업 업로더·검증자·관리자 역할을 승인해야 함 |
| 현재 기본 프로젝트 | project ID·number 조회 성공, lifecycle ACTIVE | 백업 전용으로 승인된 대상은 아님; 자동 채택하지 않음 |
| 이름으로 찾은 전용 후보 | `twodragon`/`techblog`/`backup` project ID 필터에서 0개 | 권한·필터 범위 밖 프로젝트의 부재를 의미하지 않음 |
| 현재 기본 프로젝트의 버킷 | 메타데이터 조회 성공, 목록 0개 | 다른 프로젝트나 전 세계 버킷의 부재를 의미하지 않음 |
| 전용 백업 버킷 | 선택·생성·이름 예약하지 않음 | 승인 프로젝트 번호, 이름 가용성과 지역·보안 설정 확인 필요 |
| 운영 정책 JSON | 제안 경로에 없음 | 승인 policy와 책임자를 기록해야 함 |
| 공개 recipient 파일 | 제안 경로에 없음 | off-host 운영 키 생성·인출 시험 후 공개 파일 지문 승인 필요 |
| 운영 장부 | 제안 production 경로에 없음 | 별도 승인 bootstrap·existing-DB preflight·운영 진입점 연결 필요 |
| 1Password CLI | 설치됨, account list 결과 0개 | GUI 계정·다른 인증 모드·실제 vault의 부재를 뜻하지 않음 |
| 실제 vault 접근 | 미검증, vault 항목·키 내용 읽지 않음 | 승인된 계정·보관소와 인출 권한 확인 필요 |
| primary/escrow 보관자 | 미확정 | 사람·대리자·독립 연락/복구 수단을 지정해야 함 |
| 암호화 오프라인 매체·키 사본 | 미검증 | 두 독립 위치와 해제 수단을 분리하고 인출 시험 필요 |

기본 프로젝트가 ACTIVE이고 버킷 조회가 가능하다는 사실만으로 objectCreator/objectViewer 역할이나 새 프로젝트 생성·결제 연결 권한이 검증됐다고 보고하지 않는다. 미선택 프로젝트의 IAM·billing을 임의 변경하거나 계정 로그인·MFA 승인을 시도하지 않았다.

## 확정 순서와 완료 증거

1. 실제 백업 프로젝트를 선택하고 소유·청구·책임자를 확인한다. 현재 기본 프로젝트를 쓸지, 계획대로 전용 프로젝트를 분리할지 승인 기록을 남긴다.
2. 승인된 번호를 버킷 이름에 넣고 이름 가용성을 확인한다. 미생성 이름의 가용성은 예약·생성 성공과 다르다. 서울·STANDARD·비공개·수명·soft-delete 정책을 검토한다.
3. 업로더와 검증자, IAM 변경 관리자 신원을 분리해 승인하고 최소 권한을 검증한다. 현재 로그인 계정을 자동으로 모든 역할에 배정하지 않는다.
4. primary/escrow 보관자와 실제 vault·USB·봉인 보관물의 인출 책임자를 정한다. 승인된 off-host 환경에서 운영 키를 만들고 각 독립 사본의 인출 시험을 한다.
5. recipient 지문·버전을 승인해 Mac에는 공개 파일만 배포한다. 현재 임시 fixture identity를 운영 키로 승격하거나 복사하지 않는다.
6. 별도 승인된 암호화·업로드·generation 지정 readback·off-host 복호화 시험을 수행한다. 모든 증거가 모이기 전에는 외부 백업 준비 완료로 표시하지 않는다.

실제 대상의 보관·키 분리·회전/분실 절차는 [암호화 외부 백업 런북](../runbooks/translation-ledger-encrypted-offsite-backup.md)을 따른다. 이 문서는 미확정 대상을 확정됐다고 가정하거나 새로운 지출·자격 증명 변경을 승인하는 문서가 아니다.

## 이번 검증 결과와 재실행 조건

실제 공식 바이너리 v1.3.2를 지정한 리허설에서 `status=validated`와 primary/escrow 독립 왕복, 잘못된 identity 거부, 암호문 변조 거부, 평문·snapshot 회계 보존의 여섯 판정이 모두 true였다. 결과는 `/private/tmp/techblog-age-proof-20261108-01/report.json`에만 보존했다. 해당 디렉터리에는 키·recipient·평문·암호문이 없다.

집중 검사 11개를 실제 age 바이너리로 실행해 모두 통과했으며 skip은 없었다. Ruff·format·Mypy와 별도 읽기 전용 crypto/privacy 검토도 통과했다. 테스트는 `AGE_REHEARSAL_BIN`, `AGE_REHEARSAL_KEYGEN_BIN`에 명시적인 검증 바이너리를 지정하며, 없는 환경의 실제 암호화 통합 검사는 명시적으로 skip한다. 자동 다운로드·설치·PATH fallback은 하지 않는다. 따라서 바이너리가 없는 CI의 일반 pytest 통과를 실제 암호화 검증 성공으로 해석하지 않는다.

임시 바이너리와 private 결과 파일은 장기 보존·배포 대상이 아니다. 재실행 시 공식 릴리스 provenance를 다시 확인하고 새로운 보고서 디렉터리를 사용한다. 운영 identity·복호화 passphrase·vault 비상 복구코드를 임시 fixture나 테스트 환경변수로 전달하지 않는다. 전체 commit hook 결과와 로컬 커밋은 작업 완료 보고에 남긴다.
