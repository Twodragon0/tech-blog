# CI/빌드 실패 자동 수정

Jekyll 빌드 및 CI 파이프라인 실패를 진단하고 자동 수정합니다.

## 진단 순서

### 1. 로컬 빌드 테스트
```bash
bundle exec jekyll build
```

- 빌드 출력 전체 캡처
- 에러 메시지 파싱
- 경고 메시지 수집

### 2. 일반적인 빌드 실패 원인

#### Front Matter 오류
- YAML 파싱 에러
- 필수 필드 누락
- 날짜 형식 오류
- 잘못된 인용부호 사용

#### 링크 오류
- 깨진 내부 링크
- 존재하지 않는 페이지 참조
- 잘못된 상대 경로

#### 이미지 오류
- 누락된 이미지 파일
- 잘못된 이미지 경로
- 한글 파일명 사용

#### 문법 오류
- Liquid 템플릿 문법 오류
- Markdown 파싱 에러
- HTML 태그 미완성

#### 의존성 문제
- 누락된 gem
- 버전 충돌
- 플러그인 오류

### 3. GitHub Actions CI 확인
```bash
gh run list --limit 5
```

- 최근 5개 워크플로우 실행 상태 확인
- 실패한 워크플로우의 로그 조회
```bash
gh run view <run-id> --log-failed
```

## 자동 수정 로직

### Front Matter 수정
1. YAML 파싱 에러 → 인용부호 이스케이프, 콜론(:) 처리
2. 날짜 형식 오류 → `YYYY-MM-DD HH:MM:SS +0900` 형식으로 통일
3. 필수 필드 추가 → 템플릿 기반 생성

### 링크 수정
- `python3 scripts/fix_links_unified.py --fix` 실행
- 깨진 링크 자동 수정
- 수정 내역 로그

### 이미지 수정
- 누락된 이미지 → 플레이스홀더 SVG 생성 또는 사용자에게 알림
- 한글 파일명 → `python3 scripts/rename_images_to_english.py --yes` 실행

### 문법 수정
- Liquid 태그 닫기 확인
- HTML 태그 자동 닫기
- Markdown 문법 수정

## 실행 흐름

1. **빌드 실행 및 에러 캡처**
2. **에러 분류 및 우선순위 설정**
   - HIGH: 빌드 차단 에러
   - MEDIUM: 경고
   - LOW: 최적화 권장사항
3. **자동 수정 적용**
   - 백업 생성 (`git stash` 또는 파일 복사)
   - 수정 실행
   - 수정 내역 기록
4. **재빌드 검증**
   - `bundle exec jekyll build` 재실행
   - 성공 확인
5. **사용자에게 보고**
   - 수정된 파일 목록
   - 수정 내용 요약
   - 커밋 제안

## 결과 보고 형식

```markdown
## 빌드 수정 완료

### 발견된 문제
- [HIGH] Front matter YAML 파싱 에러 (3건)
- [MEDIUM] 깨진 링크 (2건)
- [LOW] 최적화되지 않은 이미지 (1건)

### 자동 수정 완료
- ✅ `_posts/2026-02-03-Example.md`: Front matter 날짜 형식 수정
- ✅ `_posts/2026-02-01-Example.md`: 깨진 링크 수정
- ✅ `assets/images/example.png`: 파일명 영문으로 변경

### 재빌드 결과
✅ 빌드 성공 (0 errors, 0 warnings)

### 다음 단계
커밋 권장:
`git add -A && git commit -m "fix: 빌드 에러 수정 (Front matter, 링크)"`
```

## 주의사항

- 수정 전 반드시 백업 생성
- 자동 수정이 불가능한 경우 사용자에게 수동 수정 요청
- 모든 수정 사항 로그 기록
