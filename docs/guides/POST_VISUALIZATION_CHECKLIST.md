# 포스팅별 시각화 요소 체크리스트

각 포스팅에 필요한 이미지, 아키텍처, 흐름도, 표 등을 정리한 체크리스트입니다.

## 📊 시각화 요소 유형

- **🏗️ Architecture**: 아키텍처 다이어그램
- **🔄 Flow**: 프로세스 흐름도
- **📅 Timeline**: 타임라인
- **📊 Table**: 비교표/데이터 표
- **📈 Chart**: 차트/그래프
- **🎯 Summary**: 요약 인포그래픽
- **⚠️ Alert**: 경고/주의사항 박스

---

## 포스팅별 체크리스트

### 1. 클라우드 시큐리티 과정 8기 시리즈

#### 1-1. 8기 1주차: 인프라의 본질부터 보안의 미래까지
**파일**: `2025-11-26-클라우드_시큐리티_8기_1주차_인프라의_본질부터_보안의_미래까지.md`

**필요한 시각화:**
- [ ] 🏗️ **On-Premise vs Cloud 비교 아키텍처**
  - 전통적인 온프레미스 인프라 vs 클라우드 인프라
  - 주요 차이점 시각화 (비용, 확장성, 보안, 관리)
  
- [ ] 📊 **인프라 진화 타임라인**
  - 물리 서버 → 가상화 → 클라우드 → 서버리스
  - 각 단계별 특징과 장단점

- [ ] 🎯 **핵심 개념 요약 인포그래픽**
  - 클라우드의 핵심 가치 제안
  - 보안 마인드셋 전환

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style comparison diagram showing On-Premise vs Cloud infrastructure. Left side: Traditional on-premise server room with physical servers, network cables, and local storage. Right side: Cloud infrastructure with AWS logo, scalable resources, and global distribution. Style: minimalist, clean lines, professional tech illustration. Colors: Blue (#0066CC) for cloud, Gray (#666666) for on-premise. Layout: horizontal split screen comparison. Include: Key differences labeled in Korean (비용, 확장성, 보안, 관리).
```

---

#### 1-2. 8기 2주차: AWS 보안 아키텍처의 핵심, VPC부터 GuardDuty까지
**파일**: `2025-12-05-클라우드_시큐리티_8기_2주차_AWS_보안_아키텍처의_핵심_VPC부터_GuardDuty까지_완벽_정복.md`

**필요한 시각화:**
- [ ] 🏗️ **VPC 아키텍처 다이어그램**
  - Internet Gateway → Public Subnet → Private Subnet → RDS
  - NAT Gateway, Load Balancer 위치
  - Security Group 적용 범위

- [ ] 🔄 **보안 레이어 스택**
  - IAM → VPC → Security Group → GuardDuty
  - 각 레이어별 역할과 책임

- [ ] 🔄 **트래픽 흐름도**
  - 인터넷 → VPC → 애플리케이션 → 데이터베이스 접근 흐름
  - 보안 검사 포인트 표시

- [ ] 🔄 **GuardDuty 탐지 프로세스**
  - 로그 수집 → 분석 → 위협 탐지 → 알림 → 대응

- [ ] 📊 **보안 서비스 비교표**
  - GuardDuty vs Security Hub vs Config 비교

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style AWS VPC architecture diagram showing: Internet Gateway at the top, Public Subnet with NAT Gateway and Load Balancer, Private Subnet with EC2 instances and RDS database, Security Groups as protective layers around each component, GuardDuty monitoring icon watching over the entire infrastructure. Style: minimalist AWS architecture illustration. Colors: AWS orange (#FF9900), Blue for networking, Green for security. Layout: vertical flow from top (Internet) to bottom (Database). Include: Korean labels for each component (인터넷 게이트웨이, 퍼블릭 서브넷, 프라이빗 서브넷, 보안 그룹).
```

---

#### 1-3. 8기 3주차: AWS FinOps 아키텍처부터 ISMS-P 보안 감사까지
**파일**: `2025-12-12-클라우드_시큐리티_8기_3주차_AWS_FinOps_아키텍처부터_ISMS-P_보안_감사까지_완벽_공략.md`

**필요한 시각화:**
- [ ] 🏗️ **FinOps 아키텍처 다이어그램**
  - Cost Explorer → Budget → Cost Allocation Tags → Resource Optimization
  - 비용 모니터링 및 최적화 흐름

- [ ] 📊 **네트워크 비용 비교표**
  - VPC Peering vs Transit Gateway 비용 비교
  - 사용량별 비용 시뮬레이션

- [ ] 🔄 **ISMS-P 인증 프로세스 흐름도**
  - 준비 단계 → 문서화 → 심사 신청 → 현장 심사 → 인증 획득
  - 각 단계별 체크리스트

- [ ] 📈 **비용 최적화 전/후 비교 차트**
  - 리소스 최적화 전후 비용 절감 효과

- [ ] 📊 **ISMS-P 인증 항목 체크리스트 표**
  - 필수 항목별 준비 상태

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style FinOps architecture diagram showing: Cost monitoring dashboard at the top, Resource optimization engine in the middle, Cost allocation tags flowing through the system, Budget alerts and recommendations, AWS services (EC2, S3, RDS) with cost tags. Style: minimalist financial tech illustration. Colors: Green (#00AA44) for savings, Orange (#FF6600) for costs, Blue for AWS services. Layout: top-down flow showing cost management process. Include: Korean labels (비용 모니터링, 최적화, 예산 알림).
```

---

#### 1-4. 8기 4주차: 통합 보안 취약점 점검 및 ISMS-P 인증 대응 실무
**파일**: `2025-12-19-클라우드_시큐리티_8기_4주차_통합_보안_취약점_점검_및_ISMS-P_인증_대응_실무.md`

**필요한 시각화:**
- [ ] 🔄 **취약점 점검 프로세스 흐름도**
  - 자동 스캔 → 취약점 분석 → 위험도 평가 → 대응 조치 → 검증
  - 각 단계별 도구와 산출물

- [ ] 🏗️ **보안 도구 통합 아키텍처**
  - 여러 스캔 도구 → 중앙 집중식 분석 → 대시보드
  - 도구 간 연동 구조

- [ ] 📊 **위험도 매트릭스**
  - 심각도 × 영향도 매트릭스
  - 각 취약점의 위치와 우선순위

- [ ] 📊 **ISMS-P 체크리스트 표**
  - 인증 항목별 준비 상태 및 증빙 자료

- [ ] 🎯 **취약점 대응 우선순위 인포그래픽**
  - Critical → High → Medium → Low 순서

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style vulnerability scanning workflow diagram showing: Step 1: Automated scanning tools (scanner icon), Step 2: Vulnerability analysis (magnifying glass), Step 3: Risk assessment (risk matrix with severity levels), Step 4: Remediation actions (shield with checkmark), Step 5: Verification and reporting (document with checkmark). Style: minimalist security process illustration. Colors: Red (#CC0000) for critical, Orange (#FF6600) for high, Yellow (#FFCC00) for medium, Green for low. Layout: horizontal process flow from left to right. Include: Korean labels (스캔, 분석, 평가, 대응, 검증).
```

---

#### 1-5. 8기 5주차: AWS Control Tower/SCP 기반 거버넌스 및 Datadog SIEM, Cloudflare 보안
**파일**: `2025-12-24-클라우드_시큐리티_과정_8기_5주차_AWS_Control_TowerSCP_기반_거버넌스_및_Datadog_SIEM_Cloudflare_보안.md`

**필요한 시각화:**
- [ ] 🏗️ **멀티 계정 거버넌스 아키텍처**
  - Management Account → Organizational Units → Member Accounts
  - SCP 정책 적용 구조

- [ ] 🔄 **SCP 정책 적용 흐름도**
  - 정책 작성 → OU에 연결 → 계정에 상속 → 리소스 제어
  - 정책 우선순위 및 상속 규칙

- [ ] 🏗️ **SIEM 통합 아키텍처**
  - Datadog → AWS 서비스 로그 수집 → 분석 → 알림
  - 다양한 데이터 소스 통합

- [ ] 🏗️ **Cloudflare 보안 레이어**
  - WAF → DDoS 보호 → SSL/TLS → Bot Management
  - 각 레이어별 보호 기능

- [ ] 📊 **거버넌스 모델 비교표**
  - 단일 계정 vs 멀티 계정 vs Control Tower 비교

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style AWS Control Tower governance architecture showing: Management Account at the top (crown icon), Multiple Organizational Units (OU) branching down, Service Control Policies (SCP) as policy documents attached to OUs, Member accounts with different compliance levels, Guardrails and compliance checks as protective shields. Style: minimalist organizational chart style. Colors: AWS orange (#FF9900), Blue for accounts, Green for compliance. Layout: hierarchical tree structure from top to bottom. Include: Korean labels (관리 계정, 조직 단위, SCP 정책, 멤버 계정).
```

---

### 2. Post-Mortem 시리즈

#### 2-1. Cloudflare 글로벌 장애 대응 일지
**파일**: `2025-11-19-Post-Mortem_2025년_11월_18일_Cloudflare_글로벌_장애_대응_일지_우리는_무엇을_배웠나.md`

**필요한 시각화:**
- [ ] 📅 **장애 타임라인**
  - 시간별 이벤트 흐름 (18:30 ~ 20:00)
  - 각 단계별 소요 시간 및 주요 액션

- [ ] 🗺️ **장애 영향 범위 맵**
  - 전 세계 영향도 시각화
  - 모바일 vs PC 환경 차이

- [ ] 🔄 **대응 프로세스 흐름도**
  - 인지 → 조사 → 원인 파악 → 대응 → 복구 → 사후 분석
  - 각 단계별 담당자 및 액션

- [ ] 🏗️ **Multi-CDN 아키텍처 (개선 후)**
  - Traffic Manager → Cloudflare/Fastly/CloudFront
  - 자동 Failover 구조

- [ ] 📊 **장애 전/후 비교표**
  - 단일 CDN vs Multi-CDN 비교

- [ ] 🎯 **핵심 교훈 요약 인포그래픽**
  - 5가지 주요 교훈

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style incident timeline showing: Timeline from left to right, Key events marked with icons (alert, investigation, response, recovery), Color coding: Red for incident start, Orange for investigation, Yellow for response, Green for recovery, Duration indicators showing time spent in each phase. Style: minimalist timeline illustration. Colors: Red (#CC0000), Orange (#FF6600), Yellow (#FFCC00), Green (#00AA44). Layout: horizontal timeline. Include: Korean labels (인지, 조사, 대응, 복구).
```

---

#### 2-2. Karpenter v1.5.3 노드 통합 장애 분석
**파일**: `2025-10-02-Karpenter_v153_노드_통합으로_인한_대규모_장애_분석_및_해결기.md`

**필요한 시각화:**
- [ ] 🏗️ **Kubernetes 클러스터 아키텍처**
  - Control Plane → Worker Nodes → Pods
  - Karpenter Controller 위치

- [ ] 🔄 **노드 통합 전/후 비교**
  - 통합 전: 여러 노드에 분산된 Pods
  - 통합 후: 노드 통합으로 인한 Pod 재시작

- [ ] 🔄 **장애 발생 시퀀스**
  - Karpenter 노드 통합 시작 → Pod Eviction → 서비스 장애
  - 시간 순서별 이벤트

- [ ] 🏗️ **해결 방안: PodDisruptionBudget 구조**
  - PDB 적용 전/후 비교
  - 안전한 노드 통합 프로세스

- [ ] 📊 **장애 영향도 분석표**
  - 영향받은 Pod 수, 서비스 다운타임, 복구 시간

- [ ] 🎯 **모니터링 대시보드 시각화**
  - Pod 상태, 노드 리소스, Karpenter 메트릭

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style Kubernetes cluster diagram showing: Control Plane at the top, Multiple worker nodes with pods, Karpenter controller managing node lifecycle, PodDisruptionBudget as protective barriers around pod groups, Before/After comparison: Aggressive consolidation vs Safe gradual consolidation. Style: minimalist Kubernetes architecture. Colors: Kubernetes blue (#326CE5), Red for pods being terminated, Green for stable pods. Layout: vertical cluster structure. Include: Korean labels (컨트롤 플레인, 워커 노드, 파드, PDB).
```

---

### 3. 보안 가이드 시리즈

#### 3-1. AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기
**파일**: `2025-10-03-AWS에서_안전한_데이터베이스_접근_게이트웨이_구축하기_NLB__Security_Group_완벽_가이드.md`

**필요한 시각화:**
- [ ] 🏗️ **네트워크 아키텍처 다이어그램**
  - 사용자 → NLB → Bastion Host → RDS
  - Security Group 규칙 적용 범위
  - VPC 구조 (Public/Private Subnet)

- [ ] 🔄 **Zero Trust 접근 흐름도**
  - 인증 → 승인 → 네트워크 검사 → 데이터베이스 접근
  - 각 단계별 보안 검사

- [ ] 🏗️ **보안 레이어 스택**
  - Network Layer → Application Layer → Data Layer
  - 각 레이어별 보안 메커니즘

- [ ] 📊 **Security Group 규칙 비교표**
  - 허용 규칙 vs 거부 규칙
  - 최소 권한 원칙 적용

- [ ] 🏗️ **Terraform 인프라 코드 구조**
  - 모듈화된 구조도
  - 리소스 간 의존성

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style Zero Trust database gateway architecture showing: Users/Applications on the left, Network Load Balancer (NLB) in the middle as gateway, Security Groups as multiple protective layers, Database cluster on the right (RDS icon), Authentication and authorization checks at each layer, Encrypted connections (lock icons). Style: minimalist network security architecture. Colors: Blue for networking, Green for security, Orange for AWS services. Layout: horizontal flow from left (users) to right (database). Include: Korean labels (사용자, NLB 게이트웨이, 보안 그룹, 데이터베이스).
```

---

#### 3-2. Zscaler 완벽 가이드
**파일**: `2025-11-04-Zscaler_완벽_가이드_SSL_검사_샌드박스_AI_광고_유해_사이트_완벽_차단.md`

**필요한 시각화:**
- [ ] 🏗️ **Zscaler 아키텍처**
  - 사용자 디바이스 → Zscaler Cloud Gateway → 인터넷
  - 전 세계 PoP 분산 구조

- [ ] 🔄 **트래픽 흐름도**
  - 사용자 요청 → Zscaler 검사 → 인터넷/애플리케이션
  - SSL 검사 프로세스

- [ ] 🏗️ **보안 정책 스택**
  - SSL 검사 → 샌드박스 → 웹 필터링 → AI 위협 탐지
  - 각 정책별 동작 방식

- [ ] 🏗️ **ZTNA 접근 모델**
  - 전통적인 VPN vs ZTNA 비교
  - 애플리케이션별 세분화된 접근 제어

- [ ] 📊 **정책 설정 비교표**
  - 카카오톡 등 필수 앱 예외 처리
  - 보안 정책 우선순위

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style Zscaler cloud security architecture showing: Users/devices on the left (laptop, mobile icons), Zscaler Cloud Gateway in the center (cloud with shield), Security policies: SSL inspection, sandbox, web filtering, AI threat detection, Internet/Applications on the right, Encrypted tunnels connecting users to Zscaler. Style: minimalist cloud security illustration. Colors: Zscaler blue (#0066CC), Green for security, Gray for users. Layout: horizontal flow showing traffic path. Include: Korean labels (사용자, Zscaler 게이트웨이, 보안 정책, 인터넷).
```

---

#### 3-3. 이메일 발송 신뢰도 높이기: SendGrid SPF, DKIM, DMARC 설정
**파일**: `2025-06-05-이메일_발송_신뢰도_높이기_SendGrid_SPF_DKIM_DMARC_설정_완벽_가이드.md`

**필요한 시각화:**
- [ ] 🔄 **이메일 인증 프로세스 흐름도**
  - SPF 검증 → DKIM 서명 검증 → DMARC 정책 검증
  - 각 단계별 통과/실패 조건

- [ ] 🏗️ **DNS 레코드 설정 구조**
  - SPF 레코드 구조
  - DKIM 공개키 레코드 구조
  - DMARC 정책 레코드 구조

- [ ] 🔄 **인증 실패/성공 시나리오**
  - 인증 실패 시: 스팸함 이동 또는 차단
  - 인증 성공 시: 정상 수신함 도착

- [ ] 📊 **신뢰도 점수 시각화**
  - 인증 전: 낮은 신뢰도
  - 인증 후: 높은 신뢰도
  - 각 인증 단계별 점수 증가

- [ ] 📊 **SendGrid vs Google 설정 비교표**
  - 각 서비스별 설정 방법 비교

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style email authentication flow diagram showing: Email sender on the left, Three authentication steps: SPF check (shield with S), DKIM signature (key icon), DMARC policy (document), Email receiver on the right, Pass/Fail indicators for each check, Trust score meter showing authentication status. Style: minimalist email security illustration. Colors: Green for pass, Red for fail, Blue for email flow. Layout: horizontal flow from sender to receiver. Include: Korean labels (발신자, SPF 검증, DKIM 서명, DMARC 정책, 수신자).
```

---

#### 3-4. SKT 보안 이슈 완벽 대응 가이드
**파일**: `2025-04-29-SKT_보안_이슈_완벽_대응_가이드_IMEI_확인_USIMeSIM_교체_그리고_MFA의_중요성.md`

**필요한 시각화:**
- [ ] 🔄 **보안 위협 시나리오**
  - 공격자 → IMEI 탈취 → SIM 교체 공격 → 계정 탈취
  - 각 단계별 공격 벡터

- [ ] 🔄 **대응 프로세스 흐름도**
  - 위협 인지 → IMEI 확인 → SIM 차단 → 계정 보호 → 복구
  - 각 단계별 조치 사항

- [ ] 🏗️ **MFA 중요성 비교**
  - 단일 인증 (비밀번호만) vs 다중 인증 (비밀번호 + OTP/패스키)
  - 보안 강도 비교

- [ ] 📊 **보안 체크리스트 표**
  - IMEI 확인 방법
  - SIM 교체 대응 절차
  - MFA 설정 가이드

- [ ] ⚠️ **주의사항 경고 박스**
  - 주요 보안 위험 요소
  - 즉시 조치 필요 사항

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style security threat scenario showing: Attacker attempting SIM swap attack, IMEI verification as first defense layer, MFA (Multi-Factor Authentication) as second defense layer, User receiving security alerts, Account protection shield. Style: minimalist security threat illustration. Colors: Red for threats, Green for security measures, Yellow for alerts. Layout: vertical defense layers. Include: Korean labels (공격자, IMEI 확인, MFA, 보안 알림).
```

---

### 4. 인프라 구축 가이드

#### 4-1. Kubernetes Minikube & K9s 실습 가이드
**파일**: `2025-05-30-Kubernetes_Minikube_ampamp_K9s_실습_가이드_문제_해결부터_실전_테스트까지.md`

**필요한 시각화:**
- [ ] 🏗️ **Minikube 아키텍처**
  - Docker Desktop/VM → Minikube 클러스터
  - Control Plane 및 Worker Node 구조

- [ ] 🔄 **문제 해결 프로세스**
  - 에러 발생 → 로그 확인 → 원인 분석 → 해결 방법 적용 → 검증
  - 각 단계별 체크리스트

- [ ] 🎯 **K9s 대시보드 주요 기능**
  - Pod 관리, Service 관리, Deployment 관리
  - 실시간 모니터링 화면

- [ ] 📊 **실습 환경 구성도**
  - 로컬 개발 환경 구조
  - 필요한 도구 및 설정

- [ ] 📊 **문제 해결 가이드 표**
  - 흔한 에러 및 해결 방법
  - 트러블슈팅 체크리스트

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style Minikube local Kubernetes architecture showing: Docker Desktop/VM at the bottom, Minikube cluster with control plane and worker nodes, K9s terminal UI showing pods, services, deployments, Common issues and solutions as troubleshooting tips. Style: minimalist Kubernetes local development illustration. Colors: Kubernetes blue (#326CE5), Terminal green (#00FF00), Error red (#CC0000). Layout: vertical stack showing local environment. Include: Korean labels (Docker, Minikube 클러스터, K9s 대시보드).
```

---

### 5. 컨퍼런스 회고

#### 5-1. 12월 컨퍼런스 회고: AWSKRUG, OWASP, Datadog
**파일**: `2025-12-17-12월_컨퍼런스_회고_AWSKRUG_OWASP_Datadog으로_미리_보는_2025년_AI와_보안의_공존.md`

**필요한 시각화:**
- [ ] 📊 **컨퍼런스 비교표**
  - AWSKRUG vs OWASP vs Datadog
  - 주요 주제, 참석자 수, 핵심 인사이트

- [ ] 📅 **트렌드 타임라인**
  - 2025년 기술 트렌드 예측
  - AI와 보안의 융합 시점

- [ ] 🎯 **AI와 보안 융합 다이어그램**
  - AI 영역과 보안 영역의 교차점
  - 융합 분야별 예시

- [ ] 📈 **주요 인사이트 인포그래픽**
  - 각 컨퍼런스별 핵심 내용 요약
  - 실무 적용 포인트

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style conference comparison infographic showing: Three conference logos: AWSKRUG, OWASP, Datadog, Key topics for each: AI IDE, Security, Monitoring, 2025 trends timeline at the bottom, AI and Security intersection highlighted in the center. Style: minimalist infographic style. Colors: Different colors for each conference, Highlight color for trends. Layout: three-column comparison with timeline below. Include: Korean labels (컨퍼런스, 주요 주제, 트렌드).
```

---

### 6. 보안 침해 분석

#### 6-1. NPM "Shai-Hulud" 공급망 공격 완전 분석
**파일**: `2025-09-17-NPM_ampquotShai-Huludampquot_자가_복제_웜_공격_180개_이상_패키지_침해된_대규모_공급망_공격_완전_분석.md`

**필요한 시각화:**
- [ ] 🔄 **공격 벡터 다이어그램**
  - 악성 패키지 배포 → 의존성 설치 → 자동 복제 → 추가 패키지 감염
  - 공격 경로 시각화

- [ ] 🔄 **감염 전파 흐름도**
  - 초기 감염 → 의존성 트리 확산 → 대량 감염
  - 각 단계별 영향 범위

- [ ] 🔄 **대응 프로세스**
  - 탐지 → 격리 → 제거 → 업데이트 → 검증
  - 각 단계별 조치 사항

- [ ] 📊 **영향 범위 분석표**
  - 감염된 패키지 수
  - 다운로드 수
  - 영향받은 프로젝트 수

- [ ] 🎯 **공급망 보안 강화 인포그래픽**
  - 탐지 방법
  - 예방 조치
  - 모니터링 전략

**Gemini 이미지 생성 명령어:**
```
Create a nano banana style supply chain attack diagram showing: Malicious package at the top (red warning icon), Dependency tree spreading downward, Infected packages marked in red, Security scanner detecting threats (shield with alert), Remediation steps: Remove → Update → Verify. Style: minimalist security threat visualization. Colors: Red for malicious/infected, Green for safe, Yellow for warnings. Layout: tree structure showing attack propagation. Include: Korean labels (악성 패키지, 의존성, 감염 확산, 보안 스캔).
```

---

## 공통 시각화 요소

### 요약 박스 템플릿
모든 포스팅에 추가할 수 있는 핵심 내용 요약 박스:

```markdown
> **📌 핵심 요약**
> - [핵심 포인트 1]
> - [핵심 포인트 2]
> - [핵심 포인트 3]
```

### 경고/주의사항 박스
보안 관련 중요 사항 강조:

```markdown
> **⚠️ 주의사항**
> [주의해야 할 내용]
```

### 팁 박스
실무 팁 및 모범 사례:

```markdown
> **💡 실무 팁**
> [유용한 팁 내용]
```

---

## 이미지 삽입 가이드

### Markdown 이미지 삽입 형식
```markdown
![이미지 설명](assets/images/[파일명].png)
```

### 예시
```markdown
![AWS VPC 아키텍처](assets/images/2025-12-05-aws-vpc-architecture-01.png)
```

### 이미지 캡션 추가
```markdown
![AWS VPC 아키텍처](assets/images/2025-12-05-aws-vpc-architecture-01.png)
*그림 1: AWS VPC 아키텍처 구조*
```

---

## 체크리스트 사용 방법

1. **포스팅 작성 전**: 해당 포스팅의 체크리스트 확인
2. **이미지 생성**: Gemini 명령어로 이미지 생성
3. **포스팅 삽입**: 생성된 이미지를 적절한 위치에 삽입
4. **검증**: 모든 체크리스트 항목 완료 확인
5. **최종 검토**: 포스팅 내용과 이미지 일관성 확인

---

**마지막 업데이트**: 2025-12-24
