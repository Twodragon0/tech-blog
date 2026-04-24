# Tech Security Weekly Digest — Cover Layout Catalog

**Last updated**: 2026-04-24

이 문서는 Tech Security Weekly Digest 포스트의 연구 기반 SVG 커버 레이아웃 5종(L13, L14, L20, L21, L22) 및 향후 확장 슬롯(L15/L16)을 카탈로그화합니다.

각 레이아웃은 특정 뉴스 구성(1dominant+2supporting / 3-chain / 3-equal) 과 KPI 기반 의사결정에 최적화되어 있으며, 공통 파운데이션(색상, 타이포그래피, 필터)을 공유합니다.

---

## 섹션 1: 공통 파운데이션 (모든 레이아웃 적용)

### 캔버스 사양

| 항목 | 값 |
|------|-----|
| **viewBox** | `0 0 1200 630` |
| **종횡비** | 16:9 (OG/Twitter card, desktop) |
| **포맷** | `.svg` only (PNG/AVIF fallback 불가) |
| **크기 목표** | ≤ 50 KB |

### 파일 네이밍 규칙

```
YYYY-MM-DD-Tech_Security_Weekly_Digest_KW1_KW2_KW3_KW4.svg
```

- **영문만 사용** (CLAUDE.md 이미지 규칙)
- 포스트 slug과 정확히 일치
- 키워드는 뉴스 주제에서 추출 (예: `Apple`, `AI`, `Ransomware`)
- 언더스코어(`_`)로 연결, 하이픈 불가

**예시:**
- `2026-04-20-Tech_Security_Weekly_Digest_AI_Apple_AWS_Palantir.svg` (L20 Hero+2-Card)
- `2026-04-21-Tech_Security_Weekly_Digest_CVE_Apple_AI_Agent.svg` (L21 Metro Map)
- `2026-04-22-Tech_Security_Weekly_Digest_AI_Ransomware_AWS_Go.svg` (L22 Stacked Bands)

### 색상 팔레트

기본 배경 및 심각도 색상은 모든 레이아웃에서 일관성 있음:

| 용도 | 색상 | RGB / Hex |
|------|------|-----------|
| **배경 0%** | Dark Blue | `#0A1226` |
| **배경 50%** | Dark Purple | `#0C1430` |
| **배경 100%** | Deep Purple | `#131038` |
| **심각도: Critical** | Red | `#E63946` |
| **심각도: High** | Amber | `#FFB703` |
| **심각도: Medium** | Cyan | `#3A86FF` / `#2AA8CE` |
| **심각도: Low** | Green | `#4ADE80` |
| **텍스트 Primary** | Light Gray | `#F5F7FA` |
| **텍스트 Secondary** | Medium Gray | `#BFC9D9` |
| **Accent Accent** | Sky Blue | `#8FB8FF` |

### 타이포그래피

```
Font Family (prose):     "Inter, Helvetica, Arial, sans-serif"
Font Family (code/CVE):  "Monaco, monospace" (또는 `courier`)
Font Size Range:         14–72 px
Font Weight Range:       500–900 (600 body, 700 label, 800–900 heading)
Letter Spacing (label):  2–2.4 px
```

#### 텍스트 레이어 규칙

- **Eyebrow (label)**: 18px, weight 700, CAPS, 2–2.4px letter-spacing, color secondary (`#BFC9D9`)
- **Headline**: 30–36px, weight 800, color primary (`#F5F7FA`)
- **Subtitle**: 15–20px, weight 600, color secondary
- **Body/Description**: 14–16px, weight 500, color secondary
- **KPI Number**: 60–72px, weight 900, color primary
- **KPI Unit**: 12–14px, weight 600, color secondary

### 애니메이션 예산 및 제약

| 제약 | 목표 | 설명 |
|------|------|------|
| **총 애니메이션 노드** | ≤ 30개 | opacity, transform만 사용 |
| **animateMotion 경로** | ≤ 12개 | 무거운 경로 애니메이션 최소화 |
| **애니메이션 지속시간** | 1.5–9s | 부자연스러운 반복 피하기 |
| **기본 주기** | 6–8s | 대부분의 ambient 효과 |
| **prefers-reduced-motion** | 스타틱 SVG이므로 N/A | 간단한 펄스/트윈클만 사용 |

**권장 패턴:**

```xml
<!-- Opacity pulse (ambient glow) -->
<circle cx="300" cy="180" r="140" fill="url(#hotBlue)">
  <animate attributeName="opacity" values="0.55;0.9;0.55" dur="6.4s" repeatCount="indefinite"/>
  <animate attributeName="r" values="140;155;140" dur="8.2s" repeatCount="indefinite"/>
</circle>

<!-- Twinkle (starfield) -->
<circle cx="160" cy="62" r="1.2">
  <animate attributeName="opacity" values="0.2;1;0.2" dur="3.1s" repeatCount="indefinite"/>
</circle>
```

### 필터 정의 (defs 섹션)

모든 레이아웃은 `<defs>`에 다음 필터를 정의하고 필요시 재사용:

```xml
<filter id="softShadow" x="-10%" y="-10%" width="130%" height="130%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="2.5–3"/>
  <feOffset dx="1–2" dy="3–4"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.55–0.6"/></feComponentTransfer>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>

<filter id="textShadow" x="-5%" y="-5%" width="110%" height="110%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="1–1.2"/>
  <feOffset dx="0–1" dy="1.5"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.7–0.85"/></feComponentTransfer>
  <feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
```

### 보안 및 접근성

**SVG 보안:**
- 외부 `<image href>` 금지
- `<script>` 태그 금지
- `<foreignObject>` 금지
- CSP safe: `<style>` 인라인만 가능 (필요 시)

**접근성:**

루트 `<svg>` 엘리먼트에 필수:

```xml
<svg
  xmlns="http://www.w3.org/2000/svg"
  viewBox="0 0 1200 630"
  width="1200"
  height="630"
  role="img"
  aria-label="[전체 설명, 150자 이상]"
>
  <title>[한 줄 요약, 50자 이내]</title>
  <!-- ... 콘텐츠 ... -->
</svg>
```

**예시:**

```xml
<svg
  role="img"
  aria-label="Research-based weekly digest cover: Apple phishing envelope attack vector, NIST CVE funnel overflow reaching 50,000+ tracked vulnerabilities, Palantir manifesto blockchain compliance wall"
>
  <title>Apple phishing, NIST CVE halt, Palantir manifesto</title>
```

---

## 섹션 2: 레이아웃 카탈로그

### L20 — Hero + 2-Card Layout

**한국어**: 영웅 패널 + 2카드 (상하)  
**용도**: 1 dominant story (Critical) + 2 supporting stories

#### 캔버스 구성

| 영역 | 위치 | 크기 | 역할 |
|------|------|------|------|
| **Top Header** | x=0, y=0 | 1200×56 | 브랜드 레이블 + 날짜 + Weekly |
| **Hero Panel (좌측)** | x=60, y=130 | 540×380 | 1 dominant story illustration (예: Apple phishing envelope scene) |
| **Card 1 (우상)** | x=620, y=130 | 516×184 | 2nd story (예: NIST CVE funnel) |
| **Card 2 (우하)** | x=620, y=326 | 516×184 | 3rd story (예: Palantir manifesto) |

#### 스토리 슬롯 (3개)

1. **Hero (좌측 600×510 내부)**
   - Eyebrow: `CRITICAL`, color `#E63946`
   - Headline: ≤30 chars, weight 800
   - Illustration: 실제 공격 장면 (예: 봉투 슬라이딩, 피싱 메일, 화살표, 스파크)
   - Ambient: 방사형 글로우 (blue/red), 12개 스타필드 반짝임

2. **Card 1 (우상 516×184)**
   - Eyebrow: `HIGH`, color `#FFB703`
   - Headline: ≤25 chars
   - Subtitle: ≤40 chars
   - Illustration: 소형 (≤200×120)
   - KPI: 1 number + unit (예: "50K CVEs")

3. **Card 2 (우하 516×184)**
   - 카드 1과 동일 구조

#### 필터 및 그래디언트

**Gradients:**
- `bgSpread`: 배경 (0B1326 → 0D1530 → 141034)
- `heroPanel`: 영웅 패널 (12213E → 0E1A33)
- `appleMail`: 봉투 (F5F7FA → DCE2EB)
- `phishMail`: 피싱 봉투 (FFF3B5 → F6C945)
- `hotRed`, `hotBlue`, `hotAmber`: 방사형 글로우 (opacity pulse)

**Filters:**
- `softShadow`: 패널 그림자 (stdDeviation=3)
- `textShadow`: 텍스트 그림자 (stdDeviation=1.2)

**Patterns:**
- `paperWeave`: 봉투 텍스처 (6×6 격자 선)
- `envGrid`: 배경 점(40×40)

#### 애니메이션 핫스팟

- **Ambient glows**: 3개 원 (x2 opacity + radius)
- **Starfield**: 12개 반짝이는 별
- **Header title**: `WEEKLY` 텍스트 opacity pulse

**총 노드**: ~18개

#### 참고 파일

```
assets/images/2026-04-20-Tech_Security_Weekly_Digest_AI_Apple_AWS_Palantir.svg
```

#### 재사용 규칙

다른 포스트에서 L20을 사용하려면 **최소 7일 간격 필수** (시각적 다양성 유지)

#### 품질 검사

- [ ] 영웅 패널 삽화가 뚜렷한가?
- [ ] 2개 카드 레이아웃이 우하단에 정렬되어 있는가?
- [ ] KPI 카드 글꼴이 72px인가?
- [ ] 글로우가 부드러운 opacity pulse인가?
- [ ] 파일 크기 ≤50 KB?

---

### L21 — Metro Map Layout

**한국어**: 지하철 노선도 (3 라인, attack chain)  
**용도**: 3 stories, each following a multi-hop attack chain

#### 캔버스 구성

| 요소 | 위치 | 설명 |
|------|------|------|
| **3 Subway Lines** | y=170, 330, 490 | 각 라인은 4–5개 스테이션 (attack hop) |
| **Stations** | 다양 | 동그란 원, 심각도 색상 (red/amber/cyan) |
| **Travelers** | 라인 따라 | 이동하는 작은 원들 (animateMotion) |
| **Pulse Rings** | 스테이션 중심 | 펄싱 반지 (강조) |
| **Header** | y=0~80 | `WEEKLY` + legend (CRITICAL/HIGH/MEDIUM) |
| **Legend** | 우상단 | severity 점 + 텍스트 |

#### 스토리 슬롯 (3개 라인)

각 **Line** (Red/Amber/Cyan):

1. **Line Label** (좌측 y=170+offset)
   - 텍스트: `L1 CRITICAL`, `L2 HIGH`, `L3 MEDIUM`
   - 색상: 라인 색상과 일치

2. **4–5 Stations** (좌에서 우로)
   - Station 1: 초기 벡터 (예: SGLang)
   - Station 2–4: 공격 체인 (Jinja2 → RCE)
   - Station 5 (우측): 최종 영향 (Cryptocurrency theft)
   - 각 스테이션: 원 + 레이블 (≤10 chars)

3. **Travelers** (animateMotion along path)
   - 라인당 1–2개 원 (r=4–6)
   - 20–30s 지속 시간

#### 필터 및 그래디언트

**Gradients:**
- `bgGrad`: 배경 (0A1020 → 0C1630 → 0F1A3A)
- `pulseRed`, `pulseAmber`, `pulseCyan`: 라인 색상별 radial (opacity fade)

**Filters:**
- `stationShadow`: 스테이션 원 (stdDeviation=2.2)
- `textShadow`: 라벨 (stdDeviation=1)
- `glowRed`, `glowAmber`, `glowCyan`: 펄스 링 blur

**Pattern:**
- `dotGrid`: 배경 점(30×30)

#### 애니메이션 핫스팟

- **Header WEEKLY**: 텍스트 fill pulse (6s)
- **Legend boxes**: 테두리 opacity pulse (4s)
- **Pulse rings**: 원 반지름 펄스 (2–2.4s)
- **Travelers**: animateMotion along path (20–30s)
- **Guide lines**: y=150, 300, 450 opacity pulse (6s staggered)

**총 노드**: ~22개

#### 참고 파일

```
assets/images/2026-04-21-Tech_Security_Weekly_Digest_CVE_Apple_AI_Agent.svg
```

#### 재사용 규칙

최소 **7일 간격**

#### 품질 검사

- [ ] 3개 라인이 y=170/330/490에 정렬되어 있는가?
- [ ] 각 라인에 4–5개 스테이션이 있는가?
- [ ] Traveler들이 매끄럽게 이동하는가?
- [ ] Legend가 우상단에 고정되어 있는가?
- [ ] 파일 크기 ≤50 KB?

---

### L22 — Stacked Bands Layout

**한국어**: 수평 스택 밴드 (3 full-width, KPI-driven)  
**용도**: 3 equal-weight stories with strong numeric emphasis

#### 캔버스 구성

| 밴드 | y 범위 | 높이 | 구조 |
|------|--------|------|------|
| **Header** | 0–56 | 56 | 브랜드 레이블 |
| **Band A (Green)** | 56–266 | 210 | Story 1: AWS SOC 1 compliance (green accent) |
| **Band B (Red/Purple)** | 266–476 | 210 | Story 2: C2 botnet/threat (red accent) |
| **Band C (Amber)** | 476–630 | 154 | Story 3: CVE/issue (amber accent) |

#### 밴드 구조 (각 210px 높이)

**좌측 8px:** 심각도 색상 막대 (accent bar)

**테두리 레이블:** y=44
```
AWS COMPLIANCE (18px, weight 700, color green)
```

**메인 헤드라인:** y=86
```
Winter 2025 SOC 1 (36px, weight 800, color primary)
```

**서브타이틀:** y=118
```
184 services in scope (20px, weight 600, color secondary)
```

**지원 라인:** y=146
```
12 months : Jan 1 - Dec 31, 2025 : Ernst and Young LLP
(15px, weight 500, color secondary)
```

**중앙 일러스트레이션:** x=30–700, y=75–210 (예: 규정 배지, C2 hub-spoke, IP 호핑)

**우측 KPI 카드:** x=990, y=105
```
┌─────────────────────┐
│    SERVICES         │
│       184           │
│   +1 vs 2024        │
└─────────────────────┘
```

카드 크기: 180×125, radius 14, border green `#4ADE80`, stroke 2.2px

#### 필터 및 그래디언트

**Gradients:**
- `bgSpread`: 배경 (0A1226 → 0C1430 → 131038)
- `bandA`, `bandB`, `bandC`: 각 밴드 선형 (좌→우)
- `badgeCert`: 규정 배지 (4ADE80 → 16A34A)
- `ipStream`: IP 스트림 (FFB703 opacity fade)
- `c2Glow`: C2 hub 방사형 (E63946 opacity fade)

**Filters:**
- `softShadow`: KPI 카드 (stdDeviation=2.5)
- `textShadow`: 텍스트 (stdDeviation=1.2)

**Patterns:**
- `ledgerGrid`: 밴드 배경 격자 (40×20)
- `circuitDot`: 배경 점 (18×18)

#### 애니메이션 핫스팟

- **Badge parade**: 규정 배지 행진 (x 애니메이션, 6s)
- **KPI indicator**: 원 펄싱 (opacity/radius, 1.8s)
- **Band accents**: 좌측 막대 색상 pulse (2–3s)

**총 노드**: ~15개

#### 참고 파일

```
assets/images/2026-04-22-Tech_Security_Weekly_Digest_AI_Ransomware_AWS_Go.svg
```

#### 재사용 규칙

최소 **7일 간격**

#### 품질 검사

- [ ] 3개 밴드이 y=56/266/476에 정렬되어 있는가?
- [ ] 좌측 accent bar가 올바른 색상인가?
- [ ] KPI 카드 글꼴이 72px인가?
- [ ] Badge parade가 선형으로 이동하는가?
- [ ] 파일 크기 ≤50 KB?

---

## 섹션 3: 확장 슬롯 (L13/L14 구현 완료, L15/L16 제안)

### L13 — Callout Cards (4개 brief용, Implemented)

**용도**: 4개 이상 작은 뉴스, single dominant 없음

**구조**: 2×2 그리드, 300×280 카드 × 4

```
┌─────────────┬─────────────┐
│  Card 1     │  Card 2     │  y=56–336
├─────────────┼─────────────┤
│  Card 3     │  Card 4     │  y=336–616
└─────────────┴─────────────┘
```

**카드 요소:**
- Icon (32×32, 좌상단)
- Title (≤20 chars, weight 700)
- Summary (≤40 chars, 2줄)
- Severity dot (우하단)

**예시 아이콘:** shield (보안), target (취약점), alert (긴급)

**상태**: **Implemented (2026-04-24)**

**Reference**: `assets/images/2026-04-10-Tech_Security_Weekly_Digest_AI_Malware_Go_Agent.svg`
- 실제 구현 카드 크기: 상단 2개 564/556 × 248, 하단 2개 564/556 × 242 (spec 300×280 대비 와이드 비율 적용)
- 각 카드: 좌측 severity bar(6px) + 번호 배지(40×40) + 아이콘 + 타이틀 + 3줄 본문 + KPI 카드(120×100)
- 4 카드 색상: Red(EngageLab) / Amber(UAT-10362) / Blue(Agentic SOC) / Purple(WebRTC)

---

### L14 — Timeline Layout (시간순, Implemented)

**용도**: 한 주(7일) 내 3개 이상 사건의 시간순 기록, 이웃 digest와 시각 충돌 회피용 대안

**구조**: 수평 시간축 (y=170) + 하단 3개 수직 스토리 카드 (336×374)

```
APR 13   APR 14   APR 15   APR 16   APR 17   APR 18   APR 19
  │        •        │        •        │        •        │
  └────────┴────────┴────────┴────────┴────────┴────────┘  (gradient axis)
           ↓                 ↓                 ↓
      ┌────────┐        ┌────────┐        ┌────────┐
      │ Col A  │        │ Col B  │        │ Col C  │
      │ Chain  │        │ Chain  │        │ Chain  │
      │ 4 step │        │ 4 step │        │ 4 step │
      │ KPI    │        │ KPI    │        │ KPI    │
      └────────┘        └────────┘        └────────┘
```

**요소:**
- Axis gradient: Green → Blue → Amber → Red (시간 진행에 따른 심각도 의미 부여)
- Date pulse ring (3× `<animate r>` 반복): 각 이벤트 앵커 지점
- Drop line: 타임라인 → 카드 (dasharray)
- Story card: eyebrow / title / subtitle / 4-step chain (번호 배지 + 연결선) / KPI pill

**상태**: **Implemented (2026-04-24)**

**Reference**: `assets/images/2026-04-19-Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet.svg`
- 3 events: Apr 14 Mirai Nexcorium CVE-2024-3721 (Blue) / Apr 16 Helpdesk impersonation (Amber) / Apr 18 Grinex 13.74M hack (Red)
- 18 animated nodes, 20KB

---

### L15 — Geographic Map Layout (지도, TBD)

**용도**: 공격 출처/영향 지도 (예: DDoS 분포)

**구조**: 세계 지도 실루엣 + attack origin pins

**상태**: **TBD — 제안만 함**

---

### L16 — Stack Compact Layout (4행 고밀도, TBD)

**용도**: 모바일 뷰(600px) 최적화, 4개 dense 리스트

**구조**: 4 rows × full-width, 각 row 140px

```
Row 1: Eyebrow + Title + KPI (모바일 가로 스크롤)
Row 2: Eyebrow + Title + KPI
Row 3: Eyebrow + Title + KPI
Row 4: Eyebrow + Title + KPI
```

**상태**: **TBD — 제안만 함**

---

## 섹션 4: 선택 휴리스틱 (결정 트리)

포스트 frontmatter + executive summary를 읽은 후 다음 흐름:

```
1 dominant story (Critical) + 2 supporting?
   └─> L20 HERO+2-CARD

3 stories, each with ≥3-hop attack chain?
   └─> L21 METRO MAP

3 equal-weight stories + strong numbers/KPI?
   └─> L22 STACKED BANDS

4+ small briefs, no dominant?
   └─> L13 CALLOUTS (2x2 grid)

Chronological sequence of 3 events within one week, neighbor digest uses L20/L21/L22?
   └─> L14 TIMELINE (horizontal axis + 3 columns)

Geographic distribution?
   └─> L15 GEOGRAPHIC MAP (when implemented)

Mobile-first density (4 rows)?
   └─> L16 STACK COMPACT (when implemented)
```

---

## 섹션 5: 저작 워크플로우

### 단계 1: 뉴스 분석

포스트 frontmatter 읽기:
- **제목**: Korean → 영문 요약 (≤40 chars)
- **카테고리**: devsecops/security/cloud 등
- **뉴스 수**: 1개? 3개? 4+개?
- **dominance**: 뉴스 1이 critical인가?

### 단계 2: 레이아웃 선택

위의 **선택 휴리스틱** 트리 사용

### 단계 3: 콘텐츠 추출

각 스토리마다:
- **Eyebrow** (CAPS, ≤15 chars): 심각도 + 기술 범주
- **Headline** (영문, ≤30 chars): 핵심 메시지
- **Subtitle** (영문, ≤40 chars): 세부 정보
- **KPI** (1 숫자 + unit): 영향 범위 (예: "50K affected")
- **Illustration concept**: 공격 장면, 아이콘, 차트 스타일

**예시:**

```
Story 1 (Apple Phishing):
  Eyebrow:      CRITICAL
  Headline:     Apple Users Targeted
  Subtitle:     Sophisticated phishing envelope vector
  KPI:          100K+ at risk
  Illustration: Phishing envelope with sliding letter animation

Story 2 (NIST CVE):
  Eyebrow:      HIGH
  Headline:     CVE Database Halt
  Subtitle:     NIST CVE overflow reaches 50K entries
  KPI:          50K CVEs
  Illustration: Funnel diagram, overflow effect
```

### 단계 4: 파일명 생성

```
YYYY-MM-DD-Tech_Security_Weekly_Digest_KW1_KW2_KW3_KW4.svg

예:
2026-04-20-Tech_Security_Weekly_Digest_Apple_Phishing_CVE_Palantir.svg
```

### 단계 5: SVG 저작

**선택한 레이아웃 템플릿** 복사 → 콘텐츠 교체:
- 텍스트: 헤드라인, 서브타이틀, KPI
- 일러스트레이션: 색상, 모양, 애니메이션
- 필터/그래디언트: 필요시 adjust

### 단계 6: 브라우저 검증

```bash
# 데스크톱 (1200×630)
open assets/images/YYYY-MM-DD-....svg

# 모바일 (600×315)
# 브라우저 개발자 도구 → 반응형 모드 → 600×315
```

- 텍스트 가독성?
- 일러스트레이션이 뚜렷한가?
- 애니메이션이 부자연스럽지는 않은가?

### 단계 7: 커밋

```bash
git add assets/images/YYYY-MM-DD-....svg
git commit -m "feat(images): Research-based weekly digest cover (YYYY-MM-DD) — [Layout name]"
```

**예:**
```bash
git commit -m "feat(images): Research-based weekly digest cover (04-20) — hero+2-card layout"
```

---

## 섹션 6: 품질 검사 체크리스트 (커밋 전)

모든 커버는 다음을 충족해야 합니다:

### 구조

- [ ] `viewBox="0 0 1200 630"`
- [ ] `role="img"` + `aria-label` (≥150 chars)
- [ ] `<title>` (한 줄 요약)
- [ ] 파일명이 포스트 slug과 정확히 일치

### 콘텐츠

- [ ] 모든 텍스트가 **영문** (CLAUDE.md 규칙)
- [ ] 헤드라인 ≤30 chars
- [ ] Subtitle ≤40 chars
- [ ] 심각도 색상 정확 (red/amber/cyan/green)
- [ ] 일러스트레이션이 뚜렷한가?

### 보안/성능

- [ ] 외부 `<image href>` 없음
- [ ] `<script>` 없음
- [ ] `<foreignObject>` 없음
- [ ] 파일 크기 ≤50 KB
- [ ] 애니메이션 노드 ≤30개

### 애니메이션

- [ ] 부드러운 opacity pulse?
- [ ] 애니메이션 지속시간 1.5–9s?
- [ ] 스타필드/traveler 이동이 자연스러운가?
- [ ] 없는 반복이나 버벅거림?

### 접근성/반응형

- [ ] 데스크톱 (1200×630) 검증
- [ ] 모바일 (600×315) 검증 (텍스트 크기 확인)
- [ ] 고대비 색상 (contrast ratio ≥4.5:1)?

### 재사용 규칙

- [ ] 같은 레이아웃이 지난 7일 내에 사용되지 않았는가?

---

## 섹션 7: 참고 문서

### 관련 CLAUDE.md 섹션

- **Image Rules**: `/Users/yong/Desktop/personal/tech-blog/CLAUDE.md` § Image Rules
  - 파일명: English only, no Korean
  - SVG text: English only, no special chars (·•—"')
  - UTF-8 encoding

### 이전 세션 노트

- **PR #288–292 session summary**: `/Users/yong/Desktop/personal/tech-blog/notes/per-pr/PR-288-292.md`
  - Research-based SVG 커버 도입
  - L20, L21, L22 레이아웃 확정
  - CLS 0 달성, 100점 성능

### 관련 파일

```
assets/images/                        # 모든 커버 저장
  2026-04-20-Tech_Security_Weekly_Digest_AI_Apple_AWS_Palantir.svg
  2026-04-21-Tech_Security_Weekly_Digest_CVE_Apple_AI_Agent.svg
  2026-04-22-Tech_Security_Weekly_Digest_AI_Ransomware_AWS_Go.svg

_posts/                               # Weekly digest 포스트
  2026-04-20-Weekly_Digest_Vol_N.md
  2026-04-21-Weekly_Digest_Vol_N.md
  2026-04-22-Weekly_Digest_Vol_N.md

docs/guides/                          # 이 문서
  digest-cover-layouts.md
```

---

## 자주 묻는 질문 (FAQ)

### Q: L20을 방금 사용했는데 다시 쓸 수 있나?

**A**: 최소 **7일 간격**을 두세요. 같은 layout을 시각적으로 연속 사용하면 digest 포스트들이 다양성을 잃습니다.

### Q: SVG에서 폰트를 다운로드할 수 있나?

**A**: 아니요. 폰트는 시스템 기본값 사용 (Inter → Helvetica → Arial → sans-serif). 외부 폰트 import 금지 (CSP, 다운로드 시간).

### Q: 애니메이션이 iOS Safari에서 안 보이는데?

**A**: 스태틱 SVG는 `<animate>` 태그를 지원합니다. 만약 안 보이면 다음을 확인:
- `repeatCount="indefinite"` 설정 확인
- `dur` 값이 합리적인가? (1.5–9s)
- 애니메이션이 opacity/transform만 사용하는가?

### Q: 파일 크기가 50 KB를 초과했다. 뭘 줄일 수 있나?

**A**: 우선순위:
1. **일러스트레이션 수정**: 경로 간단화 (`simplify-path` tool 사용)
2. **그래디언트 제거**: 불필요한 `<stop>` 제거
3. **애니메이션 감소**: 파르스 애니메이션 제거
4. **패턴 제거**: 배경 `<pattern>` 선택적 사용

---

**Last updated**: 2026-04-23
