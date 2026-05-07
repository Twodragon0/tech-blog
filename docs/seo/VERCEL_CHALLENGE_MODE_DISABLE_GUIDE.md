# Vercel Attack Challenge Mode 비활성화 가이드

**상황**: 사용자가 Dashboard에서 OFF 시도했으나 자동 검증 결과 여전히 활성 (`x-vercel-mitigated: challenge`, HTTP 429).

이 문서는 Vercel plan 별 메뉴 위치 + 흔한 함정 + 검증 방법을 정리합니다.

## 1. 즉시 검증 명령

```bash
# Googlebot UA로 production fetch
curl -I -A "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" \
  https://tech.2twodragon.com/ | grep -E "HTTP|mitigated"
```

**기대 결과 (OFF 정상)**:
```
HTTP/2 200
(no x-vercel-mitigated header)
```

**현재 결과 (OFF 안 됨)**:
```
HTTP/2 429
x-vercel-mitigated: challenge
```

## 2. Vercel plan 별 메뉴 위치

Vercel은 plan에 따라 보안 메뉴 구성이 다릅니다.

### Hobby (Free) plan

- **Settings → Security**: Challenge Mode가 메뉴 자체에 없을 수 있음 (Pro+ 전용 기능)
- 대신 보이는 메뉴:
  - **Settings → Security → Deployment Protection**: 비밀번호 보호 (있다면 OFF)
  - **Settings → Security → Trust IPs**: IP 화이트리스트 (관계 없음)
- **결론**: Hobby plan에서 Challenge Mode가 활성이면 Vercel이 자동으로 활성화한 것 — Pro 업그레이드 또는 지원팀 문의 필요

### Pro plan

- **Settings → Security → Attack Challenge Mode** 토글 명시적으로 보임
- ON/OFF 변경 후 자동 저장 (별도 Save 버튼 없음)
- 변경 propagation: 1-5분

### Enterprise plan

- **Firewall → Rules**: Custom rules로 user-agent 기반 allowlist
- **Settings → Security → Attack Challenge Mode**: Pro와 동일

## 3. 흔한 함정

### 3-1. 변경 후 propagation 대기

- Vercel UI에서 토글 OFF 직후 1-5분간 변경이 반영 안 될 수 있음
- 캐시된 Edge response가 만료될 때까지 기존 challenge 응답 가능

### 3-2. 다른 보안 룰이 차단 중

`x-vercel-mitigated: challenge`가 보인다면 Challenge Mode가 작동 중. 그러나:
- **Bot Protection** (별도 메뉴): Pro+ 의 또 다른 봇 차단 기능
- **Firewall Rules**: Custom rule이 Googlebot UA 차단 중
- **Edge Network → DDoS Protection**: 자동 활성화된 경우

각 메뉴 모두 확인 필요.

### 3-3. project-level vs team-level 설정

- Team plan에서는 team-level 보안 정책이 project를 override 가능
- **Team Settings → Security**도 같이 확인

## 4. Plan 확인 방법

```bash
# Vercel CLI 설치된 경우
vercel projects ls --json | jq '.[] | select(.name == "tech-blog") | .accountType'
```

또는 UI:
- 좌측 상단 → 계정 또는 팀 이름 클릭 → **Settings** → **Plan**

## 5. 단계별 액션 가이드

### Step 1: Plan 확인 (1분)
1. https://vercel.com/dashboard
2. 좌측 상단 → 계정/팀 이름 → Plan 확인
3. Hobby라면 Step 2 skip하고 Step 4로

### Step 2: Pro plan에서 Challenge Mode OFF (2분)
1. Project (tech-blog) 클릭
2. Settings 탭 → 좌측 사이드바 Security
3. **Attack Challenge Mode** 토글 OFF (회색)
4. 페이지 새로고침 → 토글 상태 OFF 유지 확인

### Step 3: 다른 보안 메뉴 확인 (Pro+ 한정, 5분)
1. Settings → Security 다른 항목들:
   - Bot Protection: OFF
   - Firewall: 룰 검토 (Googlebot 차단 룰 없는지)
2. Settings → Deployment Protection: OFF (비밀번호 보호 없게)

### Step 4: Hobby plan일 경우 대안 (10분)
- **옵션 A**: Pro 업그레이드 ($20/월)
- **옵션 B**: GH Pages backup으로 영구 이전
  - GH Pages: `https://twodragon0.github.io/tech-blog/` 정상 작동
  - DNS: `tech.2twodragon.com` CNAME → `twodragon0.github.io`로 변경
  - GH Pages settings에 custom domain `tech.2twodragon.com` 등록
- **옵션 C**: Cloudflare Workers + Vercel origin
  - Cloudflare proxy 활성 → bot UA 직접 처리
  - Vercel은 origin only

### Step 5: 변경 후 검증 (1분)
```bash
curl -I -A "Mozilla/5.0 (compatible; Googlebot/2.1)" \
  https://tech.2twodragon.com/ | grep -E "HTTP|mitigated"
```

기대: `HTTP/2 200` + mitigated 헤더 없음.

## 6. 백업 검증 (Challenge Mode 안 풀려도 사용 가능)

GH Pages는 Challenge Mode 영향 없음:

```bash
# GH Pages backup이 항상 정상
curl -I -A "Mozilla/5.0 (compatible; Googlebot/2.1)" \
  https://twodragon0.github.io/tech-blog/ | grep HTTP
# 기대: HTTP/2 200
```

GSC에서 `https://twodragon0.github.io/tech-blog/`도 별도 property로 등록 가능 (다만 정식 도메인 색인 우선).

## 7. 지원팀 문의 (마지막 수단)

Vercel Dashboard 우측 하단 **?** 또는 **Contact Support** → 다음 정보 첨부:

- Project name: `tech-blog`
- Symptom: `x-vercel-mitigated: challenge` 헤더가 일반 사용자에게도 자주 노출됨
- Impact: Google Search Console 색인 80일째 0건
- 시도한 액션: Settings → Security → Attack Challenge Mode 토글 OFF
- 검증 명령 + 결과 (위 Step 5)

## 8. 관련 자료

- 메모리: `feedback_vercel_challenge_mode.md`
- 작업 가이드: `docs/seo/2026-05-07_user_actions.md`
- baseline: `docs/seo/2026-05-07_baseline_metrics.json`
- 이번 turn 시도된 fix: `vercel.json` UA 헤더 + `middleware.js` (best-effort, 효과 미보장)

## 9. 체크리스트

- [ ] 현재 Vercel plan 확인 (Hobby/Pro/Enterprise)
- [ ] Settings → Security → Attack Challenge Mode 토글 OFF (Pro+)
- [ ] Settings → Security → Bot Protection OFF (Pro+)
- [ ] Settings → Security → Firewall Rules 검토 (Pro+)
- [ ] Team Settings → Security 확인 (Team plan)
- [ ] 5분 대기 후 `curl -A Googlebot ...` 200 응답 확인
- [ ] 200 응답 + mitigation 헤더 사라지면 GSC URL Inspection으로 재크롤 요청
- [ ] (Hobby라면) Pro 업그레이드 또는 GH Pages 영구 이전 결정
