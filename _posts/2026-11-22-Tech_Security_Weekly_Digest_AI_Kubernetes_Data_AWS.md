---
layout: post
title: "2026년 11월 22일 주간 보안 다이제스트: 패치·쿠버네티스·클라우드 (16건)"
date: 2026-11-22 15:59:28 +0900
last_modified_at: 2026-11-22T15:59:28+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Kubernetes, AWS]
excerpt: "‘OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간’ 소식 · ‘연구진, 인기 앱에서 조작된 파일 업로드를 통한’ 소식을 비롯한 2026년 11월 22일 보안/기술 동향 16건을 DevSecOps 시선으로 정리합니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 11월 22일 보안 뉴스 요약. The Hacker News, BleepingComputer 등 16건을 분석하고 OpenRouter, 연구진이 AI 호스팅, 연구진 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Kubernetes, AWS]
author: Twodragon
comments: true
image: /assets/images/2026-11-22-Tech_Security_Weekly_Digest_AI_Kubernetes_Data_AWS.svg
image_alt: "OpenRouter, AI, Rackspace Spot - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 22일 주간 보안 다이제스트: 패치·쿠버네티스·클라우드 (16건)"
  period: "2026년 11월 22일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Kubernetes"
    - "AWS"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간 프롬프트 탈취 적발 후 3개 공급업체 제거" }
    - { source: "The Hacker News", title: "연구진, 인기 앱에서 조작된 파일 업로드를 통한 Ghostscript 샌드박스 탈출 RCE 시연" }
    - { source: "BleepingComputer", title: "Rackspace Spot 침해로 해커가 고객 Kubernetes 시크릿에 접근 가능해져" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 22일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 16개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 1개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간 프롬프트 탈취 적발 후 3개 공급업체 제거 | 🟠 High |
| 🔒 **Security** | The Hacker News | 연구진, 인기 앱에서 조작된 파일 업로드를 통한 Ghostscript 샌드박스 탈출 RCE 시연 | 🔴 Critical |
| 🔒 **Security** | BleepingComputer | Rackspace Spot 침해로 해커가 고객 Kubernetes 시크릿에 접근 가능해져 | 🟡 Medium |
| 🤖 **AI/ML** | AWS Machine Learning | Meta 광고, 이제 AWS Quick에서 이용 가능 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | Chainflip, 1,200만 달러 해킹 확인하고 공격자에게 10% 포상금 제안 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | ECB, 토큰화 예금·증권 실험 위한 업계 파트너 모색 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | 미국 의원들, 예측 시장 내부고발자에 최대 30% 보상 제안 | 🟡 Medium |
| 💻 **Tech** | Tech World Monitor | Tech Monitor - 실시간 AI 및 기술 산업 대시보드 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 결재 서류를 쌓아 두던 부장에서 보고받는 사장으로 – Claude Code 매니저 세션 만들기 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 젠슨 황의 추락은 실리콘밸리 가속주의자들에게 악재임 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: 연구진, 인기 앱에서 조작된 파일 업로드를 통한 Ghostscript 샌드박스 탈출 RCE 시연 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간 프롬프트 탈취 적발 후 3개 공급업체 제거, Meta 광고, 이제 AWS Quick에서 이용 가능, Chainflip, 1,200만 달러 해킹 확인하고 공격자에게 10% 포상금 제안 등 High 등급 위협 3건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 분석가 시점

현장 운영 관점에서 보면 이번 주기는 모델 라우팅 계층과 파일 처리 경계가 동시에 뚫린 주간이다. OpenRouter 프롬프트 탈취는 서드파티 추론 경로가 곧 데이터 유출 경로임을 보여줬고, Ghostscript 샌드박스 이스케이프는 업로드 검증을 ImageMagick·PDF 변환 파이프라인 전 구간에서 다시 봐야 한다는 신호다. Rackspace Spot의 Kubernetes 시크릿 노출은 관리형 컨트롤 플레인이라도 etcd 접근 권한과 RBAC 바인딩은 우리 책임이라는 점을 상기시킨다. 이번 주기에 가장 먼저 볼 신호는 **업로드·변환 워커의 실행 경계**다. Ghostscript 호출부를 seccomp·eBPF로 격리하고, Kubernetes 시크릿은 외부 KMS와 짧은 TTL로 재발급하며, 외부 추론 API는 프롬프트 로깅 정책을 계약 조항으로 못박아야 한다.

## 1. 보안 뉴스

### 1.1 OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간 프롬프트 탈취 적발 후 3개 공급업체 제거

{% include news-card.html
  title="OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간 프롬프트 탈취 적발 후 3개 공급업체 제거"
  url="https://thehackernews.com/2026/11/openrouter-drops-3-providers-after.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjEGP3P_elvK4C-QnSx5onZ67viDXCIgPCUYqtTF_RDNcLJfyQ4QMbegUmn8AJy5nEmnXfN4ACr6hHztG_DdqXlj54S21toacPQaZgRx2rgqZltN3lvREpZR2xlvgXF_iZ7zW0XT0b91mMiRDVaEB6TUvMFlWwaSa3_C7gwpxdKcNhLtIq15KqwaZrR3VI/s1600/openrouter.png"
  summary="Dragos 연구진이 3개 AI inference provider 내부에서 수개월간 prompt 도난이 발생했음을 발견했으며, 해당 업체들은 연구진이 알려주기 전까지 이를 인지하지 못했다. Zero Data Retention으로 표시된 요청까지 유출되었고, OpenRouter는 이에 해당 3개 provider를 제거했다."
  source="The Hacker News"
  severity="High"
%}

#### OpenRouter 3개 프로바이더 퇴출 사건 분석

#### 기술적 배경 및 위협 분석

AI 추론 프로바이더 내부에서 수개월간 프롬프트 탈취가 발생했고, 해당 업체들은 연구진 통보 전까지 인지하지 못했다. 핵심 위협은 **Zero Data Retention(ZDR) 플래그가 실제로는 강제되지 않았다**는 점이다. ZDR은 "프롬프트 미저장"을 보장하는 설정이지만, 프로바이더 내부 로깅·모니터링 계층에서 평문 또는 복호화 가능한 형태로 남아 있었다면 게이트웨이의 정책 신뢰 모델 자체가 붕괴한다. OpenRouter 같은 라우팅 게이트웨이는 다수 프로바이더에 요청을 분산하므로, 단일 프로바이더의 내부 통제 실패가 전체 고객 데이터 노출로 확산되는 **신뢰 체인 취약점**이다. 공격자는 추론 인프라 운영 권한 또는 내부 접근을 통해 요청 스트림을 수집한 것으로 보이며, 이는 전통적 경계 보안이 아닌 **데이터 흐름 내부 통제** 실패 사례다.

#### 실무 영향 분석

- **데이터 거버넌스 재검토**: ZDR 계약 조항이 실제 기술적 강제와 일치하는지 벤더 감사 필요. 계약서 문구만으로는 컴플라이언스 입증 불가.
- **서드파티 리스크 관리**: LLM 게이트웨이 의존 시 프로바이더별 데이터 처리 정책·감사 로그 접근권을 SLA에 명문화해야 한다.
- **로깅 최소화 원칙**: 애플리케이션 단에서 민감 프롬프트를 사전 마스킹(PII/시크릿 redaction)하는 방어 계층이 필수.
- **사고 대응 절차**: 벤더 통보 지연(수개월)을 전제로 자체 이상 탐지(요청량 급증, 비정상 egress) 역량 확보 필요.



---

### 1.2 연구진, 인기 앱에서 조작된 파일 업로드를 통한 Ghostscript 샌드박스 탈출 RCE 시연

{% include news-card.html
  title="연구진, 인기 앱에서 조작된 파일 업로드를 통한 Ghostscript 샌드박스 탈출 RCE 시연"
  url="https://thehackernews.com/2026/11/researchers-demonstrate-ghostscript.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg1BiCJUIrSJXNfKPZEkM46ynK6Rs7gba2xMaTUdoJ7yOK6Y8kcKMqJ_6PhbUIog_U1E8gRCpbj2HrkQ9UEpbPi1HOvkxdxCE5Afa5LbkNhUPvgU7Sa60IVHAWqSvgJaX1p6frMAN335QncL5UTZ3a4v1-agyb8ZXIlMGZTOtzsC0Gll2qRI0NJNMHTsf8/s1600/ghostscript.jpg"
  summary="Ghostscript의 패치된 취약점을 악용하면 조작된 파일 업로드로 샌드박스를 탈출해 서버에서 명령을 실행할 수 있다. pwn.ai는 많은 Linux 서버가 업로드된 PDF·PostScript·이미지 변환에 Ghostscript를 사용한다는 점을 들어 일반적인 파일 업로드만으로 RCE가 가능함을 시연했다."
  source="The Hacker News"
  severity="Critical"
%}

#### Ghostscript 샌드박스 이스케이프 RCE 분석

#### 기술적 배경 및 위협 분석
Ghostscript는 Linux 서버에서 업로드된 PDF·PostScript·이미지를 변환하는 인터프리터로, 애플리케이션이 직접 호출하지 않아도 이미지 라이브러리(ImageMagick, Pillow 등)나 문서 변환 파이프라인을 통해 간접 실행되는 경우가 많다. 이번 취약점은 조작된 파일이 `-dSAFER` 샌드박스를 우회해 서버 명령 실행으로 이어지는 전형적인 "간접 의존성 공격"이다. 핵심 위협은 ① 업로드 기능이 곧 RCE 진입점이 된다는 점, ② Ghostscript가 컨테이너·CI 이미지에 암묵적으로 포함되어 SBOM에서 누락되기 쉽다는 점, ③ 패치가 나와도 베이스 이미지 재빌드 없이는 반영되지 않는다는 점이다.

#### 실무 영향 분석
DevSecOps 관점에서 이 취약점은 "패치됐지만 여전히 위험한" 유형이다. 업로드 처리 서비스는 대개 외부 노출도가 높고, Ghostscript 버전이 OS 패키지 관리자에 묶여 있어 애플리케이션 의존성 스캔(SCA)에 잡히지 않는다. 따라서 컨테이너 이미지 스캔과 런타임 무결성 검증이 없으면 탐지 공백이 발생한다. 또한 파일 변환 워커가 과도한 권한(호스트 마운트, root 실행)으로 동작할 경우 샌드박스 우회가 곧 호스트 침해로 확대된다.



---

### 1.3 Rackspace Spot 침해로 해커가 고객 Kubernetes 시크릿에 접근 가능해져

{% include news-card.html
  title="Rackspace Spot 침해로 해커가 고객 Kubernetes 시크릿에 접근 가능해져"
  url="https://www.bleepingcomputer.com/news/security/rackspace-spot-breach-let-hackers-access-customer-kubernetes-secrets/"
  image="https://www.bleepstatic.com/content/hl-images/2022/12/09/Rackspace.jpg"
  summary="Rackspace는 공격자들이 탈취한 자격 증명을 이용해 Rackspace Spot 클라우드 플랫폼을 침해하고 무단 워크로드를 배포했으며 고객 클러스터의 Kubernetes secrets에 접근했다고 고객들에게 경고했습니다."
  source="BleepingComputer"
  severity="Medium"
%}


#### 권장 조치

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사


---

## 2. AI/ML 뉴스

### 2.1 Meta 광고, 이제 AWS Quick에서 이용 가능

{% include news-card.html
  title="Meta 광고, 이제 AWS Quick에서 이용 가능"
  url="https://aws.amazon.com/blogs/machine-learning/meta-ads-is-now-available-in-aws-quick/"
  summary="AWS Quick에 Meta ads AI 커넥터가 추가되어 Meta 광고주가 자연어로 캠페인을 생성·관리·분석할 수 있게 되었다. Meta 광고 데이터를 자사 및 서드파티 데이터와 결합해 대시보드, 문서, 슬라이드, 자동화 워크플로를 만들 수 있다."
  source="AWS Machine Learning Blog"
  severity="High"
%}


---

## 3. 블록체인 뉴스

### 3.1 Chainflip, 1,200만 달러 해킹 확인하고 공격자에게 10% 포상금 제안

{% include news-card.html
  title="Chainflip, 1,200만 달러 해킹 확인하고 공격자에게 10% 포상금 제안"
  url="https://cointelegraph.com/news/chainflip-12m-crypto-hack-10-percent-bounty?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/11/01M80VMG116PQ22VH13YJ5ANN8/hacky-hack-2.png"
  summary="Chainflip은 1,200만 달러 규모의 해킹을 확인하고 공격자에게 11월 23일까지 탈취 자금의 90%를 반환하면 10%의 바운티를 제공하겠다고 제안했습니다. 반환된 자금은 화이트햇 복구로 간주하고 법적 고소를 철회하겠다고 밝혔습니다."
  source="Cointelegraph"
  severity="High"
%}


---

### 3.2 ECB, 토큰화 예금·증권 실험 위한 업계 파트너 모색

{% include news-card.html
  title="ECB, 토큰화 예금·증권 실험 위한 업계 파트너 모색"
  url="https://cointelegraph.com/news/ecb-tokenized-deposits-securities-experiments-appia?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/09/01M34BTQXP52VJEXVV822SS5QM/hi-what-is-a-decentralized-money-market-and-eu-stablecoin-2.jpg"
  summary="ECB가 Appia 이니셔티브의 첫 실험 과제를 위해 업계 파트너를 모집하며, 참여를 원하는 업계 그룹은 12월 11일까지 신청해야 합니다. 이후 제출분은 수시로 검토될 예정입니다."
  source="Cointelegraph"
  severity="Medium"
%}


---

### 3.3 미국 의원들, 예측 시장 내부고발자에 최대 30% 보상 제안

{% include news-card.html
  title="미국 의원들, 예측 시장 내부고발자에 최대 30% 보상 제안"
  url="https://cointelegraph.com/news/us-prediction-market-whistleblower-rewards-30-percent?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/10/01M3TG0M8S1BAV7KN2AJ34JJE9/prediction-market.jpg"
  summary="미국 의원들이 100만 달러 이상의 제재금이 부과되는 prediction market 사기 사건에서 내부고발자에게 제재금의 10~30%를 보상으로 지급하는 방안을 제안했습니다."
  source="Cointelegraph"
  severity="Medium"
%}


---

## 4. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Tech Monitor - 실시간 AI 및 기술 산업 대시보드](https://tech.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.00&view=global&timeRange=7d&layers=cables%2Cweather%2Ceconomic%2Coutages%2Cdatacenters%2Cnatural%2CstartupHubs%2CcloudRegions%2CtechHQs%2CtechEvents) | Tech World Monitor | Tech World Monitor 글로벌 대시보드 기반 기술 동향 요약입니다. Real-time AI and tech industry dashboard tracking tech giants, AI labs, startup ecosystems, funding rounds, and technology events worldwide with live 등이 확인되었습니다. |
| [결재 서류를 쌓아 두던 부장에서 보고받는 사장으로 – Claude Code 매니저 세션 만들기](https://news.hada.io/topic?id=37609&utm_source=geeknews&utm_medium=rss&utm_campaign=news) | GeekNews (긱뉴스) | Claude Code 세션 여러 개를 동시에 돌리며 모든 응답을 직접 읽고 결정하다 보니, 세션이 늘수록 읽을 양이 늘고 언제 어느 세션에 가야 하는지도 알기 어려워짐. 에디터 탭의 응답 표시는 "서브에이전트 결과를 기다리는 중" 같은 중간 보고에도 똑같이 켜짐 |
| [젠슨 황의 추락은 실리콘밸리 가속주의자들에게 악재임](https://news.hada.io/topic?id=37608&utm_source=geeknews&utm_medium=rss&utm_campaign=news) | GeekNews (긱뉴스) | Nvidia를 이끌던 젠슨 황의 사임 은 AI의 빠른 발전을 지지하는 실리콘밸리 가속주의 진영에 큰 타격임 가속주의자들 은 AI가 계속해서 매우 빠른 속도로 발전하기를 원함 황은 이 운동에서 가장 신뢰받는 대변인 이었으며, 가속주의 진영은 이미 수세에 몰려 있었음 사임 전 마지막 인터뷰들 중 하나에서 AI 발전 속도에 대한 불안을 부추기는 목소리를 “ 등이 확인되었습니다. |


---

## 5. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 9건 | 기타 주제 |
| **AI/ML** | 2건 | The Hacker News 관련 동향, Tech World Monitor 관련 동향 |
| **클라우드 보안** | 1건 | AWS Machine Learning Blog 관련 동향 |
| **컨테이너/K8s** | 1건 | BleepingComputer 관련 동향 |
| **블록체인/암호화폐** | 1건 | CoinDesk 관련 동향 |
| **취약점/CVE** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **AI/ML**(2건)입니다. The Hacker News 관련 동향, Tech World Monitor 관련 동향 등이 주요 이슈입니다. 

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **연구진, 인기 앱에서 조작된 파일 업로드를 통한 Ghostscript 샌드박스 탈출 RCE 시연** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **OpenRouter, 연구진이 AI 호스팅 업체들의 수개월간 프롬프트 탈취 적발 후 3개 공급업체 제거** 관련 보안 검토 및 모니터링
- [ ] **악성 웹페이지 하나로 연구진이 Meta Muse를 탈취하고 비공개 채팅에 접근할 수 있었다** 관련 보안 검토 및 모니터링
- [ ] **Meta 광고, 이제 AWS Quick에서 이용 가능** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Meta 광고, 이제 AWS Quick에서 이용 가능** 관련 AI 보안 정책 검토
- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검

## 관련 포스트 및 참고 자료

- 2026년 11월 21일 주간 보안 다이제스트: {% post_url 2026-11-21-Tech_Security_Weekly_Digest_Patch_AWS_Security_Malware %}
- 2026년 11월 19일 주간 보안 다이제스트: {% post_url 2026-11-19-Tech_Security_Weekly_Digest_AWS_Security_AI %}
- 2026년 11월 18일 주간 보안 다이제스트: {% post_url 2026-11-18-Tech_Security_Weekly_Digest_AI_AWS_CVE_Patch %}

| 리소스 | 링크 | 용도 |
|--------|------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용 확인된 취약점 목록 — 패치 우선순위 기준 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 매핑 — 탐지 룰 설계 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 — CVSS 보완 |
| The Hacker News | [thehackernews.com](https://thehackernews.com) | 본문 2건 인용 |
| BleepingComputer | [bleepingcomputer.com](https://www.bleepingcomputer.com) | 본문 1건 인용 |
| AWS Machine Learning Blog | [aws.amazon.com](https://aws.amazon.com) | 본문 1건 인용 |
| Cointelegraph | [cointelegraph.com](https://cointelegraph.com) | 본문 3건 인용 |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 11월 21일 주간 보안 다이제스트: 제로데이·클라우드·패치 (30건)](/posts/2026/11/21/Tech_Security_Weekly_Digest_Patch_AWS_Security_Malware/) — 2026-11-21
- [2026년 11월 19일 주간 보안 다이제스트: 클라우드·제로데이·AI 에이전트 (30건)](/posts/2026/11/19/Tech_Security_Weekly_Digest_AWS_Security_AI/) — 2026-11-19
- [2026년 11월 15일 주간 보안 다이제스트: 제로데이·북한 위협·AI 에이전트 (15건)](/posts/2026/11/15/Tech_Security_Weekly_Digest_Security_AI_Bitcoin/) — 2026-11-15

---

**작성자**: Twodragon
