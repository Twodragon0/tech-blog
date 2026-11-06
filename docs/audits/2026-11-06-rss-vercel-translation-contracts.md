# RSS·Vercel 빌드·오프라인 번역 계약 개선

## Vercel 인증 및 실패 증거

사용자의 로그인 성공을 확인했고, 일반 비대화형 셸에는 인증이 보이지 않았지만 `zsh -lic`로 동일한 터미널 문맥을 불러오면 CLI 조회가 성공했다. 인증 파일이나 토큰을 출력·수정하지 않았다.

실패한 preview deployment `dpl_GeTQ5TniBpkmNwQLE1kTTbjvop6N`의 로그에서 다음 순서를 확인했다.

1. 2026-11-05 16:15:20 UTC: 첫 Jekyll 빌드 성공.
2. 16:15:21: Node 함수 빌더가 예약된 package 스크립트를 다시 실행.
3. 16:15:23.759: 두 번째 build.sh가 _site 정리를 시작.
4. 16:15:23.818: Vercel MultiStream이 _site의 index.html을 읽다가 ENOENT로 실패.

공식 Node 빌더는 API 함수 빌드에도 예약된 package 스크립트를 탐색한다: https://github.com/vercel/vercel/blob/main/packages/node/src/build.ts

`package.json`의 중복 예약 스크립트를 삭제했다. 명시적 vercel.json buildCommand는 유지하여 정적 사이트 빌드 소유자를 하나로 만들었다. 의존성·API 함수 코드는 변경하지 않았다. 실제 재배포의 성공과 로그 단일 실행 여부는 원격 반영 뒤 확인해야 한다.

## 백업 RSS

Pages가 base_path만 설정해 사이트 origin은 production으로 남아 있었다. configure-pages의 공식 origin 출력으로 런타임 YAML override를 만들고 build.sh의 선택적 JEKYLL_CONFIG로 넘긴다. production 기본 설정은 유지한다. 공식 출력 정의: https://github.com/actions/configure-pages/blob/main/action.yml

실제 Jekyll 빌드의 RSS 50개 항목이 모두 https://twodragon0.github.io/tech-blog/ 아래를 가리키는 것을 확인했다. production/backup 두 경우의 렌더 회귀와 workflow 연결 검사를 추가했다. Ruby가 없는 news-only runner는 렌더 검사만 명시적으로 건너뛰며, Ruby가 설치된 Jekyll 빌드 작업에서 실제 렌더를 실행한다.

## T1·T3

기존 번역 제공자 호출을 변경하지 않는 새 오프라인 계약과 회귀 테스트를 추가했다. 상세 범위와 한계는 pipeline 후속 계획 문서에 기록했다. 외부 API 호출·키 등록·발행 모드 변경은 수행하지 않았다.
