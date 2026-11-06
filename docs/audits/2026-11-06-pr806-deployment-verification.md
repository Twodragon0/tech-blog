# PR #806 배포 검증

- PR #806은 GitHub CI와 Vercel preview 성공 후 정상 병합했다.
- merge SHA: 9bd5da9f8e64c20cbf6a6ecbff6c6e3cd56da62d.
- production deployment: dpl_A41roxTNkf2hzP1aHwyPui5ATSAs. GitHub Vercel status success.
- production 최종 로그: Jekyll 시작 1회, 성공 1회, 예약 package 스크립트 재실행 0회, ENOENT 0회.
- preview deployment dpl_DjTUtkFfJEyAnfTSVR783VZtEBG7에서도 같은 수치를 확인했다.
- Pages 작업 42215140140은 build/deploy 모두 성공했다.
- 실제 백업 RSS 50개 항목이 twodragon0.github.io 및 /tech-blog/posts/ 경로를 사용했다. 새 글의 실제 링크와 HTTPS 대응 주소 모두 HTTP 200.

Pages metadata는 html_url=http://twodragon0.github.io/tech-blog/, https_enforced=false를 반환했다. HTTPS 강제 API 요청은 The certificate does not exist yet (HTTP 404)로 거부돼 설정이 바뀌지 않았다. 후속 원격 설정을 강제로 우회하지 않았다. 실패 뒤 시작된 중복 재빌드 요청 42215839774는 취소 요청했다. RSS 링크의 도메인·경로 오류는 해결됐지만 HTTPS 전용 주소 생성/강제 설정은 추가 확인 대상으로 남는다.

Vercel 인증은 로그인한 인터랙티브 셸 문맥으로 조회했다. 토큰이나 인증 파일 내용은 출력·변경하지 않았다. 기존 운영 글과 운영 RSS의 새 항목은 앞선 검증에서 HTTP 200 및 정상 canonical 링크로 확인됐다.
