# 일일 점검 및 유지보수

블로그의 일일 상태 점검 및 유지보수 작업을 수행합니다.

## 점검 항목

### 1. Git 상태 확인
```bash
git status
```
- 커밋되지 않은 변경사항 확인
- 추적되지 않는 파일 확인
- 브랜치 상태 확인

### 2. 포스트 검증
```bash
python3 scripts/check_posts.py
```
- 모든 포스트의 Front Matter 완전성 검증
- 최근 7일 내 작성된 포스트 집중 점검
- 에러 및 경고 수집

### 3. SEO 필드 점검
최근 포스트 (7일 이내)에 다음 필드 확인:
- [ ] `description`: SEO 설명 (200자 이내)
- [ ] `keywords`: 키워드 배열 (5-10개 권장)
- [ ] `author`: 작성자
- [ ] `excerpt`: 요약 (150-200자)
- [ ] `schema_type`: 스키마 타입 (Article, FAQPage 등)

### 4. 이미지 검증
```bash
python3 scripts/verify_images_unified.py --all
```
- 모든 포스트의 이미지 파일 존재 여부 확인
- Front Matter의 `image` 필드 검증
- 누락된 이미지 목록 생성

### 5. 예약 포스트 확인
- `_posts/` 디렉토리에서 미래 날짜의 포스트 확인
- 오늘 날짜 또는 이전 날짜로 설정된 포스트 중 게시 준비 완료 확인
- 게시 준비 포스트에 대한 최종 검증 (이미지, 링크, Front Matter)

### 6. 빌드 및 배포 상태
```bash
gh run list --limit 3
```
- 최근 3개 GitHub Actions 워크플로우 상태 확인
- 실패한 워크플로우 식별
- Vercel 배포 상태 확인 (프로덕션: https://tech.2twodragon.com)

### 7. 보안 스캔
- 하드코딩된 민감 정보 검색 (API 키, 비밀번호, 토큰)
- 최근 추가된 파일에서 보안 이슈 확인

### 8. 성능 메트릭
- Core Web Vitals 확인 (Vercel Analytics 또는 Google PageSpeed Insights)
- 빌드 시간 측정
- 사이트맵 생성 여부 확인

## 결과 요약 형식

```markdown
## 일일 점검 결과 (YYYY-MM-DD)

### 📊 전체 상태
- ✅ 정상 항목: X개
- ⚠️ 경고 항목: Y개
- ❌ 오류 항목: Z개

### 🔧 Git 상태
- 커밋되지 않은 변경사항: N개 파일
- 추적되지 않는 파일: M개 파일

### 📝 포스트 검증
- 전체 포스트: N개
- 최근 7일 포스트: M개
- 오류 발견: X개
  - 파일1: 이슈 설명
  - 파일2: 이슈 설명

### 🖼️ 이미지 검증
- 누락된 이미지: N개
  - 포스트1: 이미지 경로
  - 포스트2: 이미지 경로

### 📅 예약 포스트
- 게시 예정: N개
  - YYYY-MM-DD: 포스트 제목

### 🚀 배포 상태
- 최근 빌드: ✅ 성공 / ❌ 실패
- 워크플로우 상태: 정상 / 실패

### 🔒 보안
- 보안 이슈: 없음 / N개 발견

### ⚡ 성능
- 빌드 시간: N초
- LCP: N.Ns
- FID: N ms
- CLS: N.NN

### 💡 권장 조치
1. [HIGH] 이슈 설명 및 수정 방법
2. [MEDIUM] 이슈 설명 및 수정 방법
3. [LOW] 이슈 설명 및 수정 방법
```

## 자동화

- `/daily-review`: 전체 점검 실행
- `/daily-review --quick`: 빠른 점검 (Git, 포스트, 이미지만)
- `/daily-review --fix`: 자동 수정 가능한 이슈 수정

## 스케줄링

매일 오전 9시에 자동 실행 권장 (GitHub Actions 또는 로컬 cron)

```yaml
# .github/workflows/daily-review.yml
on:
  schedule:
    - cron: '0 0 * * *'  # 매일 UTC 00:00 (KST 09:00)
```
