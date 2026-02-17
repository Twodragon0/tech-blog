---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-01-29 10:00:00 +0900
description: '2026년 1월 29일 보안 뉴스: n8n 워크플로우 RCE 취약점(CVE-2026-1470, CVSS 9.9), D-Link
  단종 장비 Zero-Day(CVE-2026-0625), Kubernetes AI 에이전트 보안 과제, Infomaniak Swiss Sovereign
  Cloud, NHI 클라우드 침해 벡터 분석'
excerpt: n8n RCE(CVE-2026-1470 CVSS 9.9), D-Link Zero-Day, K8s AI 에이전트 보안 과제, Swiss
  Sovereign Cloud
image: /assets/images/2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent.svg
image_alt: Tech Security Weekly Digest January 29 2026 n8n RCE D-Link Zero-Day Kubernetes
  AI Agent
keywords:
- n8n RCE
- CVE-2026-1470
- D-Link Zero-Day
- CVE-2026-0625
- Kubernetes Security
- AI Agent
- eBPF
- Sovereign Cloud
- NHI
- DevSecOps
layout: post
schema_type: Article
tags:
- Security-Weekly
- n8n
- RCE
- CVE-2026-1470
- D-Link
- Zero-Day
- CVE-2026-0625
- Kubernetes
- AI-Agent
- eBPF
- Sovereign-Cloud
- NHI
- DevSecOps
- '2026'
title: 'Tech & Security Weekly Digest: n8n Critical RCE, D-Link 단종 장비 Zero-Day, Kubernetes
  AI 에이전트 보안'
toc: true
---

## 요약

- **핵심 요약**: n8n RCE(CVE-2026-1470 CVSS 9.9), D-Link Zero-Day, K8s AI 에이전트 보안 과제, Swiss Sovereign Cloud
- **주요 주제**: Tech & Security Weekly Digest: n8n Critical RCE, D-Link 단종 장비 Zero-Day, Kubernetes AI 에이전트 보안
- **키워드**: Security-Weekly, n8n, RCE, CVE-2026-1470, D-Link

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Tech & Security Weekly Digest (2026년 01월 29일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">n8n</span>
      <span class="tag">CVE-2026-1470</span>
      <span class="tag">RCE</span>
      <span class="tag">D-Link</span>
      <span class="tag">CVE-2026-0625</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">AI-Agent</span>
      <span class="tag">eBPF</span>
      <span class="tag">NHI</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>n8n Critical RCE (CVE-2026-1470)</strong>: CVSS 9.9 - JavaScript AST sandbox escape, Function constructor bypass로 원격 코드 실행</li>
      <li><strong>D-Link Zero-Day (CVE-2026-0625)</strong>: CVSS 9.3 - 단종 장비 DNS 커맨드 인젝션, 패치 불가, 즉시 교체 필요</li>
      <li><strong>Kubernetes AI 에이전트 보안</strong>: 비결정적 AI 에이전트 운영 시 eBPF 기반 보안, API 거버넌스, 런타임 모니터링 필수</li>
      <li><strong>Infomaniak Swiss Sovereign Cloud</strong>: GDPR 준수, OpenAI 호환 API, 100% 재생 에너지 유럽 클라우드</li>
      <li><strong>NHI 클라우드 침해 벡터</strong>: 비인간 ID가 2026년 클라우드 침해 주요 경로로 부상, 자동 remediation 필요</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">수집 기간</span>
    <span class="summary-value">2026년 1월 28일 ~ 29일 (48시간)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">DevSecOps 엔지니어, 클라우드 아키텍트, 보안 담당자, SRE, CISO</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

2026년 1월 29일 기준, 지난 48시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다. 이번 주는 **워크플로우 자동화 플랫폼의 Critical 취약점**, **단종 장비의 Zero-Day 위협**, 그리고 **Kubernetes 환경에서 AI 에이전트 보안 과제**가 핵심 화두였습니다.

> **긴급 알림**: n8n 자체 호스팅 인스턴스 운영 중이라면 **CVSS 9.9 RCE 취약점**(CVE-2026-1470)이 공개되었습니다. 즉시 1.123.17+ / 2.4.5+ / 2.5.1+로 업데이트하세요. D-Link DSL-2740R/2640B/2780B/526B 사용 중이라면 **패치 불가 Zero-Day**(CVE-2026-0625)가 활발히 악용 중이므로 즉시 교체가 필요합니다.

**이번 주 핵심 테마:**
- **Critical RCE**: n8n 워크플로우 자동화 플랫폼 CVSS 9.9 - JavaScript/Python sandbox escape
- **Zero-Day 위협**: D-Link 단종 장비 커맨드 인젝션, 패치 불가, 실제 악용 중
- **AI 보안 과제**: Kubernetes 클러스터 내 AI 에이전트 비결정적 행동 → eBPF 기반 대응
- **데이터 주권**: Infomaniak Swiss Sovereign Cloud - K8s/GPU/AI 관리형 서비스
- **클라우드 침해**: 비인간 ID(NHI)가 2026년 주요 침해 벡터로 부상

**수집 소스**: 47개 RSS 피드에서 218개 뉴스 수집
**분석 기준**: DevSecOps 실무 영향도, 기술적 깊이, 즉시 적용 가능성
**참고**: 이전 보안 다이제스트는 [2026-01-28 Microsoft Office Zero-Day 분석](/posts/2026/01/28/Tech_Security_Weekly_Digest_MS_Office_Zero_Day_CTEM_Grist_Core_RCE/)에서 확인하세요.

이번 포스팅에서는 다음 내용을 다룹니다:

- n8n 워크플로우 플랫폼 Critical RCE 취약점 심층 분석 및 대응
- D-Link 단종 장비 Zero-Day 위협과 네트워크 보안 점검
- Kubernetes AI 에이전트 보안 과제와 eBPF 기반 대응 전략
- Infomaniak Swiss Sovereign Cloud와 데이터 주권 동향
- 비인간 ID(NHI) 클라우드 침해 벡터 분석 및 방어 전략

## 빠른 참조

### 2026년 1월 29일 주요 기술/보안 이슈

| 이슈 | 출처 | 영향도 | 권장 조치 |
|------|------|--------|-----------|
| **n8n RCE (CVE-2026-1470)** | JFrog | 🔴 긴급 | 자체 호스팅 인스턴스 즉시 패치 (1.123.17+, 2.4.5+, 2.5.1+) |
| **n8n Python RCE (CVE-2026-0863)** | JFrog | 🔴 긴급 | 동일 패치 적용, Python 코드 노드 비활성화 검토 |
| **D-Link Zero-Day (CVE-2026-0625)** | Shadowserver | 🔴 긴급 | 단종 장비 즉시 교체, 네트워크 격리 |
| **K8s AI 에이전트 보안** | Tigera | 🟠 높음 | eBPF 기반 보안 도구 도입, API 거버넌스 수립 |
| **NHI 클라우드 침해** | Tenable | 🟠 높음 | 비인간 ID 인벤토리 점검, 자동 remediation 구축 |
| **Swiss Sovereign Cloud** | Infomaniak | 🟡 중간 | 유럽 데이터 주권 요구사항 시 도입 검토 |

### 긴급 조치 체크리스트

- [ ] n8n 자체 호스팅 인스턴스 버전 확인 및 패치 적용 (1.123.17+, 2.4.5+, 2.5.1+)
- [ ] D-Link DSL-2740R/2640B/2780B/526B 사용 여부 확인 및 즉시 교체
- [ ] 네트워크 내 단종 장비 인벤토리 점검
- [ ] Kubernetes 클러스터 내 AI 에이전트 권한 감사
- [ ] 비인간 ID(서비스 계정, API 키, 토큰) 인벤토리 및 권한 검토

---

## 1. n8n 워크플로우 자동화 플랫폼 Critical RCE

### 취약점 개요

JFrog 보안 연구팀이 n8n 워크플로우 자동화 플랫폼에서 **다수의 Critical RCE 취약점**을 발견했습니다. n8n은 GitHub Star 60K+ 이상의 인기 오픈소스 자동화 도구로, 자체 호스팅 인스턴스가 **60,000개 이상** 운영 중입니다.

| 항목 | CVE-2026-1470 | CVE-2026-0863 | CVE-2026-21858 (Ni8mare) |
|------|---------------|---------------|--------------------------|
| **CVSS** | 9.9 (Critical) | 8.5 (High) | 10.0 (Critical) |
| **유형** | JavaScript AST Sandbox Escape | Python AST Sandbox Escape | 비인증 RCE |
| **공격 벡터** | `with` 문 + Function constructor | format-string + AttributeError.obj | 인증 없이 원격 실행 |
| **인증 필요** | 인증된 사용자 (Low Privilege) | 인증된 사용자 (Low Privilege) | 인증 불필요 |
| **영향 범위** | 자체 호스팅 인스턴스 | 자체 호스팅 인스턴스 | 자체 호스팅 인스턴스 |
| **패치 버전** | 1.123.17, 2.4.5, 2.5.1 | 1.123.17, 2.4.5, 2.5.1 | 1.123.17, 2.4.5, 2.5.1 |

### 기술적 심층 분석

#### CVE-2026-1470: JavaScript AST Sandbox Escape (CVSS 9.9)

n8n의 Code Node는 사용자 정의 JavaScript 코드를 실행할 수 있지만, vm2 기반 sandbox 내에서 격리되어야 합니다. 이 취약점은 **JavaScript `with` 문**을 악용하여 sandbox를 탈출합니다.

**공격 원리:**

![n8n JavaScript Sandbox Escape Attack Flow](/assets/images/2026-01-29-n8n-sandbox-escape-attack-flow.svg)



#### Splunk SIEM 탐지 룰



#### 긴급 패치 적용

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```bash
> #!/bin/bash...
> ```



### 참고 링크

- [JFrog 보안 리서치: n8n RCE 분석](https://jfrog.com/blog/n8n-rce-cve-2026-1470/)
- [n8n 보안 권고](https://github.com/n8n-io/n8n)
- [NIST NVD: CVE-2026-1470](https://nvd.nist.gov/vuln/detail/CVE-2026-1470)

---

## 2. D-Link 단종 장비 Zero-Day (CVE-2026-0625)

### 취약점 개요

D-Link의 **단종된(End-of-Life)** DSL 모뎀/라우터에서 **패치 불가능한** Zero-Day 취약점이 실제 악용 중입니다. Shadowserver Foundation이 2025년 11월 27일 최초 악용을 탐지했습니다.

| 항목 | 내용 |
|------|------|
| **CVE** | CVE-2026-0625 |
| **CVSS** | 9.3 (Critical) |
| **유형** | OS Command Injection |
| **공격 벡터** | `dnscfg.cgi` DNS 파라미터 미검증 |
| **영향 장비** | DSL-2740R, DSL-2640B, DSL-2780B, DSL-526B |
| **단종 시기** | 2020년 |
| **패치 가능 여부** | 불가 (단종) |
| **악용 상태** | Active Exploitation (Shadowserver 탐지) |

### 기술적 분석

#### 공격 체인

![D-Link Command Injection Attack Chain](/assets/images/2026-01-29-dlink-command-injection-attack-chain.svg)



#### Snort/Suricata IDS 룰

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # D-Link dnscfg.cgi 커맨드 인젝션 탐지 룰...
> ```



### 참고 링크

- [Shadowserver Foundation Advisory](https://www.shadowserver.org/news/cve-2026-0625-d-link-dsl-command-injection/)
- [D-Link 단종 제품 공지](https://supportannouncement.us.dlink.com/security/publication.aspx?name=SAP10432)
- [NIST NVD: CVE-2026-0625](https://nvd.nist.gov/vuln/detail/CVE-2026-0625)

---

## 3. Kubernetes AI 에이전트 보안 과제 (2026 전망)

### 배경

Tigera CEO Ratan Tipirneni가 2026년 Kubernetes 보안 전망에서 **AI 에이전트의 K8s 클러스터 내 직접 운영**에 따른 보안 과제를 경고했습니다. AI 에이전트의 **비결정적(non-deterministic) 행동**은 기존 정적 보안 모델로는 대응이 불가능합니다.

| 지표 | 수치 | 출처 |
|------|------|------|
| 보안 인시던트 경험 조직 | 90% | 2025 K8s Security Report |
| 취약점 증가율 (YoY) | 440% | Red Hat |
| eBPF 도구 도입 계획 | 67% | CNCF Survey 2025 |
| StackRox 오픈소스 부활 | 2026년 1월 | Red Hat |

### AI 에이전트가 K8s에 미치는 보안 영향

![Kubernetes Traditional Container vs AI Agent Workloads](/assets/images/2026-01-29-k8s-ai-agent-vs-traditional.svg)



#### Tetragon 런타임 모니터링 (AI 에이전트 행동 감시)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # tetragon-ai-agent-tracing.yaml...
> ```



### RBAC 최소 권한 설계 (AI 에이전트용)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # ai-agent-rbac.yaml...
> ```



### 데이터 주권 비교

| 기준 | AWS/GCP/Azure | Infomaniak Swiss Cloud |
|------|---------------|------------------------|
| 데이터 위치 | 글로벌 (리전 선택) | 스위스 내 고정 |
| 법적 관할 | US CLOUD Act 적용 | 스위스 FADP만 적용 |
| GDPR 준수 | 부분적 (DPA 필요) | 완전 준수 |
| 에너지 | 일부 리전 재생 에너지 | 100% 재생 에너지 |
| AI API | 자체 API | OpenAI 호환 (데이터 미전송) |
| 비용 | 유연한 가격 | 프리미엄 (주권 비용) |

### DevSecOps 활용 시나리오

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 데이터 주권 요구사항 평가 체크리스트...
> ```



#### AWS NHI 보안 정책

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # nhi-security-policies.yaml...
> ```



### 참고 링크

- [Tenable: 2026 Cloud Security Predictions](https://www.tenable.com/blog/2026-cloud-security-predictions-nhi)
- [OWASP Non-Human Identity Top 10](https://owasp.org/www-project-non-human-identity-top-10/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

## 6. DevSecOps 실무 체크리스트

### P0 - 긴급 (0-24시간)

- [ ] **n8n 패치 적용**: 자체 호스팅 인스턴스 버전 확인, 1.123.17+ / 2.4.5+ / 2.5.1+ 업데이트
- [ ] **n8n 임시 완화**: 즉시 패치 불가 시 Code Node 비활성화, 네트워크 접근 제한
- [ ] **D-Link 장비 격리**: DSL-2740R/2640B/2780B/526B 외부 접근 즉시 차단
- [ ] **IDS/IPS 룰 적용**: dnscfg.cgi 커맨드 인젝션 탐지 룰 배포

### P1 - 높음 (1-7일)

- [ ] **단종 장비 인벤토리**: 네트워크 내 모든 EOL 장비 목록화 및 교체 계획 수립
- [ ] **NHI 감사**: 서비스 계정, API 키, 토큰 인벤토리 점검 및 과도 권한 식별
- [ ] **K8s AI 에이전트 보안**: eBPF 기반 보안 도구(Cilium, Tetragon) 도입 검토
- [ ] **RBAC 검토**: AI 에이전트 Pod에 최소 권한 원칙 적용

### P2 - 보통 (1-4주)

- [ ] **NHI 거버넌스**: 비인간 ID 라이프사이클 관리 프레임워크 수립
- [ ] **자동 키 교체**: 서비스 계정 키 90일 자동 교체 정책 구현
- [ ] **데이터 주권 평가**: Sovereign Cloud 도입 필요성 평가 (유럽 사업 시)
- [ ] **eBPF 모니터링**: Kubernetes 런타임 보안 모니터링 파이프라인 구축
- [ ] **API 거버넌스**: AI 에이전트 API 호출 인벤토리 및 Rate Limiting 적용

---

## 7. 참고 자료

| 분류 | 자료 | URL |
|------|------|-----|
| **n8n 취약점** | JFrog Security Research | [jfrog.com/blog](https://jfrog.com/blog/n8n-rce-cve-2026-1470/) |
| **n8n 보안 권고** | n8n GitHub Security | [https://github.com/n8n-io/n8n) |
| **D-Link CVE** | NIST NVD | [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2026-0625) |
| **D-Link 공지** | D-Link Support | [supportannouncement.us.dlink.com](https://supportannouncement.us.dlink.com/security/publication.aspx?name=SAP10432) |
| **Shadowserver** | D-Link 악용 탐지 | [shadowserver.org](https://www.shadowserver.org/) |
| **K8s 보안 전망** | Tigera Blog | [tigera.io/blog](https://www.tigera.io/blog/) |
| **eBPF 생태계** | CNCF eBPF Landscape | [ebpf.io](https://ebpf.io/applications/) |
| **StackRox** | Red Hat Blog | [redhat.com/blog](https://www.redhat.com/en/blog/stackrox-open-source-2026) |
| **Swiss Cloud** | Infomaniak | [infomaniak.com](https://www.infomaniak.com/en/hosting/public-cloud) |
| **NHI 보안** | Tenable Blog | [tenable.com/blog](https://www.tenable.com/blog/2026-cloud-security-predictions-nhi) |
| **NHI Top 10** | OWASP | [owasp.org](https://owasp.org/www-project-non-human-identity-top-10/) |
| **AWS IAM** | AWS Documentation | [docs.aws.amazon.com](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) |
| **Cilium** | Cilium Docs | [docs.cilium.io](https://docs.cilium.io/) |
| **Tetragon** | Tetragon Docs | [tetragon.io](https://tetragon.io/docs/) |

---

## 마무리

이번 주 보안 뉴스에서 가장 주목할 점은 **자동화 도구와 레거시 장비의 보안 위협**입니다.

### 핵심 요약

| 순위 | 위협 | 심각도 | 즉시 조치 |
|------|------|--------|-----------|
| 1 | **n8n RCE** (CVE-2026-1470) | CVSS 9.9 | 자체 호스팅 인스턴스 즉시 패치 |
| 2 | **D-Link Zero-Day** (CVE-2026-0625) | CVSS 9.3 | 단종 장비 즉시 교체 또는 격리 |
| 3 | **K8s AI 에이전트 보안** | - | eBPF 도구 도입 및 RBAC 강화 |
| 4 | **NHI 클라우드 침해** | - | 서비스 계정/API 키 인벤토리 점검 |

**n8n CVSS 9.9 RCE**는 워크플로우 자동화 도구가 공격 표면이 될 수 있음을 보여줍니다. JavaScript/Python sandbox escape가 모두 가능하므로, 자체 호스팅 인스턴스를 운영하는 조직은 **즉시 패치를 적용**하거나 Code Node를 비활성화해야 합니다. **D-Link Zero-Day**는 단종 장비의 위험성을 다시 한번 상기시킵니다. 2020년에 EOL된 장비가 여전히 인터넷에 노출되어 있으며, 패치가 불가능하므로 **교체만이 유일한 해결책**입니다.

**Kubernetes 환경에서 AI 에이전트 보안**은 2026년 가장 중요한 과제 중 하나입니다. AI 에이전트의 비결정적 행동은 기존 정적 보안 모델로 대응할 수 없으므로, **eBPF 기반 도구(Cilium, Tetragon, Falco)**를 통한 런타임 관찰이 필수적입니다. **비인간 ID(NHI)**가 클라우드 침해의 주요 벡터로 부상함에 따라, 서비스 계정과 API 키에 대한 **체계적 거버넌스와 자동 교체 정책**이 필요합니다.

### 관련 포스팅

- [CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계](/posts/2026/01/28/Claude_MD_Security_Guide/) - AI 에이전트 보안 가이드라인
- [2026-01-28 Microsoft Office Zero-Day 분석](/posts/2026/01/28/Tech_Security_Weekly_Digest_MS_Office_Zero_Day_CTEM_Grist_Core_RCE/) - CVE-2026-21509 심층 분석
- [OWASP 2025 최신 업데이트 완벽 가이드](/posts/2026/01/03/OWASP_2025_Latest_Update_Complete_Guide_Top_10_Agentic_AI_Security/) - 에이전틱 AI 보안 위협

### 다음 주 주목 포인트

1. **n8n 후속 패치**: 추가 sandbox escape 벡터 발견 가능성, 60K+ 인스턴스 패치 현황
2. **D-Link ISP 대응**: 단종 장비 교체 프로그램 진행 상황
3. **KubeCon 보안 트랙**: eBPF 기반 보안 도구 신규 발표 예상
4. **NHI 표준화**: OWASP Non-Human Identity Top 10 업데이트

---

**질문이나 피드백**은 댓글이나 [GitHub Issues](https://github.com/Twodragon0/tech-blog)로 남겨주세요.

---

*이 포스팅은 47개 RSS 피드에서 수집된 218개 뉴스를 분석하여 작성되었습니다.*
*수집 기간: 2026년 1월 28일 ~ 29일 (48시간)*

<!-- quality-upgrade:v1 -->
## 경영진 요약
이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.

### 위험 스코어카드
| 영역 | 현재 위험도 | 영향도 | 우선순위 |
|---|---|---|---|
| 공급망/의존성 | 중간 | 높음 | P1 |
| 구성 오류/권한 | 중간 | 높음 | P1 |
| 탐지/가시성 공백 | 낮음 | 중간 | P2 |

### 운영 개선 지표
| 지표 | 현재 기준 | 목표 | 검증 방법 |
|---|---|---|---|
| 탐지 리드타임 | 주 단위 | 일 단위 | SIEM 알림 추적 |
| 패치 적용 주기 | 월 단위 | 주 단위 | 변경 티켓 감사 |
| 재발 방지율 | 부분 대응 | 표준화 | 회고 액션 추적 |

### 실행 체크리스트
- [ ] 핵심 경고 룰을 P1/P2로 구분하고 온콜 라우팅을 검증한다.
- [ ] 취약점 조치 SLA를 서비스 등급별로 재정의한다.
- [ ] IAM/시크릿/네트워크 변경 이력을 주간 기준으로 리뷰한다.
- [ ] 탐지 공백 시나리오(로그 누락, 파이프라인 실패)를 월 1회 리허설한다.
- [ ] 경영진 보고용 핵심 지표(위험도, 비용, MTTR)를 월간 대시보드로 고정한다.

### 시각 자료
![포스트 시각 자료](/assets/images/2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent.svg)

