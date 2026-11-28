---
layout: post
title: "2026년 11월 29일 주간 보안 다이제스트: 클라우드·북한 위협·블록체인 (16건)"
date: 2026-11-29 00:32:40 +0900
last_modified_at: 2026-11-29T00:32:40+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Cloud, Bitcoin]
excerpt: "‘pCloud Password Manager’ 소식 · ‘베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려’ 소식 등 2026년 11월 29일 보고된 16건의 보안/기술 이슈를 운영 관점에서 점검합니다. 실무 체크리스트에 패치 적용 항목을 함께 정리했습니다."
description: "2026년 11월 29일 보안 뉴스 요약. The Hacker News, BleepingComputer 등 16건을 분석하고 pCloud Password Manager, 베트남 연계 의심 해커, 남중국해 스파이 활동 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Cloud, Bitcoin]
author: Twodragon
comments: true
image: /assets/images/2026-11-29-Tech_Security_Weekly_Digest_AI_Cloud_Data_Zero-Day.svg
image_alt: "pCloud Password Manager, pCloud - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 29일 주간 보안 다이제스트: 클라우드·북한 위협·블록체인 (16건)"
  period: "2026년 11월 29일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Cloud"
    - "Bitcoin"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "pCloud Password Manager, 이메일 주소 노출 및 로그인 시도 관련 사이버 공격 당해" }
    - { source: "The Hacker News", title: "베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려" }
    - { source: "BleepingComputer", title: "pCloud, 의심스러운 로그인 경고 후 비밀번호 관리자 해킹 확인" }
redirect_from:
- /posts/2026/11/29/Tech_Security_Weekly_Digest_AI_Cloud_Data_Zero-Day/
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 29일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

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
| 🔒 **Security** | The Hacker News | pCloud Password Manager, 이메일 주소 노출 및 로그인 시도 관련 사이버 공격 당해 | 🟠 High |
| 🔒 **Security** | The Hacker News | 베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려 | 🟠 High |
| 🔒 **Security** | BleepingComputer | pCloud, 의심스러운 로그인 경고 후 비밀번호 관리자 해킹 확인 | 🟠 High |
| 🤖 **AI/ML** | Cointelegraph | Anthropic, 기술주 반등에 합류하면서 Bitcoin 가격 5만9천 달러 아래로 하락 | 🟡 Medium |
| ⛓️ **Blockchain** | Bitcoin Magazine | Binance, 63억 달러 해킹 한 달 만에 출금 중단 전면 해제 | 🟡 Medium |
| ⛓️ **Blockchain** | Bitcoin Magazine | 러시아 VTB, 중앙은행 암호화폐 테스트 마무리 속 Bitcoin 거래 개시 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | Justin Sun, Trump 가족과 연관된 WLFI 토큰 상장 폐지 촉구 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | Claude Code의 사보타주: 예비 벤치마킹 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 작별 인사: Heretic 개발 활동 종료와 저장소 아카이브 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | Rayshader 1.0: 행렬을 벗어나 공간 데이터를 바로 3D로 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: pCloud Password Manager, 이메일 주소 노출 및 로그인 시도 관련 사이버 공격 당해, 베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려, pCloud, 의심스러운 로그인 경고 후 비밀번호 관리자 해킹 확인 등 High 등급 위협 3건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 분석가 시점

이번 분석 사이클에서 가장 먼저 눈에 띄는 신호는 pCloud 비밀번호 관리자 침해가 이메일 노출과 로그인 시도로 이어졌다는 점, 그리고 남중국해 스파이 활동 정황이 동시에 포착됐다는 사실입니다. 표면적으로는 서로 무관해 보이지만 제가 주목하는 건 인증 경계의 붕괴입니다. 비밀번호 관리자는 결국 자격증명의 단일 실패점이고, 여기서 새어나온 이메일은 표적형 스피어피싱의 시드가 됩니다. DevSecOps 실무자라면 이번 주기에 **GitHub Actions 시크릿과 OIDC 신뢰 정책의 범위를 먼저 감사**해야 합니다. 파이프라인에 흩어진 장기 자격증명이 곧 다음 캠페인의 초기 접근 벡터가 되기 때문입니다. 클라우드나 블록체인 통계는 부차적입니다. 지금 당장 손댈 지점은 CI 워크플로의 토큰 수명과 권한 최소화입니다.

## 1. 보안 뉴스

### 1.1 pCloud Password Manager, 이메일 주소 노출 및 로그인 시도 관련 사이버 공격 당해

{% include news-card.html
  title="pCloud Password Manager, 이메일 주소 노출 및 로그인 시도 관련 사이버 공격 당해"
  url="https://thehackernews.com/2026/11/pcloud-password-manager-hit-by-cyber.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEizySCkvtf5mXH_3zoxzuk-QyEdUnYmspglEsVYdqRITloUFrUDZCQJcwtQG09teFmXo2IJOknOQb7CXhUpjKjGnadD6TuOIvVWIoWmKcaxb8-1uwf-3AiXZPYCFf2RzDkHNZ06d2Q5OS6AcCV7JHjTACCJH2f5aipC8vllpOwj1dSBYQJtqJ_wDc5nXQwU/s1600/pcloud.jpg"
  summary="pCloud Pass가 사이버 공격을 받아 일부 사용자의 이메일 주소가 노출되고 계정에 알 수 없는 기기 연결 및 로그인 시도가 발생했다. pCloud는 공격을 즉시 차단했다고 밝혔으며, 피해 규모는 소수로 파악된다."
  source="The Hacker News"
  severity="High"
%}

#### pCloud Pass 사이버 공격, DevSecOps 실무자 관점 분석

#### 기술적 배경 및 위협 분석

pCloud Pass는 마스터 패스워드 기반의 제로-knowledge 암호화를 표방하는 크로스플랫폼 비밀번호 관리자다. 이번 사고의 핵심은 **이메일 주소 노출과 미상 디바이스의 계정 연결**이다. 이는 단순 정보 유출을 넘어, 공격자가 인증 흐름(로그인/디바이스 등록)에 개입했을 가능성을 시사한다. 비밀번호 관리자는 "모든 자격증명의 단일 실패점(SPOF)"이므로, 이메일 노출만으로도 크리덴셜 스터핑·피싱·세션 하이재킹의 표적 목록이 형성된다. 특히 미상 디바이스 연결은 디바이스 신뢰 등록 로직이나 세션 토큰 검증의 결함, 혹은 내부자/API 남용 가능성을 배제할 수 없게 만든다. 제로-knowledge 설계라도 **메타데이터(이메일, 디바이스, 로그인 이력)는 서버 측에 평문으로 존재**할 수밖에 없어, 공격 표면이 인증·세션 계층에 집중된다는 점이 위협의 본질이다.

#### 실무 영향 분석

실무적으로는 ① **서드파티 SaaS 의존 리스크**가 즉시 부각된다. 조직이 pCloud Pass를 표준으로 채택했다면 전 사용자 대상 자격증명 회전·세션 무효화가 필요하다. ② **공급망 신뢰 모델 재점검**: 비밀번호 관리자조차 침해될 수 있다는 전제하에, 중요 시스템은 관리자 내 저장 자격증명과 별도로 하드웨어 키(FIDO2)·단기 토큰·시크릿 매니저(Vault 등)로 이중 통제해야 한다. ③ **탐지·모니터링 공백**: 미상 디바이스 연결은 IDP/SSO 로그의 이상 디바이스·지리·UA 변화 탐지 룰로 포착 가능하나, 사내 정책에 디바이스 핑거프린팅 기준이 없으면 사후 인지에 그친다. ④ **IR 커뮤니케이션**: 벤더의 "소수 사용자" 표현만으로는 영향 범위를 확정할 수 없어, 자체 로그 기반 영향 평가가 선행되어야 한다.



---

### 1.2 베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려

{% include news-card.html
  title="베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려"
  url="https://thehackernews.com/2026/11/suspected-vietnam-linked-hackers-target.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj19T-kU1dmVfKt2PtUQ2I25MGovj8kmv6lMkk6inlif4yLeezJS4kVRTvsARL5UkpTT66jYru6k2b5bmWfjjlkmG4JznSKmkmd4ldXcyxTw3xsU5nP6_jxfWMw9thW37m5usfr-eWAZBHq6bPuS613CIx9XgWxPcSVFcZVgz_9tWd5Nu8YWAxexuqcVPrN/s1600/data.jpg"
  summary="Vietnam 연계로 의심되는 해킹 그룹이 동남아시아의 군사·정부·입법 기관을 대상으로 South China Sea 방어 및 군사 협정 관련 정보를 수집하는 스파이 활동을 벌인 것으로 분석됐다. SOCRadar가 공개한 이번 캠페인은 WeaveLotus로 명명됐으며, 태국에서 5건의 침입이 포함된 것으로 평가된다."
  source="The Hacker News"
  severity="High"
%}

#### 기술적 배경 및 위협 분석

WeaveLotus는 베트남 연계로 추정되는 위협 행위자가 동남아시아 군사·정부·입법 기관을 대상으로 남중국해 방어 체계 및 군사 협정 관련 첩보를 수집하는 캠페인이다. SOCRadar가 최초 문서화한 미기록 침해 세트로, 태국에서 최소 5건의 침해가 확인되었다. 표적 특성상 지속적 접근(APT) 성격을 띠며, 군사·외교 정보라는 고가치 자산을 노린다. 공격자는 정부·군 관련 문서를 미끼로 한 스피어피싱, 측면 이동, 장기 잠복을 통한 정보 유출 전술을 구사할 가능성이 높다. 지정학적 이해관계가 첩보 수집의 직접 동기로 작용한다는 점에서, 유사 분쟁 지역(한반도·대만해협) 관련 기관도 동형 위협에 노출될 수 있다.

#### 실무 영향 분석

DevSecOps 관점에서 핵심은 **공급망·CI/CD 경유 침투 가능성**과 **탐지 사각지대**다. 국방·정부 협력사를 대상으로 한 표적형 피싱은 개발자 계정 탈취→리포지토리 접근→빌드 파이프라인 오염으로 이어질 수 있다. 또한 첩보형 공격은 흔적 최소화(정상 도구 악용, Living-off-the-Land)를 선호하므로 기존 시그니처 기반 탐지로는 포착이 어렵다. SBOM·아티팩트 서명·최소 권한 원칙이 실제 통제 효과를 발휘하는지 재점검이 필요하며, 개발-운영 경계에서의 이상 행위(비정상 시간대 접근, 대량 코드 열람) 모니터링 강화가 요구된다.



---

### 1.3 pCloud, 의심스러운 로그인 경고 후 비밀번호 관리자 해킹 확인

{% include news-card.html
  title="pCloud, 의심스러운 로그인 경고 후 비밀번호 관리자 해킹 확인"
  url="https://www.bleepingcomputer.com/news/security/pcloud-confirms-password-manager-hack-after-suspicious-login-alerts/"
  image="https://www.bleepstatic.com/content/hl-images/2026/11/27/pcloud-logo.jpg"
  summary="pCloud Pass 비밀번호 관리자가 사이버 공격을 받아 2FA가 활성화된 상태에서도 알 수 없는 기기가 계정에 연결되었다는 사용자 신고가 이어졌습니다. pCloud는 이번 해킹 사실을 확인했습니다."
  source="BleepingComputer"
  severity="High"
%}

#### pCloud Pass 해킹 사건 DevSecOps 분석

#### 기술적 배경 및 위협 분석
pCloud Pass는 2FA가 활성화된 계정에도 불구하고 미확인 기기에서의 세션 연결이 발생했다고 확인했다. 이는 비밀번호 자체의 유출보다 **세션 토큰 탈취 또는 인증 우회 취약점** 가능성을 시사한다. 2FA는 인증 시점만 보호할 뿐, 발급된 세션·리프레시 토큰이 탈취되면 무력화된다. 비밀번호 관리자는 "마스터키" 성격의 단일 실패점(SPOF)이므로, 공급망 신뢰 경계가 무너질 경우 사용자 전 자격증명이 연쇄 노출되는 고위험 자산이다. 또한 클라우드 동기화 아키텍처에서 서버 측 세션 관리 취약점이 의심되므로, 제로트러스트 원칙(세션 재검증, 디바이스 바인딩) 미적용 가능성을 배제할 수 없다.

#### 실무 영향 분석
- **공급망 리스크 현실화**: 외부 SaaS 비밀번호 관리자 의존 조직은 즉시 자격증명 순환 정책을 검토해야 한다.
- **2FA 신화 재검토**: "2FA=안전" 가정을 폐기하고 세션 수명주기 관리, 디바이스 핑거프린팅, 조건부 접근(Conditional Access)을 파이프라인에 통합해야 한다.
- **탐지 공백**: 비정상 로그인 알림이 사후 통보에 그쳤다는 점은 SIEM/UEBA 연동 및 실시간 이상행위 탐지 부재를 드러낸다.
- **컴플라이언스**: ISO 27001 A.5.17(인증정보 관리), NIST 800-63B 세션 정책 재점검 트리거.



---

## 2. AI/ML 뉴스

### 2.1 Anthropic, 기술주 반등에 합류하면서 Bitcoin 가격 5만9천 달러 아래로 하락

{% include news-card.html
  title="Anthropic, 기술주 반등에 합류하면서 Bitcoin 가격 5만9천 달러 아래로 하락"
  url="https://cointelegraph.com/markets/bitcoin-price-below-59k-anthropic-tech-stock-rebound?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/11/01M8ESH2B3W3M02NVS1RNS6AQH/crypto-bitcoin-btc-price-960x640-960x640.webp"
  summary="Bitcoin 가격이 월스트리트 개장과 함께 변동성을 보이며 BTC/USD가 58,700달러의 지역 저점까지 하락했고, 주식과 금은 상승세를 나타냈다. Anthropic이 기술주 반등에 합류한 가운데 Bitcoin은 이와 반대 흐름을 보였다."
  source="Cointelegraph"
  severity="Medium"
%}


---

## 3. 블록체인 뉴스

### 3.1 Binance, 63억 달러 해킹 한 달 만에 출금 중단 전면 해제

{% include news-card.html
  title="Binance, 63억 달러 해킹 한 달 만에 출금 중단 전면 해제"
  url="https://bitcoinmagazine.com/news/binance-lifts-withdrawal-suspension-hack"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Binance-Says-6.34-Billion-Hack-Began-With-Fake-Job-Interview-.jpg"
  summary="Binance는 10월 29일 발생한 63억 달러 규모 해킹과 관련된 출금 중단 조치를 전면 해제하고 출금 복구 작업이 완료되었다고 밝혔다. 한편 연구진들은 북한 해커 조직이 탈취 자금을 세탁하며 이동시키는 정황을 추적하고 있다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 3.2 러시아 VTB, 중앙은행 암호화폐 테스트 마무리 속 Bitcoin 거래 개시

{% include news-card.html
  title="러시아 VTB, 중앙은행 암호화폐 테스트 마무리 속 Bitcoin 거래 개시"
  url="https://bitcoinmagazine.com/news/russia-vtb-bitcoin-trading-crypto-test"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/U.S.-Sanctioned-Moscow-Exchange-Will-List-Bitcoin-on-Dec.-1-as-Russia-Pulls-Crypto-Trading-Home.jpg"
  summary="러시아 VTB 은행이 자격을 갖춘 투자자들을 대상으로 앱에서 bitcoin 거래를 개시했으며, 이는 Bank of Russia가 모든 암호화폐 구매자가 통과해야 하는 지식 테스트를 승인한 다음 날 이루어졌습니다. SPB Exchange는 12월 1일 현물 거래 개시를 계획하고 있습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 3.3 Justin Sun, Trump 가족과 연관된 WLFI 토큰 상장 폐지 촉구

{% include news-card.html
  title="Justin Sun, Trump 가족과 연관된 WLFI 토큰 상장 폐지 촉구"
  url="https://cointelegraph.com/news/justin-sun-calls-for-trump-family-linked-wlfi-token-to-be-delisted?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/11/01M8H5C1A6GBRN04YFGTX7SKRM/justin-sun-vs-trump.jpg"
  summary="저스틴 선은 트럼프 가족과 연관된 WLFI 토큰의 상장 폐지를 촉구했다. 그는 또한 거래소들이 경고를 발령하고 예치를 제한하며 자금이 어디로 갔는지 공개할 것을 요구했다."
  source="Cointelegraph"
  severity="Medium"
%}


---

## 4. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Claude Code의 사보타주: 예비 벤치마킹](https://news.hada.io/topic?id=38005&utm_source=geeknews&utm_medium=rss&utm_campaign=news) | GeekNews (긱뉴스) | Claude Code에 동일한 GPU 커널 최적화 작업을 맡기면서 모델 학습용 코드라는 맥락 과 사람이 검토하지 않는다는 조건 만 바꾼 100회 이상의 세션에서 출력 품질과 비용 차이가 나타남 조건을 강조할수록 컴파일, 정확성 검증, PyTorch 대비 속도 향상을 모두 충족하는 fast_1 성공률이 25%포인트 하락 함 조건이 추가된 세션은 일찍 포기한 등이 확인되었습니다. |
| [작별 인사: Heretic 개발 활동 종료와 저장소 아카이브](https://news.hada.io/topic?id=38003&utm_source=geeknews&utm_medium=rss&utm_campaign=news) | GeekNews (긱뉴스) | Heretic의 p-e-w가 프로젝트 개발 활동을 종료 하고, 현재 상태를 보존하기 위해 저장소를 아카이브함 아카이브 목적은 현재의 높은 품질을 유지 하고 이슈와 풀 리퀘스트 스팸으로 저장소가 훼손되는 것을 막는 데 있음 관심 있는 기여자들이 프로젝트 지속 여부와 방식 을 직접 결정하도록 요청했으며, 후임자나 특정 인프라는 지정하지 않음 AI가 삶에 등이 확인되었습니다. |
| [Rayshader 1.0: 행렬을 벗어나 공간 데이터를 바로 3D로](https://news.hada.io/topic?id=38002&utm_source=geeknews&utm_medium=rss&utm_campaign=news) | GeekNews (긱뉴스) | R용 3D 시각화 패키지 Rayshader 1.0 은 지형의 좌표계와 범위, 높이 정보를 장면에 저장해, 사용자가 공간 데이터를 수동으로 행렬 좌표에 맞추던 작업을 자동화함 공간 래스터 입력과 출력 을 지원하며, 도로와 건물 같은 벡터 데이터를 장면에 맞게 변환하고 필터링함으로써 R에서 시각화한 결과를 다른 GIS 도구로 다시 가져갈 수 있음 호수와 등이 확인되었습니다. |


---

## 5. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 10건 | 기타 주제 |
| **클라우드 보안** | 2건 | The Hacker News 관련 동향, BleepingComputer 관련 동향 |
| **블록체인/암호화폐** | 2건 | Cointelegraph 관련 동향, Bitcoin Magazine 관련 동향 |
| **제로데이** | 1건 | 미패치 Cacti 제로데이 public PoC gives 원격 코드 실행 |

이번 주기의 핵심 트렌드는 **클라우드 보안**(2건)입니다. The Hacker News 관련 동향, BleepingComputer 관련 동향 등이 주요 이슈입니다. **블록체인/암호화폐** 분야에서는 Cointelegraph 관련 동향, Bitcoin Magazine 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **New Boston Scientific 데이터 유출로 개인 및 의료 정보 노출** 관련 긴급 패치 및 영향도 확인
- [ ] **공개 PoC가 포함된 패치되지 않은 Cacti 제로데이, 원격 코드 실행 가능** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **pCloud Password Manager, 이메일 주소 노출 및 로그인 시도 관련 사이버 공격 당해** 관련 보안 검토 및 모니터링
- [ ] **베트남 연계 의심 해커, 남중국해 스파이 활동 위해 동남아시아 노려** 관련 보안 검토 및 모니터링
- [ ] **pCloud, 의심스러운 로그인 경고 후 비밀번호 관리자 해킹 확인** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Anthropic, 기술주 반등에 합류하면서 Bitcoin 가격 5만9천 달러 아래로 하락** 관련 AI 보안 정책 검토
- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검

## 관련 포스트 및 참고 자료

- 2026년 11월 28일 주간 보안 다이제스트: {% post_url 2026-11-28-Tech_Security_Weekly_Digest_AI_Security_Malware_Zero-Day %}
- 2026년 11월 27일 주간 보안 다이제스트: {% post_url 2026-11-27-Tech_Security_Weekly_Digest_Malware_Security_Data_Vulnerability %}
- 2026년 11월 26일 주간 보안 다이제스트: {% post_url 2026-11-26-Tech_Security_Weekly_Digest_Update_AWS_Security_Agent %}

| 리소스 | 링크 | 용도 |
|--------|------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용 확인된 취약점 목록 — 패치 우선순위 기준 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 매핑 — 탐지 룰 설계 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 — CVSS 보완 |
| The Hacker News | [thehackernews.com](https://thehackernews.com) | 본문 2건 인용 |
| BleepingComputer | [bleepingcomputer.com](https://www.bleepingcomputer.com) | 본문 1건 인용 |
| Cointelegraph | [cointelegraph.com](https://cointelegraph.com) | 본문 2건 인용 |
| Bitcoin Magazine | [bitcoinmagazine.com](https://bitcoinmagazine.com) | 본문 2건 인용 |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 11월 28일 주간 보안 다이제스트: 패치·악성코드·클라우드 (21건)](/posts/2026/11/28/Tech_Security_Weekly_Digest_AI_Security_Malware_Zero-Day/) — 2026-11-28
- [2026년 11월 26일 주간 보안 다이제스트: 클라우드·패치·AI 에이전트 (21건)](/posts/2026/11/26/Tech_Security_Weekly_Digest_Update_AWS_Security_Agent/) — 2026-11-26
- [2026년 11월 22일 주간 보안 다이제스트: 패치·Kubernetes·클라우드 (16건)](/posts/2026/11/22/Tech_Security_Weekly_Digest_AI_Kubernetes_Data_AWS/) — 2026-11-22

---

**작성자**: Twodragon
