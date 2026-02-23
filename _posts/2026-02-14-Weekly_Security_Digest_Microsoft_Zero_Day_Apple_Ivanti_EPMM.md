---
layout: post
title: "2026년 2월 2주차 보안 위협 종합 분석: Microsoft 6건 Zero-Day, Apple 긴급 패치, Ivanti EPMM 대규모 공격"
date: 2026-02-14 09:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, Zero-Day, Patch-Tuesday, CVE-2026-21510, CVE-2026-20700, Ivanti-EPMM, Ransomware, AI-Security, Supply-Chain, Kubernetes, "2026"]
excerpt: "Microsoft Patch Tuesday 6건 Zero-Day 긴급 패치, Apple CVE-2026-20700 표적 공격, Ivanti EPMM 대규모 익스플로잇, SAP CVSS 9.9 SQL Injection, 랜섬웨어 $74B 피해 전망 등 2026년 2월 2주차 핵심 보안 위협을 심층 분석합니다."
description: "2026년 2월 14일 보안 주간 다이제스트: Microsoft 6건 Zero-Day (CVE-2026-21510, CVE-2026-21513), Apple dyld Zero-Day (CVE-2026-20700), Ivanti EPMM RCE (CVE-2026-1281), SAP SQL Injection (CVE-2026-0488, CVSS 9.9), BeyondTrust Pre-Auth RCE, AI 보안 위협, 랜섬웨어 동향, 블록체인 보안 등 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Zero-Day, Patch-Tuesday, CVE-2026-21510, CVE-2026-20700, Ivanti-EPMM, Ransomware, AI-Security]
author: Twodragon
comments: true
image: /assets/images/2026-02-14-Weekly_Security_Digest_Microsoft_Zero_Day_Apple_Ivanti_EPMM.svg
image_alt: "Weekly Security Digest February 14 2026 Microsoft Zero Day Apple Ivanti EPMM"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='2026년 2월 2주차 보안 위협 종합 분석: Microsoft 6건 Zero-Day, Apple 긴급 패치, Ivanti EPMM 대규모 공격'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">Zero-Day</span> <span class="tag">Patch-Tuesday</span> <span class="tag">CVE-2026-21510</span> <span class="tag">CVE-2026-20700</span>'
  highlights_html='<li><strong>Microsoft Patch Tuesday 6건 Zero-Day</strong>: CVE-2026-21510, CVE-2026-21513 포함 6건의 Zero-Day 긴급 패치 배포, 특권 상승 및 원격 코드 실행 취약점으로 즉각 적용 필요</li>
      <li><strong>Apple dyld Zero-Day (CVE-2026-20700) 표적 공격</strong>: Apple 운영체제 dyld 컴포넌트 Zero-Day가 실제 표적 공격에 악용 중, 긴급 업데이트 배포 및 전 Apple 기기 패치 권고</li>
      <li><strong>Ivanti EPMM RCE 대규모 익스플로잇 및 SAP CVSS 9.9</strong>: Ivanti EPMM CVE-2026-1281 원격 코드 실행 취약점 대규모 악용 확산, SAP SQL Injection CVE-2026-0488(CVSS 9.9) 동시 대응 필요</li>'
  period='2026-02-14 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

