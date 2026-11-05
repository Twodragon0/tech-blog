# 후속 개선 계획 및 증거

## 변경 전 계획

- 범위: 지정된 4개 글의 10줄 초과 비-Mermaid 코드 블록. 코드를 실행하거나 의미를 바꾸지 않고 docs/examples 아래 원문으로 분리한다. 본문에는 GitHub 참조와 HTML 주석을 남긴다.
- 보존 조건: 분리 파일 내용과 기존 코드 문자열의 동일성을 검사한다. Mermaid는 코드 길이 규칙 때문에 도표가 없어지지 않도록 유지한다.
- 진단 훅: 현재 core.bare=false, 지정 로그와 상태 파일이 발견되지 않았다. 원인 해결을 주장하지 않고, 증거를 만들지 못하는 임시 관찰을 종료한다. 스크립트·연결·만료 레지스트리를 함께 제거하며 다른 훅은 유지한다.
- 검증: 기존 훅 회귀 테스트를 먼저 실행하고 변경 후 다시 실행한다. 게시물 검사, 초안 포함 빌드, diff 검사를 수행한다.
- 호스트: 읽기 전용으로 PR 목록·부팅·전원·FileVault·launchd 상태를 확인한다. 재부팅, PR 생성, 네트워크 설정 변경은 하지 않는다.

## 변경 후 검증 기록

- 코드 27개를 원문 동일성 검사 후 분리했다. 4개 글의 비-Mermaid 코드는 모두 10줄 이하이다.
- 기존 5개 경고 중 4개는 코드 분리로 해소했고 나머지 1개는 23줄 Mermaid이다. 도표를 유지했으며 검사 경고를 숨기거나 기준을 변경하지 않았다.
- 훅 관련 회귀 테스트 변경 전후 각각 7개 통과. Ruff/Mypy 통과.
- 초안 포함 Jekyll 빌드 성공(15.606초), 추출 예제 27개와 본문 참조 검사 통과.
- 전체 테스트 최종 결과는 작업 응답에 기록한다.
- GitHub main 링크는 예제와 글을 함께 커밋·반영한 뒤 확인해야 한다. 이번 작업은 push/배포하지 않았다.

## 분리 예제 목록

- `docs/examples/2026-08-31-AI_Agent_MCP_Server_Security_Threat_Modeling_Defense/example-01.jsonc`: 11줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-01.xml`: 32줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-02.sh`: 19줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-03.sh`: 18줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-04.sh`: 17줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-05.sh`: 12줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-06.jsonc`: 14줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-07.jsonc`: 24줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-08.sh`: 12줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-09.sh`: 11줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-10.sh`: 12줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-11.sh`: 15줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-12.sh`: 11줄
- `docs/examples/2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide/example-13.sh`: 12줄
- `docs/examples/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security/example-01.jsonc`: 54줄
- `docs/examples/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security/example-02.sh`: 21줄
- `docs/examples/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security/example-03.sh`: 23줄
- `docs/examples/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security/example-04.ql`: 28줄
- `docs/examples/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security/example-05.yml`: 41줄
- `docs/examples/2025-05-23-Cloud_Security_Course_7Batch_-_6Week_Cloudflare_And_github_Security/example-06.sh`: 12줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-01.jsonc`: 27줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-02.jsonc`: 16줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-03.yml`: 47줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-04.yml`: 28줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-05.yml`: 37줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-06.yml`: 26줄
- `docs/examples/2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS/example-07.py`: 81줄

## 점수 스냅샷 갱신

전체 테스트는 6068 통과, 변경한 4개 글의 점수 스냅샷 비교 4개 실패, 3개 skip이었다. 본문에서 코드를 분리해 길이와 코드 블록 점수가 바뀐 것이 원인이다. 검사 알고리즘은 바꾸지 않고 해당 4개 글의 기준값만 갱신했다. 총점 변화는 Kandji 96→98, Cloudflare 96→100, Amazon Q 96→100, MCP 95→95다. MCP는 세부 길이/코드 점수만 바뀌었다. 다른 게시물의 기준값이 바뀌지 않았음을 검사했다. 이후 관련 점수 회귀 테스트 356개가 통과했다. 전체 재실행은 하지 않았다.
