# 뉴스 발행 중단 원인과 수정

## 관측 근거

GitHub Actions 실행 [41967080988](https://github.com/Twodragon0/tech-blog/actions/runs/41967080988)의 2026-11-05 실패 로그를 읽었다. 스케줄이 시작되지 않은 문제가 아니라, 생성한 11월 5일 digest를 발행하기 전 전체 pytest gate가 실패했다. 최근 목록에는 성공 실행도 있었으므로 모든 날짜에 같은 원인이 발생했다고 단정하지 않는다.

## 수정 대상

1. 만료된 core-bare 진단 훅 테스트: 관측 종료에 따라 훅·연결·만료 항목을 함께 제거했다.
2. `_ConfigProxy` 속성 삭제 누락: monkeypatch가 원래 없던 속성을 추가한 뒤 teardown에서 삭제할 때 프록시가 실제 모듈로 삭제를 전달하지 못했다. 뒤의 렌더 함수 복원도 중단되어 empty-render 실패가 연쇄 발생했다. 삭제 전달을 추가하고 복원 경로를 회귀 검사한다.
3. `OpenAI AI 파이프라인` 제목: OpenAI는 일반 AI 수식어가 아닌 공급자 브랜드다. Claude와 같은 브랜드 검토 목록에 추가하여 렌더 결과를 바꾸지 않고 올바른 브랜드 표기를 인정한다. 임의의 단어를 모두 허용하거나 corpus 검사를 끄지 않는다.

## 적용과 한계

초기 로컬 수정 후 사용자의 원격 반영 요청에 따라 main에 push하고 실제 발행을 검증 중이다. 아래 실행 기록은 각 시점의 결과이며, 최종 판정은 새 커밋·게시 URL·RSS를 대조한 결과로 갱신한다.

반영 후에는 같은 워크플로를 먼저 dry_run=true, use_ai=none으로 실행해 발행 전 gate를 확인한다. 이어 정상 발행 실행에서 published_to_main, 커밋 SHA, 새 글 URL, production 응답과 RSS 반영을 대조한다. 실패하면 기존 실패 로그와 비교하고 테스트나 보안 gate를 건너뛰지 않는다. 누락 기간 기사를 당일 기사인 것처럼 자동 재발행하지 않는다.

## 로컬 검증 결과

전체 pytest 6075 passed, 3 skipped, 기존 font tier 경고 1개. 정밀 회귀를 강화한 뒤 관련 105개 테스트와 새 회귀 2개 재통과. 변경한 Python 파일 Ruff/Mypy 통과. 초안 포함 Jekyll 빌드 성공. 커밋 훅에서도 전체 테스트와 SVG 검사가 통과했다. 게시물 검사에는 보존한 Mermaid 23줄 경고 1개가 남는다.

## 원격 반영 및 실제 실행에서 추가 발견

- 두 커밋과 원격 변경을 merge한 `3a1faa2c`를 main에 push했다.
- dry-run [42057213382](https://github.com/Twodragon0/tech-blog/actions/runs/42057213382)는 성공했으나 파일을 쓰지 않는 모드이므로 전체 corpus 발행 gate 성공을 의미하지 않는다.
- 첫 실제 실행 [42057555197](https://github.com/Twodragon0/tech-blog/actions/runs/42057555197)은 KST 11월 6일 파일을 생성했으나 UTC 11월 5일 파일을 찾아 publish를 건너뛰었다. 워크플로 세 곳의 TODAY를 KST로 통일하고 회귀 테스트를 추가했다 (`e4f49115`). 전체 테스트 6082개 통과 후 push했다.
- 재실행 [42057987536](https://github.com/Twodragon0/tech-blog/actions/runs/42057987536)은 새 글을 찾았지만 KST 자정 timestamp의 filename-date redirect 누락을 corpus gate가 차단했다. 생성기 보완 대상으로 확인했다. 성공 상태만으로 발행 성공을 판정하지 않은 이유다.
- 자정 redirect 수정 `ac61a3db`를 main에 반영했다. 로컬 전체 테스트 6092개 통과.
- 실행 [42058846379](https://github.com/Twodragon0/tech-blog/actions/runs/42058846379)은 날짜 게이트를 통과했으나 use_ai=none으로 남은 영문 카드 제목 13건을 한국어 gate가 차단했다. 현재 Claude/OpenAI Actions 키가 비어 있어 해당 모드만으로 한국어 자동 번역을 완료할 수 없다. 이번 글은 한국어 검수 발행으로 복구하고 정기 번역 제공자 결정은 별도로 남긴다.
- 별도 worktree 검수에서는 중복 요약 12개를 제거하고 모든 corpus 정적 gate를 통과시켰다. 후보 30건과 본문 카드 15건을 구분하는 설명을 추가했다. 직접 편집 검수이므로 이를 무인 번역 성공으로 표기하지 않는다.
