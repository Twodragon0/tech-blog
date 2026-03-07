---
author: Twodragon
categories:
- security
- cloud
certifications:
- aws-saa
comments: true
date: 2026-01-14 11:00:00 +0900
description: AWS 클라우드 환경에서의 보안 아키텍처 설계 및 구현 가이드. IAM, VPC, S3, RDS, EKS 등 주요 서비스별
  보안 모범 사례, Defense in Depth 전략, 최소 권한 원칙, 암호화, 로그 관리 및 모니터링까지 실무 중심 가이드.
excerpt: "AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처 - AWS 클라우드 환경에서의 보안 아키텍처 설계 및 구현 가이드. IAM, VPC, S3, RDS, EKS 등 주요 서비스별"
image: /assets/images/2026-01-14-AWS_Cloud_Security_Complete_Guide_IAM_to_EKS_Practical_Security_Architecture.svg
image_alt: 'AWS Cloud Security Complete Guide: IAM to EKS Practical Security Architecture'
keywords: AWS 보안, IAM, VPC, S3, RDS, EKS, CloudTrail, CloudWatch, Security Hub, GuardDuty,
  KMS, Defense in Depth, 최소 권한 원칙, AWS-SAA
layout: post
tags:
- AWS
- Security
- IAM
- VPC
- S3
- RDS
- EKS
- CloudTrail
- CloudWatch
- Security-Hub
title: 'AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처'
toc: true
---

{%- include ai-summary-card.html
  title='AWS 클라우드 보안 완벽 가이드: IAM부터 EKS까지 실무 중심 보안 아키텍처'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag cloud">Cloud</span>'
  tags_html='<span class="tag">AWS</span>
      <span class="tag">Security</span>
      <span class="tag">IAM</span>
      <span class="tag">VPC</span>
      <span class="tag">S3</span>
      <span class="tag">RDS</span>
      <span class="tag">EKS</span>
      <span class="tag">CloudTrail</span>
      <span class="tag">CloudWatch</span>
      <span class="tag">Security-Hub</span>'
  highlights_html='<li><strong>AWS 보안 아키텍처 개요</strong>: Defense in Depth 전략, 다층 보안 방어, AWS 서비스별 보안 레이어, 보안 그룹, NACL, IAM 통합</li>
      <li><strong>IAM 보안</strong>: IAM 정책 작성, 역할 기반 접근 제어 (RBAC), MFA 설정, 최소 권한 원칙, 정기적인 권한 검토</li>
      <li><strong>VPC 보안</strong>: VPC 아키텍처 설계 (Public/Private Subnet), NAT Gateway 설정, Security Group 및 NACL 구성, 네트워크 분리</li>
      <li><strong>S3 보안</strong>: 버킷 정책, 암호화 설정 (서버 측 암호화, KMS), 버전 관리, 접근 로그, Public Access 차단</li>
      <li><strong>RDS 보안</strong>: 데이터베이스 암호화, 보안 그룹 구성, 파라미터 그룹, 스냅샷, 자동 백업</li>
      <li><strong>EKS 보안</strong>: Pod Security Standards, Network Policy, RBAC, 컨테이너 이미지 보안, 시크릿 관리</li>
      <li><strong>모니터링 및 감사</strong>: CloudTrail 설정, CloudWatch 모니터링, Security Hub 통합, GuardDuty 위협 탐지</li>'
  audience='AWS 보안 엔지니어, 클라우드 아키텍트, DevOps 엔지니어, 보안 전문가, AWS-SAA 준비자'
-%}

## 🎯 경영진 요약 (Executive Summary)

### AWS/EKS 보안 태세 평가

| 보안 영역 | 현재 위협 수준 | 주요 공격 벡터 | 권장 우선순위 |
|----------|-------------|-------------|-------------|
| **IAM/인증** | 🔴 **HIGH** | Credential stuffing, 권한 에스컬레이션 | 1순위 |
| **EKS/Container** | 🔴 **HIGH** | Escape to Host, 특권 컨테이너 실행 | 2순위 |
| **VPC/네트워크** | 🟡 **MEDIUM** | Lateral movement, 무단 네트워크 접근 | 3순위 |
| **S3/데이터** | 🟡 **MEDIUM** | Public bucket 노출, 암호화 미적용 | 4순위 |
| **RDS/데이터베이스** | 🟢 **LOW** | SQL injection, 암호화되지 않은 백업 | 5순위 |

**핵심 권장사항:**
1. **즉시 조치**: 모든 루트 계정에 MFA 활성화 + IAM Access Analyzer 실행
2. **1주 내**: EKS Pod Security Standards 적용 + Network Policy 구성
3. **1개월 내**: Security Hub + GuardDuty 활성화 + 자동화된 위협 대응 워크플로 구축

**투자 대비 효과 (ROI):**
- **보안 사고 감소**: 평균 67% (CIS AWS Foundations Benchmark 적용 시)
- **컴플라이언스 비용 절감**: 30-40% (ISMS-P, CSAP 자동 감사)
- **평균 복구 시간 (MTTR)**: 4시간 → 45분 (GuardDuty + Lambda 자동 대응)

---

## 서론

안녕하세요, **Twodragon**입니다.

AWS 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 EKS까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다. 이 포스팅은 **SK Shieldus의 2024년 AWS 클라우드 보안 가이드**를 기반으로, 실무에서 즉시 활용 가능한 AWS 보안 아키텍처 설계 및 구현 가이드를 제공합니다.

주요 AWS 서비스별 보안 모범 사례와 코드 예제, 보안 체크리스트를 포함하여 실무 중심의 보안 구축 방법을 제시합니다.

## 📊 빠른 참조

### AWS 보안 서비스 개요

| 서비스 | 용도 | 주요 기능 |
|--------|------|----------|
| **IAM** | 접근 제어 | 사용자, 역할, 정책 관리 |
| **VPC** | 네트워크 보안 | 네트워크 격리, 접근 제어 |
| **Security Hub** | 통합 보안 관리 | 보안 상태 통합 대시보드 |
| **CloudTrail** | 감사 및 컴플라이언스 | API 호출 로깅 |
| **CloudWatch** | 모니터링 | 메트릭, 로그, 알람 |
| **GuardDuty** | 위협 탐지 | 이상 활동 탐지 |
| **KMS** | 암호화 | 키 관리 서비스 |
| **Config** | 설정 관리 | 리소스 설정 모니터링 |

---

## 🛡️ MITRE ATT&CK 매핑: AWS/EKS 위협 모델링

### 컨테이너 및 Kubernetes 주요 공격 기법

| MITRE Technique | 공격 설명 | AWS/EKS 대응 방안 |
|----------------|----------|------------------|
| **T1610: Deploy Container** | 악성 컨테이너 배포 | ECR Image Scanning + Admission Controller |
| **T1611: Escape to Host** | 컨테이너 탈출 → 호스트 권한 획득 | Pod Security Standards (restricted) + seccomp/AppArmor |
| **T1078.004: Cloud Accounts** | 탈취된 클라우드 자격 증명 악용 | IAM Access Analyzer + CloudTrail 이상 탐지 |
| **T1552.001: Credentials in Files** | 하드코딩된 시크릿 탈취 | AWS Secrets Manager + IRSA (IAM Roles for Service Accounts) |
| **T1613: Container & Resource Discovery** | 컨테이너 환경 정찰 | Network Policy + VPC Flow Logs |
| **T1204: User Execution** | 사용자 유도 악성 실행 | GuardDuty Runtime Monitoring + Falco |
| **T1053.003: Cron** | 예약 작업을 통한 지속성 확보 | Pod Security Admission + ReadOnlyRootFilesystem |
| **T1486: Data Encrypted for Impact** | 랜섬웨어 공격 | S3 Versioning + Object Lock + EBS Snapshot 정책 |

### AWS 특화 공격 체인 예시

```json
[Initial Access]           [Execution]              [Persistence]           [Defense Evasion]
T1078.004                  T1610                    T1053.003               T1562.001
└─ IAM 자격증명 탈취  →  악성 컨테이너 배포  →  CronJob 등록     →  CloudTrail 로그 삭제

[Lateral Movement]         [Collection]             [Exfiltration]
T1613                      T1552.001                T1567.002
└─ Cluster 정찰       →  시크릿 탈취        →  S3 버킷으로 데이터 유출
```

### EKS Pod Security Standards 적용

```yaml
# Pod Security Admission - namespace 레벨 적용
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### EKS Network Policy 예시

| 항목 | 설정 | 설명 |
|------|------|------|
| 정책 이름 | `default-deny-all` | 기본 전체 차단 정책 |
| 네임스페이스 | `production` | 프로덕션 환경 적용 |
| podSelector | `{}` (전체) | 모든 Pod에 적용 |
| 차단 대상 | Ingress + Egress | 인바운드/아웃바운드 모두 기본 차단 후 필요한 트래픽만 허용 |

### 증거 수집 (Evidence Collection)

```bash
# Pod 로그 백업
kubectl logs <pod-name> -n <namespace> --all-containers > /evidence/pod-logs-$(date +%s).log

# EKS 감사 로그 조회 (CloudWatch Logs Insights)
aws logs start-query \
  --log-group-name "/aws/eks/my-cluster/audit" \
  --start-time $(date -d '24 hours ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, verb, objectRef.resource | filter verb="delete"'
```

### 시나리오: IAM 자격증명 노출 대응

**GuardDuty 탐지 Alert 예시:**

```json
{
  "GuardDutyFinding": {
    "Type": "UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration",
    "Severity": 8.0,
    "Description": "IAM credentials from EC2 instance i-0abc123 used from IP 198.51.100.42"
  }
}
```

**즉시 대응 Lambda 함수:**

![Mermaid Diagram](/assets/images/mermaid/AWS_Cloud_Security_Complete_Guide_IAMFrom_EKSTo_Security_Architecture-mermaid-1.svg)

| 단계 | 대응 조치 | AWS API |
|------|----------|---------|
| 1 | Access Key 비활성화 | `iam.update_access_key(Status="Inactive")` |
| 2 | 전체 권한 차단 (DenyAll) | `iam.put_user_policy(DenyAllAfterCompromise)` |
| 3 | 보안팀 알림 | `sns.publish(Subject="[CRITICAL] IAM Compromised")` |

> **참고**: Lambda 함수를 EventBridge 룰과 연동하면 GuardDuty → EventBridge → Lambda 자동 대응 파이프라인을 구축할 수 있습니다. 자세한 내용은 [AWS 보안 사고 대응 가이드](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html)를 참조하세요.

---

## 결론

AWS 클라우드 환경에서 보안을 강화하기 위해서는 IAM부터 EKS까지 모든 서비스 계층에서 Defense in Depth 전략을 적용해야 합니다.

주요 보안 원칙:

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **암호화**: 전송 중/저장 데이터 암호화
3. **로그 관리**: 모든 활동 로깅 및 모니터링
4. **정기적 검토**: 보안 설정 정기적 검토 및 개선
5. **자동화된 대응**: GuardDuty + EventBridge + Lambda를 통한 즉시 대응 체계 구축

### 핵심 실무 체크리스트

**즉시 적용 (오늘 내):**
- [ ] 모든 루트 계정 MFA 활성화
- [ ] S3 Public Access Block 전체 활성화
- [ ] CloudTrail 로깅 활성화 (모든 리전)

**1주일 내 적용:**
- [ ] Security Hub + GuardDuty 활성화
- [ ] EKS Pod Security Standards 적용
- [ ] IAM Access Analyzer 실행 및 결과 검토

**1개월 내 적용:**
- [ ] 자동화된 보안 사고 대응 워크플로 구축
- [ ] CSAP/ISMS-P 컴플라이언스 점검 자동화
- [ ] 정기 보안 교육 프로그램 시작

이 가이드를 참고하여 AWS 환경에서 강력한 보안 아키텍처를 구축하시기 바랍니다.

---

## 📚 참고 자료

### 공식 문서 및 가이드

1. **AWS 공식 보안 문서**
   - [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
   - [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
   - [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
   - [Amazon EKS Security Best Practices](https://aws.github.io/aws-eks-best-practices/security/docs/)

2. **컴플라이언스 및 규제**
   - [SK Shieldus 2024년 AWS 클라우드 보안 가이드](https://www.skshieldus.com/download/files/download.do?o_fname=2024%20%ED%81%AC%EB%9D%BC%EC%9A%B0%EB%93%9C%20%EB%B3%B4%EC%95%88%EA%B0%80%EC%9D%B4%EB%93%9C(AWS).pdf&r_fname=20240703112722479.pdf)
   - [CSAP (Cloud Security Assurance Program) 인증 기준](https://www.kisa.or.kr/2060301)
   - [ISMS-P 인증 기준 해설서](https://www.kisa.or.kr/2060204)
   - [CIS AWS Foundations Benchmark v1.5.0](https://www.cisecurity.org/benchmark/amazon_web_services)

3. **MITRE ATT&CK 프레임워크**
   - [MITRE ATT&CK: Containers](https://attack.mitre.org/matrices/enterprise/containers/)
   - [MITRE ATT&CK: Cloud (IaaS)](https://attack.mitre.org/matrices/enterprise/cloud/iaas/)
   - [AWS 보안 사고 대응 가이드](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html)

### 보안 도구 및 서비스

4. **AWS 보안 서비스 문서**
   - [AWS Security Hub User Guide](https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html)
   - [Amazon GuardDuty User Guide](https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html)
   - [AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
   - [AWS Config Developer Guide](https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html)
   - [Amazon Inspector User Guide](https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html)

5. **Kubernetes 보안**
   - [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
   - [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
   - [Calico Network Policy Tutorial](https://docs.tigera.io/calico/latest/network-policy/get-started/kubernetes-policy/kubernetes-policy-basic)
   - [Falco Runtime Security](https://falco.org/docs/)

### 커뮤니티 및 학습 자료

6. **보안 블로그 및 연구**
   - [AWS Security Blog](https://aws.amazon.com/blogs/security/)
   - [AWS re:Inforce 2025 세션 자료](https://reinforce.awsevents.com/)
   - [Cloud Security Alliance (CSA)](https://cloudsecurityalliance.org/)
   - [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)

7. **실습 및 교육**
   - [AWS Security Workshops](https://workshops.aws/categories/Security)
   - [AWS Skill Builder - Security Learning Plan](https://explore.skillbuilder.aws/learn/public/learning_plan/view/91/security-learning-plan)
   - [AWS-SAA 인증 페이지](/certifications/aws-saa/)
   - [온라인 강의 (2twodragon.com)](https://edu.2twodragon.com/courses/aws-saa)

### 오픈소스 보안 도구

8. **Infrastructure as Code (IaC) 보안 스캐닝**
   - [Checkov - Terraform/CloudFormation 보안 스캔](https://www.checkov.io/)
   - [tfsec - Terraform 정적 분석](https://github.com/aquasecurity/tfsec)
   - [Prowler - AWS 보안 베스트 프랙티스 점검](https://github.com/prowler-cloud/prowler)

9. **컨테이너 보안**
   - [Trivy - 컨테이너 이미지 취약점 스캐너](https://github.com/aquasecurity/trivy)
   - [Anchore - 컨테이너 보안 플랫폼](https://anchore.com/)
   - [Kube-bench - CIS Kubernetes Benchmark 점검](https://github.com/aquasecurity/kube-bench)

10. **보안 자동화**
    - [AWS Lambda Security Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)
    - [AWS Systems Manager - 보안 자동화](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
    - [Terraform AWS Security Modules](https://registry.terraform.io/modules/terraform-aws-modules/security-group/aws/latest)

### 사고 대응 및 포렌식

11. **AWS 보안 사고 대응**
    - [AWS Security Incident Response Whitepaper](https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html)
    - [AWS Systems Manager Incident Manager](https://docs.aws.amazon.com/incident-manager/latest/userguide/what-is-incident-manager.html)
    - [CloudTrail 로그 분석 가이드](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html)

12. **관련 인증 및 자격증**
    - [AWS Certified Security - Specialty](https://aws.amazon.com/certification/certified-security-specialty/)
    - [Certified Kubernetes Security Specialist (CKS)](https://www.cncf.io/certification/cks/)
    - [CISSP (Certified Information Systems Security Professional)](https://www.isc2.org/Certifications/CISSP)

---

**마지막 업데이트**: 2026-01-14
**작성 기준**: SK Shieldus 2024년 AWS 클라우드 보안 가이드, MITRE ATT&CK v14, CIS AWS Foundations Benchmark v1.5.0


