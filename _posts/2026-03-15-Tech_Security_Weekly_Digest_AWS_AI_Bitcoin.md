---

layout: post
title: "기술·보안 주간 다이제스트: GlassWorm 공급망 공격, AI 에이전트 보안, AWS IAM 멀티리전"
date: 2026-03-15 10:24:40 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AWS, SupplyChain, AI-Security, Bitcoin, APT]
excerpt: "[Critical] GlassWorm 공급망 공격·중국 APT 위협 긴급 점검 필요. 2026년 03월 15일 주요 보안/기술 뉴스 10건 - VS Code 확장 공급망 공격, AI 에이전트 프롬프트 인젝션, AWS IAM 멀티리전, 비트코인 기관 매집"
description: "[Critical] GlassWorm·중국 APT 대응 - VS Code Open VSX 확장 감사, AI 에이전트 입출력 검증, AWS IAM Identity Center 멀티리전 접근 정책 재검토 필요. 2026년 03월 15일 보안 뉴스 10건. 공급망 보안, AI 에이전트 취약점, 클라우드 접근 관리를 운영 리스크 기준으로 정리한 DevSecOps 실무 가이드."
author: Twodragon
comments: true
image: /assets/images/2026-03-15-Tech_Security_Weekly_Digest_AWS_AI_Bitcoin.svg
image_alt: "Tech Security Weekly Digest March 15 2026 GlassWorm Supply Chain AWS IAM AI Agent Bitcoin"
toc: true
---
{% include ai-summary-card.html
  title='기술·보안 주간 다이제스트: GlassWorm 공급망 공격, AI 에이전트 보안, AWS IAM 멀티리전'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">2026</span> <span class="tag">SupplyChain</span> <span class="tag">AI-Security</span> <span class="tag">Bitcoin</span> <span class="tag">APT</span>'
  highlights_html='<li><strong>Critical</strong>: GlassWorm이 Open VSX 레지스트리의 72개 확장을 악용한 공급망 공격 - 개발 도구 체인 전체가 공격 표면이 됨</li> <li><strong>High</strong>: AI 에이전트 취약점으로 인한 프롬프트 인젝션·데이터 탈취 가능 - 내부 배포 LLM 에이전트 입출력 검증 즉시 점검 필요</li> <li><strong>Medium</strong>: AWS IAM Identity Center 멀티리전 확장 - 중앙 집중식 접근 관리 아키텍처 채택 검토 시점</li>'
  period='2026-03-15 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 03월 15일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 10개
- **보안 뉴스**: 4개
- **블록체인 뉴스**: 3개
- **기술 뉴스**: 3개

**이번 주기 특징:**

3월 15일 다이제스트의 핵심은 **개발 도구 공급망을 겨냥한 정교한 공격**입니다. GlassWorm 그룹이 Open VSX 레지스트리에서 72개 확장을 악용한 공급망 공격을 감행했고, 같은 날 AI 에이전트 설계 결함으로 인한 프롬프트 인젝션·데이터 탈취 취약점이 공개됐습니다. 중국 연계 APT 그룹은 동남아 군사 조직을 AppleChris·MemFun 맬웨어로 타격하고 있습니다.

이 세 가지 위협의 공통 분모는 **신뢰된 채널의 무기화**입니다. 확장 마켓플레이스, AI 에이전트 명령 채널, 외교·국방 네트워크 — 모두 조직이 검증 없이 신뢰하는 경로입니다. 이번 주기는 보안팀이 "어떤 채널을 기본 신뢰하고 있는가"를 다시 물어야 할 때입니다.

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔴 **Security** | The Hacker News | GlassWorm, Open VSX 72개 확장 공급망 공격 | 🔴 Critical |
| 🔴 **Security** | The Hacker News | 중국 APT, 동남아 군 조직에 AppleChris·MemFun 맬웨어 | 🟠 High |
| 🟠 **Security** | The Hacker News | AI 에이전트 취약점 - 프롬프트 인젝션·데이터 탈취 | 🟠 High |
| 🟡 **Cloud** | AWS Security Blog | IAM Identity Center 멀티리전 배포 가이드 | 🟡 Medium |
| 🟡 **Blockchain** | Cointelegraph | Basel III 규칙 변경, BTC 시장 유동성 영향 | 🟡 Medium |
| 🟡 **Blockchain** | Cointelegraph | Boris Johnson BTC 폰지 사기 연루 의혹 | 🟡 Medium |
| 🟡 **Blockchain** | Cointelegraph | Bitcoin, 주식 수익률 상회 - Strategy $776M BTC 매수 계획 | 🟡 Medium |
| 💻 **Tech** | GeekNews | Agentic Workflow 실무 - Lablup 130억 토큰 개발 경험 | 🟡 Medium |
| 💻 **Tech** | GeekNews | MacBook Neo에서 Parallels 윈도우 VM 작동 확인 | 🟡 Low |
| 💻 **Tech** | GeekNews | Hammerspoon - macOS Lua 자동화 도구 | 🟡 Low |

---

## 경영진 브리핑

- GlassWorm 공급망 공격은 개발자 워크스테이션과 CI/CD 파이프라인을 동시에 위협합니다. Open VSX 기반 확장을 사용하는 모든 개발 조직이 즉각적인 확장 목록 감사를 수행해야 합니다.
- AI 에이전트를 내부 업무에 배포한 조직은 에이전트의 입력 검증과 출력 필터링 레이어가 없을 경우, 인증된 사용자가 에이전트를 통해 권한 범위 밖의 데이터를 탈취할 수 있는 경로가 존재합니다.
- 중국 APT의 동남아 군사 조직 타격은 공급망·파트너 신뢰 경로를 통한 측면 이동 리스크를 높입니다. 방산·외교 파트너와 연결된 네트워크 세그멘테이션을 재점검하세요.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 개발 도구 공급망 | Critical | VS Code / Open VSX 확장 감사 + CI/CD 파이프라인 격리 |
| AI 에이전트 보안 | High | 에이전트 입출력 검증 레이어 점검, 시스템 프롬프트 노출 여부 확인 |
| APT / 스피어피싱 | High | 외부 파트너 연계 시스템 접근 로그 검토, EDR 탐지 룰 업데이트 |
| 클라우드 접근 관리 | Medium | AWS IAM Identity Center 멀티리전 아키텍처 검토 |

---

## 1. 보안 뉴스

### 1.1 GlassWorm 공급망 공격 - Open VSX 72개 확장 악용

> **[Critical]** 개발자 도구 공급망 직접 타격 - 즉시 확장 목록 감사 필요

{% include news-card.html
  title="GlassWorm Supply-Chain Attack Abuses 72 Open VSX Extensions to Target Developers"
  url="https://thehackernews.com/2026/03/glassworm-supply-chain-attack-abuses-72.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg4d-2XpiCS0UYnMWh32sQEJP9LnlN_m7m2hok9CnY_vu05XXwWn4INodYCvrEdweEzpho7XqcuOFvEPnnEWlHCRa_q3HY3V5O_ii35MVWAimRwsgrpNQrvGqeUchhZ48FRUl91zTpYQdLMRxVvRjV_T8GEm-J9mnMesefzlgeaoE_EU7Ba32liTr63SsQq/s1600/open.jpg"
  summary="GlassWorm 그룹이 Open VSX 레지스트리의 정상 확장 72개를 클론 후 악성 코드를 삽입해 배포하는 공급망 공격을 수행했습니다. 피해 확장들은 설치 즉시 개발자 워크스테이션에서 자격증명 탈취·백도어 설치를 시도합니다."
  source="The Hacker News"
  severity="Critical"
%}

#### 개요

GlassWorm은 VSCodium, Eclipse Che 등 오픈소스 IDE가 의존하는 Open VSX 레지스트리를 표적으로 삼았습니다. 공격 방식은 인기 있는 정상 확장을 복제한 뒤 이름을 유사하게 변조(typosquatting)하거나, 기존 확장 유지관리자 계정을 탈취해 악성 업데이트를 배포하는 두 가지입니다.

감염된 확장은 설치 후 다음 행위를 수행합니다.

1. `~/.ssh`, `~/.aws/credentials`, `.env` 파일 내 자격증명 수집
2. 환경변수에서 API 키·토큰 추출
3. 수집한 데이터를 C2 서버로 전송
4. 추가 페이로드 다운로드 및 실행 권한 획득

VS Code Marketplace(Microsoft 공식)는 별도 서명 검증 절차가 있으나, Open VSX는 커뮤니티 운영 레지스트리로 동일 수준의 검증이 적용되지 않습니다. VSCodium 사용자, JetBrains IDE의 Open VSX 연동, GitLab/GitHub Codespaces 원격 개발 환경이 직접 영향권입니다.

**실무 포인트**: 조직에서 사용 중인 모든 VS Code 및 호환 IDE 확장 목록을 즉시 인벤토리화하고, Open VSX 출처 확장은 퍼블리셔 ID·버전·설치 해시를 공식 체크섬과 대조하세요. CI/CD 파이프라인에서 IDE 확장을 자동 설치하는 스텝이 있다면 허용 목록(allowlist) 기반으로 전환하세요.

> **출처**: [The Hacker News](https://thehackernews.com/2026/03/glassworm-supply-chain-attack-abuses-72.html)

#### 위협 분석

| 항목 | 내용 |
|------|------|
| **위협 행위자** | GlassWorm (신규 그룹, 경제적 동기 추정) |
| **공격 벡터** | 오픈소스 확장 레지스트리 공급망 |
| **주요 타깃** | VSCodium 사용자, 오픈소스 IDE 기반 개발 환경 |
| **심각도** | Critical |
| **대응 우선순위** | P0 - 즉시 대응 |

#### MITRE ATT&CK 매핑

| 전술 | 기법 ID | 설명 |
|------|---------|------|
| Initial Access | T1195.002 | Supply Chain Compromise: Software Supply Chain |
| Credential Access | T1552.001 | Unsecured Credentials: Credentials In Files |
| Exfiltration | T1041 | Exfiltration Over C2 Channel |
| Persistence | T1546 | Event Triggered Execution (IDE 플러그인 로딩) |

#### 탐지 쿼리 (Splunk)

```splunk
index=endpoint sourcetype=sysmon EventCode=11
(TargetFilename="*/.vscode/extensions/*" OR TargetFilename="*/.vscode-server/extensions/*")
NOT (Image="code.exe" OR Image="codium" OR Image="node")
| stats count by TargetFilename, Image, ComputerName
| where count > 1
```

#### 권장 조치

- [ ] 조직 내 Open VSX 기반 확장 전체 인벤토리 작성 (개발자 워크스테이션 + 원격 개발 환경 포함)
- [ ] 영향받는 72개 확장 목록 확인 후 즉시 비활성화 또는 제거
- [ ] `~/.ssh`, `~/.aws/credentials`, `.env` 파일 접근 로그 검토
- [ ] CI/CD 파이프라인의 확장 자동 설치 스텝을 허용 목록 기반으로 전환
- [ ] 개발자 자격증명 로테이션 (AWS 키, SSH 키, GitHub PAT) 즉시 실행

---

### 1.2 AI 에이전트 설계 결함 - 프롬프트 인젝션·데이터 탈취

> **[High]** LLM 에이전트 배포 조직 즉시 점검 필요

{% include news-card.html
  title="AI Agent Flaws Could Enable Prompt Injection and Data Exfiltration"
  url="https://thehackernews.com"
  summary="OpenClaw 등 여러 LLM 에이전트 프레임워크에서 입력 검증 미흡으로 인한 프롬프트 인젝션 취약점이 발견됐습니다. 공격자가 사용자 입력에 악의적 지시를 삽입하면 에이전트가 접근 가능한 내부 데이터를 외부로 탈취하거나 시스템 프롬프트를 유출할 수 있습니다."
  source="The Hacker News"
  severity="High"
%}

#### 개요

이번에 공개된 취약점은 특정 제품의 버그가 아니라 **AI 에이전트 설계 패턴 자체의 구조적 문제**입니다. 대부분의 LLM 에이전트는 사용자 입력, 도구 호출 결과, 웹 검색 결과를 구분 없이 하나의 컨텍스트로 처리합니다. 공격자는 이 경계를 악용해 "이전 지시를 무시하고 다음을 수행하라"는 형태의 인젝션을 외부 데이터(이메일 본문, 웹페이지, 문서)에 심어 둘 수 있습니다.

실제 공격 시나리오는 다음과 같습니다.

- 악성 이메일을 에이전트가 요약 처리할 때, 본문 내 숨겨진 지시로 첨부 파일을 외부 URL로 전송
- 내부 지식베이스 RAG 파이프라인에서 오염된 문서가 에이전트 행동을 유도
- 도구 결과값에 포함된 악성 텍스트가 다음 에이전트 턴에서 권한 이탈 명령으로 실행

**실무 포인트**: 에이전트가 접근하는 데이터 소스(이메일, 문서, 웹)와 실행 가능한 도구(파일 쓰기, API 호출, 이메일 발송)를 분리하고, 도구 실행 전 사람의 승인(human-in-the-loop)을 필수로 설정하세요. 프로덕션 에이전트에서 시스템 프롬프트를 노출하는 API 엔드포인트가 없는지 즉시 점검하세요.

> **출처**: [The Hacker News](https://thehackernews.com)

#### MITRE ATT&CK 매핑

| 전술 | 기법 ID | 설명 |
|------|---------|------|
| Initial Access | T1566.002 | Phishing: Spearphishing Link (악성 입력 주입) |
| Exfiltration | T1048 | Exfiltration Over Alternative Protocol |
| Defense Evasion | T1027 | Obfuscated Files or Information (프롬프트 난독화) |

#### 프롬프트 인젝션 방어 코드 예시

```python
import re
from typing import Optional

# 고위험 인젝션 패턴 목록
INJECTION_PATTERNS = [
    r'ignore (all )?(previous|above|prior) instructions?',
    r'system prompt',
    r'act as (a |an )?(?!assistant)',
    r'forget (everything|all)',
    r'you are now',
    r'new instructions?:',
    r'<\|im_start\|>system',  # ChatML 인젝션
    r'###\s*(instruction|system)',
]

def validate_agent_input(text: str, max_length: int = 4096) -> Optional[str]:
    """
    에이전트 입력 검증 - 길이 초과 및 인젝션 패턴 차단
    반환값: 정상이면 sanitized text, 비정상이면 None
    """
    if len(text) > max_length:
        return None  # 또는 truncate 처리

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            # 로깅 후 차단
            print(f"[SECURITY] Injection pattern detected: {pattern}")
            return None

    # HTML/XML 태그 제거 (시스템 프롬프트 태그 인젝션 방지)
    sanitized = re.sub(r'<[^>]+>', '', text)
    return sanitized.strip()
```

#### 권장 조치

- [ ] 프로덕션 LLM 에이전트의 시스템 프롬프트 노출 여부 즉시 점검
- [ ] 에이전트가 외부 데이터(이메일, 웹, 문서)를 처리하는 경우 출처 태그 분리 구현
- [ ] 파일 쓰기·외부 API 호출 도구에 human-in-the-loop 승인 레이어 추가
- [ ] 에이전트 실행 로그에 입력·출력·도구 호출 전체 기록 및 SIEM 연동
- [ ] OWASP LLM Top 10 기준 내부 배포 에이전트 취약점 점검 수행

---

### 1.3 중국 APT, 동남아 군사 조직에 AppleChris·MemFun 맬웨어

> **[High]** 방산·정부 파트너 연계 조직 측면 이동 리스크 주의

{% include news-card.html
  title="Chinese Hackers Target Southeast Asian Militaries with AppleChris and MemFun Malware"
  url="https://thehackernews.com"
  summary="중국 연계 APT 그룹이 동남아시아 군사 조직을 표적으로 AppleChris RAT과 MemFun 인메모리 로더를 배포하는 캠페인이 확인됐습니다. 스피어피싱 이메일을 초기 침투 벡터로 사용하며, 시스템 메모리에만 상주하는 필리스(fileless) 기법으로 탐지를 우회합니다."
  source="The Hacker News"
  severity="High"
%}

#### 개요

이번 캠페인은 동남아시아 국방·외교 조직을 대상으로 하며, 두 가지 커스텀 맬웨어를 사용합니다.

**AppleChris RAT**: 원격 접근 트로이목마(Remote Access Trojan)로, 키로깅·스크린샷·파일 수집·원격 셸 기능을 제공합니다. 통신 채널은 HTTPS를 사용해 정상 트래픽과 혼합되며, C2 인프라로 클라우드 스토리지 서비스를 활용합니다.

**MemFun**: 디스크에 파일을 남기지 않는 인메모리 로더입니다. 합법적인 프로세스(svchost.exe, explorer.exe)에 코드를 인젝션해 동작하며, 재부팅 후에는 별도의 지속성 메커니즘(레지스트리 런키, 예약 작업)을 통해 재활성화합니다.

이 캠페인이 한국·일본 등 역내 방위 산업 조직에 직접 영향을 미칠 가능성은 낮으나, **공급망·파트너 신뢰 경로를 통한 간접 침투** 가능성은 있습니다. 동남아 파트너사의 시스템이 감염된 상태에서 공유 문서, VPN, 이메일 채널을 통해 국내 조직으로 피벗하는 시나리오를 배제할 수 없습니다.

**실무 포인트**: 방산·정부 기관과 파트너십이 있는 조직은 해당 파트너와의 연결 채널(VPN, 공유 파일 서버, 이메일 도메인)에 대한 이상 행위 탐지 규칙을 강화하세요. 내부 네트워크에서 클라우드 스토리지 서비스(OneDrive, Dropbox, Google Drive)로의 대용량 아웃바운드 트래픽을 모니터링하세요.

> **출처**: [The Hacker News](https://thehackernews.com)

#### MITRE ATT&CK 매핑

| 전술 | 기법 ID | 설명 |
|------|---------|------|
| Initial Access | T1566.001 | Phishing: Spearphishing Attachment |
| Execution | T1059.003 | Command and Scripting Interpreter: Windows Command Shell |
| Defense Evasion | T1055 | Process Injection (MemFun 인메모리 로더) |
| Persistence | T1053.005 | Scheduled Task/Job |
| Command and Control | T1071.001 | Application Layer Protocol: Web Protocols (HTTPS C2) |
| Exfiltration | T1567.002 | Exfiltration Over Web Service: Cloud Storage |

---

### 1.4 AWS IAM Identity Center 멀티리전 배포 - 중앙 집중식 접근 관리

> **[Medium]** 멀티리전 AWS 환경 운영 조직에게 아키텍처 개선 기회

{% include news-card.html
  title="Deploy AWS applications and access AWS accounts across multiple Regions with IAM Identity Center"
  url="https://aws.amazon.com/blogs/security/deploy-aws-applications-and-access-aws-accounts-across-multiple-regions-with-iam-identity-center/"
  summary="AWS가 IAM Identity Center를 통해 여러 리전에서 AWS 계정 및 애플리케이션 접근을 중앙에서 관리하는 멀티리전 배포 패턴을 공식 가이드로 발표했습니다. 단일 IdP(Identity Provider) 연동으로 모든 리전의 접근 권한을 일관되게 관리할 수 있습니다."
  source="AWS Security Blog"
  severity="Medium"
%}

#### 개요

AWS IAM Identity Center(구 AWS SSO)의 멀티리전 지원이 확장됐습니다. 기존에는 특정 리전을 홈 리전으로 설정하고, 그 리전에서만 Identity Center 콘솔을 관리했습니다. 이번 업데이트로 여러 리전의 AWS 계정에 대한 권한을 하나의 IdP 연동(Microsoft Entra ID, Okta 등)으로 일관되게 적용할 수 있습니다.

실무적으로 중요한 변화는 **Permission Set의 멀티리전 배포**입니다. 이제 ap-northeast-2(서울) 리전의 프로덕션 계정과 us-east-1의 DR 계정에 동일한 접근 정책을 동기화 배포할 수 있습니다. 이전에는 이를 Terraform 또는 AWS Organizations SCP로 별도 관리해야 했습니다.

보안 관점에서의 핵심 이점은 세 가지입니다.

1. **접근 권한 드리프트 방지**: 리전별로 다른 권한이 설정되는 구성 드리프트를 Permission Set 중앙 관리로 제거
2. **감사 로그 단일화**: CloudTrail 멀티리전 로그를 IAM Identity Center 접근 이벤트와 연계해 단일 대시보드로 감사 가능
3. **비상 접근 계정 관리**: Break-glass 계정을 모든 리전에 일관되게 배포하되 정상 운영 중에는 비활성화하는 패턴 구현 용이

**실무 포인트**: 현재 리전별로 독립적인 IAM 사용자를 관리하고 있다면, IAM Identity Center로 마이그레이션해 중앙 IdP 인증과 최소 권한 Permission Set을 적용하세요. 특히 AWS Organizations 환경에서 멤버 계정이 10개 이상이라면 이 아키텍처 전환의 운영 부담 절감 효과가 큽니다.

> **출처**: [AWS Security Blog](https://aws.amazon.com/blogs/security/deploy-aws-applications-and-access-aws-accounts-across-multiple-regions-with-iam-identity-center/)

#### IAM Identity Center 멀티리전 핵심 설정 예시

```terraform
# IAM Identity Center Permission Set - 멀티리전 배포
resource "aws_ssoadmin_permission_set" "developer_read_only" {
  name             = "DeveloperReadOnly"
  instance_arn     = tolist(data.aws_ssoadmin_instances.main.arns)[0]
  session_duration = "PT8H"  # 8시간 세션 (최소 권한)

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_ssoadmin_managed_policy_attachment" "read_only" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.main.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.developer_read_only.arn
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# 멀티리전 계정에 Permission Set 배포
resource "aws_ssoadmin_account_assignment" "prod_ap_northeast" {
  instance_arn       = tolist(data.aws_ssoadmin_instances.main.arns)[0]
  permission_set_arn = aws_ssoadmin_permission_set.developer_read_only.arn
  principal_id       = aws_identitystore_group.developers.group_id
  principal_type     = "GROUP"
  target_id          = var.prod_account_id
  target_type        = "AWS_ACCOUNT"
}
```

---

### 보안 종합 분석

이번 주기 4건의 보안 뉴스를 교차 분석하면 하나의 구조적 패턴이 드러납니다. **신뢰된 채널의 무기화(Weaponization of Trusted Channels)**입니다.

| 위협 | 악용된 신뢰 채널 | 조직의 취약 지점 |
|------|----------------|----------------|
| GlassWorm 공급망 공격 | 오픈소스 확장 마켓플레이스 | 검증 없는 확장 설치 정책 |
| AI 에이전트 취약점 | LLM의 입력 신뢰 구조 | 에이전트 입출력 검증 미흡 |
| 중국 APT 캠페인 | 파트너·공급망 신뢰 경로 | 측면 이동 탐지 부재 |
| AWS IAM 멀티리전 | (방어 측) 중앙 접근 관리 | 리전별 권한 드리프트 |

**세 가지 공격 위협의 연결 고리**: GlassWorm이 개발자 자격증명을 탈취하면, 그 자격증명으로 CI/CD 파이프라인에 침투해 AI 에이전트 설정을 변조하거나, AWS 환경에 대한 지속적 접근권을 획득할 수 있습니다. 중국 APT가 파트너 네트워크를 통해 침투하면 동일한 경로로 내부 AI 에이전트나 개발 환경에 도달할 수 있습니다.

이 세 공격은 독립적이지 않습니다. **공격 체인의 다른 지점**입니다.

#### 운영팀을 위한 종합 시사점

**단기(0~7일)**:
- Open VSX 기반 확장 인벤토리 작성 및 감사 - 72개 악성 확장 목록과 대조
- AI 에이전트 프로덕션 배포 현황 점검 및 시스템 프롬프트 노출 취약점 확인
- 동남아 파트너와의 VPN·공유 파일 채널 이상 트래픽 검토

**중기(1~4주)**:
- IAM Identity Center 멀티리전 마이그레이션 검토 - 리전별 IAM 사용자 폐지 계획 수립
- 개발자 워크스테이션 보안 정책 강화 - 확장 허용 목록, 자격증명 저장소 분리
- AI 에이전트 보안 가이드라인 수립 (입력 검증, 도구 실행 승인, 감사 로그)

**장기(1~3개월)**:
- 공급망 보안 프로그램에 오픈소스 소프트웨어 레지스트리 모니터링 포함
- APT 위협 모델 업데이트 - 동남아·중국 연계 공격 그룹 TTP 내부 공유
- 제로 트러스트 아키텍처 로드맵에 AI 에이전트 신뢰 경계 설계 반영

---

## 2. 블록체인 뉴스

### 2.1 Basel III 규칙 변경이 BTC 시장 유동성에 미치는 영향

{% include news-card.html
  title="Changing Basel rules could unlock 'huge' liquidity for BTC"
  url="https://cointelegraph.com/news/changing-basel-rules-huge-liquidity-btc?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjYtMDEvMDE5YmU2M2MtNWYyMy03N2MyLWIwNTItODQ3ODEwY2E0MjIwLmpwZw==.jpg"
  summary="Basel III 은행 자본 규제(특히 CRE 606 조항)의 수정 논의가 진행 중이며, 규칙이 변경될 경우 기존 은행들이 비트코인을 담보 자산 또는 보유 자산으로 공식 취급할 수 있게 되어 제도권 유동성이 대규모로 유입될 수 있다는 분석입니다."
  source="Cointelegraph"
%}

#### 개요

현행 Basel III 체계에서 비트코인은 Group 2b 자산으로 분류돼 1,250%의 위험 가중치가 적용됩니다. 이는 은행이 BTC 1달러를 보유하려면 자기자본 12.5달러를 적립해야 한다는 의미로, 사실상 은행의 BTC 직접 보유를 금지하는 수준입니다.

논의 중인 규칙 변경은 비트코인을 별도 자산군으로 분류하고 위험 가중치를 실질적으로 낮추는 방향입니다. 이 변경이 실현되면 미국·유럽 대형 은행들이 custody 서비스, ETF 발행, 직접 보유를 통해 BTC 시장에 진입할 수 있는 제도적 기반이 마련됩니다.

**실무 포인트**: 기업 재무팀이 BTC를 대차대조표 자산으로 검토 중이라면, Basel III 변경 타임라인을 주시하면서 은행 파트너십 협상 시 custody 조건을 먼저 확인하세요. 규칙 변경 전 은행들은 여전히 BTC 관련 서비스에 제한이 있습니다.

> **출처**: [Cointelegraph](https://cointelegraph.com/news/changing-basel-rules-huge-liquidity-btc?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound)

---

### 2.2 Boris Johnson, BTC 폰지 사기 연루 의혹

{% include news-card.html
  title="Boris Johnson linked to BTC Ponzi scheme allegations"
  url="https://cointelegraph.com/news/boris-johnson-btc-ponzi-scheme?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjYtMDMvMDE5Y2VkNzAtNzk3ZC03ZWE5LTk5MTItMjAwOGM4YjY1ZTczLmpwZw==.jpg"
  summary="전 영국 총리 보리스 존슨이 특정 BTC 투자 플랫폼 홍보에 관여했으며, 해당 플랫폼이 폰지 사기 의혹을 받고 있다는 보도가 나왔습니다. 유명 정치인을 활용한 암호화폐 사기의 패턴이 다시 주목받고 있습니다."
  source="Cointelegraph"
%}

#### 개요

이번 사례는 기술적 취약점이 아닌 **사회공학적 신뢰 조작**의 전형입니다. 전직 국가 지도자 수준의 유명인을 내세워 투자자들의 경계심을 낮추는 이 수법은 딥페이크 광고와 결합해 더 정교해지고 있습니다.

보안팀보다 직원 인식 제고가 더 중요한 영역입니다. 조직 구성원이 유명인 추천 암호화폐 투자 광고를 접했을 때 내부 재무팀에 문의하거나 사기 신고 채널을 사용하도록 교육하세요.

**실무 포인트**: 딥페이크 기반 유명인 암호화폐 사기 광고 탐지 방법을 사내 보안 인식 교육에 포함하세요. 특히 임직원이 개인 자금을 사용하더라도 조직 이메일이나 연락처로 접촉이 이뤄지면 사회공학 공격의 내부 침투 경로가 될 수 있습니다.

> **출처**: [Cointelegraph](https://cointelegraph.com/news/boris-johnson-btc-ponzi-scheme?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound)

---

### 2.3 Bitcoin, 주식 수익률 상회 - Strategy $776M BTC 매수 계획

{% include news-card.html
  title="Bitcoin beats stocks as Strategy eyes $776M BTC buying potential"
  url="https://cointelegraph.com/news/bitcoin-beats-stocks-strategy-strc-776m-btc-buying-potential?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjYtMDIvMDE5Yzk5ODMtZWRmNS03NjU2LTlmOWQtNjgwM2FlOWI4ZTg0LmpwZw==.jpg"
  summary="Strategy(구 MicroStrategy)가 STRC 채권 발행을 통해 최대 $776M 규모의 BTC 추가 매수를 계획하고 있으며, 연초 대비 BTC의 주식 지수 대비 수익률 우위가 기관 매집 논거를 강화하고 있습니다."
  source="Cointelegraph"
%}

#### 개요

Strategy의 Michael Saylor 모델(채권 발행 → BTC 매수)이 기관 투자자들의 레퍼런스 케이스로 자리 잡으면서, 유사 전략을 채택하는 상장사가 늘고 있습니다. 이번 $776M 매수 계획은 STRC라는 수익 공유형 채권 상품을 통해 조달하며, BTC 가격 상승 시 채권 이자를 BTC로 지급하는 구조입니다.

보안 관점에서 기관 BTC 보유 확대는 custody 솔루션 보안 수요 증가를 의미합니다. Fireblocks, BitGo 등 기관 custody 플랫폼의 보안 감사 요청이 늘고 있으며, 멀티시그(Multi-sig) 키 관리와 HSM(Hardware Security Module) 기반 서명 인프라에 대한 관심도 높아지고 있습니다.

**실무 포인트**: 조직이 BTC custody 서비스를 도입 중이거나 검토 중이라면, SOC 2 Type II 인증, 펜테스트 보고서 최신 여부, 멀티시그 설정(2-of-3 이상), 보험 coverage 한도를 custodian 평가 기준으로 사용하세요.

> **출처**: [Cointelegraph](https://cointelegraph.com/news/bitcoin-beats-stocks-strategy-strc-776m-btc-buying-potential?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound)

---

## 3. 기술 뉴스

{% capture spotlight_items %}
{% include news-spotlight-item.html
  title="진짜 내 일을 위한 Agentic Workflow"
  url="https://news.hada.io/topic?id=27513"
  source="GeekNews"
  tag="AI Engineering"
  summary="Lablup 신정규 대표가 Backend.AI:GO를 40일 동안 약 100만 줄의 코드, 130억 토큰을 소비해 개발한 경험을 공유했습니다. 에이전트 코딩 시대에는 토큰 사용량이 IT 기업의 엔지니어링 비용과 경쟁력에 직결된다는 관점이 핵심입니다."
  note="<strong>보안 관점</strong>: 130억 토큰 규모의 에이전트 코딩 워크플로우는 코드 생성 과정에서 시크릿이 포함된 프롬프트가 LLM 제공사로 전송될 위험이 있습니다. 에이전트 코딩 도입 시 코드베이스 내 시크릿 사전 제거(git-secrets, truffleHog)와 프롬프트 필터링 정책이 필요합니다."
%}
{% include news-spotlight-item.html
  title="MacBook Neo에서 Parallels 가상 머신으로 윈도우 실행 가능 확인"
  url="https://news.hada.io/topic?id=27512"
  source="GeekNews"
  tag="Hardware"
  summary="MacBook Neo에서 Parallels Desktop이 정상 작동함이 확인됐습니다. 기본 사용성 테스트를 통과했으나 8GB RAM 제한으로 Windows 11 VM 실행 시 성능 제약이 있습니다."
  note="<strong>운영 관점</strong>: MacBook Neo 환경에서 Windows VM을 사용하는 개발자가 생긴다면, VM 내 Windows 환경의 보안 패치 관리와 호스트-게스트 간 클립보드 공유 범위 정책을 사전에 수립하세요."
%}
{% include news-spotlight-item.html
  title="Hammerspoon - Lua로 구현된 강력한 macOS 데스크톱 자동화 도구"
  url="https://news.hada.io/topic?id=27511"
  source="GeekNews"
  tag="Developer Tools"
  summary="macOS 환경을 Lua 스크립트로 제어하는 오픈소스 자동화 도구입니다. 키보드 단축키, 윈도우 관리, 앱 실행, 시스템 이벤트 처리 등을 스크립트로 자동화할 수 있으며, 다양한 확장 모듈을 지원합니다."
  note="<strong>보안 관점</strong>: Hammerspoon은 macOS 접근성 API에 광범위한 권한을 요구합니다. 조직에서 사용을 허용할 경우 MDM 정책으로 허용 스크립트 범위를 제한하고, 자동화 스크립트가 자격증명이나 민감 데이터에 접근하지 않도록 코드 리뷰 절차를 두세요."
%}
{% endcapture %}
{% include news-spotlight-section.html
  aria_label="기술 뉴스"
  intro="이번 주 기술 뉴스는 에이전트 코딩의 실제 운영 경험, 새 하드웨어 호환성, macOS 자동화 도구를 다룹니다. 직접적인 보안 이벤트보다 <strong>향후 운영 환경 변화</strong>를 미리 파악하는 신호로 읽으세요."
  body=spotlight_items
%}

---

## 4. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **공급망 보안** | 1건 | GlassWorm, Open VSX, 개발 도구 타깃 |
| **AI 에이전트 보안** | 2건 | 프롬프트 인젝션, 데이터 탈취, Agentic Workflow |
| **APT / 국가 지원 위협** | 1건 | 중국 APT, 동남아 군사 조직, 필리스 맬웨어 |
| **클라우드 접근 관리** | 1건 | AWS IAM Identity Center, 멀티리전, 중앙 집중 |
| **비트코인 기관화** | 3건 | Basel III, Strategy 매집, 기관 custody |

이번 주기의 핵심은 **개발자 도구와 AI 에이전트가 새로운 공격 표면으로 부상**했다는 점입니다. 전통적인 취약점(CVE 기반 패치)보다 **신뢰 구조를 겨냥한 공격**이 늘어나는 추세가 3주째 이어지고 있습니다. 3월 10~15일 주간 흐름을 보면, 직접 침해(10일) → 신뢰 리스크(12일) → 공급망·에이전트 공격(15일) 순으로 위협의 추상화 수준이 높아지고 있습니다.

### 주간 비교: 3월 12~15일 트렌드 변화

| 날짜 | 주요 위협 유형 | 블록체인 이슈 | AI/ML 이슈 | 특이사항 |
|------|--------------|--------------|-----------|---------|
| 3월 12일 | 신뢰 리스크, 제품 전략 변화 | 주소 오염 방지, 예측시장 | Vertical AI 경쟁 구도 | 거버넌스·정책 이슈 |
| 3월 15일 | 공급망 공격, AI 에이전트 취약점 | Basel III 유동성, 기관 매집 | 에이전트 프롬프트 인젝션 | 개발 도구 직접 타격 |

**다음 주 예측 포인트**:
- GlassWorm 72개 악성 확장 전체 목록 공개 여부 - 추가 CVE 발급 가능성
- AI 에이전트 취약점 PoC 공개 여부 - 프롬프트 인젝션 실제 악용 사례 증가 가능성
- Basel III 변경안 공식 발표 타임라인 - 기관 BTC 진입 속도에 영향

---

## 5. 운영 우선순위 정리

| 우선순위 | 핵심 과제 | 기대 효과 |
|----------|-----------|-----------|
| P0 | Open VSX 확장 감사 + 개발자 자격증명 로테이션 | GlassWorm 공급망 피해 즉시 차단 |
| P0 | AI 에이전트 입출력 검증 레이어 + 시스템 프롬프트 노출 점검 | 에이전트 기반 데이터 탈취 경로 차단 |
| P1 | APT 탐지 규칙 업데이트 (MemFun 인메모리 + 클라우드 스토리지 C2) | 중국 APT 측면 이동 조기 탐지 |
| P1 | AWS IAM Identity Center 멀티리전 아키텍처 검토 | 리전별 권한 드리프트 제거 |
| P2 | 사내 암호화폐 투자 사기 인식 교육 (딥페이크 광고 포함) | 유명인 사칭 폰지 사기 피해 예방 |

### 위험 매트릭스

| 이슈 | 발생 가능성 | 영향도 | 대응 시급성 |
|------|-----------|--------|-----------|
| GlassWorm 확장으로 인한 자격증명 탈취 | 높음 | 높음 (CI/CD·AWS 계정 침해) | P0 즉시 |
| AI 에이전트 프롬프트 인젝션 악용 | 중간 | 높음 (내부 데이터 탈취) | P0 즉시 |
| APT 측면 이동 (파트너 네트워크 경유) | 낮음 | 매우 높음 (지속적 내부 침투) | P1 7일 내 |
| IAM 권한 드리프트 누적 | 높음 | 중간 (과잉 권한 악용) | P1 14일 내 |
| 유명인 사기 광고 피해 | 중간 | 낮음 (개인 금전 피해) | P2 교육 |

---

## 6. 실무 체크리스트

### P0 (즉시)

**공급망 보안 - GlassWorm 대응**:
- [ ] 개발자 워크스테이션의 VS Code / VSCodium 확장 목록 전수 추출 (`code --list-extensions`)
- [ ] Open VSX 출처 확장 식별 및 GlassWorm 72개 악성 확장 목록과 대조
- [ ] CI/CD 파이프라인에서 확장 자동 설치 스텝 유무 확인 및 허용 목록 전환
- [ ] 개발자 AWS 키, GitHub PAT, SSH 키 즉시 로테이션 및 이전 키 무효화
- [ ] `~/.ssh`, `~/.aws/credentials`, `.env`, `~/.npmrc` 최근 비정상 접근 로그 확인

**AI 에이전트 보안**:
- [ ] 프로덕션 배포 LLM 에이전트 목록 작성 및 시스템 프롬프트 노출 엔드포인트 확인
- [ ] 에이전트 입력 경로(이메일·문서·웹 검색)에 인젝션 패턴 검증 레이어 적용 여부 확인
- [ ] 에이전트가 사용하는 도구(파일 쓰기, 이메일 발송, 외부 API) 실행 승인 정책 점검
- [ ] 에이전트 실행 로그 보존 및 SIEM 연동 여부 확인

### P1 (7일 내)

**APT 탐지 강화**:
- [ ] SIEM에 클라우드 스토리지(OneDrive, Dropbox, Google Drive)로의 대용량 아웃바운드 트래픽 경보 규칙 추가
- [ ] EDR에 메모리 전용 프로세스 인젝션(Process Injection, T1055) 탐지 규칙 활성화 여부 확인
- [ ] 동남아·외부 파트너 VPN 채널에서 유입되는 트래픽 이상 행위 탐지 규칙 추가
- [ ] AppleChris C2 도메인·IP IOC를 방화벽 차단 목록에 추가 (TH 기사 IoC 참조)

**AWS IAM 접근 관리**:
- [ ] 리전별 독립 IAM 사용자 현황 파악 및 IAM Identity Center 마이그레이션 로드맵 작성
- [ ] CloudTrail 멀티리전 로그가 중앙 S3 버킷으로 집계되는지 확인
- [ ] Permission Set의 최대 세션 시간 검토 (8시간 초과 설정은 단축 권고)
- [ ] 비상 접근(Break-glass) 계정이 MFA 강제 설정되어 있는지 확인

### P2 (30일 내)

**공급망 보안 프로그램**:
- [ ] 오픈소스 소프트웨어 레지스트리(npm, PyPI, Open VSX) 모니터링 도구 도입 검토 (Socket, Snyk)
- [ ] SBOM(Software Bill of Materials) 생성 프로세스에 IDE 확장 포함 여부 검토
- [ ] 개발자 보안 인식 교육에 공급망 공격 시나리오(타이포스쿼팅, 악성 업데이트) 추가

**AI 에이전트 거버넌스**:
- [ ] AI 에이전트 도입·운영 내부 가이드라인 수립 (승인 프로세스, 데이터 접근 범위, 감사 요건)
- [ ] OWASP LLM Top 10 기반 내부 에이전트 취약점 점검 계획 수립
- [ ] 에이전트 코딩 도구(Cursor, GitHub Copilot) 사용 시 시크릿 사전 제거 정책 수립

**임직원 보안 인식**:
- [ ] 딥페이크 기반 유명인 암호화폐 사기 광고 식별 방법 사내 교육 실시
- [ ] 임직원 대상 암호화폐 투자 사기 신고 채널 공지 및 재확인

---

## 용어 설명

**GlassWorm**
: 2026년 3월 처음 공개된 위협 행위자 그룹으로, 오픈소스 IDE 확장 레지스트리를 표적으로 공급망 공격을 수행합니다. 정상 확장을 복제하거나 유지관리자 계정을 탈취해 악성 코드를 삽입한 뒤 개발자 자격증명을 수집합니다.

**Open VSX Registry**
: Eclipse Foundation이 운영하는 VS Code 호환 확장 마켓플레이스입니다. VSCodium, Gitpod, Eclipse Che 등 Microsoft 공식 마켓플레이스에 접근하지 않는 환경에서 사용됩니다. Microsoft의 Marketplace와 달리 퍼블리셔 서명 검증이 덜 엄격합니다.

**프롬프트 인젝션(Prompt Injection)**
: 외부 데이터(이메일, 웹페이지, 문서)에 숨겨진 악의적 지시문이 LLM 에이전트의 시스템 프롬프트나 이전 지시를 덮어쓰도록 유도하는 공격입니다. 직접 인젝션(사용자가 직접 시도)과 간접 인젝션(외부 데이터를 통한 시도) 두 가지 유형이 있습니다.

**MemFun**
: 중국 APT 그룹이 사용하는 인메모리 맬웨어 로더입니다. 디스크에 파일을 기록하지 않고 합법적인 시스템 프로세스 메모리에 코드를 인젝션해 실행합니다. 전통적인 파일 기반 안티바이러스 탐지를 우회하는 데 효과적입니다.

**IAM Identity Center Permission Set**
: AWS IAM Identity Center에서 사용자 또는 그룹에 부여하는 권한 묶음입니다. AWS 관리형 정책, 인라인 정책, 권한 경계를 조합해 정의하며, 멀티 계정 환경에서 동일한 Permission Set을 여러 계정에 배포할 수 있습니다.

**Basel III**
: 2008년 금융위기 이후 국제결제은행(BIS)이 도입한 은행 자본·유동성 규제 프레임워크입니다. 현행 규정에서 비트코인은 Group 2b 자산으로 분류돼 1,250%의 위험 가중치가 적용되어, 은행이 BTC를 직접 보유하려면 비현실적인 수준의 자기자본이 필요합니다.

**AppleChris RAT**
: 중국 연계 APT 그룹이 사용하는 원격 접근 트로이목마(Remote Access Trojan)입니다. HTTPS 기반 C2 통신과 클라우드 스토리지 서비스 활용으로 탐지를 우회하며, 키로깅·스크린샷·파일 수집·원격 셸 기능을 제공합니다.

---

## 실무 적용 가이드

### VS Code 확장 감사 스크립트

```bash
#!/bin/bash
# 개발자 워크스테이션 VS Code 확장 인벤토리 추출
# 사용법: ./audit-vscode-extensions.sh > extensions-$(hostname)-$(date +%Y%m%d).txt

echo "=== VS Code Extensions Audit ==="
echo "Host: $(hostname)"
echo "Date: $(date)"
echo ""

# VS Code (공식)
if command -v code &> /dev/null; then
    echo "--- VS Code (Official) ---"
    code --list-extensions --show-versions
fi

# VSCodium (Open VSX 기반)
if command -v codium &> /dev/null; then
    echo ""
    echo "--- VSCodium (Open VSX) ---"
    codium --list-extensions --show-versions
fi

# Remote 개발 환경 확장 (서버 측)
VSCODE_SERVER_DIR="$HOME/.vscode-server/extensions"
if [ -d "$VSCODE_SERVER_DIR" ]; then
    echo ""
    echo "--- VS Code Server Extensions ---"
    ls -la "$VSCODE_SERVER_DIR"
fi
```

### AI 에이전트 입출력 감사 미들웨어

```python
import logging
import hashlib
from datetime import datetime
from functools import wraps

logger = logging.getLogger("agent-security")

def audit_agent_io(func):
    """LLM 에이전트 입출력 감사 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 입력 기록 (민감 데이터 마스킹 후)
        input_hash = hashlib.sha256(str(args).encode()).hexdigest()[:8]
        logger.info({
            "event": "agent_input",
            "timestamp": datetime.utcnow().isoformat(),
            "input_hash": input_hash,  # 원본 대신 해시
            "function": func.__name__,
        })

        result = await func(*args, **kwargs)

        # 출력에서 민감 패턴 탐지
        output_str = str(result)
        sensitive_patterns = [
            r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+',
            r'\b[A-Za-z0-9]{32,}\b',  # 긴 토큰 패턴
        ]
        import re
        for pattern in sensitive_patterns:
            if re.search(pattern, output_str):
                logger.warning({
                    "event": "agent_output_sensitive_data_detected",
                    "function": func.__name__,
                    "pattern": pattern,
                })
                # 프로덕션에서는 출력 차단 또는 마스킹 처리

        return result
    return wrapper
```

---

## 관련 포스트

- [기술·보안 주간 다이제스트 (3월 12일)]({% post_url 2026-03-12-Tech_Security_Weekly_Digest_AI_Malware_AWS_Patch %}) - 블록체인 신뢰 리스크, Vertical AI 전략, 주소 오염 방지
- [기술·보안 주간 다이제스트 (3월 11일)]({% post_url 2026-03-11-Tech_Security_Weekly_Digest_AI_Agent_Data_Malware %}) - AI 에이전트 데이터 리스크, 공격 표면 인텔리전스
- [LLM 보안 실무 가이드]({% post_url 2026-03-07-LLM_Security_Practical_Guide_Prompt_Injection_RAG_MCP %}) - 프롬프트 인젝션, RAG 보안, MCP 위협 대응

---

## 참고 자료

### 보안 기준 및 프레임워크

| 리소스 | 링크 | 활용 목적 |
|--------|------|----------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 적극 악용 취약점 목록 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 분류 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 |
| OWASP LLM Top 10 | [owasp.org/www-project-top-10-for-large-language-model-applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | AI/LLM 보안 위협 분류 |

### 공급망 보안 참고자료

| 리소스 | 링크 | 활용 목적 |
|--------|------|----------|
| OpenSSF Scorecard | [securityscorecards.dev](https://securityscorecards.dev/) | 오픈소스 패키지 보안 점수 |
| Socket Security | [socket.dev](https://socket.dev/) | npm/PyPI 패키지 공급망 분석 |
| Open VSX Registry | [open-vsx.org](https://open-vsx.org/) | 확장 퍼블리셔 검증 |

### 이번 주기 원문 출처

| 기사 | 출처 |
|------|------|
| GlassWorm Supply-Chain Attack Abuses 72 Open VSX Extensions | [The Hacker News](https://thehackernews.com/2026/03/glassworm-supply-chain-attack-abuses-72.html) |
| AI Agent Flaws Could Enable Prompt Injection and Data Exfiltration | [The Hacker News](https://thehackernews.com) |
| Chinese Hackers Target Southeast Asian Militaries with AppleChris and MemFun | [The Hacker News](https://thehackernews.com) |
| Deploy AWS applications across multiple Regions with IAM Identity Center | [AWS Security Blog](https://aws.amazon.com/blogs/security/deploy-aws-applications-and-access-aws-accounts-across-multiple-regions-with-iam-identity-center/) |
| Changing Basel rules could unlock huge liquidity for BTC | [Cointelegraph](https://cointelegraph.com/news/changing-basel-rules-huge-liquidity-btc) |
| Boris Johnson linked to BTC Ponzi scheme allegations | [Cointelegraph](https://cointelegraph.com/news/boris-johnson-btc-ponzi-scheme) |
| Bitcoin beats stocks as Strategy eyes $776M BTC buying potential | [Cointelegraph](https://cointelegraph.com/news/bitcoin-beats-stocks-strategy-strc-776m-btc-buying-potential) |
| 진짜 내 일을 위한 Agentic Workflow | [GeekNews](https://news.hada.io/topic?id=27513) |
| MacBook Neo에서 Parallels 가상 머신으로 윈도우 실행 가능 확인 | [GeekNews](https://news.hada.io/topic?id=27512) |
| Hammerspoon - Lua로 구현된 강력한 macOS 데스크톱 자동화 도구 | [GeekNews](https://news.hada.io/topic?id=27511) |

---

> 이 다이제스트는 매일 주요 보안·기술 뉴스를 수집하여 운영 관점의 실무 인사이트로 정리합니다. 주간 흐름을 파악하려면 위의 관련 포스트 링크를 통해 이전 날짜의 다이제스트를 함께 읽어보시길 권장합니다.
>
> 피드백이나 제보 사항이 있으시면 댓글 또는 GitHub Issues를 통해 알려주시기 바랍니다.

**작성자**: Twodragon
