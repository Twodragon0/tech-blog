# 자동 공유 시스템 가이드

## 📋 개요

새 블로그 포스트가 생성되거나 커밋될 때마다 자동으로 LinkedIn에 공유하는 시스템입니다.

## 🔧 설정 방법

### 1. Git Hook (자동 공유)

포스트를 Git에 커밋할 때마다 자동으로 공유됩니다.

**위치**: `.git/hooks/post-commit`

**동작 방식:**
- 포스트 파일(`_posts/*.md`)이 커밋되면 자동 실행
- 변경된 포스트만 공유 (중복 방지)
- 공유 실패해도 커밋은 정상 완료

**사용법:**
```bash
# 포스트 작성 후 커밋
git add _posts/2026-01-10-example.md
git commit -m "새 포스트 추가"
# → 자동으로 LinkedIn에 공유됨
```

### 2. 수동 실행 스크립트

최근 24시간 내 생성/수정된 포스트를 찾아 공유합니다.

**스크립트**: `scripts/auto_share_new_posts.sh`

**사용법:**
```bash
# 최근 포스트 자동 공유
./scripts/auto_share_new_posts.sh
```

**특징:**
- 최근 24시간 내 포스트만 공유
- 중복 공유 방지 (`.shared_posts.log` 파일 사용)
- 공유 기록 자동 저장

### 3. 직접 공유

특정 포스트를 직접 공유할 수 있습니다.

**사용법:**
```bash
# 특정 포스트 공유
python3 scripts/share_sns.py _posts/2026-01-10-example.md

# 파일명만 지정 (자동 검색)
python3 scripts/share_sns.py 2026-01-10-example.md
```

## 🔒 보안 및 설정

### 필요한 환경 변수

`.env` 파일에 다음이 설정되어 있어야 합니다:

```bash
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_ID=your_person_id
LINKEDIN_REDIRECT_URI=http://localhost:8000/auth/linkedin/callback
SITE_URL=https://tech.2twodragon.com
```

### OAuth 2.0 인증

Access Token이 만료되면 재인증이 필요합니다:

```bash
python3 scripts/linkedin_oauth.py
```

## 📝 공유 메시지 형식

LinkedIn에 공유되는 메시지 형식:

```
🚀 새로운 기술 블로그 포스트를 공유합니다!

📝 [포스트 제목]

[포스트 요약 (최대 300자)]

이 글에서는 실무에서 바로 적용할 수 있는 내용을 다룹니다.

👉 전체 글 읽기: [포스트 URL]

[태그 해시태그]

#DevSecOps #CloudSecurity #AWS #Kubernetes #TechBlog
```

## 🐛 문제 해결

### 문제 1: Git Hook이 실행되지 않음

**해결 방법:**
```bash
# Hook 실행 권한 확인
ls -l .git/hooks/post-commit

# 실행 권한 부여
chmod +x .git/hooks/post-commit
```

### 문제 2: "OAuth 2.0 credentials not configured"

**원인:** `.env` 파일이 로드되지 않음

**해결 방법:**
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. 환경 변수가 올바르게 설정되어 있는지 확인
3. Access Token이 만료되지 않았는지 확인

### 문제 3: 중복 공유

**해결 방법:**
- Git Hook은 커밋 시에만 실행되므로 중복 공유 없음
- 수동 스크립트는 `.shared_posts.log`로 중복 방지
- 로그 파일 삭제 시 재공유 가능:
  ```bash
  rm .shared_posts.log
  ```

### 문제 4: 공유 실패

**확인 사항:**
1. Access Token이 유효한지 확인
2. LinkedIn API Rate Limit 확인 (분당 100회)
3. 포스트 URL이 올바른지 확인
4. 네트워크 연결 확인

## ✅ 체크리스트

자동 공유 시스템 설정 확인:

- [ ] `.env` 파일에 LinkedIn 인증 정보 설정
- [ ] OAuth 2.0 인증 완료 (Access Token 획득)
- [ ] Git Hook 실행 권한 설정 (`chmod +x .git/hooks/post-commit`)
- [ ] 테스트 포스트 공유 성공
- [ ] `.shared_posts.log` 파일 생성 확인 (수동 스크립트 사용 시)

## 📚 참고 자료

- [LinkedIn API 연동 가이드](README_LINKEDIN.md)
- [LinkedIn 앱 생성 가이드](../LINKEDIN_APP_CREATION_GUIDE.md)
- [SNS 공유 스크립트](share_sns.py)

---

**Last Updated**: 2026-01-08  
**Maintainer**: DevSecOps Team
