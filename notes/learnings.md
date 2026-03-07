# Learnings

기술적 발견과 패턴을 기록합니다.

## 2026-02

- Jekyll 빌드 시 한글 파일명은 URL 인코딩 이슈 발생 → 영문 파일명 필수
- SVG 내 한글 텍스트는 일부 브라우저에서 깨짐 → 영문만 사용

## 2026-03-07

### 포스트 품질 검증에서 발견된 패턴
- `verify_images_unified.py --all` 실행 시 포스트에서 참조하는 섹션 배너 SVG가 실제로 존재하는지 확인됨
- 기존 섹션 배너: `section-security.svg`, `section-devops.svg`, `section-ai-ml.svg`, `section-cloud.svg`, `section-blockchain.svg`
- 새 포스트에서 `section-devsecops.svg`, `section-ai.svg` 참조 시 기존 파일명과 불일치 → 신규 생성 필요
- 코드 블록 bare ``` 패턴 중 대부분은 닫는 태그 → `^```$` grep 결과만으로는 opening/closing 구분 불가, 앞뒤 컨텍스트 확인 필수

### 코드 블록 언어 태그 누락 패턴
- 공격 시나리오 (번호 목록) → `text`
- 아키텍처 다이어그램 (화살표/박스) → `text`
- SIEM 탐지 쿼리 (필드 기반) → `splunk` 또는 해당 언어
- 닫는 태그는 항상 bare ``` 이므로 수정 불필요
