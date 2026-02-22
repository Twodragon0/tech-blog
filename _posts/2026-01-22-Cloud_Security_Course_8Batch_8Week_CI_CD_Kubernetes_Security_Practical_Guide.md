---
layout: post
title: "🚀 클라우드 보안 과정 8기 8주차: CI/CD와 Kubernetes 보안 실전 가이드 - DevSecOps 파이프라인부터 클러스터 보안까지"
date: 2026-01-22 18:30:00 +0900
categories: [security, devsecops, kubernetes]
tags: [CI/CD, Kubernetes, DevSecOps, K8s-Security, Cloud-Security, ArgoCD, Jenkins, Network-Policies, RBAC, Pod-Security-Standards]
excerpt: "CI/CD 보안, K8s Network Policies, Pod Security Standards, AI 기반 보안 자동화"
description: "클라우드 보안 과정 8기 8주차: CI/CD 파이프라인 보안(Trivy, Snyk, Vault), Kubernetes 네트워크 보안(Network Policies, RBAC), Pod Security Standards, AI 활용 DevSecOps 강화(Cursor, Claude API, GitHub Copilot), 실전 보안 사례 제공"
keywords: [CI/CD-Security, Kubernetes-Security, DevSecOps, Pod-Security-Standards, Network-Policies, RBAC, Trivy, Vault, ArgoCD, Jenkins, AI-DevSecOps, Cursor, Claude-API]
author: Twodragon
comments: true
original_url: https://twodragon.tistory.com/708
image: /assets/images/2026-01-22-Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide.svg
image_alt: "Cloud Security Course 8Batch 8Week: CI/CD and Kubernetes Security Practical Guide"
toc: true
schema_type: Article
category: devsecops
---

## 서론

안녕하세요, **Twodragon**입니다.

지난 7주차에서는 Docker & Kubernetes 보안 실전 가이드를 다루었습니다. 이번 **클라우드 보안 과정 8기 8주차**에서는 **CI/CD와 Kubernetes 보안 실전 가이드**를 통해 DevSecOps 파이프라인부터 클러스터 보안까지 실무 중심으로 다루고자 합니다.

특히 이번 주에는 **CI/CD 파이프라인 보안**과 **Kubernetes 클러스터 보안**을 통합하여, 실제 서비스 환경에 적용 가능한 보안 전략을 깊이 있게 다뤄보겠습니다.

본 과정은 **온라인 미팅**으로 진행되며, **'20분 강의 + 5분 휴식'** 사이클로 멘티분들의 집중력을 최대로 유지하며 진행됩니다.

---

### **📅 8주차 타임테이블 (Agenda)**

| 시간 | 주제 | 내용 |
|------|------|------|
| **10:00 - 10:20** | **근황 토크 & 과제 피드백** | 한 주간의 보안 이슈 공유 및 Q&A |
| **10:25 - 11:00** | **Kubernetes 네트워크 및 보안** | Kubernetes 네트워크, Network Policies, RBAC, Pod Security Standards |
| **11:10 - 11:40** | **지속적 통합, 지속적 제공/배포(CI/CD) 및 보안** | CI/CD 파이프라인 보안, 코드 스캔, 이미지 스캔, Secret 관리 |
| **11:45 - 12:00** | **AI 활용을 통한 DevSecOps 강화** | Cursor, Claude API, GitHub Copilot 활용 방법, AI 기반 보안 모니터링 |
| **12:05 - 12:10** | **실습 및 Q&A** | 보안 강화된 CI/CD 파이프라인 구축, Kubernetes 보안 환경 구성, AI 도구 통합 |

---

## 1. Kubernetes 네트워크 및 보안

Kubernetes 네트워크 보안은 클러스터 보안의 핵심입니다. 네트워크 정책부터 접근 제어까지 다층 방어 전략을 적용해야 합니다.

#### **1.1 Kubernetes 네트워크 기본 개념**

##### **Kubernetes 핵심 오브젝트**

*Kubernetes 핵심 오브젝트: Namespace, Deployment, Service, ConfigMap, Secret, PersistentVolumeClaim, PersistentVolume, HPA*

| 오브젝트 | 설명 | 역할 |
|---------|------|------|
| **Namespace** | 리소스를 논리적으로 분리하는 가상 클러스터 | 리소스 그룹핑 및 격리 |
| **Deployment** | Pod의 배포, 업데이트, 스케일링을 관리 | Pod 생명주기 관리 |
| **Service** | Pod에 대한 안정적인 네트워크 엔드포인트 제공 | Pod 간 통신 및 로드 밸런싱 |
| **ConfigMap** | 설정 데이터를 저장하는 리소스 | 애플리케이션 설정 관리 |
| **Secret** | 민감한 데이터를 저장하는 리소스 | 비밀 정보 관리 |
| **PersistentVolumeClaim** | 스토리지 요청 리소스 | 영구 스토리지 요청 |
| **PersistentVolume** | 클러스터의 스토리지 리소스 | 영구 스토리지 제공 |
| **HPA** | Horizontal Pod Autoscaler | 자동 스케일링 |

> **참고**: Kubernetes 기본 개념은 [Kubernetes 공식 문서](https://kubernetes.io/docs/concepts/) 및 [Kubernetes GitHub 저장소](https://github.com/kubernetes/kubernetes)를 참조하세요.

##### **Kubernetes 네트워크 아키텍처**

![Kubernetes Security Architecture with AI Monitoring](/assets/images/2026-01-22-Kubernetes_Security_Architecture_AI_Monitoring.svg)
*Kubernetes 네트워크 아키텍처: Pod 간 통신, Service를 통한 로드 밸런싱, Ingress를 통한 외부 접근 (AI 모니터링 통합)*

| 구성 요소 | 설명 | 역할 |
|----------|------|------|
| **Pod Network** | Pod 간 통신을 위한 네트워크 | CNI 플러그인으로 구현 |
| **Service** | Pod에 대한 안정적인 엔드포인트 | 내부 로드 밸런싱 |
| **Ingress** | 외부에서 클러스터로의 HTTP/HTTPS 트래픽 관리 | 외부 접근 제어 |
| **Network Policy** | Pod 간 통신을 제어하는 정책 | 네트워크 보안 강화 |

#### **1.2 Network Policies**

##### **네트워크 트래픽 제어**

Network Policies를 통해 Pod 간 통신을 제어하여 방어 깊이를 강화합니다.

*Network Policy를 통한 Pod 간 통신 제어: Ingress(들어오는 트래픽), Egress(나가는 트래픽), Default Deny(기본 거부)*

| 정책 유형 | 설명 | 적용 예시 |
|----------|------|----------|
| **Ingress** | 들어오는 트래픽 제어 | 특정 네임스페이스에서만 접근 허용 |
| **Egress** | 나가는 트래픽 제어 | 특정 서비스로만 통신 허용 |
| **Default Deny** | 기본 거부 정책 | 명시적으로 허용된 트래픽만 통신 |

> **참고**: Network Policy 설정 예시는 [Kubernetes Network Policies 공식 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Kubernetes 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.** | GitHub 통합 종속성 관리 | 자동 업데이트, 보안 알림 | GitHub 자동 통합 |
| **WhiteSource** | 상용 SCA 도구 | 포괄적인 공급망 보안 | 다양한 CI/CD 통합 |

> **참고**: 코드 스캔 도구는 [OWASP Top 10](https://owasp.org/www-project-top-ten/) 및 [OWASP CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)를 참조하세요.

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.과 통합 | 취약점 패치 자동화 |

##### **GitHub Actions AI 통합 예시**

> **참고**: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)를 참조하세요./ai-powered-security.yml
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
{% endraw %}

```
-->
-->

#### **3.6 AI 기반 보안 모니터링**

##### **AI 기반 이상 탐지**

| 도구 | 설명 | 활용 방법 |
|------|------|----------|
| **Claude API + Falco** | 런타임 보안 이벤트 분석 | 이상 행위 패턴 탐지 |
| **GitHub Copilot + Prometheus** | 메트릭 분석 및 알림 | 보안 이벤트 자동 분석 |
| **Cursor + Kubernetes Audit** | 감사 로그 분석 | 보안 이벤트 패턴 탐지 |

##### **AI 기반 보안 모니터링 아키텍처**

*AI 기반 보안 모니터링: Kubernetes Audit 로그 → Claude API 분석 → 이상 행위 탐지 → 자동화된 대응*

> **참고**: AI 기반 보안 모니터링은 [OWASP AI Security](https://owasp.org/www-project-top-10-for-large-language-model-applications/) 및 [MITRE ATLAS](https://atlas.mitre.org/)를 참조하세요.

#### **3.7 AI 활용 Best Practices**

##### **보안 고려사항**

| 항목 | 설명 | 권장 사항 |
|------|------|----------|
| **API 키 관리** | AI 도구 API 키 보안 관리 | 환경 변수 사용, Secret 관리 도구 활용 |
| **코드 검증** | AI 생성 코드 검증 필수 | 자동화된 테스트 및 보안 스캔 |
| **비용 관리** | AI API 사용 비용 최적화 | 캐싱, 배치 처리, 프롬프트 최적화 |

##### **AI 활용 체크리스트**

| 항목 | 설명 | 상태 |
|------|------|------|
| **Cursor 보안 설정** | `.cursorrules` 파일에 보안 규칙 정의 | ✅ |
| **Claude API 통합** | CI/CD 파이프라인에 Claude API 통합 | ✅ |
| **GitHub Copilot 활성화** | GitHub Copilot 활성화 및 보안 설정 | ✅ |
| **AI 생성 코드 검증** | 자동화된 테스트 및 보안 스캔 | ✅ |
| **비용 모니터링** | AI API 사용량 및 비용 모니터링 | ✅ |

---

## 4. DevSecOps 통합 전략

DevSecOps는 개발, 보안, 운영을 통합하여 보안을 개발 프로세스에 자연스럽게 통합하는 접근 방식입니다.

#### **3.1 자동화된 보안 검증**

##### **CI/CD 파이프라인 보안 통합**

| 단계 | 보안 검증 항목 | 도구 | 적용 방법 |
|------|--------------|------|----------|
| **빌드 단계** | 이미지 스캔, Dockerfile 검증 | Trivy, Hadolint | CI 파이프라인 통합 |
| **배포 전** | Kubernetes 매니페스트 검증 | Polaris, Kube-score | Pre-commit hook |
| **배포 후** | 런타임 보안 모니터링 | Falco, Sysdig | Kubernetes Operator |

##### **보안 강화된 CI/CD 파이프라인**

![CI/CD Security Pipeline with AI Integration](/assets/images/2026-01-22-CI_CD_Security_Pipeline_AI_Integration.svg)
*보안 강화된 CI/CD 파이프라인: 코드 스캔 → 이미지 스캔 → Secret 관리 → 배포 검증 → 런타임 모니터링 (AI 통합)*

> **참고**: DevSecOps 통합 전략은 [OWASP DevSecOps Maturity Model](https://owasp.org/www-project-devsecops-maturity-model/) 및 [OWASP CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)를 참조하세요.

#### **3.2 보안 강화된 파이프라인 구축**

##### **실습 예시: 보안 강화된 CI/CD 파이프라인**

이번 주차 실습에서는 보안이 강화된 CI/CD 파이프라인을 구축해보았습니다. 주요 구성은 다음과 같습니다:

1. **코드 저장소**: GitHub를 사용하여 소스코드를 관리하고, GPG 서명을 통해 커밋의 무결성을 검증합니다.
2. **CI 도구**: Jenkins를 활용하여 빌드 및 테스트를 자동화하고, SonarQube를 통합하여 코드 품질을 분석합니다.
3. **CD 도구**: ArgoCD를 사용하여 Kubernetes 클러스터에 애플리케이션을 배포하고, Helm을 통해 배포를 관리합니다.
4. **보안 스캔**: Trivy를 사용하여 컨테이너 이미지의 취약점을 스캔하고, 결과를 Slack으로 알림받습니다.

#### **3.3 정기적인 보안 감사**

##### **보안 감사 체크리스트**

| 항목 | 설명 | 주기 | 담당 |
|------|------|------|------|
| **코드 스캔** | 정적/동적 분석 실행 | 매 커밋 | 개발팀 |
| **이미지 스캔** | 컨테이너 이미지 취약점 스캔 | 매 빌드 | DevOps팀 |
| **Secret 감사** | 하드코딩된 Secret 검색 | 주 1회 | 보안팀 |
| **권한 감사** | RBAC 권한 검토 | 월 1회 | 보안팀 |
| **파이프라인 감사** | CI/CD 파이프라인 설정 검토 | 분기 1회 | DevOps팀 |

---

## 4. 실전 보안 강화 사례

보안 엔지니어에게 실전 경험은 이론보다 중요합니다. 이번 주에는 실제 프로젝트에서 적용한 보안 강화 사례를 공유합니다.

#### **💡 멘토의 관점: CI/CD 보안도 '코드'로 관리됩니다.**

##### **DevSecOps 워크플로우**

CI/CD 보안은 DevSecOps 사이클을 통해 코드로 관리됩니다. 실제 보안 강화 사례를 통해 구체적인 개선 방법을 살펴보겠습니다.

#### **보안 강화 사례: Secret 관리 개선**

| **구분** | **수정 전 (Before)** | **수정 후 (After)** |
|---------|-------------------|-------------------|
| **Secret 관리** | 환경 변수에 하드코딩<br>_(코드에 평문 저장)_ | HashiCorp Vault 통합<br>_(중앙 관리, 동적 생성)_ |
| **위협 요소** | Git 히스토리에 Secret 노출 위험 | Secret이 코드에 노출되지 않음 |
| **보안 효과** | Secret 유출 시 전체 시스템 위험 | Secret 로테이션, 접근 제어 가능 |

#### **보안 강화 사례: 이미지 스캔 자동화**

| **구분** | **수정 전 (Before)** | **수정 후 (After)** |
|---------|-------------------|-------------------|
| **이미지 스캔** | 수동 스캔<br>_(배포 전 수동 실행)_ | CI/CD 파이프라인 통합<br>_(자동 스캔, 실패 시 배포 차단)_ |
| **위협 요소** | 취약점이 있는 이미지 배포 가능 | 취약점 발견 시 자동 차단 |
| **보안 효과** | 취약점 탐지 지연 | 실시간 취약점 탐지 및 차단 |

> 👨‍🏫 멘토의 조언 (Takeaway)
> 
> CI/CD 보안은 한 번의 설정으로 끝나는 것이 아닙니다. 지속적인 모니터링과 자동화된 보안 검증을 통해 보안 상태를 유지해야 합니다. 이번 주 실습을 통해 여러분의 CI/CD 파이프라인도 점검해 보세요.
> 
> 👉 **CI/CD 보안 Best Practices 및 실습 가이드 보러가기**

---

## 5. 실습: 보안 강화된 CI/CD 파이프라인 구축

#### **5.1 GitHub Actions 보안 강화 설정**

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```yaml
> {% raw %}...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```yaml
> {% raw %}...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
{% raw %}
# .github/workflows/security-scan.yml
name: Security Scan
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
jobs:
  code-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

  image-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
{% endraw %}

```
-->
-->

#### **5.2 Kubernetes 보안 환경 구성**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # Namespace 생성 및 보안 정책 적용...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # Namespace 생성 및 보안 정책 적용...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# Namespace 생성 및 보안 정책 적용
kubectl create namespace production
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted

# Network Policy 적용
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF

# RBAC 설정
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: production
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "create", "update", "patch"]
EOF

```
-->
-->

#### **5.3 ArgoCD 보안 설정**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # ArgoCD Application 보안 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # ArgoCD Application 보안 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# ArgoCD Application 보안 설정 예시
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true

```
-->
-->

---

## 보안 체크리스트

| 보안 영역 | 체크리스트 항목 | 설명 |
|----------|---------------|------|
| **CI/CD 보안** | 코드 스캔 자동화 | SAST, DAST 도구 통합 |
| | 이미지 스캔 자동화 | Trivy, Snyk 등 CI/CD 파이프라인 통합 |
| | Secret 관리 | HashiCorp Vault, AWS Secrets Manager 사용 |
| | 파이프라인 무결성 검증 | GPG 서명, 자동화된 테스트 |
| **AI 활용** | Cursor 보안 설정 | `.cursorrules` 파일에 보안 규칙 정의 |
| | Claude API 통합 | CI/CD 파이프라인에 Claude API 통합 |
| | GitHub Copilot 활성화 | 보안 모범 사례 제안 활성화 |
| | AI 생성 코드 검증 | 자동화된 테스트 및 보안 스캔 |
| **Kubernetes 보안** | Network Policies 적용 | Pod 간 통신 제어 정책 설정 |
| | RBAC 최소 권한 원칙 | 필요한 권한만 부여 |
| | Pod Security Standards 적용 | Namespace에 PSS 레벨 설정 |
| | 감사 로깅 활성화 | Kubernetes Audit 로그 활성화 |
| **모니터링** | 런타임 보안 모니터링 | Falco 등 런타임 보안 도구 통합 |
| | 보안 이벤트 알림 | Prometheus, Grafana 통합 |

---

## 결론

CI/CD와 Kubernetes 보안은 DevSecOps의 핵심입니다. 개발부터 배포까지 전 과정에서 보안을 고려해야 합니다.

주요 포인트:

1. **Kubernetes 네트워크 및 보안**: Network Policies, RBAC, Pod Security Standards, 감사 로깅
2. **CI/CD 파이프라인 보안**: 코드 스캔(SAST, DAST), 이미지 스캔, Secret 관리, 파이프라인 무결성 검증
3. **AI 활용을 통한 DevSecOps 강화**: Cursor 보안 코딩, Claude API 자동화된 보안 검증, GitHub Copilot 보안 모범 사례, GitHub Actions AI 통합, AI 기반 보안 모니터링
4. **DevSecOps 통합 전략**: 자동화된 보안 검증, 보안 강화된 파이프라인 구축, 정기적인 보안 감사
5. **실전 보안 강화 사례**: Secret 관리 개선, 이미지 스캔 자동화, AI 기반 보안 모니터링 등 실제 적용 사례
6. **실습**: 보안 강화된 CI/CD 파이프라인 구축, Kubernetes 보안 환경 구성, AI 도구 통합

이 가이드를 참고하여 여러분의 CI/CD 파이프라인과 Kubernetes 클러스터 보안을 강화하시기 바랍니다.

## 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **Kubernetes 보안** | 클러스터 보안, RBAC, Network Policies, Pod Security | [수강하기](https://edu.2twodragon.com/courses/kubernetes-security) |
| **CI/CD 보안** | 파이프라인 보안, Secret 관리, 이미지 스캔 자동화 | [수강하기](https://edu.2twodragon.com/courses/cicd-security) |
| **DevSecOps 실전** | DevSecOps 전략, 보안 자동화, 모니터링 | [수강하기](https://edu.2twodragon.com/courses/devsecops) |
| **AWS 클라우드 보안** | IAM, VPC, Security Groups, GuardDuty | [수강하기](https://edu.2twodragon.com/courses/aws-security) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

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
