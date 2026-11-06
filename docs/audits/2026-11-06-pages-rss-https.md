# 백업 RSS HTTPS 주소 고정

Pages API의 https_enforced=false이면 configure-pages origin도 HTTP가 된다. GitHub의 HTTPS 강제 설정은 인증서 미준비로 거부됐지만 기존 HTTPS 백업 URL은 정상 동작했다. RSS 주소 생성은 이 원격 설정과 분리한다.

workflow의 실제 설정 생성 단계를 `scripts/build/write_pages_config.rb`로 옮겼다. 정상 HTTP/HTTPS origin을 HTTPS origin으로 정규화하고, 사용자 정보·query·fragment·경로·비표준 port·지원하지 않는 scheme은 값 노출 없이 거부한다. production 기본 _config.yml은 바꾸지 않는다.

기존 코드로 회귀 테스트가 실패하는 것을 먼저 확인했다. 수정 후 실제 workflow 실행 단계와 Jekyll 렌더를 연결한 테스트 14개가 통과했고, 실제 사이트 빌드의 RSS 항목 50개가 모두 https://twodragon0.github.io/tech-blog/ 주소를 사용했다. Ruby 구문·Ruff check/format·Mypy·diff 검사를 수행한다. 원격 Pages 인증서 설정이나 계정 인증 정보는 변경하지 않는다.

배포 후에는 새 RSS의 self/channel/item URL을 다시 확인하고 실제 글 응답을 대조해야 한다. 이 문서는 로컬 구현 검증이며 원격 적용 완료 기록이 아니다.
