# 포스팅 작성 규칙 (Posting Writing Rules)

이 문서는 현재까지 작성된 모든 포스팅을 분석하여 정리한 작성 규칙입니다. 새로운 포스팅을 작성할 때 이 규칙을 준수해야 합니다.

## 📋 목차

1. [Front Matter 규칙](#front-matter-규칙)
2. [포스팅 구조](#포스팅-구조)
3. [AI 요약 카드 형식](#ai-요약-카드-형식)
4. [본문 작성 규칙](#본문-작성-규칙)
5. [코드 블록 규칙](#코드-블록-규칙)
6. [이미지 규칙](#이미지-규칙)
7. [표 형식 규칙](#표-형식-규칙)
8. [보안 관련 규칙](#보안-관련-규칙)
9. [링크 규칙](#링크-규칙)
10. [카테고리 및 태그 규칙](#카테고리-및-태그-규칙)

---

## Front Matter 규칙

### 필수 필드

```yaml
---
layout: post
title: "포스팅 제목 (한글 가능)"
date: YYYY-MM-DD HH:MM:SS +0900
categories: [카테고리1, 카테고리2]
tags: [태그1, 태그2, 태그3]
excerpt: "포스트 요약 (150-200자 권장, 핵심 내용 포함)"
comments: true
original_url: https://twodragon.tistory.com/[번호]  # 선택사항
image: /assets/images/YYYY-MM-DD-[영문_제목].svg
image_alt: "영문 이미지 설명"
toc: true  # 목차 표시 여부
---
```

### Front Matter 예시

```yaml
---
layout: post
title: "클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전"
date: 2026-01-08 19:58:00 +0900
categories: [security, devsecops]
tags: [AWS, CloudFront, cloudsecurity, Cybersecurity, DevSecOps, github, githubactions, SecurityEngineering, TechBlog, waf]
excerpt: "클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처(OAI/OAC, WAF 규칙, Geo-blocking), GitHub DevSecOps 실전(CodeQL, Dependabot, Secret Scanning), 실전 보안 패치 사례(SSRF 수정, Data Masking), 테크 블로그 보안 개선(Jekyll, CodeQL 기반 취약점 진단), Amazon Q Developer 활용까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/707
image: /assets/images/2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg
image_alt: "Cloud Security Course 8Batch 6Week: AWS WAF CloudFront Security Architecture and GitHub DevSecOps Practical"
toc: true
---
```

### 주의사항

- **파일명**: `YYYY-MM-DD-[영문_제목].md` 형식 (한글 제외)
- **이미지 파일명**: 반드시 영어로 작성 (한글 사용 금지)
- **excerpt**: 핵심 내용을 간결하게 요약 (150-200자 권장)
- **categories**: 배열 형식으로 최대 2-3개 권장
- **tags**: 배열 형식으로 5-10개 권장

---

## 포스팅 구조

### 표준 구조

1. **Front Matter** (YAML 헤더)
2. **AI 요약 카드** (HTML 또는 마크다운 형식)
3. **이미지** (메인 이미지)
4. **서론** (배경 및 목적)
5. **본문** (주제별 섹션)
   - 명확한 제목과 계층 구조 (##, ###)
   - 코드 예제 (필요시)
   - 이미지/다이어그램 (필요시)
   - 실무 팁 및 주의사항
   - 단계별 가이드 제공
6. **결론** (요약 및 다음 단계)

### 서론 작성 규칙

- 포스팅의 배경 및 목적 명확히 설명
- 문제 상황 또는 해결 방법 개요 제시
- 대상 독자 언급 (선택사항)
- 포스팅의 목적 명시

**예시:**
```markdown
## 서론

안녕하세요, **Twodragon**입니다.

[배경 설명]
[문제 상황 또는 목적]
[포스팅의 목적 및 구성]
```

### 본문 작성 규칙

- **명확한 제목**: 각 섹션은 명확한 제목으로 구분
- **계층 구조**: H2(##), H3(###), H4(####) 적절히 사용
- **단계별 가이드**: 복잡한 프로세스는 단계별로 설명
- **실무 중심**: 이론보다 실무 경험과 실제 사용 사례 중심
- **코드 예제**: 구체적인 코드 예제와 설정 파일 제공
- **문제 해결**: 트러블슈팅 섹션 포함

### 결론 작성 규칙

- 핵심 내용 요약
- 추가 학습 자료 (선택)
- 원본 포스트 링크 (있는 경우)

---

## AI 요약 카드 형식

### HTML 형식 (권장)

```html
<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">[제목]</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">[태그1]</span>
      <span class="tag">[태그2]</span>
      <span class="tag">[태그3]</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>[핵심 포인트 1]</li>
      <li>[핵심 포인트 2]</li>
      <li>[핵심 포인트 3]</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">[기술1, 기술2, 기술3]</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">[대상 독자]</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>
```

### 마크다운 형식 (대안)

```markdown
## 📋 포스팅 요약

> **제목**: [제목]
> 
> **카테고리**: [카테고리]
> 
> **태그**: [태그1, 태그2, 태그3]
> 
> **핵심 내용**: 
> - [핵심 포인트 1]
> - [핵심 포인트 2]
> - [핵심 포인트 3]
> 
> **주요 기술/도구**: [기술1, 기술2, 기술3]
> 
> **대상 독자**: [대상 독자]
> 
> ---
> 
> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*
```

### 핵심 내용 작성 규칙

- **3-5개 bullet points**: 핵심 내용을 3-5개로 요약
- **구체적이고 명확한 설명**: 각 포인트는 구체적으로 작성
- **기술/도구명 포함**: 관련 기술이나 도구명을 명시
- **실무 중심**: 이론보다 실무 적용 사례 중심

---

## 본문 작성 규칙

### 제목 계층

- `#` (H1): 포스트 제목 (front matter에서 처리)
- `##` (H2): 주요 섹션
- `###` (H3): 하위 섹션
- `####` (H4): 세부 항목 (최소한으로 사용)

### 리스트

- 순서 없는 리스트: `-` 사용
- 순서 있는 리스트: 숫자 사용
- 중첩 리스트는 2칸 들여쓰기

### 강조

- **굵게**: 중요한 개념, 키워드
- *기울임*: 강조 (최소한으로 사용)
- `코드`: 명령어, 파일명, 변수명

### 인용 블록

```markdown
> **💡 실무 팁**
> [팁 내용]

> **⚠️ 주의사항**
> [주의사항]

> **📌 핵심 요약**
> [요약 내용]
```

### 빠른 참조 섹션

복잡한 내용의 경우 빠른 참조 표를 제공:

```markdown
## 📊 빠른 참조

### [주제] 개요

| 항목 | 내용 |
|------|------|
| **항목1** | 설명1 |
| **항목2** | 설명2 |
```

---

## 코드 블록 규칙

### 코드 블록 형식

```markdown
```language
# 코드 내용
```
```

### 코드 블록 처리 원칙

- **가독성 향상**: 긴 코드 블록(10줄 이상 또는 500자 이상)은 GitHub 링크로 대체하고 원본은 주석 처리
- **짧은 예시 유지**: 짧은 코드 블록(3줄 이상, 10줄 미만)은 유지하되 관련 GitHub 링크 추가
- **매우 짧은 코드**: 3줄 미만의 매우 짧은 예시 코드는 원본 유지
- **언어 태그 필수**: `python`, `bash`, `yaml` 등
- **보안 관련 코드**: 민감 정보 제거 필수

### 긴 코드 블록 링크 형식

```markdown
> **참고**: 전체 코드는 [관련 링크 텍스트](링크 URL)를 참조하세요.
> 
> ```language
> # 코드 미리보기...
> ```

<!-- 전체 코드는 위 링크 참조
```language
[전체 코드 내용]
```
-->
```

### 코드 예제 모범 사례

```markdown
```bash
# 좋은 예: 설명이 포함된 명령어
aws ec2 describe-instances --filters "Name=tag:Name,Values=production-*"

# 나쁜 예: 민감한 정보 포함
aws ec2 describe-instances --region us-east-1 --profile my-secret-profile
```
```

---

## 이미지 규칙

### 이미지 생성 워크플로우

포스팅 작성 후 이미지는 다음 순서로 생성합니다:

1. **프롬프트 자동 생성**: `scripts/generate_post_images.py` 스크립트 실행
2. **프롬프트 확인**: 생성된 프롬프트 파일 확인
3. **이미지 생성**: DALL-E, Midjourney, Stable Diffusion 등으로 이미지 생성
4. **이미지 저장**: `assets/images/` 디렉토리에 저장
5. **포스팅 연결**: front matter의 `image` 필드 확인

```bash
# 포스팅 작성 후 이미지 생성 프롬프트 생성
python3 scripts/generate_post_images.py _posts/새포스팅.md

# 생성된 프롬프트 확인
cat assets/images/새포스팅_prompt.txt
```

### 이미지 파일명 규칙

- **⚠️ 중요**: 모든 이미지 파일명은 반드시 영어로 작성해야 합니다
- 한글이 포함된 이미지 파일명은 사용하지 않음
- 파일명 형식: `YYYY-MM-DD-[영문_제목].svg` 또는 `.png`, `.jpg`
- 예시: `2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_and_GitHub_DevSecOps_Practical.svg`
- **파일명 변환**: 한글 파일명이 있으면 `scripts/rename_images_to_english.py` 스크립트 사용

### 이미지 삽입 형식

#### Jekyll Liquid 형식 (권장)

```markdown
<img src="{{ '/assets/images/[영문_파일명].svg' | relative_url }}" alt="영문 이미지 설명" loading="lazy" class="post-image">
```

#### 마크다운 형식

```markdown
![이미지 설명](assets/images/[영문_파일명].svg)
*그림 1: 이미지 설명*
```

### 이미지 스타일 가이드

#### Nano Banana 스타일

모든 이미지는 **nano banana 스타일**을 따릅니다:

- **스타일**: 미니멀하고 깔끔한 일러스트
- **색상**: 보안/기술 블로그에 맞는 전문적인 색상 팔레트
- **크기**: 블로그 포스팅에 최적화된 가로형 레이아웃 (1200x800px 권장)
- **텍스트**: SVG 내 텍스트는 영어만 사용 (한글 사용 금지)

#### 카테고리별 색상 팔레트

| 카테고리 | 색상 팔레트 | 설명 |
|---------|------------|------|
| `security` | Red (#CC0000) for threats, Green (#00AA44) for security measures, Blue (#0066CC) for infrastructure | 보안 위협과 대응 방안 시각화 |
| `devsecops` | Blue (#0066CC) for CI/CD, Green (#00AA44) for security, Orange (#FF6600) for deployment | DevSecOps 파이프라인 시각화 |
| `cloud` | AWS orange (#FF9900), Blue (#0066CC) for networking, Green (#00AA44) for security | 클라우드 아키텍처 시각화 |
| `kubernetes` | Kubernetes blue (#326CE5), Green (#00AA44) for pods, Orange (#FF6600) for services | Kubernetes 클러스터 시각화 |
| `incident` | Red (#CC0000) for incident start, Orange (#FF6600) for investigation, Yellow (#FFCC00) for response, Green (#00AA44) for recovery | 인시던트 타임라인 시각화 |

### 이미지 타입별 가이드

#### 아키텍처 다이어그램

- **용도**: 시스템 구조, 네트워크 구조 시각화
- **요소**: 컴포넌트, 연결 관계, 보안 레이어
- **레이아웃**: 상하 또는 좌우 흐름

**예시 프롬프트:**
```
Create a nano banana style AWS VPC architecture diagram showing:
- Internet Gateway at the top
- Public Subnet with NAT Gateway and Load Balancer
- Private Subnet with EC2 instances and RDS database
- Security Groups as protective layers around each component
Style: minimalist AWS architecture illustration
Colors: AWS orange (#FF9900), Blue for networking, Green for security
Layout: vertical flow from top (Internet) to bottom (Database)
Include: Korean labels for each component (인터넷 게이트웨이, 퍼블릭 서브넷, 프라이빗 서브넷, 보안 그룹)
```

#### 프로세스 흐름도

- **용도**: 워크플로우, 프로세스 단계 시각화
- **요소**: 단계별 프로세스, 의사결정 포인트, 결과
- **레이아웃**: 좌우 또는 상하 흐름

**예시 프롬프트:**
```
Create a nano banana style vulnerability scanning workflow diagram showing:
- Step 1: Automated scanning tools (scanner icon)
- Step 2: Vulnerability analysis (magnifying glass)
- Step 3: Risk assessment (risk matrix with severity levels)
- Step 4: Remediation actions (shield with checkmark)
- Step 5: Verification and reporting (document with checkmark)
Style: minimalist security process illustration
Colors: Red (#CC0000) for critical, Orange (#FF6600) for high, Yellow (#FFCC00) for medium, Green for low
Layout: horizontal process flow from left to right
Include: Korean labels (스캔, 분석, 평가, 대응, 검증)
```

#### 타임라인

- **용도**: 이벤트 순서, 장애 타임라인 시각화
- **요소**: 시간별 이벤트, 단계별 소요 시간, 주요 액션
- **레이아웃**: 좌우 타임라인

**예시 프롬프트:**
```
Create a nano banana style incident timeline showing:
- Timeline from left to right
- Key events marked with icons (alert, investigation, response, recovery)
- Color coding: Red for incident start, Orange for investigation, Yellow for response, Green for recovery
- Duration indicators showing time spent in each phase
Style: minimalist timeline illustration
Colors: Red (#CC0000), Orange (#FF6600), Yellow (#FFCC00), Green (#00AA44)
Layout: horizontal timeline
Include: Korean labels (인지, 조사, 대응, 복구)
```

#### 비교표/인포그래픽

- **용도**: 솔루션 비교, 데이터 시각화
- **요소**: 비교 항목, 차이점, 추천 사항
- **레이아웃**: 좌우 또는 상하 비교

### SVG 이미지 텍스트 규칙

- **⚠️ 중요**: SVG 이미지 내의 모든 텍스트는 반드시 영어로만 작성해야 합니다
- 한글 텍스트는 인코딩 문제로 인해 깨질 수 있으므로 사용하지 않음
- SVG 파일의 `<text>` 요소에는 영어만 사용
- 예시:
  - ❌ "클라우드 보안 과정" → ✅ "Cloud Security Course"
  - ❌ "보안 방어" → ✅ "Security Defense"
  - ❌ "정적 분석" → ✅ "Static Analysis"

### SVG 파일 인코딩 규칙

- **UTF-8 인코딩**: SVG 파일은 반드시 UTF-8 인코딩으로 저장
- **특수 문자 사용 금지**: 다음 특수 문자는 인코딩 문제를 일으킬 수 있으므로 사용하지 않음
  - ❌ `·` (middle dot) → ✅ `|` 또는 `&amp;`
  - ❌ `•` (bullet) → ✅ `-` 또는 `*`
  - ❌ `—` (em dash) → ✅ `-` 또는 `--`
  - ❌ `–` (en dash) → ✅ `-`
  - ❌ `"` `"` (curly quotes) → ✅ `"` 또는 `&quot;`
  - ❌ `'` `'` (curly apostrophes) → ✅ `'` 또는 `&apos;`
  - ❌ `…` (ellipsis) → ✅ `...`
- **XML 검증**: 모든 SVG 파일은 `xmllint --noout` 명령으로 검증 가능해야 함
- **인코딩 검증**: 파일 저장 후 UTF-8 인코딩 오류가 없는지 확인

### 이미지 크기 및 해상도

- **SVG**: 벡터 이미지 (권장, 무한 확대 가능)
- **PNG**: 래스터 이미지
  - **일반 이미지**: 1200x800px (가로형 블로그 포스트용)
  - **OG 이미지**: 1200x630px (Open Graph 표준)
  - **해상도**: 300 DPI 권장 (고해상도 출력용)

### 이미지 생성 도구

#### 자동 프롬프트 생성

```bash
# 포스팅 작성 후 자동으로 프롬프트 생성
python3 scripts/generate_post_images.py _posts/포스팅명.md
```

#### 이미지 생성 도구

1. **DALL-E (OpenAI)**: https://platform.openai.com/docs/guides/images
2. **Midjourney**: https://www.midjourney.com/
3. **Stable Diffusion**: https://stability.ai/
4. **Gemini Studio**: https://makersuite.google.com/app/prompts/image

### 이미지 검증 체크리스트

포스팅 작성 완료 후 이미지 확인:

- [ ] 이미지 파일명이 영어로 작성되었는지 확인
- [ ] SVG 이미지 내 텍스트가 영어로만 작성되었는지 확인
- [ ] SVG 파일이 유효한 XML 형식인지 확인 (`xmllint --noout` 검증)
- [ ] SVG 파일에 특수 문자가 없는지 확인
- [ ] SVG 파일이 UTF-8 인코딩으로 저장되었는지 확인
- [ ] 이미지 경로가 front matter의 `image` 필드와 일치하는지 확인
- [ ] 이미지가 포스팅 내용과 일관성이 있는지 확인
- [ ] 이미지 크기가 적절한지 확인 (1200x800px 권장)

---

## 표 형식 규칙

### 프로세스/워크플로우 표

프로세스나 워크플로우를 설명할 때는 표 형식을 사용:

```markdown
| 단계 | 프로세스 | 설명 | 결과 |
|------|---------|------|------|
| 1 | 사용자 요청 | 사용자가 리소스 접근 요청 | - |
| 2 | Identity Verification | 사용자 신원 확인 | 인증 성공/실패 |
```

### 위험도별 정책 표

보안 정책이나 접근 제어를 설명할 때는 위험도별로 표로 정리:

```markdown
| 위험도 | 접근 권한 | 추가 조치 | 설명 |
|--------|----------|----------|------|
| **Low** | Full Access | 없음 | 신뢰할 수 있는 사용자/디바이스 |
| **Medium** | Limited Access | MFA 필수 | 부분적 신뢰, 제한적 접근 |
| **High** | Block + Alert | 보안 팀 알림 | 의심스러운 활동, 접근 차단 |
```

### 모니터링 대상 표

모니터링이나 체크리스트를 설명할 때는 표 형식 사용:

```markdown
| 모니터링 대상 | 설명 | 목적 |
|-------------|------|------|
| **Identity Verification** | 사용자 인증 상태 지속 확인 | 세션 하이재킹 방지 |
| **Device Trust Assessment** | 디바이스 상태 실시간 모니터링 | 디바이스 변조 탐지 |
```

### 표 변환 우선순위

1. **프로세스/워크플로우**: 단계별 설명은 표로 변환
2. **정책/규칙**: 위험도별, 레벨별 정책은 표로 변환
3. **체크리스트**: 보안 체크리스트, 기능 목록은 표로 변환
4. **비교표**: Before/After, 솔루션 비교는 표로 변환
5. **모니터링 대상**: 모니터링 항목은 표로 변환

### 중복 제거

- 표에 포함된 내용과 중복되는 텍스트 설명은 제거하여 가독성 향상

---

## 보안 관련 규칙

### 민감 정보 처리

- API 키, 비밀번호, 토큰은 절대 실제 값 사용 금지
- 예시: `YOUR_API_KEY`, `your-secret-key`, `***` 사용
- 환경 변수나 시크릿 관리 도구 사용 예시 제공
- 로그 파일에 민감 정보가 기록되지 않도록 주의

### 민감 정보 마스킹 패턴

- API 키: `sk-***MASKED***`, `AIza***MASKED***`
- 비밀번호: `***MASKED***`
- 토큰: `***TOKEN_MASKED***`
- 실제 IP 주소: 예시 IP 사용 (예: `192.0.2.0`)

### 보안 경고 박스

```markdown
> **⚠️ 보안 주의사항**
> 
> [주의해야 할 보안 관련 내용]
> 
> - [주의사항 1]
> - [주의사항 2]
```

### 보안 모범 사례 강조

- 코드 예제에 보안 주석 추가
- 취약점 및 대응 방법 명시
- 보안 체크리스트 제공 (필요시)
- Defense in Depth 전략 설명
- 최소 권한 원칙 적용 예시

---

## 링크 규칙

### 링크 검증 원칙

- **모든 링크는 실제 존재하는 리소스로만 사용**
- `github.com/example/*` 같은 더미 링크는 절대 사용하지 않음
- 링크 추가 전 웹 검색을 통해 실제 존재 여부 확인
- GitHub 링크는 실제 리포지토리, 문서, 도구 링크만 사용

### 링크 교체 전략

1. **더미 링크 발견 시**:
   - 웹 검색을 통해 관련 실제 리소스 찾기
   - 공식 문서, 오픈소스 프로젝트, 실제 GitHub 리포지토리 우선
   - 관련 리소스를 찾을 수 없으면 링크 제거하고 텍스트 설명으로 대체

2. **참고 자료 섹션**:
   - 실제 존재하는 공식 문서, GitHub 리포지토리, 표준 스펙 링크 추가
   - 각 링크에 명확한 설명 포함

3. **코드 예제 링크**:
   - 실제 구현 예시는 가능한 한 실제 GitHub 리포지토리 링크로 대체
   - 공식 문서나 예제 리포지토리 우선 사용

### 코드 블록 링크 매핑 규칙

각 코드 타입에 맞는 적절한 GitHub 저장소 또는 공식 문서 링크를 사용:

- **AWS 관련 코드**: `https://github.com/aws-samples` 또는 구체적인 예제 저장소
- **Terraform/HCL**: `https://github.com/terraform-aws-modules` (AWS 관련), `https://registry.terraform.io/` (일반)
- **Kubernetes YAML**: `https://github.com/kubernetes/examples` (Kubernetes 리소스), `https://kubernetes.io/docs/` (공식 문서)
- **Python (AWS)**: `https://github.com/aws-samples`
- **Python (일반)**: `https://docs.python.org/3/`
- **Bash/Shell**: `https://www.gnu.org/software/bash/manual/bash.html` (공식 문서)
- **GitHub Actions/Dependabot**: `https://docs.github.com/en/actions`, `https://docs.github.com/en/code-security/dependabot`
- **CodeQL**: `https://docs.github.com/en/code-security/code-scanning/using-codeql-code-scanning-with-your-ci`

---

## 카테고리 및 태그 규칙

### 카테고리 목록

- `security`: 보안 관련 글
- `devsecops`: DevSecOps 관련
- `devops`: DevOps 관련
- `cloud`: 클라우드 관련
- `kubernetes`: Kubernetes 관련
- `finops`: FinOps 관련
- `incident`: 보안 사고 분석

### 태그 작성 규칙

- **5-10개 권장**: 너무 많거나 적지 않게
- **일관성 유지**: 유사한 포스팅은 유사한 태그 사용
- **대소문자**: 카멜케이스 또는 케밥케이스 사용 (예: `DevSecOps`, `GitHub-Actions`)
- **영문 권장**: 태그는 영문으로 작성하는 것을 권장

### 태그 예시

```yaml
tags: [AWS, CloudFront, cloudsecurity, Cybersecurity, DevSecOps, github, githubactions, SecurityEngineering, TechBlog, waf]
```

---

## 검증 체크리스트

### 포스트 작성 완료 후 확인

- [ ] Front matter 형식 올바름
- [ ] 포스팅 요약 섹션 포함 (HTML 또는 마크다운 형식)
- [ ] 이미지 경로 올바름 (`/assets/images/` 디렉토리)
- [ ] **이미지 파일명이 영어로 작성되었는지 확인** (한글 파일명 사용 금지)
- [ ] **SVG 이미지 내 텍스트가 영어로만 작성되었는지 확인** (한글 텍스트 사용 금지)
- [ ] **SVG 파일이 유효한 XML 형식인지 확인** (`xmllint --noout` 검증)
- [ ] **SVG 파일에 특수 문자가 없는지 확인**
- [ ] **모든 링크가 실제 존재하는 리소스를 가리키는지 확인** (더미 링크 사용 금지)
- [ ] **코드 블록 링크 개선 확인**: 긴 코드 블록은 링크로 대체되었는지 확인
- [ ] **프로세스/워크플로우 설명이 표 형식으로 작성되었는지 확인**
- [ ] **표에 포함된 내용과 중복되는 텍스트 설명이 없는지 확인**
- [ ] 코드에 민감 정보 없음 (API 키, 비밀번호, 토큰)
- [ ] 보안 고려사항 명시
- [ ] 마크다운 형식 올바름
- [ ] 서론 섹션 포함
- [ ] 본문 길이 1500자 이상 (권장)
- [ ] 원본 포스트 링크 포함 (있는 경우)

---

## 참고 문서

- `.cursorrules`: 프로젝트 전체 규칙
- `BEST_PRACTICES.md`: 포스팅 작성 모범 사례
- `GEMINI_IMAGE_GUIDE.md`: 이미지 생성 가이드
- `POST_VISUALIZATION_CHECKLIST.md`: 시각화 체크리스트
- `_config.yml`: Jekyll 설정 및 카테고리 목록

---

**마지막 업데이트**: 2026-01-11
**작성 기준**: 기존 포스팅 34개 분석 결과
