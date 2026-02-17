---
author: Yongho Ha
categories:
- kubernetes
category: kubernetes
certifications:
- ckad
- cka
comments: true
date: 2025-06-06 19:45:40 +0900
description: CI/CD 파이프라인 보안(GitHub Actions, SAST/DAST, Secret 스캐닝), Kubernetes 클러스터
  보안(RBAC, Pod Security Standards, Network Policy), 이미지 서명, 런타임 보안까지 정리.
excerpt: CI/CD 파이프라인 보안 및 Kubernetes 클러스터 보안 실전 가이드
image: /assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide.svg
image_alt: 'Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical
  Guide'
keywords:
- CI/CD
- Kubernetes
- Security
- DevSecOps
- GitOps
- Pipeline-Security
layout: post
original_url: https://twodragon.tistory.com/689
schema_type: Article
tags:
- CI/CD
- Kubernetes
- Security
- DevSecOps
- GitOps
- Pipeline-Security
title: '클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드'
toc: true
---

## 요약

- **핵심 요약**: CI/CD 파이프라인 보안 및 Kubernetes 클러스터 보안 실전 가이드
- **주요 주제**: 클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드
- **키워드**: CI/CD, Kubernetes, Security, DevSecOps, GitOps

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag devops">Kubernetes</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">CI/CD</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Security</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">GitOps</span>
      <span class="tag">Pipeline-Security</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>CI/CD 파이프라인 보안</strong>: GitHub Actions 보안 설정(permissions 최소화, Secret 관리), SAST/DAST 통합(Semgrep, SonarQube, Gitleaks, Trivy, OWASP ZAP), Secret 스캐닝, 의존성 취약점 스캔</li>
      <li><strong>Kubernetes 클러스터 보안</strong>: RBAC(Role, RoleBinding, ClusterRole, ClusterRoleBinding), Pod Security Standards(Restricted/Baseline/Privileged), Network Policy(트래픽 제어, 네임스페이스 격리), Service Account 최소 권한</li>
      <li><strong>이미지 서명 및 Secret 관리</strong>: Cosign 이미지 서명, Kubernetes Secrets 관리, External Secrets Operator, Sealed Secrets, Vault 통합</li>
      <li><strong>런타임 보안</strong>: Kyverno 정책 엔진(Admission Control, Policy as Code), Falco 이상 행위 탐지, GitOps 보안 모범 사례(ArgoCD, Flux), 실무 적용 체크리스트</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Kubernetes, GitHub Actions, Kyverno, Falco, Cosign</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">클라우드 보안 전문가, DevOps 엔지니어, 보안 담당자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

<img src="{{ '/assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide_image.png' | relative_url }}" alt="Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical Guide" loading="lazy" class="post-image">

## 서론

안녕하세요, **Twodragon**입니다. 이번 포스팅에서는 컨테이너 및 Kubernetes 보안에 대해 실무 중심으로 정리합니다.

2025년 Docker와 Kubernetes는 여전히 클라우드 네이티브 애플리케이션의 핵심 기술이며, 보안은 더욱 중요해지고 있습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- 클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드의 핵심 내용 및 실무 적용 방법
- 2025-2026년 최신 트렌드 및 업데이트 사항
- 실전 사례 및 문제 해결 방법
- 보안 모범 사례 및 권장 사항

## 1. CI/CD 파이프라인 보안 기초

<figure>
<img src="{{ '/assets/images/diagrams/diagram_devsecops_pipeline.png' | relative_url }}" alt="DevSecOps CI/CD Pipeline Architecture" loading="lazy" class="post-image">
<figcaption>DevSecOps CI/CD 파이프라인 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

### 1.1 CI/CD 보안의 중요성

### 1.2 GitHub Actions 보안 설정

> **참고**: GitHub Actions 보안 설정 관련 내용은 [GitHub Actions 보안 가이드](https://docs.github.com/en/actions) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.

<!-- 전체 코드는 위 GitHub 링크 참조 -->
<!-- 전체 코드는 위 GitHub 링크 참조 -->

## 2. Kubernetes RBAC 보안

<figure>
<img src="{{ '/assets/images/diagrams/diagram_k8s_security.png' | relative_url }}" alt="Kubernetes Security Architecture" loading="lazy" class="post-image">
<figcaption>Kubernetes 보안 아키텍처 - Python diagrams로 생성</figcaption></figure>

### 2.1 최소 권한 원칙 적용

> **참고**: Kubernetes RBAC 및 최소 권한 원칙 관련 내용은 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) 및 [Kubernetes 보안 모범 사례](https://kubernetes.io/docs/concepts/security/)를 참조하세요.
>
> ```yaml
> # 개발자용 제한된 Role...
> ```

<!-- 전체 코드는 위 링크 참조
> **참고**: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions)를 참조하세요./oidc-deploy.yml...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

---
