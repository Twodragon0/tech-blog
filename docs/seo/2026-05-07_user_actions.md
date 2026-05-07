# GSC 색인 복구: 사용자 직접 액션 가이드

**작성 날짜**: 2026-05-07  
**상황**: Vercel Attack Challenge Mode 재활성화로 Googlebot 차단 → GSC 색인 0회  
**필요 액션**: 2가지 (Vercel 대시보드 설정 + Google Search Console URL 제출)  
**예상 소요 시간**: 약 20-30분

---

## 배경: 문제 상황

### 증상
- GSC 노출(Impressions): 0회
- 모든 URL에 대해 Googlebot이 `HTTP 429` + `x-vercel-mitigated: challenge` 응답 수신
- Sitemap을 읽지 못해 신규 콘텐츠 발견 불가
- `investing.2twodragon.com`은 정상 (동일 계정, 동일 Vercel)

### 근본 원인
Vercel 프로젝트 **대시보드 설정**에서 **Attack Challenge Mode**가 활성화된 상태. 이 설정은:
- `vercel.json` 또는 코드로 자동화 불가
- **사용자가 Vercel 웹 대시보드에서 직접 비활성화**해야 함
- 2026-01에 한 번 해결되었으나 2026-05-04에 다시 활성화됨

---

## 액션 1: Vercel Attack Challenge Mode 비활성화

### ⚠️ 우선순위
**가장 큰 임팩트. 이것만 해도 색인 복구 첫 단계 완료.**

### 단계별 가이드

#### Step 1: Vercel 로그인
1. https://vercel.com 접속
2. GitHub/Google 계정으로 로그인
3. 로그인 완료 확인

#### Step 2: `tech-blog` 프로젝트 선택
1. 대시보드 좌상단 "Dashboard" 확인
2. 프로젝트 목록에서 `tech-blog` 찾기
3. `tech-blog` 클릭하여 프로젝트 페이지 이동

**예상 URL**: `https://vercel.com/twodragon0s-projects/tech-blog`

#### Step 3: Settings 메뉴 열기
1. 프로젝트 페이지 최상단 탭 메뉴 확인
2. "Settings" 탭 클릭
3. 좌측 사이드바 메뉴 로드 완료 대기

#### Step 4: Security 섹션 접근
1. 좌측 사이드바에서 "Security" 항목 찾기
2. "Security" 클릭
3. Security 페이지 로드 완료 대기

**현재 URL**: `https://vercel.com/twodragon0s-projects/tech-blog/settings/security`

#### Step 5: Attack Challenge Mode 비활성화
1. Security 페이지 콘텐츠 스크롤하여 "Attack Challenge Mode" 섹션 찾기
2. 현재 상태 확인 (활성/비활성)
3. **토글 버튼이 ON인 경우**: 클릭하여 OFF로 변경
4. "Disabled" 상태 확인

**예상 모습**:
```
Attack Challenge Mode
└─ Status: Disabled ✓
```

#### Step 6: 변경사항 저장 확인
1. 페이지 새로고침 (Cmd+R 또는 Ctrl+R)
2. Attack Challenge Mode 상태가 "Disabled"로 유지되는지 확인
3. 저장 완료

#### Step 7: Googlebot 접근 가능 확인 (자동 검증)
터미널에서 다음 명령 실행:

```bash
# 스크립트로 한 번에 검증 (PR #358)
bash scripts/check_googlebot_access.sh
```

**예상 출력** (성공):
```
✓ https://tech.2twodragon.com/ → HTTP 200
✓ https://tech.2twodragon.com/sitemap.xml → HTTP 200
✓ https://tech.2twodragon.com/feed.xml → HTTP 200
✓ https://tech.2twodragon.com/tags-data.json → HTTP 200

All checks passed!
```

**예상 출력** (실패 - Challenge Mode 아직 ON):
```
✗ https://tech.2twodragon.com/ → HTTP 429 (x-vercel-mitigated: challenge)
```

#### 또는 수동 검증 (curl 직접 사용)
```bash
curl -sI -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  https://tech.2twodragon.com/ | head -8
```

**성공 시**:
```
HTTP/2 200
content-type: text/html; charset=utf-8
...
```

**실패 시** (아직 Challenge Mode ON):
```
HTTP/2 429
x-vercel-mitigated: challenge
...
```

---

## 액션 2: Google Search Console URL 검사 및 색인 요청

### ⚠️ 우선순위
**액션 1 완료 후 실행. 21개 URL을 GSC에 제출하여 색인 재시작.**

### 사전 확인
- Google Search Console: https://search.google.com/search-console
- `tech.2twodragon.com` 속성 소유권 확인 필수
- 로그인 상태 확인

### 제출 대상 URL (21개)

#### 그룹 1: 신규 포스트 및 주요 업데이트 (2026-05 기간)

| # | URL | 상태 | 비고 |
|----|-----|------|------|
| 1 | `/2026/05/03/Tech_Security_Weekly_Digest_May_3_2026_AI_Data_CVE_Malware.html` | 신규 | May 3 Weekly |
| 2 | `/2026/05/04/Tech_Security_Weekly_Digest_May_4_2026_LLM_Model_Supply_Chain.html` | 신규 | May 4 Weekly |
| 3 | `/2026/05/05/Tech_Security_Weekly_Digest_May_5_2026_Cloud_Container_Kubernetes.html` | 신규 | May 5 Weekly |
| 4 | `/2026/05/01/Tech_Security_Weekly_Digest_April_28_May_1_2026_Rollup.html` | 업데이트 | 5/1 Rollup (image_alt 추가) |
| 5 | `/2026/04/30/Tech_Security_Weekly_Digest_April_24_30_2026_Rollup.html` | 업데이트 | 4/30 Rollup (image_alt 추가) |
| 6 | `/2026/04/23/Tech_Security_Weekly_Digest_April_17_23_2026_Rollup.html` | 업데이트 | 4/23 Rollup (image_alt 추가) |
| 7 | `/2026/04/16/Tech_Security_Weekly_Digest_April_9_16_2026_Rollup.html` | 업데이트 | 4/16 Rollup (image_alt 추가) |
| 8 | `/2026/04/09/Tech_Security_Weekly_Digest_April_2_9_2026_Rollup.html` | 업데이트 | 4/9 Rollup (image_alt 추가) |

#### 그룹 2: 구조적 메타데이터 수정 (2026-04-25 이후)

| # | URL | 수정 내용 |
|----|-----|---------|
| 9 | `/2026/04/25/Kubernetes_Pod_Disruption_Budget_PDB_Guide.html` | JSON-LD 파싱 에러 수정 |
| 10 | `/2026/04/22/Kubernetes_Network_Policy_Advanced_Examples.html` | JSON-LD 파싱 에러 수정 |
| 11 | `/2026/04/19/Cosign_Image_Signing_Verification_Kubernetes_Admission.html` | JSON-LD 파싱 에러 수정 |
| 12 | `/2026/04/15/Istio_Authorization_Policy_RBAC_in_Kubernetes.html` | JSON-LD 파싱 에러 수정 |
| 13 | `/2026/04/12/Container_Image_Scanning_Trivy_Harbor_Best_Practices.html` | JSON-LD 파싱 에러 수정 |

#### 그룹 3: Redirect 수정 및 이전 콘텐츠 (2026-05-03 이후 수정)

| # | URL | 상태 |
|----|-----|------|
| 14 | `/2026/02/06/Kubernetes_DNS_Cache_Poisoning_CVE_2024_24786.html` | redirect 대상 수정 |
| 15 | `/2026/02/28/Kubernetes_API_Server_Vulnerability_Analysis.html` | redirect 대상 수정 |
| 16 | `/2025/12/03/Argo_Workflows_Kubernetes_CI_CD_Best_Practices.html` | redirect 대상 수정 |
| 17 | `/2025/11/20/Harbor_Container_Registry_Kubernetes_Integration.html` | redirect 대상 수정 |
| 18 | `/2025/11/14/Sealed_Secrets_Kubernetes_Secret_Management.html` | redirect 대상 수정 |
| 19 | `/2025/11/10/KEDA_Kubernetes_Autoscaling_Event_Driven.html` | redirect 대상 수정 |
| 20 | `/2025/11/01/OPA_Gatekeeper_Kubernetes_Policy_as_Code.html` | redirect 대상 수정 |
| 21 | `/index.html` | 홈페이지 |

### 단계별 제출 가이드

#### Step 1: Google Search Console 접속
1. https://search.google.com/search-console 접속
2. Google 계정으로 로그인 (필요 시)
3. `tech.2twodragon.com` 속성 선택

**현재 URL**: `https://search.google.com/search-console/property/https://tech.2twodragon.com/`

#### Step 2: URL 검사 도구 열기
1. 좌측 메뉴에서 "URL 검사" 또는 "Inspect URL" 찾기
2. 클릭하여 URL 검사 입력창 열기
3. 상단 검색 상자 준비 완료 확인

#### Step 3: URL 제출 (21개 반복)
각 URL에 대해 다음을 반복:

1. **URL 입력**
   ```
   https://tech.2twodragon.com{PATH}
   ```
   (예: `https://tech.2twodragon.com/2026/05/03/Tech_Security_Weekly_Digest_May_3_2026_AI_Data_CVE_Malware.html`)

2. **Enter 또는 검사 버튼 클릭**

3. **URL 상태 확인**
   - ✓ "URL이 Google에 등재됨" → 기존 색인
   - ⚠️ "URL이 등재되지 않음" → 색인 필요
   - ✓ "색인 요청 제출 완료" → 제출 성공

4. **색인 요청 버튼 클릭** (표시된 경우)
   - "색인 요청" 또는 "Request indexing" 버튼 클릭
   - 대기: "요청 제출됨" 메시지 확인

5. **다음 URL로 이동**

### ⏱️ 소요 시간
- 21개 URL × 약 30초/URL = **약 10-15분**

### 자동화 검증 (수동 액션 완료 후)
```bash
# GSC에 제출된 URL이 실제로 크롤링 가능한지 확인
for url in \
  "https://tech.2twodragon.com/2026/05/03/Tech_Security_Weekly_Digest_May_3_2026_AI_Data_CVE_Malware.html" \
  "https://tech.2twodragon.com/index.html"; do
  status=$(curl -sI "$url" | head -1)
  echo "$url: $status"
done
```

**예상 출력**:
```
https://tech.2twodragon.com/2026/05/03/...: HTTP/2 200
https://tech.2twodragon.com/index.html: HTTP/2 200
```

---

## 추가 권장 액션 (선택)

이 섹션은 색인 복구 속도를 높이기 위한 추가 스텝입니다. 액션 1, 2 완료 후 필요에 따라 실행하세요.

### 권장 액션 A: Sitemap 재제출 (GSC)

1. GSC 좌측 메뉴에서 "Sitemap" 또는 "Sitemaps" 클릭
2. 현재 등록된 sitemap 확인:
   - `https://tech.2twodragon.com/sitemap.xml`
3. 삭제 후 재추가 또는 URL 필드에 다시 입력하여 강제 재크롤링
4. "제출" 또는 "Request crawl" 클릭

**효과**: 한 번에 모든 페이지를 색인 요청

### 권장 액션 B: 모바일 유용성 검사 (GSC)
1. GSC 좌측 메뉴에서 "모바일 유용성" 클릭
2. 이전 오류 내역 확인
3. 현재 상태 (0개 오류) 확인 및 모니터링

### 권장 액션 C: 다른 검색 엔진 등록 (선택)
- **Bing Webmaster Tools**: https://www.bing.com/webmasters
- **Naver Search Advisor**: https://searchadvisor.naver.com/
- 동일한 sitemap 제출 프로세스

---

## 모니터링 및 검증

### 자동 검증 명령어

#### Googlebot 접근 가능 확인
```bash
bash scripts/check_googlebot_access.sh
```

#### 현재 sitemap 크롤링 가능 여부
```bash
curl -sI https://tech.2twodragon.com/sitemap.xml | grep -E "HTTP|Content-Type"
```

**예상 출력**:
```
HTTP/2 200
content-type: application/xml
```

#### RSS Feed 접근 가능 여부
```bash
curl -sI https://tech.2twodragon.com/feed.xml | head -1
```

### GSC 수동 모니터링

#### 체크리스트 (24~48시간 후)
- [ ] 액션 1 완료: Vercel Attack Challenge Mode = Disabled
- [ ] 액션 2 완료: 21개 URL GSC 제출
- [ ] GSC "색인 상태" 다시 확인: 색인 수 > 0
- [ ] GSC "커버리지" 탭: "오류" 섹션 비워짐 (또는 0개)
- [ ] GSC "Sitemap" 탭: 마지막 요청 시간이 오늘 날짜

#### 색인 회복 예상 타이밍
- **즉시** (1-2시간): Googlebot 접근 가능 확인
- **24시간 이내**: GSC 노출 수 증가 관찰
- **48-72시간**: 대부분의 주요 포스트 색인 완료

---

## 참고 문서

### 관련 메모리 파일
- **메인 이슈**: `~/.claude/projects/.../memory/feedback_vercel_challenge_mode.md`
  - 2026-01 첫 발생 및 해결
  - 2026-05-04 재활성화 감지
  - 자동화 불가 이유 설명

- **SEO 색인 분석**: `docs/seo/GSC_INDEXING_FIXES.md`
  - 구조적 메타데이터 문제 분석
  - JSON-LD 파싱 에러 목록

- **Vercel 보안 troubleshooting**: `docs/troubleshooting/VERCEL_SECURITY_CHECKPOINT_FIX.md`
  - 2026-01-26 작성
  - 동일 이슈 해결 방법

### 관련 커밋
| 커밋 해시 | 설명 | 날짜 |
|----------|------|------|
| 2474bddc | JSON-LD 파싱 에러 수정 (5개 포스트) | 2026-05-03 |
| bf3ab7e6 | image_alt 추가 (7개 rollup 포스트) | 2026-05-03 |
| 8929cc48 | vercel.json redirect 대상 수정 (13건) | 2026-05-03 |
| 184fb2a2 | last_modified_at 추가 (모든 167 포스트) | 2026-05-04 |
| 0c84c176 | Googlebot access probe script (PR #358) | 2026-05-04 |
| a53cedec | Sitemap exclusion + 301 redirects | 2026-05-04 |
| 68faed12 | 콘텐츠 통합 및 SEO 롤업 | 2026-04-30 |

---

## FAQ

### Q1: 액션 1 완료 후 얼마나 기다려야 하나요?
**A**: 액션 2를 바로 실행해도 됩니다. 액션 1이 완료되면 Googlebot이 즉시 크롤링할 수 있습니다.

### Q2: GSC에 모든 21개를 수동으로 입력해야 하나요?
**A**: 네, 현재는 수동 입력이 필요합니다. 약 10-15분 소요.

### Q3: 색인이 안 되면 어떻게 하나요?
**A**: 
1. 액션 1 재확인: `bash scripts/check_googlebot_access.sh`
2. GSC "크롤 통계" 확인: 마지막 크롤 날짜와 200 응답 개수
3. 301 redirect 체인 확인: `curl -I -L https://tech.2twodragon.com/...`

### Q4: Vercel Challenge Mode은 다시 활성화될 수 있나요?
**A**: 가능성이 있습니다. 월 1회 정도 모니터링 권장:
```bash
# 주간 자동 검증 스크립트 추가 가능
bash scripts/check_googlebot_access.sh
```

---

## 최종 체크리스트

액션 완료 시 확인:

- [ ] **액션 1**: Vercel Attack Challenge Mode = **Disabled**
  - 확인: `bash scripts/check_googlebot_access.sh` → HTTP 200
  
- [ ] **액션 2**: GSC 21개 URL 제출 완료
  - 확인: GSC 색인 상태 탭에서 주소 수 > 0

- [ ] **후속**: Sitemap 재제출 (선택)
  - 확인: GSC Sitemap 탭 > 마지막 요청 시간 = 오늘

- [ ] **모니터링**: 24-48시간 후 GSC 색인 수 증가 확인
