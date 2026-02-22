---
layout: post
title: "2026년 1월 클라우드 보안 동향: Kubernetes 82% 프로덕션 도입, VS Code 악용 위협 증가, CNCF 연례 조사 분석"
date: 2026-01-22 12:00:00 +0900
categories: [security, kubernetes]
tags: [Kubernetes, Cloud-Security, CNCF, VS-Code-Security, Platform-Engineering, GPU-Scheduling, CRI-O-Audit, Net-NTLMv1, DevSecOps, "2026"]
excerpt: "Kubernetes 82% 프로덕션 도입, VS Code 악용 위협, CNCF 조사 분석 등 클라우드 보안 동향"
description: "2026년 1월 클라우드 보안 핵심 동향. CNCF 연례 조사 Kubernetes 프로덕션 82% 달성, VS Code 터널 악용 위협 확대, CRI-O 보안 감사 완료, Net-NTLMv1 레인보우 테이블 공개 등 주요 보안 이슈와 대응 방안"
keywords: [Kubernetes, Cloud Security, CNCF, VS Code Security, Platform Engineering, CRI-O, Net-NTLMv1, DevSecOps]
author: Twodragon
comments: true
image: /assets/images/2026-01-22-Cloud_Security_Trends_January_2026.svg
image_alt: "Cloud Security Trends January 2026 - Kubernetes, VS Code Threats, CNCF Survey"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='2026년 1월 클라우드 보안 동향: Kubernetes 82% 프로덕션 도입, VS Code 악용 위협 증가, CNCF 연례 조사 분석'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devops">쿠버네티스</span>'
  tags_html='<span class="tag">Kubernetes</span> <span class="tag">Cloud-Security</span> <span class="tag">CNCF</span> <span class="tag">VS-Code-Security</span> <span class="tag">Platform-Engineering</span> <span class="tag">GPU-Scheduling</span> <span class="tag">CRI-O-Audit</span> <span class="tag">Net-NTLMv1</span>'
  highlights_html='<li><strong>포인트 1</strong>: ### 위험 스코어카드</li> <li><strong>포인트 2</strong>: 실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다</li> <li><strong>포인트 3</strong>: 운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-01-22 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## 핵심 요약

### 위험 스코어카드

| 위협 범주 | 심각도 | 긴급성 | 비즈니스 영향 | 대응 난이도 |
|----------|--------|--------|--------------|------------|
| **VS Code 악용 (공급망 공격)** | ⚠️ CRITICAL | 높음 | 높음 (지적 재산 탈취) | 중간 |
| **Net-NTLMv1 레거시 프로토콜** | ⚠️ CRITICAL | 매우 높음 | 높음 (자격증명 탈취) | 높음 |
| **Kubernetes 미흡한 보안 구성** | ⚠️ HIGH | 높음 | 매우 높음 (데이터 유출) | 중간 |
| **CRI-O 컨테이너 런타임 취약점** | ℹ️ MEDIUM | 중간 | 중간 (권한 상승) | 낮음 |
| **GPU 리소스 낭비** | ℹ️ LOW | 낮음 | 중간 (비용 증가) | 낮음 |

**종합 평가:**
- **가장 시급한 조치**: Net-NTLMv1 마이그레이션 (레인보우 테이블 공개로 즉각 악용 가능)
- **장기 전략**: Kubernetes 보안 강화 (AI 워크로드 증가로 공격 표면 확대)
- **비즈니스 리스크**: VS Code 공급망 공격 (개발자 자격증명 및 소스코드 탈취)

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 1월 클라우드 네이티브 생태계에서 주목할 만한 보안 동향이 발표되었습니다. CNCF(Cloud Native Computing Foundation)의 연례 조사에 따르면 Kubernetes가 이제 **프로덕션 환경에서 82%** 사용률을 기록하며 사실상 AI 워크로드의 운영 체제로 자리 잡았습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- CNCF 2025 연례 조사 결과 및 Kubernetes의 AI 인프라 역할
- Visual Studio Code 악용 위협 확대 및 대응 방안
- CRI-O 컨테이너 런타임 보안 감사 결과
- Net-NTLMv1 프로토콜 폐기 촉구 및 레인보우 테이블 공개
- 플랫폼 엔지니어링 유지보수 전략

## 📊 빠른 참조

### 2026년 1월 주요 클라우드 보안 이슈

| 이슈 | 출처 | 영향도 | 권장 조치 |
|------|------|--------|----------|
| **Kubernetes 82% 프로덕션 사용** | CNCF Survey | 높음 | K8s 보안 강화, AI 워크로드 최적화 |
| **VS Code 악용 위협** | Jamf Threat Labs | 높음 | 확장 프로그램 검증, 터널링 모니터링 |
| **CRI-O 보안 감사 완료** | OSTIF/CNCF | 중간 | CRI-O 업데이트 적용 |
| **Net-NTLMv1 폐기** | Mandiant | 높음 | NTLMv2/Kerberos 마이그레이션 |
| **GPU 스케줄링 최적화** | CNCF/HPE | 중간 | 유휴 GPU 재활용 정책 수립 |

---

## 1. MITRE ATT&CK 매핑 (클라우드 및 컨테이너)

이번 달 주요 위협을 MITRE ATT&CK 프레임워크에 매핑하여 조직의 위협 인텔리전스에 통합할 수 있습니다.

| 위협 시나리오 | MITRE 기법 | 전술 (Tactic) | 탐지 전략 |
|--------------|-----------|--------------|-----------|
| **VS Code 악성 확장 프로그램** | [T1195.002](https://attack.mitre.org/techniques/T1195/002/) - Supply Chain Compromise: Compromise Software Supply Chain | Initial Access | 확장 프로그램 무결성 검증, marketplace 활동 모니터링 |
| **VS Code 터널링 C2** | [T1071.001](https://attack.mitre.org/techniques/T1071/001/) - Application Layer Protocol: Web Protocols | Command and Control | `*.vscode.dev` 트래픽 분석, 비인가 터널 탐지 |
| **컨테이너 이스케이프** | [T1611](https://attack.mitre.org/techniques/T1611/) - Escape to Host | Privilege Escalation | CRI-O 런타임 무결성 검증, seccomp/AppArmor 로그 |
| **K8s RBAC 악용** | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) - Valid Accounts: Cloud Accounts | Persistence, Privilege Escalation | K8s audit log 분석, 비정상 ClusterRoleBinding 탐지 |
| **컨테이너 내 크레덴셜 접근** | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) - Unsecured Credentials: Credentials In Files | Credential Access | Secret 볼륨 접근 로그, 환경변수 덤프 탐지 |
| **Net-NTLMv1 릴레이 공격** | [T1557.001](https://attack.mitre.org/techniques/T1557/001/) - Man-in-the-Middle: LLMNR/NBT-NS Poisoning | Credential Access | NTLM 인증 로그, 비정상 인증 패턴 |
| **K8s 리소스 하이재킹** | [T1496](https://attack.mitre.org/techniques/T1496/) - Resource Hijacking | Impact | GPU 사용률 급증 탐지, 비인가 Pod 생성 |

<!-- HTML Comment: SIEM Detection Queries for Cloud Security Trends

=== Splunk SPL Queries ===

### 1. VS Code 터널링 탐지 (네트워크 트래픽)
```spl
index=firewall OR index=proxy
| search dest_domain IN ("*.tunnels.api.visualstudio.com", "*.devtunnels.ms", "*.vscode.dev")
| where NOT [| inputlookup approved_developers.csv | fields user]
| stats count by src_ip, user, dest_domain, bytes_out
| where bytes_out > 10485760 OR count > 100
| eval severity="high"
| eval description="VS Code Remote Tunnel activity detected from unauthorized user"
```

### 2. Kubernetes RBAC 권한 상승 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```spl
index=k8s sourcetype=kube:audit
| search verb IN ("create", "update", "patch")
  objectRef.resource IN ("clusterrolebindings", "rolebindings")
| eval is_admin_role=if(match(requestObject.roleRef.name, "(?i)(cluster-admin|admin|edit)"), 1, 0)
| where is_admin_role=1
| stats count by user.username, objectRef.name, requestObject.roleRef.name
| where count > 5 OR match(user.username, "^system:")=0
| eval severity="critical"
```

### 3. 컨테이너 이스케이프 시도 탐지 (CRI-O 런타임)
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요.

```spl
index=linux sourcetype=syslog OR sourcetype=auditd
| search (process="runc" OR process="crio") AND
  (command="*--privileged*" OR command="*--cap-add*" OR command="*/proc/*/root*")
| rex field=command "(?<container_id>[a-f0-9]{12,64})"
| stats count by host, user, command, container_id
| where count > 3
| eval severity="high"
```

### 4. GPU 리소스 하이재킹 탐지
> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```spl
index=k8s sourcetype=kube:metrics metric_name="nvidia_gpu_duty_cycle"
| timechart span=5m avg(value) by pod_name
| foreach * [eval <<FIELD>>_delta=abs(<<FIELD>> - avg(<<FIELD>>))]
| where *_delta > 50
| eval severity="medium"
| eval description="Sudden GPU usage spike detected - potential cryptomining"
```

### 5. Net-NTLMv1 인증 탐지 (Windows Event Log)
```spl
index=windows sourcetype=WinEventLog:Security EventCode=4624
| search Authentication_Package="NTLM" Logon_Process!="NtLmSsp"
| eval ntlm_version=if(match(Workstation_Name, "^[A-Z0-9]{15}$"), "NTLMv1", "NTLMv2")
| where ntlm_version="NTLMv1"
| stats count by src_ip, user, ntlm_version, Workstation_Name
| eval severity="critical"
| eval recommendation="Migrate to NTLMv2 or Kerberos immediately"
```

=== Azure Sentinel KQL Queries ===

### 1. VS Code 악성 확장 프로그램 설치 탐지
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
DeviceProcessEvents
| where ProcessCommandLine has_any ("code --install-extension", "code.exe --install-extension")
| extend ExtensionID = extract(@"--install-extension\s+([^\s]+)", 1, ProcessCommandLine)
| where ExtensionID !in (approved_extensions) // 사전 승인된 확장 목록
| join kind=inner (
    DeviceNetworkEvents
    | where RemoteUrl has_any ("marketplace.visualstudio.com", "github.com")
) on DeviceId, InitiatingProcessCreationTime
| summarize InstallCount=count(), DistinctExtensions=make_set(ExtensionID) by DeviceName, AccountName, bin(Timestamp, 1h)
| where InstallCount > 5
| extend Severity = "High", ThreatType = "Supply Chain Compromise"


```
-->
-->
-->

### 2. Kubernetes 비정상 ClusterRoleBinding 생성
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
KubeAuditEvents
| where ObjectRef_Resource == "clusterrolebindings"
| where Verb in ("create", "update", "patch")
| extend RoleName = tostring(RequestObject.roleRef.name)
| where RoleName has_any ("cluster-admin", "admin", "edit")
| extend SubjectKind = tostring(RequestObject.subjects[0].kind)
| extend SubjectName = tostring(RequestObject.subjects[0].name)
| where SubjectKind == "ServiceAccount" and SubjectName startswith "default"
| extend Severity = "Critical", MITRE_Technique = "T1078.004"
| project TimeGenerated, User, SourceIPs, RoleName, SubjectName, Severity, MITRE_Technique


```
-->
-->
-->

### 3. 컨테이너 런타임 보안 프로필 우회
```kql
Syslog
| where Facility == "kern" and SeverityLevel == "warning"
| where SyslogMessage has_any ("apparmor", "seccomp", "SELinux")
| where SyslogMessage has_any ("denied", "blocked", "violation")
| parse SyslogMessage with * "profile=" Profile " " * "comm=" Command " " *
| summarize ViolationCount=count(), Commands=make_set(Command) by Computer, Profile, bin(TimeGenerated, 5m)
| where ViolationCount > 20
| extend Severity = "High", MITRE_Technique = "T1611"
```

### 4. GPU 크립토마이닝 의심 활동
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
InsightsMetrics
| where Namespace == "prometheus" and Name == "nvidia_smi_utilization_gpu_ratio"
| extend PodName = tostring(parse_json(Tags).pod)
| summarize AvgGPUUsage=avg(Val) by PodName, bin(TimeGenerated, 10m)
| where AvgGPUUsage > 0.95
| join kind=inner (
    KubePodInventory
    | where PodLabel_app !in ("ml-training", "ai-inference") // 정상 AI 워크로드
) on PodName
| extend Severity = "Medium", MITRE_Technique = "T1496"
| project TimeGenerated, PodName, AvgGPUUsage, Namespace, Severity


```
-->
-->
-->

### 5. Net-NTLMv1 레거시 인증 탐지
```kql
SecurityEvent
| where EventID == 4624 // Successful Logon
| where AuthenticationPackageName == "NTLM"
| extend NTLMVersion = iff(LogonProcessName == "NtLmSsp", "NTLMv2", "NTLMv1")
| where NTLMVersion == "NTLMv1"
| summarize Count=count(), DistinctAccounts=dcount(TargetUserName) by SourceNetworkAddress, NTLMVersion, bin(TimeGenerated, 1h)
| where Count > 10
| extend Severity = "Critical", MITRE_Technique = "T1557.001"
| extend Recommendation = "Disable NTLMv1 via GPO: LmCompatibilityLevel >= 3"
```

### 6. VS Code Remote Tunnel C2 트래픽 패턴
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
DeviceNetworkEvents
| where RemoteUrl has_any ("vscode.dev", "devtunnels.ms", "tunnels.api.visualstudio.com")
| extend TunnelType = case(
    RemoteUrl has "vscode.dev", "Web-based Tunnel",
    RemoteUrl has "devtunnels.ms", "Dev Tunnel",
    "API Tunnel"
)
| summarize TotalBytes=sum(SentBytes + ReceivedBytes),
            SessionCount=dcount(LocalPort),
            Duration=max(Timestamp) - min(Timestamp)
    by DeviceName, InitiatingProcessAccountName, TunnelType, bin(Timestamp, 1h)
| where TotalBytes > 104857600 or SessionCount > 10 // 100MB or 10+ sessions
| extend Severity = "High", MITRE_Technique = "T1071.001"


```
-->
-->
-->

End of SIEM Queries -->

---

## 2. CNCF 2025 연례 조사: Kubernetes의 AI 운영 체제화

### 2.1 핵심 조사 결과

CNCF의 2025년 연례 클라우드 네이티브 조사에서 Kubernetes는 더 이상 신흥 기술이 아닌 **엔터프라이즈 인프라의 표준**으로 확립되었습니다:

| 지표 | 수치 | 의미 |
|------|------|------|
| **컨테이너 사용자 중 K8s 프로덕션 사용률** | 82% | 컨테이너 오케스트레이션 표준 |
| **AI 채택 기업 중 K8s 추론 워크로드 사용률** | 66% | AI 인프라의 핵심 플랫폼 |
| **K8s를 AI '운영 체제'로 인식** | - | 인프라 레이어 역할 확대 |

> **참고**: [CNCF 공식 발표](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)

### 2.2 조직 문화의 결정적 역할

기술 도입만으로는 성공을 보장하지 않습니다. CNCF 조사에서 강조된 핵심은 **조직 문화**입니다:

![Successful AI/K8s Adoption Factors - Technology + Organizational Culture = Business Outcomes](/assets/images/diagrams/2026-01-22-k8s-ai-adoption-success.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```
Successful AI/K8s Adoption Formula:
Technology Adoption (K8s, AI) + Organizational Culture (DevOps) = Real Business Outcomes
Key insight: Technology alone is insufficient → Collaboration, automation, continuous improvement culture required
```

</details>

### 2.3 DevSecOps 관점에서의 시사점

Kubernetes 82% 프로덕션 도입은 보안 팀에게 다음을 의미합니다:

1. **K8s 보안 역량 필수화**: RBAC, Network Policy, Pod Security Standards 숙지
2. **AI 워크로드 보안**: 모델 서빙, 데이터 파이프라인 보안
3. **멀티테넌시 보안**: 네임스페이스 격리, 리소스 쿼터 관리

---

## 3. Visual Studio Code 악용 위협 확대

### 3.1 위협 개요

Jamf Threat Labs의 분석에 따르면, 공격자들이 Microsoft Visual Studio Code를 악용하는 사례가 증가하고 있습니다:

| 공격 벡터 | 설명 | 위험도 |
|----------|------|--------|
| **악성 확장 프로그램** | 마켓플레이스를 통한 악성 코드 배포 | 높음 |
| **VS Code 터널링** | 원격 개발 기능을 C2 채널로 악용 | 높음 |
| **설정 파일 조작** | `.vscode` 설정을 통한 지속성 확보 | 중간 |

> **참고**: [Jamf Threat Labs 분석](https://www.jamf.com/blog/threat-actors-expand-abuse-of-visual-studio-code/)

### 3.2 공격 시나리오

#### ASCII 공격 흐름도: VS Code 공급망 공격

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. 통합 | CRI-O 옵션 | 인증 완료 |
| **LG CNS** | DataCanvas K8s, AI 플랫폼 | containerd | 진행 중 |

### 8.5 실무 권장사항 (한국 조직 대상)

#### 즉시 실행 (1개월 내)
1. **Net-NTLMv1 환경 감사**: Windows AD 환경에서 레거시 인증 확인
2. **VS Code 정책 수립**: 확장 프로그램 화이트리스트 작성
3. **K8s RBAC 점검**: 과도한 권한 부여 검토 (cluster-admin 역할 최소화)

#### 단기 과제 (3개월 내)
1. **CRI-O 업데이트 계획**: OSTIF 감사 결과 반영, 패치 적용
2. **컨테이너 보안 정책**: Pod Security Standards Restricted 프로파일 적용
3. **SIEM 통합**: Kubernetes audit log → 기존 보안관제 시스템 연동

#### 장기 전략 (6개월 이상)
1. **Zero Trust 전환**: 컨테이너 네트워크 마이크로세그멘테이션
2. **AI 보안 역량**: AI/ML 워크로드 특화 보안 팀 구성
3. **CSAP 재인증**: 컨테이너 보안 강화 사항 반영

---

## 9. 경영진 보고 형식 (Board Reporting Format)

### 9.1 경영진 요약 (1페이지)

**보고 일자**: 2026년 1월 22일
**보고 대상**: CISO, CTO, 이사회
**보고자**: DevSecOps Team

#### 핵심 메시지

> **Kubernetes 82% 프로덕션 도입**은 클라우드 인프라의 표준화를 의미하지만, 동시에 **새로운 보안 위협 표면**이 확대되고 있습니다. 특히 개발자 도구(VS Code) 악용과 레거시 프로토콜(Net-NTLMv1) 위험이 시급한 조치가 필요합니다.

#### 비즈니스 영향 요약

| 위협 | 비즈니스 리스크 | 재무 영향 (추정) | 대응 비용 |
|------|----------------|----------------|----------|
| **VS Code 공급망 공격** | 지적 재산 유출, 소스코드 탈취 | $5M - $50M (IP 가치 기준) | $200K (EDR 도입) |
| **Net-NTLMv1 크레덴셜 탈취** | 내부망 침투, 랜섬웨어 | $2M - $10M (다운타임 기준) | $500K (마이그레이션) |
| **컨테이너 이스케이프** | 데이터 유출, 규제 위반 | $1M - $20M (GDPR/PIPA 벌금) | $100K (보안 정책 강화) |
| **GPU 리소스 낭비** | 클라우드 비용 과다 지출 | $500K/년 (유휴 GPU) | $50K (스케줄러 최적화) |

**총 위험 노출 금액**: $8.5M - $80M
**총 대응 비용**: $850K (1년 기준)

#### 권고 사항 (3가지 우선순위)

1. **[긴급] Net-NTLMv1 마이그레이션 프로젝트 승인** (Q1 2026 완료 목표)
   - 예산: $500K
   - 기대 효과: 자격 증명 탈취 위험 90% 감소

2. **[높음] 개발자 보안 프로그램 강화** (VS Code, Git 보안)
   - 예산: $200K
   - 기대 효과: 공급망 공격 탐지율 70% 향상

3. **[중간] Kubernetes 보안 성숙도 향상** (Pod Security Standards, RBAC)
   - 예산: $150K
   - 기대 효과: 컨테이너 이스케이프 위험 80% 감소

### 9.2 리스크 매트릭스 (시각화)

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```
> Impact...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```
> Impact...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```
> Impact [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
Impact
  ↑
HIGH│  [VS Code]    [Net-NTLMv1]
    │   (공급망)      (인증)
    │
MED │              [Container Escape]
    │               (런타임)
    │
LOW │                        [GPU 낭비]
    │                         (비용)
    └────────────────────────────────→ Likelihood
       LOW        MED         HIGH


```
-->
-->
-->

### 9.3 투자 우선순위 (ROI 관점)

| 투자 항목 | 비용 | 위험 감소 효과 | ROI | 우선순위 |
|----------|------|---------------|-----|----------|
| Net-NTLMv1 마이그레이션 | $500K | $6M (평균 랜섬웨어 피해) | 1200% | 1 |
| VS Code EDR 도입 | $200K | $25M (평균 IP 유출 피해) | 12500% | 2 |
| K8s 보안 강화 | $150K | $10M (평균 데이터 유출) | 6667% | 3 |
| GPU 스케줄러 최적화 | $50K | $500K/년 (비용 절감) | 1000% | 4 |

### 9.4 타임라인 및 마일스톤

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```
> Q1 2026 (Jan - Mar)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```
> Q1 2026 (Jan - Mar)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```
> Q1 2026 (Jan - Mar) [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```
Q1 2026 (Jan - Mar)
├─ Week 1-2: Net-NTLMv1 환경 감사 완료
├─ Week 3-4: VS Code 보안 정책 배포
├─ Week 5-8: CRI-O 보안 패치 적용 (프로덕션 롤아웃)
└─ Week 9-12: Net-NTLMv2 마이그레이션 1단계 완료

Q2 2026 (Apr - Jun)
├─ K8s Pod Security Standards 전사 적용
├─ GPU 스케줄러 플러그인 파일럿
└─ CSAP 재인증 준비

Q3 2026 (Jul - Sep)
├─ Kerberos 전환 완료 (Net-NTLM 완전 폐기)
├─ 개발자 보안 교육 프로그램 런칭
└─ 컨테이너 보안 성숙도 평가 (외부 감사)


```
-->
-->
-->

### 9.5 KPI (핵심 성과 지표)

| KPI | 현재 (Baseline) | Q2 2026 목표 | Q4 2026 목표 |
|-----|----------------|-------------|-------------|
| **NTLM 인증 비율** | 45% (NTLMv1 포함) | 10% (NTLMv2만) | 0% (Kerberos 100%) |
| **K8s 프리빌리지드 Pod 비율** | 12% | 3% | <1% |
| **VS Code 비인가 확장 차단율** | 미측정 | 95% | 99% |
| **컨테이너 보안 스캔 커버리지** | 60% | 90% | 100% |
| **GPU 평균 활용률** | 42% | 65% | 75% |
| **보안 사고 MTTD (평균 탐지 시간)** | 72시간 | 24시간 | 4시간 |

---

## 10. Threat Hunting Queries (Kubernetes 이상 징후 탐지)

### 10.1 Kubernetes Audit Log 기반 위협 헌팅

#### Query 1: 비정상 시간대 클러스터 접근

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
// Azure Sentinel KQL
KubeAuditEvents
| where TimeGenerated between (datetime(2026-01-01) .. now())
| extend Hour = datetime_part("hour", TimeGenerated)
| where Hour < 6 or Hour > 22  // 업무 외 시간 (한국 시간 기준)
| where User !startswith "system:"
| summarize AccessCount=count(), Operations=make_set(Verb) by User, SourceIPs, bin(TimeGenerated, 1h)
| where AccessCount > 10
| extend ThreatScore = case(
    AccessCount > 50, "High",
    AccessCount > 20, "Medium",
    "Low"
)
| project TimeGenerated, User, SourceIPs, AccessCount, Operations, ThreatScore


```
-->
-->
-->

#### Query 2: Secrets 대량 접근 (데이터 유출 전조)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```spl
> # Splunk SPL...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```spl
> # Splunk SPL...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```spl
> # Splunk SPL [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```spl
# Splunk SPL
index=k8s sourcetype=kube:audit
| search objectRef.resource="secrets" verb IN ("get", "list")
| stats count by user.username, sourceIPs{}, objectRef.namespace
| where count > 50
| eval severity=case(
    count > 200, "critical",
    count > 100, "high",
    1=1, "medium"
)
| table _time, user.username, sourceIPs{}, objectRef.namespace, count, severity
| sort - count


```
-->
-->
-->

#### Query 3: 의심스러운 kubectl exec 사용

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Falco Rule (Kubernetes Runtime Security)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Falco Rule (Kubernetes Runtime Security)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Falco Rule (Kubernetes Runtime Security) [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Falco Rule (Kubernetes Runtime Security)
- rule: Suspicious kubectl exec into Pod
  desc: Detect interactive shell execution in production pods
  condition: >
    kevt and pod_exec and
    k8s.ns.name in (production_namespaces) and
    proc.name in (bash, sh, zsh) and
    not user.name in (approved_sre_users)
  output: >
    Interactive shell in production pod
    (user=%user.name pod=%k8s.pod.name namespace=%k8s.ns.name
     command=%proc.cmdline container=%container.name)
  priority: WARNING
  tags: [kubernetes, exec, shell]


```
-->
-->
-->

### 10.2 컨테이너 런타임 이상 행위 탐지

#### Query 4: 특권 컨테이너 생성 추적

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```spl
# Splunk SPL
index=k8s sourcetype=kube:audit
| search verb="create" objectRef.resource="pods"
  requestObject.spec.containers{}.securityContext.privileged=true
| eval pod_name=objectRef.name, namespace=objectRef.namespace
| table _time, user.username, namespace, pod_name, sourceIPs{}
| eval threat_level="HIGH - Privileged container created"
```

#### Query 5: hostPath 볼륨 마운트 탐지 (컨테이너 이스케이프 위험)

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```kql
> // Azure Sentinel KQL...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```kql
> // Azure Sentinel KQL...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```kql
> // Azure Sentinel KQL [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```kql
// Azure Sentinel KQL
KubeAuditEvents
| where Verb == "create" and ObjectRef_Resource == "pods"
| extend Volumes = parse_json(RequestObject).spec.volumes
| mv-expand Volume = Volumes
| where Volume.hostPath != ""
| extend HostPath = tostring(Volume.hostPath.path)
| where HostPath has_any ("/", "/etc", "/var", "/proc", "/sys")
| project TimeGenerated, User, Namespace, PodName=ObjectRef_Name, HostPath, SourceIPs
| extend Severity = case(
    HostPath in ("/", "/etc", "/var/run/docker.sock"), "Critical",
    HostPath startswith "/proc", "High",
    "Medium"
)


```
-->
-->
-->

### 10.3 네트워크 이상 징후 탐지

#### Query 6: 비정상 아웃바운드 트래픽 (C2 통신 가능성)

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```spl
# Splunk SPL (Kubernetes + Network Flow Data)
index=k8s_network OR index=firewall
| search src_pod_namespace=* dest_port IN (4444, 5555, 8888, 9000, 9999)
  OR dest_domain IN ("*.tor2web.org", "*.onion.to", "*.pastebin.com")
| stats sum(bytes_out) as total_bytes, dc(dest_ip) as unique_destinations by src_pod_name, src_namespace
| where total_bytes > 104857600 OR unique_destinations > 50
| eval severity="HIGH - Potential C2 Communication"
```

#### Query 7: Kubernetes API Server 무차별 대입 공격

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
// Azure Sentinel KQL
KubeAuditEvents
| where ResponseStatus_code == 401  // Unauthorized
| summarize FailedAttempts=count() by SourceIPs, bin(TimeGenerated, 5m)
| where FailedAttempts > 20
| join kind=inner (
    KubeAuditEvents
    | where ResponseStatus_code == 200  // Successful after failures
) on SourceIPs
| extend Severity = "Critical - Potential brute force attack followed by success"
| project TimeGenerated, SourceIPs, FailedAttempts, User, Severity


```
-->
-->
-->

### 10.4 AI/ML 워크로드 특화 헌팅

#### Query 8: GPU 크립토마이닝 패턴 탐지

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # Prometheus PromQL → Python 분석 스크립트...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # Prometheus PromQL → Python 분석 스크립트...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/python/cpython/tree/main/Doc)를 참조하세요.
> 
> ```python
> # Prometheus PromQL → Python 분석 스크립트 [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```python
# Prometheus PromQL → Python 분석 스크립트
"""
Prometheus Query:
rate(nvidia_smi_utilization_gpu_ratio[5m]) > 0.95

Python 분석:
"""
import requests
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://prometheus-server:9090"

def detect_crypto_mining():
    query = 'avg_over_time(nvidia_smi_utilization_gpu_ratio[1h]) > 0.9'
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    data = response.json()["data"]["result"]

    for item in data:
        pod_name = item["metric"]["pod"]
        namespace = item["metric"]["namespace"]
        gpu_usage = float(item["value"][1])

        # 크립토마이닝 의심 조건
        if (pod_name not in APPROVED_ML_PODS and
            gpu_usage > 0.9 and
            namespace != "ai-training"):

            print(f"[ALERT] Crypto mining suspected: {namespace}/{pod_name} GPU={gpu_usage:.2%}")
            # SIEM으로 알림 전송


```
-->
-->
-->

### 10.5 헌팅 워크플로 자동화

#### Query 9: 종합 위협 스코어 계산 (SIEM Correlation Rule)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Azure Sentinel Analytics Rule...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Azure Sentinel Analytics Rule...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Azure Sentinel Analytics Rule [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Azure Sentinel Analytics Rule
name: Kubernetes Multi-Stage Attack Detection
severity: High
query: |
  let privileged_pods = KubeAuditEvents
    | where Verb == "create" and ObjectRef_Resource == "pods"
    | where RequestObject has "privileged: true"
    | project PodName=ObjectRef_Name, Namespace, User, TimeGenerated;

  let secret_access = KubeAuditEvents
    | where ObjectRef_Resource == "secrets" and Verb in ("get", "list")
    | summarize SecretAccessCount=count() by User, TimeGenerated=bin(TimeGenerated, 10m);

  let exec_shells = KubeAuditEvents
    | where Verb == "create" and ObjectRef_Subresource == "exec"
    | project User, ExecPod=ObjectRef_Name, TimeGenerated;

  privileged_pods
  | join kind=inner (secret_access | where SecretAccessCount > 10) on User
  | join kind=inner (exec_shells) on User
  | extend ThreatScore = 90  // High confidence multi-stage attack
  | project TimeGenerated, User, PodName, SecretAccessCount, ExecPod, ThreatScore
  | extend Recommendation = "Immediate investigation required - Potential APT activity"


```
-->
-->
-->

---

## 11. 실무 체크리스트

### 11.1 이번 달 필수 점검 항목

- [ ] **Kubernetes 보안**: RBAC, Network Policy, Pod Security Standards 검토
- [ ] **VS Code 보안**: 확장 프로그램 감사, 터널링 정책 수립
- [ ] **CRI-O 업데이트**: 최신 보안 패치 적용
- [ ] **NTLM 감사**: Net-NTLMv1 사용 현황 파악 및 마이그레이션 계획
- [ ] **GPU 활용률**: 유휴 GPU 모니터링 및 재활용 정책 검토
- [ ] **플랫폼 의존성**: OSS 의존성 업데이트 상태 확인

### 11.2 한국 조직 특화 체크리스트

#### CSAP 인증 대상 기업
- [ ] **컨테이너 보안 정책**: NIPA 가이드라인 준수 여부 확인
- [ ] **로그 보관**: Kubernetes audit log 1년 이상 보관
- [ ] **암호화**: Secret 암호화 (etcd encryption at rest 활성화)
- [ ] **접근통제**: RBAC + MFA 적용 확인

#### K-ISMS-P 인증 대상 (금융/통신)
- [ ] **개인정보 처리**: 컨테이너 내 PIPA 준수 확인
- [ ] **보안 모니터링**: 24/7 보안관제 체계 구축
- [ ] **사고 대응**: 컨테이너 환경 포렌식 절차 수립
- [ ] **공급망 보안**: 컨테이너 이미지 스캔 100% 적용

---

## 12. 참고 자료 (Comprehensive References)

### 12.1 주요 출처

| 리소스 | 링크 | 설명 |
|--------|------|------|
| **CNCF 2025 Survey** | [공식 발표](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/) | Kubernetes 82% 프로덕션 사용률 원본 데이터 |
| **VS Code 위협 분석** | [Jamf Threat Labs](https://www.jamf.com/blog/threat-actors-expand-abuse-of-visual-studio-code/) | VS Code 악용 공격 벡터 및 사례 분석 |
| **CRI-O 감사 결과** | [CNCF Blog](https://www.cncf.io/blog/2026/01/16/cri-o-completes-second-ostif-audit/) | OSTIF 두 번째 보안 감사 전문 |
| **Net-NTLMv1 폐기** | [Google Threat Intel](https://cloud.google.com/blog/topics/threat-intelligence/net-ntlmv1-deprecation-rainbow-tables/) | Mandiant 레인보우 테이블 공개 및 기술 분석 |
| **GPU 스케줄링** | [CNCF Blog](https://www.cncf.io/blog/2026/01/20/reclaiming-underutilized-gpus-in-kubernetes-using-scheduler-plugins/) | Kubernetes GPU 재활용 스케줄러 플러그인 가이드 |

### 12.2 보안 프레임워크 및 표준

| 프레임워크 | 링크 | 적용 분야 |
|-----------|------|----------|
| **MITRE ATT&CK for Containers** | [https://attack.mitre.org/matrices/enterprise/containers/](https://attack.mitre.org/matrices/enterprise/containers/) | 컨테이너 환경 위협 모델링 |
| **CIS Kubernetes Benchmark** | [https://www.cisecurity.org/benchmark/kubernetes](https://www.cisecurity.org/benchmark/kubernetes) | K8s 보안 설정 기준 |
| **Kubernetes Pod Security Standards** | [https://kubernetes.io/docs/concepts/security/pod-security-standards/](https://kubernetes.io/docs/concepts/security/pod-security-standards/) | Pod 보안 정책 (Privileged/Baseline/Restricted) |
| **NIST SP 800-190** | [https://csrc.nist.gov/publications/detail/sp/800-190/final](https://csrc.nist.gov/publications/detail/sp/800-190/final) | 컨테이너 보안 애플리케이션 가이드 |

### 12.3 한국 규제 및 가이드라인

| 기관/문서 | 링크 | 설명 |
|----------|------|------|
| **KISA 클라우드 보안 가이드** | [https://www.kisa.or.kr](https://www.kisa.or.kr) | 한국인터넷진흥원 클라우드 보안 권고사항 |
| **CSAP 인증 기준** | [https://www.nipa.kr](https://www.nipa.kr) | 클라우드보안인증제 (정보통신산업진흥원) |
| **금융보안원 K8s 가이드** | [https://www.fsec.or.kr](https://www.fsec.or.kr) | 금융권 Kubernetes 보안 가이드라인 |
| **K-ISMS-P 인증 기준** | [https://isms.kisa.or.kr](https://isms.kisa.or.kr) | 정보보호 및 개인정보보호 관리체계 인증 |

### 12.4 기술 문서 및 도구

| 도구/문서 | 링크 | 용도 |
|----------|------|------|
| **Falco (Runtime Security)** | [https://falco.org](https://falco.org) | Kubernetes 런타임 위협 탐지 |
| **Trivy (Container Scanner)** | [https://github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy) | 컨테이너 이미지 취약점 스캔 |
| **kube-bench** | [https://github.com/aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench) | CIS Kubernetes Benchmark 자동 검증 |
| **NVIDIA DCGM Exporter** | [https://github.com/NVIDIA/dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter) | GPU 메트릭 수집 (Prometheus) |
| **VS Code Security Baseline** | [https://github.com/microsoft/vscode/wiki/Code-Signing](https://github.com/microsoft/vscode/wiki/Code-Signing) | Microsoft 공식 보안 가이드 |

### 12.5 학습 리소스

| 리소스 | 링크 | 대상 |
|--------|------|------|
| **Kubernetes Security Specialist (CKS)** | [https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/](https://training.linuxfoundation.org/certification/certified-kubernetes-security-specialist/) | K8s 보안 전문가 인증 |
| **CNCF Security TAG** | [https://github.com/cncf/tag-security](https://github.com/cncf/tag-security) | 클라우드 네이티브 보안 모범 사례 |
| **Kubernetes Goat** | [https://github.com/madhuakula/kubernetes-goat](https://github.com/madhuakula/kubernetes-goat) | K8s 보안 실습 환경 (취약한 클러스터) |
| **Container Security Book (Liz Rice)** | [https://www.oreilly.com/library/view/container-security/9781492056690/](https://www.oreilly.com/library/view/container-security/9781492056690/) | 컨테이너 보안 이론 및 실무 |

### 12.6 커뮤니티 및 뉴스

| 리소스 | 링크 | 설명 |
|--------|------|------|
| **Cloud Native Security News** | [https://www.cncf.io/blog/category/security/](https://www.cncf.io/blog/category/security/) | CNCF 보안 관련 최신 소식 |
| **Kubernetes Security Slack** | [#kubernetes-security on Slack](https://kubernetes.slack.com) | 글로벌 K8s 보안 커뮤니티 |
| **Korean DevSecOps Community** | [https://www.facebook.com/groups/k8skr](https://www.facebook.com/groups/k8skr) | 한국 쿠버네티스 사용자 그룹 |

### 12.7 CVE 및 보안 권고

| CVE | 영향 | 링크 |
|-----|------|------|
| **CVE-2024-21626** | runc 컨테이너 이스케이프 | [https://nvd.nist.gov/vuln/detail/CVE-2024-21626](https://nvd.nist.gov/vuln/detail/CVE-2024-21626) |
| **CVE-2022-0492** | cgroups v1 권한 상승 | [https://nvd.nist.gov/vuln/detail/CVE-2022-0492](https://nvd.nist.gov/vuln/detail/CVE-2022-0492) |
| **Kubernetes Security Advisories** | K8s 공식 보안 권고 | [https://kubernetes.io/docs/reference/issues-security/security/](https://kubernetes.io/docs/reference/issues-security/security/) |

---

## 결론

2026년 1월 클라우드 보안 동향의 핵심은 **Kubernetes의 AI 인프라 표준화**와 **개발 도구 보안**입니다. Kubernetes 82% 프로덕션 도입은 보안 팀에게 K8s 네이티브 보안 역량을 요구하며, VS Code 악용 사례 증가는 개발 환경 보안의 중요성을 상기시킵니다.

특히 Net-NTLMv1과 같은 레거시 프로토콜은 20년이 넘은 취약점에도 불구하고 여전히 활성 환경에서 발견되고 있어, 보안 부채(Security Debt) 관리의 중요성이 강조됩니다.

다음 포스팅에서는 KISA 보안 공지를 기반으로 한 랜섬웨어 예방 및 리눅스 루트킷 점검 가이드를 다루겠습니다.

---

## 참고 문헌

1. CNCF. (2026). "Kubernetes Established as the De Facto 'Operating System' for AI". [Link](https://www.cncf.io/announcements/2026/01/20/kubernetes-established-as-the-de-facto-operating-system-for-ai-as-production-use-hits-82-in-2025-cncf-annual-cloud-native-survey/)
2. Jamf Threat Labs. (2026). "Threat Actors Expand Abuse of Visual Studio Code". [Link](https://www.jamf.com/blog/threat-actors-expand-abuse-of-visual-studio-code/)
3. OSTIF. (2026). "CRI-O Completes Second OSTIF Audit". [Link](https://www.cncf.io/blog/2026/01/16/cri-o-completes-second-ostif-audit/)
4. Mandiant. (2026). "Closing the Door on Net-NTLMv1: Releasing Rainbow Tables". [Link](https://cloud.google.com/blog/topics/threat-intelligence/net-ntlmv1-deprecation-rainbow-tables/)
5. HPE/CNCF. (2026). "Reclaiming Underutilized GPUs in Kubernetes". [Link](https://www.cncf.io/blog/2026/01/20/reclaiming-underutilized-gpus-in-kubernetes-using-scheduler-plugins/)