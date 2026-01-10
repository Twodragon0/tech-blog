---
layout: post
title: "[Post-Mortem] 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지"
date: 2025-11-19 12:25:20 +0900
category: incident
tags: [Cloudflare, Post-Mortem, Incident-Response, CDN, Network, SRE]
excerpt: "Post-Mortem: 2025년 11월 18일 Cloudflare 글로벌 네트워크 장애 대응 일지. 모바일/PC 환경 상이한 증상 분석(모바일 100% 접속 불가, PC 간헐적 접속), Multi-CDN 전략 및 자동 Failover 구현 방안, 2025년 Cloudflare 보안 업데이트(Post-Quantum Encryption, DDoS 위협 동향), 인시던트 대응 프로세스, 모니터링 및 알림 체계 개선까지 실무 중심 정리."
comments: true
toc: true
original_url: https://twodragon.tistory.com/699
image: /assets/images/2025-11-19-Post-Mortem_2025년_11월_18일_Cloudflare_글로벌_장애_대응_일지_우리는_무엇을_배웠나.svg
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">[Post-Mortem] 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Incident</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Cloudflare</span>
      <span class="tag">Post-Mortem</span>
      <span class="tag">Incident-Response</span>
      <span class="tag">CDN</span>
      <span class="tag">Network</span>
      <span class="tag">SRE</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>Cloudflare 글로벌 네트워크 장애 대응 및 분석</li>
      <li>모바일과 PC 환경에서 나타난 상이한 증상 분석</li>
      <li>Multi-CDN 전략 및 자동 Failover 구현 방안</li>
      <li>2025년 Cloudflare 보안 업데이트: Post-Quantum Encryption, DDoS 위협 동향</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Cloudflare, Multi-CDN, Prometheus, BGP</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">SRE, 인시던트 대응 담당자, 운영 엔지니어</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>



<img src="{{ '/assets/images/2025-11-19-Post-Mortem_2025년_11월_18일_Cloudflare_글로벌_장애_대응_일지_우리는_무엇을_배웠나_image.png' | relative_url }}" alt="포스트 이미지" loading="lazy" class="post-image">
*그림: 포스트 이미지*


## 1. 들어가며

2025년 11월 18일 저녁, 전 세계 수많은 인터넷 서비스를 마비시킨 **Cloudflare의 글로벌 네트워크 장애**가 발생했습니다. 우리 서비스 역시 예외는 아니었습니다.

이 글은 긴박했던 장애 상황에서 우리 팀이 어떻게 문제를 인지하고 대응했는지, 특히 **모바일과 PC 환경에서 나타난 상이한 증상**을 어떻게 분석했는지를 기록합니다.

## 2. 타임라인

| 시간 (KST) | 이벤트 |
|-----------|--------|
| 18:30 | 사용자 문의 시작 - "서비스 접속이 안 됩니다" |
| 18:35 | 모니터링 알림 발생 - HTTP 5xx 에러 급증 |
| 18:40 | 1차 조사 시작 - 내부 시스템 정상 확인 |
| 18:45 | Cloudflare Status 페이지 확인 - 장애 공지 없음 |
| 18:50 | SNS에서 글로벌 장애 정보 포착 |
| 18:55 | Cloudflare 공식 장애 공지 |
| 19:30 | 서비스 정상화 시작 |
| 20:00 | 완전 복구 |

## 3. 증상 분석

### 3.1 모바일 vs PC 환경 차이

흥미롭게도, **모바일과 PC 환경에서 다른 증상**이 나타났습니다.

```
📱 모바일 환경
├── 증상: 완전 접속 불가
├── 원인: DNS 캐시 짧음 + 모바일 네트워크 특성
└── 영향: 100% 사용자

💻 PC 환경
├── 증상: 간헐적 접속 가능
├── 원인: 브라우저 DNS 캐시 + 로컬 DNS 캐시
└── 영향: 약 60% 사용자
```

### 3.2 근본 원인

Cloudflare의 글로벌 네트워크에서 발생한 **BGP 라우팅 이슈**로 인해:

1. **DNS 응답 지연**: Cloudflare DNS 서버 응답 시간 급증
2. **Edge 서버 연결 실패**: 일부 PoP(Point of Presence) 접근 불가
3. **SSL/TLS 핸드셰이크 실패**: 인증서 검증 타임아웃

## 4. 대응 과정

### 4.1 즉시 대응

```bash
# 1. 상태 모니터링 강화
watch -n 5 'curl -o /dev/null -s -w "%{http_code}\n" https://our-service.com'

# 2. Cloudflare 상태 확인
curl -s https://www.cloudflarestatus.com/api/v2/status.json | jq '.status'

# 3. 대체 DNS 확인
dig @8.8.8.8 our-service.com
dig @1.1.1.1 our-service.com
```

### 4.2 커뮤니케이션

**내부 커뮤니케이션:**
- Slack 채널에 실시간 상황 공유
- 5분 간격 상태 업데이트

**외부 커뮤니케이션:**
- 상태 페이지 업데이트
- SNS 공지 (Twitter, Facebook)
- 고객사 직접 연락

## 5. 교훈 및 개선 사항

### 5.1 Multi-CDN 전략

단일 CDN 의존도를 낮추기 위한 **Multi-CDN 아키텍처** 도입:

```
┌─────────────────────────────────────────────┐
│ Traffic Manager │
│ (DNS-based Load Balancing) │
└─────────────────────────────────────────────┘
 │
 ┌───────────────┼───────────────┐
 ▼ ▼ ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Cloudflare│ │ Fastly │ │CloudFront│
│ (주) │ │ (백업) │ │ (백업) │
└─────────┘ └─────────┘ └─────────┘
```

### 5.2 모니터링 강화

```yaml
# Prometheus Alert Rule 예시
groups:
- name: cdn-monitoring
 rules:
 - alert: CDNLatencyHigh
 expr: cdn_response_time_seconds > 2
 for: 1m
 labels:
 severity: warning
 annotations:
 summary: "CDN 응답 지연 감지"

 - alert: CDNErrorRateHigh
 expr: rate(cdn_errors_total[5m]) > 0.1
 for: 2m
 labels:
 severity: critical
```

### 5.3 자동 Failover 구현

```python
# 간단한 CDN Failover 로직
class CDNFailover:
 def __init__(self):
 self.primary = "cloudflare"
 self.secondary = ["fastly", "cloudfront"]
 self.health_check_interval = 30

 def check_health(self, cdn):
 try:
 response = requests.get(f"https://{cdn}-endpoint/health", timeout=5)
 return response.status_code == 200
 except:
 return False

 def get_active_cdn(self):
 if self.check_health(self.primary):
 return self.primary
 for cdn in self.secondary:
 if self.check_health(cdn):
 return cdn
 raise Exception("All CDNs are down!")
```

## 6. 2025년 Cloudflare 보안 업데이트

이번 장애 대응을 계기로 Cloudflare의 최신 보안 기능과 위협 동향을 정리했습니다. 2025년 Cloudflare는 급변하는 보안 환경에 대응하기 위해 여러 중요한 업데이트를 발표했습니다.

### 6.1 Security Week 2025 주요 발표

**자동화된 Botnet 보호**
- AI 기반 봇 탐지 시스템 강화
- 실시간 봇넷 트래픽 분석 및 자동 차단
- Machine Learning 모델을 통한 정상 트래픽과 악성 봇 구분

**Cipher Suite 선택 기능**
- 고객이 직접 암호화 스위트를 선택할 수 있는 기능 제공
- 규정 준수(Compliance) 요구사항에 맞춘 암호화 설정 가능
- 레거시 시스템 호환성과 보안 강화 사이의 균형 조정

### 6.2 Post-Quantum Encryption 현황

```
┌─────────────────────────────────────────────┐
│     Post-Quantum Encryption 적용 현황       │
├─────────────────────────────────────────────┤
│  Human Traffic 보호율: 52% 달성             │
│  ├── HTTPS 연결의 과반수가 양자내성 암호화  │
│  ├── Kyber/ML-KEM 알고리즘 적용             │
│  └── 향후 100% 적용 목표                    │
└─────────────────────────────────────────────┘
```

양자 컴퓨터의 위협에 대비한 Post-Quantum Cryptography(PQC) 적용이 빠르게 진행 중입니다. 현재 전체 사람 트래픽의 **52%가 양자내성 암호화로 보호**되고 있습니다.

### 6.3 긴급 보안 대응: React CVE-2025-55182

2025년에 발견된 **React CVE-2025-55182 (CVSS 10.0)** 취약점에 대해 Cloudflare는 신속하게 WAF 규칙을 배포했습니다.

```yaml
# Cloudflare WAF Rule 예시
- name: Block React CVE-2025-55182
  expression: |
    (http.request.uri.path contains "/__webpack_hmr" and
     http.request.method eq "POST" and
     any(http.request.headers["content-type"][*] contains "application/json"))
  action: block
  priority: 1
  enabled: true
```

**CVSS 10.0 (Critical)** 등급의 이 취약점은 원격 코드 실행(RCE)을 가능하게 하며, Cloudflare는 취약점 공개 후 **24시간 이내에 전역 보호 규칙을 배포**했습니다.

### 6.4 DDoS 위협 동향

2025년 DDoS 공격은 전년 대비 **10배 증가**했으며, 특히 **1Tbps 이상의 Hyper-Volumetric 공격**이 급증했습니다.

```
DDoS 공격 규모 변화 (2024 vs 2025)
─────────────────────────────────────────────
2024년 평균  ████████░░░░░░░░░░░░  ~100Gbps
2025년 평균  ████████████████████  ~1Tbps+
─────────────────────────────────────────────
             10배 증가
```

**주요 특징:**
- 대규모 봇넷을 활용한 volumetric 공격 증가
- IoT 기기를 이용한 분산 공격 확대
- 다중 벡터(Multi-vector) 공격 기법 고도화

### 6.5 Email Security 강화

Cloudflare Email Security는 전체 이메일 트래픽 중 **5% 이상의 악성 이메일을 탐지**하고 있습니다.

| 위협 유형 | 탐지 비율 | 주요 특징 |
|----------|----------|----------|
| 피싱 | 45% | 브랜드 사칭, 긴급성 유도 |
| 멀웨어 첨부 | 25% | 문서 매크로, 실행 파일 |
| BEC 공격 | 20% | 임원 사칭, 송금 요청 |
| 스팸 | 10% | 대량 발송, 광고성 |

### 6.6 비영리 단체 공격 급증

2025년 가장 주목할 만한 변화는 **비영리 단체(Non-profit Organizations)가 가장 많이 공격받는 섹터**로 부상했다는 점입니다.

**공격 증가 원인:**
- 상대적으로 취약한 보안 인프라
- 사회적 영향력을 노린 핵티비즘(Hacktivism)
- 기부금 및 개인정보 탈취 목적
- 정치적/이념적 동기의 표적 공격

**Cloudflare의 대응:**
- Project Galileo를 통한 비영리 단체 무료 보호 확대
- 취약 조직 대상 보안 교육 프로그램 제공
- DDoS 방어 및 WAF 무료 지원

## 7. 체크리스트

향후 유사 상황 대비 체크리스트:

- [ ] Multi-CDN 설정 완료
- [ ] 자동 Failover 테스트
- [ ] Runbook 업데이트
- [ ] 팀 훈련 실시
- [ ] 커뮤니케이션 템플릿 준비
- [ ] Post-Quantum Encryption 지원 여부 확인
- [ ] 최신 CVE 보호 규칙 적용 확인
- [ ] DDoS 방어 임계값 검토

## 8. 결론

이번 장애를 통해 **외부 인프라 의존성 관리**의 중요성을 다시 한번 깨달았습니다. 100% 가용성은 불가능하지만, **장애 발생 시 빠르게 대응하고 복구할 수 있는 체계**를 갖추는 것이 핵심입니다.

> "Everything fails, all the time." - Werner Vogels, AWS CTO

---

📚 **참고 자료:**
- [Cloudflare Incident Report](https://www.cloudflarestatus.com/)
- [Cloudflare Security Week 2025](https://blog.cloudflare.com/security-week-2025/)
- [Cloudflare DDoS Threat Report 2025](https://blog.cloudflare.com/ddos-threat-report-2025/)
- [Cloudflare Post-Quantum Encryption](https://blog.cloudflare.com/post-quantum-encryption/)
- [SRE Book - Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [AWS Well-Architected - Reliability Pillar](https://aws.amazon.com/architecture/well-architected/)
