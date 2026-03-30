---

layout: post
title: "OpenAI Codex 보안 스캔, Claude Firefox 취약점, USDC 동향"
date: 2026-03-08 12:33:37 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Security]
keywords: [Security-Weekly,  DevSecOps,  Cloud-Security,  Weekly-Digest,  2026,  AI,  Security]
excerpt: "OpenAI Codex 보안 스캔 도입, Firefox 148 취약점 14건 패치, USDC 스테이블코인 동향 이슈를 중심으로 공격 경로·영향 자산·탐지 포인트를 기술 관점에서 정리하고, 경영진이 즉시 판단할 우선순위·서비스 영향·대응 체크리스트를 함께 제시한 주간 다이제스트입니다."
description: "[High] 애플리케이션 보안 - AI 스캔 결과를 기존 SAST와 교차 검증 필요. [High] Firefox 148 업데이트 필수(14건 High 취약점 수정). 2026년 03월 08일 보안 뉴스 12건. DevSecOps 실무 위협 분석 가이드."
author: Twodragon
comments: true
image: /assets/images/2026-03-08-Tech_Security_Weekly_Digest_AI_Security.svg
image_alt: "Tech Security Weekly Digest March 08 2026 AI Security"
toc: true
---
{% include ai-summary-card.html
  title='OpenAI Codex 보안 스캔, Claude Firefox 취약점, USDC 동향'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">2026</span> <span class="tag">AI</span> <span class="tag">Security</span>'
  highlights_html='<li><strong>AI 보안 스캔</strong>: OpenAI Codex Security가 120만 커밋에서 10,561건 취약점 탐지, Anthropic Claude가 Firefox 22개 취약점 발견</li>
      <li><strong>블록체인</strong>: USDC 스테이블코인 전송량 $1.8T 돌파, Go 표준 라이브러리 UUID 패키지 추가 제안</li>
      <li><strong>실무 권장</strong>: 영향 범위와 우선순위를 점검하고 운영 절차를 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-03-08 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

---

## 경영진 브리핑

- AI 기반 코드/브라우저 보안 분석 도구의 실전 성과가 확인되면서 기존 SAST와 병행 운영하는 하이브리드 보안 전략이 중요해졌습니다.
- 단기적으로는 AI 보안 도구 도입 기준 정리, 오탐 관리 프로세스 수립, 고위험 레포 우선 적용이 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 애플리케이션 보안 | High | AI 스캔 결과를 기존 SAST와 교차 검증 |
| 브라우저/클라이언트 | Medium | 취약점 공개 항목 기반 패치 우선순위 조정 |
| AI 도구 거버넌스 | Medium | 오탐 처리·승인 절차와 책임자 정의 |

## 서론

안녕하세요, Twodragon입니다.

2026년 03월 08일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

수집 통계:
- 총 뉴스 수: 8개
- 보안 뉴스: 2개
- AI/Tech 뉴스: 3개
- 클라우드 뉴스: 0개
- DevOps 뉴스: 0개
- 블록체인 뉴스: 3개

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 Security | The Hacker News | [보안] OpenAI Codex Security, 120만 커밋 스캔해 10,561건 취약점 발견 | 🟡 Medium |
| 🔒 Security | The Hacker News | [보안] Anthropic, Claude Opus 4.6로 Firefox 취약점 22건 발견 | 🟡 Medium |
| ⛓️ Blockchain | Cointelegraph | [블록체인] 예측 시장 Kalshi, 하메네이 거래 면제 조항으로 소송 피소 | 🟡 Medium |
| ⛓️ Blockchain | Cointelegraph | [블록체인] Kalshi·Polymarket, 200억 달러 밸류에이션 목표 자금 조달 추진 | 🟡 Medium |
| ⛓️ Blockchain | Cointelegraph | [블록체인] USDC, Tether 제치고 스테이블코인 전송량 1.8조 달러 돌파 | 🟡 Medium |
| 💻 Tech | GeekNews | AI에이전트 도입의 가장 큰 병목은 성능 보다 신뢰(feat. 시간)이다. | 🟡 Medium |
| 💻 Tech | GeekNews | Autoresearch - Karpathy의 자동 연구 프레임워크 | 🟡 Medium |
| 💻 Tech | GeekNews | Go 표준 라이브러리에 UUID 패키지 추가 제안 | 🟡 Medium |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스

### 1.1 [보안] OpenAI Codex Security, 120만 커밋 스캔해 10,561건 취약점 발견

{% include news-card.html title="[보안] OpenAI Codex Security, 120만 커밋 스캔해 10,561건 취약점 발견" url="https://thehackernews.com/2026/03/openai-codex-security-scanned-12.html" image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgzxRjA2uB_r2z4AtvhADiDGrxTc62766WI5jApivjtuLfb2aS2kz9RWk7f9P3Lm7Nj5HH3u-7Etx4-8xr_Y4PflexsuMsAzXjvPoPLSQaSt1O-t4U3yBAnKm4HLm-64dbHDsWF-EXYVMvaMrMnhfbhV_qn2cvwmJE6x-U42aTjGbIOTNOXxpiH3x15C6Ag/s1600/codex.jpg" summary="OpenAI Codex Security - AI 기반 보안 에이전트로 취약점 탐지, 검증, 수정 제안" source="The Hacker News" severity="Medium" %}

#### 요약

OpenAI는 금요일 Codex Security를 공개했습니다. 이는 취약점을 탐지·검증하고 수정안을 제안하는 AI 기반 보안 에이전트입니다. ChatGPT Pro, Enterprise, Business, Edu 고객을 대상으로 Codex 웹을 통해 리서치 프리뷰로 제공되며, 향후 한 달간 무료로 사용할 수 있습니다.

핵심 성과:

- 120만 개 커밋을 대상으로 스캔을 수행하여 10,561건의 보안 취약점을 발견했습니다.
- 기존 정적 분석(SAST) 도구 대비 컨텍스트 이해 기반의 취약점 탐지가 가능하여, 단순 패턴 매칭을 넘어 비즈니스 로직 취약점까지 식별합니다.
- 탐지된 취약점에 대한 자동 수정 제안(Auto-fix) 기능을 제공하여, 개발자가 즉시 패치를 적용할 수 있습니다.

AI 기반 보안 스캔의 의미:

기존 SAST 도구(SonarQube, Semgrep, CodeQL 등)는 사전 정의된 규칙 기반으로 작동하여, 새로운 유형의 취약점이나 복잡한 데이터 흐름을 놓치는 경우가 많았습니다. Codex Security는 LLM의 코드 이해 능력을 활용해 "이 함수가 왜 위험한지"를 맥락적으로 판단합니다. 다만, AI 기반 도구의 오탐률(False Positive Rate)과 실제 탐지 정확도에 대한 독립적 벤치마크가 아직 부족하므로, 기존 SAST 도구의 보완 용도로 활용하는 것이 권장됩니다.

실무 포인트: CI/CD 파이프라인에 AI 기반 보안 스캔을 기존 SAST 도구와 병행 적용하여 탐지 범위를 확장하세요.


#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | 미공개 또는 해당 없음 |
| 심각도 | Medium |
| 대응 우선순위 | P1 - 7일 이내 검토 권장 |

#### 권장 조치

- 조직 내 SAST/SCA 도구 현황 인벤토리 확인
- Codex Security 리서치 프리뷰 도입 가능성 평가 (무료 기간 활용)
- 기존 보안 스캔 결과와 AI 기반 스캔 결과 비교 분석
- CI/CD 파이프라인에 AI 보안 스캔 단계 추가 검토
- 보안팀 내 AI 보안 도구 동향 공유 및 평가 기준 마련


---

### 1.2 [보안] Anthropic, Claude Opus 4.6로 Firefox 취약점 22건 발견

{% include news-card.html title="[보안] Anthropic, Claude Opus 4.6로 Firefox 취약점 22건 발견" url="https://thehackernews.com/2026/03/anthropic-finds-22-firefox.html" image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg2DaQuy20IkM7M8iL7NBmzJhI9m5KDEpf6CBgxcI9rAhiVLO1VyfdAeQKaInOY3dlIiwy1FWtusinpu8Yyj1fChemLiVCTLnMLRtKaKNvDbOOa0ZjVFt5zoT7yON1ljb2DAlgki_aVmVuWSmAPn2jFszCpJdjzN7DGGRzeEzD5OYcSn2oeLzcaBARYzmOS/s1600/firefox-claude.jpg" summary="Anthropic이 Mozilla와 보안 파트너십으로 Firefox에서 22개 보안 취약점 발견 (14개 High)" source="The Hacker News" severity="High" %}

#### 요약

Anthropic은 Mozilla와의 보안 파트너십 일환으로 Firefox 웹 브라우저에서 22개의 신규 보안 취약점을 발견했다고 밝혔습니다. 이 중 14건은 High(높음), 7건은 Moderate(보통), 1건은 Low(낮음) 등급으로 분류됐으며, 해당 취약점들은 지난달 말 출시된 Firefox 148에서 모두 수정됐습니다.

AI 기반 보안 연구의 새로운 패러다임:

이번 발견은 AI가 대규모 C/C++ 코드베이스에서 인간 연구자가 놓칠 수 있는 취약점을 체계적으로 찾아낼 수 있음을 입증한 사례입니다. Firefox는 수천만 줄의 코드로 구성된 복잡한 프로젝트로, 전통적인 수동 코드 리뷰만으로는 모든 보안 문제를 발견하기 어렵습니다.

주요 취약점 유형:

- 메모리 안전성 문제 (Use-after-free, Buffer overflow): C/C++ 코드에서 가장 흔한 유형으로, 14건의 High 등급 취약점 다수가 이 범주에 해당합니다.
- 로직 오류: 특정 조건에서만 발현되는 비정상 동작으로, 기존 퍼징(fuzzing) 도구로는 발견하기 어려운 유형입니다.
- 권한 상승 가능성: 브라우저 샌드박스를 우회할 수 있는 잠재적 경로가 포함됩니다.

OpenAI Codex Security와의 시너지:

같은 날 공개된 OpenAI Codex Security(1.1절)와 함께 보면, AI 기반 보안 도구 생태계가 빠르게 성숙하고 있음을 알 수 있습니다. OpenAI는 코드 커밋 단계의 취약점 탐지에, Anthropic은 대규모 코드베이스의 심층 보안 연구에 각각 강점을 보입니다.

실무 포인트: Firefox 148로 업데이트하고, 조직 내 브라우저 버전 관리 정책을 점검하세요.


#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | Firefox 148 보안 업데이트로 수정 (개별 CVE 미공개) |
| 심각도 | High (14건), Moderate (7건), Low (1건) |
| 대응 우선순위 | P1 - 7일 이내 Firefox 업데이트 적용 |

#### MITRE ATT&CK 매핑

- T1189 (Drive-by Compromise)
- T1203 (Exploitation for Client Execution)

#### 권장 조치

- 조직 내 Firefox 브라우저 버전 현황 확인 및 148 이상으로 업데이트
- 브라우저 자동 업데이트 정책 활성화 여부 점검
- 브라우저 샌드박스 설정 강화 검토
- 보안팀 내 AI 기반 취약점 연구 동향 공유
- 유사한 AI 보안 연구 결과 모니터링 체계 구축


---

![Blockchain Web3 News Section Banner](/assets/images/section-blockchain.svg)

## 2. 블록체인 뉴스

### 2.1 [블록체인] 예측 시장 Kalshi, 하메네이 거래 면제 조항으로 소송 피소

{% include news-card.html title="[블록체인] 예측 시장 Kalshi, 하메네이 거래 면제 조항으로 소송 피소" url="https://cointelegraph.com/news/kalshi-sued-khamenei-trade-carveout" image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-02/019c6e96-85c8-7884-9654-dc0171468534.jpg" summary="예측 시장 Kalshi의 Khamenei 거래 면제 조항에 대한 소송" source="Cointelegraph" severity="Medium" %}

#### 요약

원고 측은 전 이란 최고지도자의 축출을 다루는 예측 시장에서 사망 관련 면제 조항을 "기만적"이라고 규정했습니다. 이 소송은 블록체인 기반 예측 시장의 법적 경계와 규제 범위에 대한 중요한 선례를 만들 수 있습니다.

실무 포인트: 예측 시장 관련 스마트 컨트랙트의 법적 리스크와 규제 동향을 모니터링하세요.

#### 실무 적용 포인트

- 예측 시장 프로토콜의 법적 리스크 평가 및 컴플라이언스 검토
- 관련 DeFi 프로토콜 스마트 컨트랙트 감사 결과 확인
- 규제 변화에 따른 서비스 영향도 분석


---

### 2.2 [블록체인] Kalshi·Polymarket, 200억 달러 밸류에이션 목표 자금 조달 추진

{% include news-card.html title="[블록체인] Kalshi·Polymarket, 200억 달러 밸류에이션 목표 자금 조달 추진" url="https://cointelegraph.com/news/kalshi-polymarket-20b-valuation-fundraising-wsj" image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-03/019cc81b-97fc-7395-95eb-9812def8889f.jpg" summary="예측 시장 Kalshi, Polymarket이 200억달러 밸류에이션 목표 자금 조달 추진" source="Cointelegraph" severity="Medium" %}

#### 요약

미국과 이스라엘의 이란 공격을 둘러싼 Polymarket 베팅의 수상한 타이밍이 내부자 거래 우려를 낳으면서, 의원들이 예측 시장에 대한 새로운 규제를 추진하고 있습니다. Kalshi와 Polymarket은 이런 논란에도 불구하고 200억 달러 밸류에이션을 목표로 자금 조달을 추진 중이며, 이는 예측 시장의 성장세와 규제 리스크가 동시에 커지고 있음을 보여줍니다.

실무 포인트: 예측 시장 플랫폼 이용 시 내부자 거래 모니터링 및 규제 리스크를 점검하세요.

#### 실무 적용 포인트

- 예측 시장 플랫폼의 이상 거래 탐지 체계 확인
- 내부자 거래 방지를 위한 거래 모니터링 강화
- 관련 규제 변화에 따른 서비스 운영 리스크 평가


---

### 2.3 [블록체인] USDC, Tether 제치고 스테이블코인 전송량 1.8조 달러 돌파

{% include news-card.html title="[블록체인] USDC, Tether 제치고 스테이블코인 전송량 1.8조 달러 돌파" url="https://cointelegraph.com/news/usdc-beats-tether-stablecoin-transfer-volume-1-8-trillion-all-time-high" image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-01/019c0d4e-b508-75a6-9e53-3b5366fbcc6c.jpg" summary="스테이블코인 월간 거래량 1.8조 달러 사상 최고치, USDC가 70% 차지" source="Cointelegraph" severity="Medium" %}

#### 요약

2월 스테이블코인 월간 거래량이 1.8조 달러로 사상 최고치를 기록했습니다. USDC가 전체 거래량의 70%를 차지하며 분석가들의 예상을 뒤엎었습니다. 이는 규제 준수 스테이블코인(USDC)이 비규제 스테이블코인(USDT)을 거래량에서 압도하기 시작했다는 신호로, 기관 투자자들의 규제 친화적 자산 선호가 반영된 결과입니다.

보안 관점:

- 대규모 스테이블코인 전송량 증가에 따라, 스마트 컨트랙트 취약점 공격의 잠재적 피해 규모도 비례하여 증가합니다.
- USDC의 기관 채택 확대는 기업 재무 시스템과 블록체인 인프라 간 연결 지점(브릿지)의 보안이 더욱 중요해짐을 의미합니다.

실무 포인트: 스테이블코인 관련 자금 흐름 모니터링을 강화하고, AML 정책을 점검하세요.

#### 실무 적용 포인트

- 스테이블코인 관련 AML/CFT 정책 점검 및 모니터링 강화
- USDC 연동 시스템의 스마트 컨트랙트 보안 감사 확인
- 대규모 전송 이상 탐지 체계 구축


---

![AI ML News Section Banner](/assets/images/section-ai-ml.svg)

## 3. AI/Tech 뉴스

### 3.1 AI 에이전트 도입의 병목은 성능보다 신뢰

{% include news-card.html
  title="AI 에이전트 도입의 가장 큰 병목은 성능보다 신뢰(feat. 시간)"
  url="https://news.hada.io/topic?id=27301"
  image="https://social.news.hada.io/topic/27301"
  summary="AI 에이전트 도입의 가장 큰 병목은 성능보다 신뢰를 기준으로 기술적으로는 공격 벡터·영향 범위·탐지 지표를 요약하고, 운영 측면에서는 우선 대응 순서와 의사결정 체크포인트를 함께 정리했습니다."
  source="GeekNews"
  severity="Medium"
%}

#### 요약

Anthropic이 수백만 건의 Claude Code 상호작용 데이터를 분석한 결과, AI 에이전트 도입의 핵심 병목은 모델 성능이 아니라 사용자가 에이전트를 신뢰하기까지 걸리는 시간이라는 사실을 확인했습니다. 사용자들은 처음에 단순 작업만 맡기다가, 에이전트가 일관되게 올바른 결과를 제공하는 것을 확인한 후에야 점차 복잡한 작업을 위임합니다.

DevSecOps 시사점:

- 보안 도구에서도 동일한 패턴이 관찰됩니다. AI 기반 SAST/DAST 도구의 오탐률이 높으면 팀이 경고를 무시하게 되고, 이는 실제 취약점도 놓치게 만듭니다.
- 에이전트 신뢰 구축을 위해 감사 로그, 설명 가능한 결과, 점진적 권한 확장 전략이 필요합니다.

#### 실무 적용 포인트

- AI 에이전트 도입 시 단계적 권한 확장 전략 수립
- 에이전트 작업 결과에 대한 감사 로그 및 설명 가능성 확보
- 팀 내 AI 도구 신뢰도 측정 기준 마련


---

### 3.2 Autoresearch - Karpathy의 자율 연구 프레임워크

{% include news-card.html
  title="Autoresearch - Karpathy의 자동 연구 프레임워크"
  url="https://news.hada.io/topic?id=27300"
  image="https://social.news.hada.io/topic/27300"
  summary="Autoresearch - Karpathy의 자동 연구 프레임워크를 기준으로 기술적으로는 공격 벡터·영향 범위·탐지 지표를 요약하고, 운영 측면에서는 우선 대응 순서와 의사결정 체크포인트를 함께 정리했습니다."
  source="GeekNews"
  severity="Medium"
%}

#### 요약

Andrej Karpathy가 공개한 Autoresearch는 LLM 학습의 핵심을 단일 GPU·단일 파일 630줄로 압축한 자기완결형 연구 프레임워크입니다. AI 에이전트가 밤새 실험을 반복하고 인간은 프롬프트만 수정하는 방식으로, 연구 자동화의 새로운 패러다임을 제시합니다.

보안 연구 적용 가능성:

- 퍼징(fuzzing) 캠페인 자동화: 에이전트가 퍼징 결과를 분석하고 새로운 시드를 생성하여 반복 실행
- 취약점 패턴 학습: 발견된 취약점 데이터를 기반으로 유사 패턴을 자동 탐색
- 보안 정책 최적화: 다양한 보안 설정 조합을 자동으로 테스트하여 최적 구성 탐색

#### 실무 적용 포인트

- 반복적 보안 테스트 자동화에 Autoresearch 패턴 적용 검토
- AI 기반 연구 자동화의 보안 위험(의도치 않은 외부 접근 등) 평가
- 자율 에이전트 실행 환경의 네트워크 격리 정책 수립


---

### 3.3 Go 표준 라이브러리에 UUID 패키지 추가 제안

{% include news-card.html
  title="Go 표준 라이브러리에 UUID 패키지 추가 제안"
  url="https://news.hada.io/topic?id=27299"
  image="https://social.news.hada.io/topic/27299"
  summary="Go 표준 라이브러리에 UUID 패키지 추가 제안를 기준으로 기술적으로는 공격 벡터·영향 범위·탐지 지표를 요약하고, 운영 측면에서는 우선 대응 순서와 의사결정 체크포인트를 함께 정리했습니다."
  source="GeekNews"
  severity="Medium"
%}

#### 요약

Go 언어에 UUID 생성·파싱 기능을 표준 라이브러리(`unique/uuid`)로 추가하자는 제안이 논의 중입니다. 현재 대부분의 Go 프로젝트가 `google/uuid`나 `gofrs/uuid` 같은 외부 패키지에 의존하고 있어, 표준화가 공급망 보안 측면에서도 긍정적입니다.

보안 관점:

- 외부 의존성 감소는 공급망 공격 표면을 줄이는 효과가 있습니다. UUID는 거의 모든 프로젝트에서 사용되므로, 표준 라이브러리 포함 시 수백만 개 프로젝트의 외부 의존성이 한 단계 줄어듭니다.
- UUID v7(시간 기반 정렬)의 표준 구현은 데이터베이스 성능 최적화와 분산 시스템 추적에 유용합니다.

#### 실무 적용 포인트

- Go 프로젝트의 UUID 외부 패키지 의존성 점검
- 표준 라이브러리 포함 시 마이그레이션 계획 수립
- 공급망 보안 관점에서 외부 패키지 의존성 최소화 전략 검토


---


## 4. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| AI 보안 도구 | 2건 | AI 기반 취약점 자동 탐지, 대규모 코드 스캔, 브라우저 보안 취약점 발견 |
| 블록체인 규제·성장 | 3건 | 스테이블코인 전송량 최고치, 예측 시장 밸류에이션, 규제 명확성 |
| AI 에이전트 생태계 | 3건 | 에이전트 신뢰 구축 병목, 자율 연구 자동화, 표준 라이브러리 공급망 보안 |

이번 주기의 핵심 인사이트:

이번 주 뉴스는 **AI가 보안의 양면에서 동시에 작용**하고 있음을 보여줍니다. OpenAI Codex Security(120만 커밋, 10,561건 취약점)와 Anthropic Claude(Firefox 22건 취약점)는 AI가 방어 측 무기로서 실전에 쓸 만한 수준에 도달했음을 입증합니다. 동시에, Anthropic의 Claude Code 분석 결과가 보여주듯 AI 에이전트 도입의 핵심 병목은 기술 성능이 아니라 신뢰 구축입니다.

블록체인 영역에서는 USDC가 전송량의 70%를 차지하며 $1.8T를 돌파한 것이 주목됩니다. 이는 규제 준수 스테이블코인이 기관 투자자의 선택을 받고 있다는 신호로, 보안 및 컴플라이언스 관점에서 스테이블코인 인프라의 중요성이 급격히 커지고 있습니다. 예측 시장의 규제 논란(Kalshi 소송, Polymarket 내부자 거래 의혹)은 블록체인 기반 금융 서비스의 법적 경계가 아직 불확실함을 보여줍니다.

---

## 실무 체크리스트

### P0 (즉시)

- Firefox 브라우저 148 이상으로 업데이트 (14건 High 취약점 수정)
- AI 기반 보안 스캔 도구(Codex Security) 평가 및 파일럿 도입 검토

### P1 (7일 내)

- CI/CD 파이프라인에 AI 보안 스캔 단계 추가 검토
- 조직 내 AI 에이전트 도입 현황 파악 및 권한 감사
- 스테이블코인 관련 AML/CFT 정책 점검

### P2 (30일 내)

- AI 에이전트 신뢰 구축을 위한 단계적 도입 전략 수립
- Go 프로젝트 외부 UUID 패키지 의존성 검토 및 공급망 보안 점검
- 예측 시장 관련 규제 동향 모니터링 체계 마련

---


---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |
| OWASP Top 10 for LLM | [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| NIST AI RMF | [NIST AI RMF](https://www.nist.gov/system/files/documents/2023/01/26/AI-RMF-001.pdf) |

---

작성자: Twodragon
