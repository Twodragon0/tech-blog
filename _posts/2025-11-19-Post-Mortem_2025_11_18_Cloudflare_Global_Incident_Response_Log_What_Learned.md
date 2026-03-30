---

author: Twodragon
categories:
- incident
comments: true
date: 2025-11-19 12:25:20 +0900
description: 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지. Multi-CDN 전략 및 자동 Failover 구현
  방안을 다룹니다.
excerpt: "2025년 11월 18일 Cloudflare 글로벌 장애 실시간 대응 일지. 장애 발생 타임라인, 원인 분석, 서비스 영향 범위 파악, Multi-CDN 전환 전략, 자동 Failover 구현 방법, 재발 방지를 위한 인프라 복원력 설계까지 SRE 관점에서 정리합니다."
image: /assets/images/2025-11-19-Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_what_Learned.svg
image_alt: 'Post-Mortem November 18 2025 Cloudflare Global Incident Response Log: What We'
layout: post
original_url: https://twodragon.tistory.com/699
tags:
- Cloudflare
- Post-Mortem
- Incident-Response
- CDN
- Network
- SRE
keywords: [Cloudflare, Post-Mortem, Incident-Response, CDN, Network, SRE]
title: '[Post-Mortem] 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지'
toc: true
---
{%- include ai-summary-card.html
  title='[Post-Mortem] 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지'
  categories_html='<span class="category-tag security">Incident</span>'
  tags_html='<span class="tag">Cloudflare</span>
      <span class="tag">Post-Mortem</span>
      <span class="tag">Incident-Response</span>
      <span class="tag">CDN</span>
      <span class="tag">Network</span>
      <span class="tag">SRE</span>'
  highlights_html='<li>Cloudflare 글로벌 네트워크 장애 대응 및 분석</li>
      <li>모바일과 PC 환경에서 나타난 상이한 증상 분석</li>
      <li>Multi-CDN 전략 및 자동 Failover 구현 방안</li>
      <li>2025년 Cloudflare 보안 업데이트: Post-Quantum Encryption, DDoS 위협 동향</li>'
  audience='SRE, 인시던트 대응 담당자, 운영 엔지니어'
-%}

### 사고 대응 체크리스트

- 영향 범위 및 심각도 평가 완료
- 긴급 패치 또는 완화 조치 적용
- 근본 원인 분석 (RCA) 수행
- 재발 방지 대책 수립
- 사후 보고서 작성 및 공유

## Executive Summary

> **경영진 브리핑**: 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지. Multi-CDN 전략 및 자동 Failover 구현

### 위험도 평가

| 항목 | 위험도 | 설명 |
|------|--------|------|
| 전체 위험도 | 🔴 높음 | 즉시 대응 및 패치 적용 필요 |

<img src="{{ '/assets/images/2025-11-19-Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_what_Learned_image.png' | relative_url }}" alt="Post-Mortem November 18 2025 Cloudflare Global Incident Response Log: What We Learned" loading="lazy" class="post-image">

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 경영진 요약

### 인시던트 심각도 평가

| 평가 지표 | 등급 | 상세 |
|---------|------|------|
| 심각도 | P1 (Critical) | 전체 서비스 영향 |
| 비즈니스 영향 | High | 매출 손실 + 브랜드 신뢰도 하락 |
| 사용자 영향 | 100% (모바일), 60% (PC) | 전체 사용자 대상 |
| 복구 시간 | 90분 | RTO 목표 대비 지연 |
| 데이터 손실 | None | 데이터 무결성 유지 |

### 비즈니스 영향 분석

직접 비용:
- 매출 손실: 약 1.5시간 × 시간당 평균 매출
- 고객 보상: SLA 위반에 따른 크레딧 지급
- 인건비: 긴급 대응 인력 투입 (엔지니어 5명 × 2시간)

간접 비용:
- 브랜드 신뢰도 저하
- 고객 이탈 가능성 증가
- 향후 계약 협상 시 불리한 위치

대응 조치:
- Multi-CDN 전략 수립 (1개월 내 구현)
- 자동 Failover 시스템 도입
- 모니터링 강화 및 알림 체계 개선

### 주요 교훈

1. 단일 장애점(SPOF) 제거: CDN 단일 의존도 제거
2. 모바일 환경 특성 이해: DNS 캐시 동작 차이 고려
3. 자동화된 Failover: 수동 대응의 한계 극복
4. 다중 모니터링: 외부 의존성 모니터링 강화

## 서론

안녕하세요, Twodragon입니다. 이번 포스팅에서는 클라우드 인프라 장애 대응에 대해 실무 중심으로 정리합니다.

2025년 11월 18일 발생한 Cloudflare 글로벌 장애는 분산 시스템 운영의 중요성을 다시 한번 일깨워주었습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- [Post-Mortem] 2025년 11월 18일 Cloudflare 글로벌 장애 대응 일지의 핵심 내용 및 실무 적용 방법
- 2025-2026년 최신 트렌드 및 업데이트 사항
- 실전 사례 및 문제 해결 방법
- 보안 모범 사례 및 권장 사항

## 1. 들어가며

2025년 11월 18일 저녁, 전 세계 수많은 인터넷 서비스를 마비시킨 Cloudflare의 글로벌 네트워크 장애가 발생했습니다. 우리 서비스 역시 예외는 아니었습니다.

이 글은 긴박했던 장애 상황에서 우리 팀이 어떻게 문제를 인지하고 대응했는지, 특히 모바일과 PC 환경에서 나타난 상이한 증상을 어떻게 분석했는지를 기록합니다.

## 빠른 참조

### 인시던트 요약

| 항목 | 내용 |
|------|------|
| 발생 일시 | 2025년 11월 18일 18:30 KST |
| 장애 지속 시간 | 약 1시간 30분 (18:30 ~ 20:00) |
| 영향 범위 | Cloudflare 글로벌 네트워크 장애 |
| 근본 원인 | Cloudflare 인프라 문제 (BGP 라우팅 이슈 추정) |
| 영향 받은 서비스 | 전 세계 수많은 인터넷 서비스 |

### 장애 타임라인

| 시간 (KST) | 이벤트 | 조치 |
|-----------|--------|------|
| 18:30 | 사용자 문의 시작 | - |
| 18:35 | 모니터링 알림 발생 | 1차 조사 시작 |
| 18:40 | 내부 시스템 정상 확인 | 외부 원인 의심 |
| 18:45 | Cloudflare Status 확인 | 장애 공지 없음 |
| 18:50 | SNS에서 글로벌 장애 정보 포착 | 상황 파악 |
| 18:55 | Cloudflare 공식 장애 공지 | 대응 계획 수립 |
| 19:30 | 서비스 정상화 시작 | 모니터링 강화 |
| 20:00 | 완전 복구 | 사후 분석 |

### 모바일 vs PC 환경 증상 차이

| 환경 | 증상 | 원인 | 영향도 |
|------|------|------|--------|
| 모바일 | 완전 접속 불가 | DNS 캐시 짧음 + 모바일 네트워크 특성 | 100% 사용자 |
| PC | 간헐적 접속 가능 | 브라우저 DNS 캐시 + 로컬 DNS 캐시 | 일부 사용자 |

### 대응 방안 및 개선 사항

| 개선 영역 | Before | After | 효과 |
|----------|--------|-------|------|
| Multi-CDN 전략 | Cloudflare 단일 의존 | Cloudflare + AWS CloudFront | 장애 격리 |
| 자동 Failover | 수동 전환 | 자동 Failover 구현 | 빠른 복구 |
| 모니터링 | 기본 모니터링 | 다중 CDN 모니터링 | 조기 탐지 |
| 알림 체계 | 단일 채널 | 다중 채널 (Slack, PagerDuty) | 신속한 알림 |

### 2025년 Cloudflare 보안 업데이트

2025년 Cloudflare는 급변하는 보안 환경에 대응하기 위해 여러 중요한 업데이트를 발표했습니다.

| 업데이트 항목 | 설명 | 적용 시기 |
|-------------|------|----------|
| Post-Quantum Encryption | 양자 내성 암호화 지원 | 2025년 |
| DDoS 위협 대응 | 향상된 DDoS 방어 | 지속적 |
| Zero Trust 네트워크 | Zero Trust 아키텍처 강화 | 2025년 |

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

흥미롭게도, 모바일과 PC 환경에서 다른 증상이 나타났습니다.


Runbook: CDN 장애 대응

> 참고: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요.

![Mermaid Diagram](/assets/images/mermaid/Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned-mermaid-1.svg)

| 명령어 | 동작 | 설명 |
|--------|------|------|
| `./runbook.sh check` | 헬스체크 | Primary/Backup CDN 상태 확인 (HTTP 200 체크, timeout 5s) |
| `./runbook.sh failover` | 전환 | Backup CDN으로 DNS 전환 + Slack 알림 |
| `./runbook.sh rollback` | 복원 | Primary CDN으로 DNS 복원 |

## 4. 교훈 및 개선 사항

### 4.1 Multi-CDN 전략

단일 CDN 의존도를 낮추기 위한 Multi-CDN 아키텍처 도입:

![Mermaid Diagram](/assets/images/mermaid/Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned-mermaid-1.svg)

### 4.2 모니터링 강화

> 참고: Prometheus Alert Rule 설정 관련 내용은 [Prometheus 공식 문서](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) 및 [Awesome Prometheus Alerts](https://github.com/samber/awesome-prometheus-alerts)를 참조하세요.
> ```yaml
> # Prometheus Alert Rule 예시...
> ```
<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

CVSS 10.0 (Critical) 등급의 이 취약점은 원격 코드 실행(RCE)을 가능하게 하며, Cloudflare는 취약점 공개 후 24시간 이내에 전역 보호 규칙을 배포했습니다.

### 4.3 DDoS 위협 동향

2025년 DDoS 공격은 전년 대비 10배 증가했으며, 특히 1Tbps 이상의 Hyper-Volumetric 공격이 급증했습니다.

2. 사이버 보험 검토

추천 보험 커버리지:
- Business Interruption Loss (영업 중단 손실)
- Cyber Extortion (사이버 협박)
- Data Breach Response (데이터 유출 대응)
- Third-Party Service Failure (제3자 서비스 장애) ← 이번 케이스

> 참고: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요. Documentation](https://docs.aws.amazon.com/cloudfront/) - AWS CDN 문서
- [Fastly Documentation](https://docs.fastly.com/) - Fastly CDN 문서
- [Akamai Developer Portal](https://developer.akamai.com/) - Akamai 개발자 포털
- [Multi-CDN Strategy Guide](https://www.cdnplanet.com/guides/multi-cdn/) - Multi-CDN 전략 가이드
- [BGP Best Practices](https://www.rfc-editor.org/rfc/rfc7454.html) - RFC 7454: BGP 모범 사례

SRE & 인시던트 관리:
- [Google SRE Book - Managing Incidents](https://sre.google/sre-book/managing-incidents/) - 구글 SRE 책
- [Google SRE Workbook - Incident Response](https://sre.google/workbook/incident-response/) - SRE 워크북
- [PagerDuty Incident Response Guide](https://response.pagerduty.com/) - PagerDuty IR 가이드
- [Atlassian Incident Management Handbook](https://www.atlassian.com/incident-management/handbook) - Atlassian 핸드북

### 모니터링 & 관찰성

Prometheus & Grafana:
- [Prometheus Documentation](https://prometheus.io/docs/) - Prometheus 공식 문서
- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) - 알림 규칙
- [Awesome Prometheus Alerts](https://github.com/samber/awesome-prometheus-alerts) - 알림 규칙 모음
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/) - 대시보드 템플릿

SIEM & 로그 관리:
- [Splunk Documentation](https://docs.splunk.com/) - Splunk 문서
- [Azure Sentinel Documentation](https://docs.microsoft.com/azure/sentinel/) - Azure Sentinel 문서
- [ELK Stack Guide](https://www.elastic.co/guide/) - Elasticsearch, Logstash, Kibana

### 보안 & 컴플라이언스

MITRE ATT&CK:
- [MITRE ATT&CK Framework](https://attack.mitre.org/) - 공격 기법 프레임워크
- [T1498 - Network Denial of Service](https://attack.mitre.org/techniques/T1498/) - 네트워크 DoS
- [T1499 - Endpoint Denial of Service](https://attack.mitre.org/techniques/T1499/) - 엔드포인트 DoS
- [T1190 - Exploit Public-Facing Application](https://attack.mitre.org/techniques/T1190/) - 공개 애플리케이션 익스플로잇

CVE & 보안 패치:
- [NIST CVE Database](https://nvd.nist.gov/) - CVE 데이터베이스
- [CVE-2025-55182 Details](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-55182) - React 취약점 (예시)
- [Cloudflare WAF Documentation](https://developers.cloudflare.com/waf/) - WAF 규칙 설정

한국 규제:
- [전자금융거래법](https://www.law.go.kr/) - 금융권 장애 보고 의무
- [개인정보보호법](https://www.privacy.go.kr/) - 개인정보 처리시스템 안전성

### 아키텍처 & 베스트 프랙티스

AWS Well-Architected:
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) - AWS 아키텍처 프레임워크
- [Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/) - 안정성 기둥
- [AWS Route 53 Health Checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html) - DNS Failover

기타 아키텍처:
- [12 Factor App](https://12factor.net/) - 클라우드 네이티브 앱 원칙
- [Netflix Chaos Engineering](https://netflix.github.io/chaosmonkey/) - Chaos Monkey
- [Martin Fowler - Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html) - 회로 차단 패턴

### 도구 & 오픈소스

CDN & Failover:
- [Terraform Cloudflare Provider](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs) - IaC로 CDN 관리
- [cdnjs](https://cdnjs.com/) - 오픈소스 CDN
- [Bunny CDN](https://bunny.net/) - 저렴한 대체 CDN

모니터링 도구:
- [Uptime Robot](https://uptimerobot.com/) - 무료 업타임 모니터링
- [Pingdom](https://www.pingdom.com/) - 성능 모니터링
- [StatusCake](https://www.statuscake.com/) - 다중 리전 모니터링

인시던트 관리:
- [Incident.io](https://incident.io/) - 인시던트 관리 플랫폼
- [FireHydrant](https://firehydrant.com/) - 인시던트 대응 자동화
- [Rootly](https://rootly.com/) - Slack 기반 인시던트 관리

### 커뮤니티 & 학습 자료

포럼 & 커뮤니티:
- [Cloudflare Community](https://community.cloudflare.com/) - Cloudflare 커뮤니티
- [SRE Weekly Newsletter](https://sreweekly.com/) - 주간 SRE 뉴스레터
- [r/sre Subreddit](https://www.reddit.com/r/sre/) - SRE 커뮤니티

학습 자료:
- [Coursera - Site Reliability Engineering](https://www.coursera.org/learn/site-reliability-engineering-slos) - SRE 강좌
- [Linux Foundation - SRE Fundamentals](https://training.linuxfoundation.org/training/fundamentals-of-site-reliability-engineering/) - SRE 기초
- [O'Reilly - Building Secure and Reliable Systems](https://sre.google/books/) - 구글 SRE 책

### 블로그 & 기술 아티클

인시던트 Post-Mortem 사례:
- [GitHub Status - Incident History](https://www.githubstatus.com/history) - GitHub 장애 이력
- [Slack Engineering Blog](https://slack.engineering/) - Slack 엔지니어링 블로그
- [Stripe Engineering Blog](https://stripe.com/blog/engineering) - Stripe 기술 블로그

한국어 자료:
- [KISA 한국인터넷진흥원](https://www.kisa.or.kr/) - 보안 가이드
- [NIA 한국지능정보사회진흥원](https://www.nia.or.kr/) - 클라우드 보안
- [한국정보통신기술협회(TTA)](https://www.tta.or.kr/) - 표준 문서

### RFC & 표준

- [RFC 8305 - Happy Eyeballs v2](https://www.rfc-editor.org/rfc/rfc8305.html) - 듀얼 스택 연결 최적화
- [RFC 7454 - BGP Operations and Security](https://www.rfc-editor.org/rfc/rfc7454.html) - BGP 보안
- [RFC 7871 - Client Subnet in DNS Queries](https://www.rfc-editor.org/rfc/rfc7871.html) - EDNS Client Subnet

---

마지막 업데이트: 2025-11-19
작성자: Twodragon
라이선스: CC BY-NC-SA 4.0

