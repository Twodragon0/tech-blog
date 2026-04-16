---

author: Twodragon
categories:
- security
- devsecops
- kubernetes
comments: true
date: 2026-01-22 18:30:00 +0900
description: '클라우드 보안 과정 8기 8주차: CI/CD 파이프라인 보안(Trivy, Snyk, Vault), Kubernetes 네트워크 보안(Network Policies, RBAC), Pod Security Standards, AI 활용 DevSecOps 강화(Cursor, Claude...'
excerpt: "클라우드 보안 과정 8기 8주차: CI/CD 파이프라인 보안(Trivy·Snyk·Vault 통합), Kubernetes 네트워크 보안 정책(Network Policy·RBAC), Pod Security Standards, Cursor·Claude를 활용한 AI 기반 DevSecOps 강화 실습을 다룹니다."
image: /assets/images/2026-01-22-Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide.svg
image_alt: 'Cloud Security Course 8Batch 8Week: CI/CD and Kubernetes Security Practical'
layout: post
original_url: https://twodragon.tistory.com/708
series: "Cloud Security Course 8기"
series_order: 9
series_total: 9
tags:
- CI/CD
- Kubernetes
- DevSecOps
- K8s-Security
- Cloud-Security
- ArgoCD
- Jenkins
- Network-Policies
- RBAC
- Pod-Security-Standards
keywords: [CI/CD, Kubernetes, DevSecOps, K8s-Security, Cloud-Security, ArgoCD, Jenkins, Network-Policies]
title: "클라우드 보안 8기 8주차: CI/CD와 Kubernetes 보안 실전 가이드"
toc: true
---
{%- include ai-summary-card.html
  title='🚀 클라우드 보안 과정 8기 8주차: CI/CD와 Kubernetes 보안 실전 가이드'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span> <span class="category-tag kubernetes">Kubernetes</span>'
  tags_html='<span class="tag">CI/CD</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">K8s-Security</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">ArgoCD</span>
      <span class="tag">Jenkins</span>
      <span class="tag">Network-Policies</span>
      <span class="tag">RBAC</span>
      <span class="tag">Pod-Security-Standards</span>'
  highlights_html='<li><strong>CI/CD 파이프라인 보안</strong>: 코드 스캔(SAST, DAST), 이미지 스캔(Trivy, Snyk), Secret 관리(HashiCorp Vault, AWS Secrets Manager), 파이프라인 무결성 검증(GPG 서명, 자동화된 테스트)</li>
      <li><strong>Kubernetes 네트워크 보안</strong>: Network Policies(Pod 간 통신 제어), Service Mesh(Istio, Linkerd), Ingress Controller 보안, 네트워크 세분화 전략</li>
      <li><strong>Kubernetes 보안 아키텍처</strong>: RBAC 최소 권한 원칙, Pod Security Standards(PSS), 감사 로깅(Kubernetes Audit), 모니터링 및 알림(Prometheus, Grafana)</li>
      <li><strong>AI 활용을 통한 DevSecOps 강화</strong>: Cursor 보안 코딩, Claude API 자동화된 보안 검증, GitHub Copilot 보안 모범 사례, GitHub Actions AI 통합, AI 기반 보안 모니터링</li>
      <li><strong>DevSecOps 통합 전략</strong>: 자동화된 보안 검증(CI/CD 통합), 보안 강화된 파이프라인 구축, 정기적인 보안 감사, 지속적인 보안 모니터링</li>
      <li><strong>실전 보안 사례 및 실습</strong>: 보안 강화된 CI/CD 파이프라인 구축, Kubernetes 보안 환경 구성, 실전 보안 강화 사례</li>'
  audience='보안 엔지니어, DevOps 엔지니어, 클라우드 보안 전문가, DevSecOps 실무자'
-%}

## Executive Summary

> **경영진 브리핑**: 클라우드 보안 과정 8기 8주차: CI/CD 파이프라인 보안(Trivy, Snyk, Vault), Kubernetes 네트워크

### 위험도 평가

| 항목 | 위험도 | 설명 |
|------|--------|------|
| 전체 위험도 | 🟢 낮음 | 교육 목적 실습 환경 중심 |

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 서론

안녕하세요, Twodragon입니다.

지난 7주차에서는 Docker & Kubernetes 보안 실전 가이드를 다루었습니다. 이번 클라우드 보안 과정 8기 8주차에서는 CI/CD와 Kubernetes 보안 실전 가이드를 통해 DevSecOps 파이프라인부터 클러스터 보안까지 실무 중심으로 다루고자 합니다.

특히 이번 주에는 CI/CD 파이프라인 보안과 Kubernetes 클러스터 보안을 통합하여, 실제 서비스 환경에 적용 가능한 보안 전략을 깊이 있게 다뤄보겠습니다.

본 과정은 온라인 미팅으로 진행되며, '20분 강의 + 5분 휴식' 사이클로 멘티분들의 집중력을 최대로 유지하며 진행됩니다.

---

### **📅 8주차 타임테이블 (Agenda)**

| 시간 | 주제 | 내용 |
|------|------|------|
| 10:00 - 10:20 | 근황 토크 & 과제 피드백 | 한 주간의 보안 이슈 공유 및 Q&A |
| 10:25 - 11:00 | Kubernetes 네트워크 및 보안 | Kubernetes 네트워크, Network Policies, RBAC, Pod Security Standards |
| 11:10 - 11:40 | 지속적 통합, 지속적 제공/배포(CI/CD) 및 보안 | CI/CD 파이프라인 보안, 코드 스캔, 이미지 스캔, Secret 관리 |
| 11:45 - 12:00 | AI 활용을 통한 DevSecOps 강화 | Cursor, Claude API, GitHub Copilot 활용 방법, AI 기반 보안 모니터링 |
| 12:05 - 12:10 | 실습 및 Q&A | 보안 강화된 CI/CD 파이프라인 구축, Kubernetes 보안 환경 구성, AI 도구 통합 |

---

## 1. Kubernetes 네트워크 및 보안

Kubernetes 네트워크 보안은 클러스터 보안의 핵심입니다. 네트워크 정책부터 접근 제어까지 다층 방어 전략을 적용해야 합니다.

#### **1.1 Kubernetes 네트워크 기본 개념**

##### **Kubernetes 핵심 오브젝트**

*Kubernetes 핵심 오브젝트: Namespace, Deployment, Service, ConfigMap, Secret, PersistentVolumeClaim, PersistentVolume, HPA*

| 오브젝트 | 설명 | 역할 |
|---------|------|------|
| Namespace | 리소스를 논리적으로 분리하는 가상 클러스터 | 리소스 그룹핑 및 격리 |
| Deployment | Pod의 배포, 업데이트, 스케일링을 관리 | Pod 생명주기 관리 |
| Service | Pod에 대한 안정적인 네트워크 엔드포인트 제공 | Pod 간 통신 및 로드 밸런싱 |
| ConfigMap | 설정 데이터를 저장하는 리소스 | 애플리케이션 설정 관리 |
| Secret | 민감한 데이터를 저장하는 리소스 | 비밀 정보 관리 |
| PersistentVolumeClaim | 스토리지 요청 리소스 | 영구 스토리지 요청 |
| PersistentVolume | 클러스터의 스토리지 리소스 | 영구 스토리지 제공 |
| HPA | Horizontal Pod Autoscaler | 자동 스케일링 |

> 참고: Kubernetes 기본 개념은 [Kubernetes 공식 문서](https://kubernetes.io/docs/concepts/) 및 [Kubernetes GitHub 저장소](https://kubernetes.io/docs/reference/)를 참조하세요.

##### **Kubernetes 네트워크 아키텍처**

![Kubernetes Security Architecture with AI Monitoring](/assets/images/2026-01-22-Kubernetes_Security_Architecture_AI_Monitoring.svg)
*Kubernetes 네트워크 아키텍처: Pod 간 통신, Service를 통한 로드 밸런싱, Ingress를 통한 외부 접근 (AI 모니터링 통합)*

| 구성 요소 | 설명 | 역할 |
|----------|------|------|
| Pod Network | Pod 간 통신을 위한 네트워크 | CNI 플러그인으로 구현 |
| Service | Pod에 대한 안정적인 엔드포인트 | 내부 로드 밸런싱 |
| Ingress | 외부에서 클러스터로의 HTTP/HTTPS 트래픽 관리 | 외부 접근 제어 |
| Network Policy | Pod 간 통신을 제어하는 정책 | 네트워크 보안 강화 |

#### **1.2 Network Policies**

##### **네트워크 트래픽 제어**

Network Policies를 통해 Pod 간 통신을 제어하여 방어 깊이를 강화합니다.

*Network Policy를 통한 Pod 간 통신 제어: Ingress(들어오는 트래픽), Egress(나가는 트래픽), Default Deny(기본 거부)*

| 정책 유형 | 설명 | 적용 예시 |
|----------|------|----------|
| Ingress | 들어오는 트래픽 제어 | 특정 네임스페이스에서만 접근 허용 |
| Egress | 나가는 트래픽 제어 | 특정 서비스로만 통신 허용 |
| Default Deny | 기본 거부 정책 | 명시적으로 허용된 트래픽만 통신 |

> 참고: Network Policy 설정 예시는 [Kubernetes Network Policies 공식 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Kubernetes 예제 저장소](https://kubernetes.io/docs/home/)를 참조하세요.

> 참고: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security) 및 [GitHub Actions 예제](https://docs.github.com/en/actions/using-workflows/workflow-templates)를 참조하세요. | GitHub 통합 종속성 관리 | 자동 업데이트, 보안 알림 | GitHub 자동 통합 |
| WhiteSource | 상용 SCA 도구 | 포괄적인 공급망 보안 | 다양한 CI/CD 통합 |

> 참고: 코드 스캔 도구는 [OWASP Top 10](https://owasp.org/www-project-top-ten/) 및 [OWASP CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)를 참조하세요.

> 참고: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security) 및 [GitHub Actions 예제](https://docs.github.com/en/actions/using-workflows/workflow-templates)를 참조하세요.과 통합 | 취약점 패치 자동화 |

##### **GitHub Actions AI 통합 예시**

> 참고: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions)를 참조하세요./ai-powered-security.yml
name: AI-Powered Security Scan
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # GitHub Copilot으로 생성된 코드 검증
      - name: Run Security Scan with AI
        uses: github/super-linter@v4
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          VALIDATE_ALL_CODEBASE: true

      # Claude API로 보안 리뷰
      - name: Claude Security Review
        uses: anthropic/claude-code-review@v1
        with:
          api-key: ${{ secrets.CLAUDE_API_KEY }}
          focus: "security"

      # Trivy로 이미지 스캔
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      # 결과를 GitHub Security 탭에 업로드
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
#### **5.3 ArgoCD 보안 설정**

---

## 보안 체크리스트

| 보안 영역 | 체크리스트 항목 | 설명 |
|----------|---------------|------|
| CI/CD 보안 | 코드 스캔 자동화 | SAST, DAST 도구 통합 |
| | 이미지 스캔 자동화 | Trivy, Snyk 등 CI/CD 파이프라인 통합 |
| | Secret 관리 | HashiCorp Vault, AWS Secrets Manager 사용 |
| | 파이프라인 무결성 검증 | GPG 서명, 자동화된 테스트 |
| AI 활용 | Cursor 보안 설정 | `.cursorrules` 파일에 보안 규칙 정의 |
| | Claude API 통합 | CI/CD 파이프라인에 Claude API 통합 |
| | GitHub Copilot 활성화 | 보안 모범 사례 제안 활성화 |
| | AI 생성 코드 검증 | 자동화된 테스트 및 보안 스캔 |
| Kubernetes 보안 | Network Policies 적용 | Pod 간 통신 제어 정책 설정 |
| | RBAC 최소 권한 원칙 | 필요한 권한만 부여 |
| | Pod Security Standards 적용 | Namespace에 PSS 레벨 설정 |
| | 감사 로깅 활성화 | Kubernetes Audit 로그 활성화 |
| 모니터링 | 런타임 보안 모니터링 | Falco 등 런타임 보안 도구 통합 |
| | 보안 이벤트 알림 | Prometheus, Grafana 통합 |

---

## 결론

CI/CD와 Kubernetes 보안은 DevSecOps의 핵심입니다. 개발부터 배포까지 전 과정에서 보안을 고려해야 합니다.

주요 포인트:

1. Kubernetes 네트워크 및 보안: Network Policies, RBAC, Pod Security Standards, 감사 로깅
2. CI/CD 파이프라인 보안: 코드 스캔(SAST, DAST), 이미지 스캔, Secret 관리, 파이프라인 무결성 검증
3. AI 활용을 통한 DevSecOps 강화: Cursor 보안 코딩, Claude API 자동화된 보안 검증, GitHub Copilot 보안 모범 사례, GitHub Actions AI 통합, AI 기반 보안 모니터링
4. DevSecOps 통합 전략: 자동화된 보안 검증, 보안 강화된 파이프라인 구축, 정기적인 보안 감사
5. 실전 보안 강화 사례: Secret 관리 개선, 이미지 스캔 자동화, AI 기반 보안 모니터링 등 실제 적용 사례
6. 실습: 보안 강화된 CI/CD 파이프라인 구축, Kubernetes 보안 환경 구성, AI 도구 통합

이 가이드를 참고하여 여러분의 CI/CD 파이프라인과 Kubernetes 클러스터 보안을 강화하시기 바랍니다.

## 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| Kubernetes 보안 | 클러스터 보안, RBAC, Network Policies, Pod Security | [수강하기](https://edu.2twodragon.com/courses/kubernetes-security) |
| CI/CD 보안 | 파이프라인 보안, Secret 관리, 이미지 스캔 자동화 | [수강하기](https://edu.2twodragon.com/courses/cicd-security) |
| DevSecOps 실전 | DevSecOps 전략, 보안 자동화, 모니터링 | [수강하기](https://edu.2twodragon.com/courses/devsecops) |
| AWS 클라우드 보안 | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| AWS WAF 네트워크 시나리오 | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

### 외부 참고 자료

- [OWASP CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)
- [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [ArgoCD 공식 문서](https://argo-cd.readthedocs.io/)
- [Jenkins 공식 문서](https://www.jenkins.io/doc/)
- [Trivy GitHub 저장소](https://github.com/aquasecurity/trivy)
- [HashiCorp Vault 문서](https://www.vaultproject.io/docs)
- [Cursor 공식 문서](https://cursor.sh/docs)
- [Claude API 문서](https://docs.anthropic.com/)
- [GitHub Copilot 문서](https://docs.github.com/en/copilot)
- [AI Coding Assistants Comparison](https://tech.2twodragon.com/posts/2026-01-17-AI_Coding_Assistants_Comparison_Gemini_Claude_Code_ChatGPT_OpenCode_2025_2026_Research_Analysis/)

---

<div class="post-metadata">
  <div class="metadata-item">
    <strong>마지막 업데이트</strong>
    <span>2026-01-22</span>
  </div>
  <div class="metadata-item">
    <strong>작성 기준</strong>
    <span>클라우드 보안 과정 8기 8주차 강의 자료</span>
  </div>
</div>

## CI/CD 보안 실습 체크리스트

### CI/CD 파이프라인 보안 점검

- SAST(정적 분석) 도구를 CI 파이프라인에 통합했는지 확인
- DAST(동적 분석) 도구를 스테이징 환경 배포 후 자동 실행 설정
- 컨테이너 이미지 빌드 시 Trivy/Snyk 취약점 스캔 자동화
- Pipeline Secret을 환경 변수가 아닌 Vault/Secrets Manager로 관리
- 파이프라인 무결성 검증을 위한 GPG 서명 또는 Attestation 적용

### Kubernetes 운영 보안 점검

- Namespace별 Network Policies 적용 여부 확인
- RBAC ServiceAccount 최소 권한 원칙 검토
- Pod Security Standards(restricted 레벨) Namespace 적용
- Kubernetes Audit 로그 외부 SIEM으로 전송 설정
- Falco 또는 런타임 보안 도구 클러스터에 배포

