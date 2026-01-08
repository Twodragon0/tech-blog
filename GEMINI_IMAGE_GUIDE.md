# Gemini 이미지 생성 가이드

각 포스팅에 맞는 nano banana 스타일 이미지 생성 명령어 및 시각화 요소 가이드입니다.

## 📋 목차
1. [이미지 생성 기본 원칙](#이미지-생성-기본-원칙)
2. [포스팅별 이미지 가이드](#포스팅별-이미지-가이드)
3. [공통 시각화 요소](#공통-시각화-요소)

---

## 이미지 생성 기본 원칙

### 스타일 가이드
- **스타일**: nano banana (미니멀하고 깔끔한 일러스트 스타일)
- **색상**: 보안/기술 블로그에 맞는 전문적인 색상 팔레트
- **크기**: 블로그 포스팅에 최적화된 가로형 레이아웃
- **텍스트**: 한글 지원, 명확하고 읽기 쉬운 폰트

### Gemini 명령어 템플릿
```
Create a nano banana style illustration showing [주제]. 
Style: minimalist, clean, professional tech blog illustration.
Colors: [색상 팔레트]
Layout: horizontal, optimized for blog post.
Include: [포함 요소]
Text: Korean language support.
```

---

## 포스팅별 이미지 가이드

### 1. 클라우드 시큐리티 과정 시리즈

#### 1-1. 8기 1주차: 인프라의 본질부터 보안의 미래까지
**필요한 이미지:**
- [ ] **아키텍처 비교도**: On-Premise vs Cloud 비교
- [ ] **진화 타임라인**: 인프라 진화 과정
- [ ] **보안 레이어 다이어그램**: Defense in Depth 구조

**Gemini 명령어 예시:**
```
Create a nano banana style comparison diagram showing On-Premise vs Cloud infrastructure. 
Left side: Traditional on-premise server room with physical servers, network cables, and local storage.
Right side: Cloud infrastructure with AWS logo, scalable resources, and global distribution.
Style: minimalist, clean lines, professional tech illustration.
Colors: Blue (#0066CC) for cloud, Gray (#666666) for on-premise.
Layout: horizontal split screen comparison.
Include: Key differences labeled in Korean (비용, 확장성, 보안, 관리).
```

#### 1-2. 8기 2주차: AWS 보안 아키텍처의 핵심, VPC부터 GuardDuty까지
**필요한 이미지:**
- [ ] **VPC 아키텍처 다이어그램**: Public/Private Subnet 구조
- [ ] **보안 레이어 스택**: IAM → VPC → Security Group → GuardDuty
- [ ] **트래픽 흐름도**: 인터넷 → VPC → RDS 접근 흐름
- [ ] **GuardDuty 탐지 프로세스**: 위협 탐지 및 대응 흐름

**Gemini 명령어 예시:**
```
Create a nano banana style AWS VPC architecture diagram showing:
- Internet Gateway at the top
- Public Subnet with NAT Gateway and Load Balancer
- Private Subnet with EC2 instances and RDS database
- Security Groups as protective layers around each component
- GuardDuty monitoring icon watching over the entire infrastructure
Style: minimalist AWS architecture illustration
Colors: AWS orange (#FF9900), Blue for networking, Green for security
Layout: vertical flow from top (Internet) to bottom (Database)
Include: Korean labels for each component (인터넷 게이트웨이, 퍼블릭 서브넷, 프라이빗 서브넷, 보안 그룹)
```

#### 1-3. 8기 3주차: AWS FinOps 아키텍처부터 ISMS-P 보안 감사까지
**필요한 이미지:**
- [ ] **FinOps 아키텍처 다이어그램**: 비용 최적화 구조
- [ ] **네트워크 비용 비교표**: VPC Peering vs Transit Gateway
- [ ] **ISMS-P 인증 프로세스 흐름도**: 준비 → 심사 → 인증
- [ ] **비용 모니터링 대시보드**: Cost Explorer 시각화

**Gemini 명령어 예시:**
```
Create a nano banana style FinOps architecture diagram showing:
- Cost monitoring dashboard at the top
- Resource optimization engine in the middle
- Cost allocation tags flowing through the system
- Budget alerts and recommendations
- AWS services (EC2, S3, RDS) with cost tags
Style: minimalist financial tech illustration
Colors: Green (#00AA44) for savings, Orange (#FF6600) for costs, Blue for AWS services
Layout: top-down flow showing cost management process
Include: Korean labels (비용 모니터링, 최적화, 예산 알림)
```

#### 1-4. 8기 4주차: 통합 보안 취약점 점검 및 ISMS-P 인증 대응 실무
**필요한 이미지:**
- [ ] **취약점 점검 프로세스 흐름도**: 스캔 → 분석 → 대응 → 검증
- [ ] **보안 도구 통합 아키텍처**: 여러 도구 연동 구조
- [ ] **ISMS-P 체크리스트**: 인증 항목별 준비 상태
- [ ] **위험도 매트릭스**: 심각도 × 영향도 매트릭스

**Gemini 명령어 예시:**
```
Create a nano banana style vulnerability scanning workflow diagram showing:
- Step 1: Automated scanning tools (scanner icon)
- Step 2: Vulnerability analysis (magnifying glass)
- Step 3: Risk assessment (risk matrix with severity levels)
- Step 4: Remediation actions (shield with checkmark)
- Step 5: Verification and reporting (document with checkmark)
Style: minimalist security process illustration
Colors: Red (#CC0000) for critical, Orange (#FF6600) for high, Yellow (#FFCC00) for medium, Green for low
Layout: horizontal process flow from left to right
Include: Korean labels (스캔, 분석, 평가, 대응, 검증)
```

#### 1-5. 8기 5주차: AWS Control Tower/SCP 기반 거버넌스 및 Datadog SIEM, Cloudflare 보안
**필요한 이미지:**
- [ ] **멀티 계정 거버넌스 아키텍처**: Control Tower + SCP 구조
- [ ] **SCP 정책 적용 흐름도**: 정책 → 계정 → 리소스
- [ ] **SIEM 통합 아키텍처**: Datadog + AWS 서비스 연동
- [ ] **Cloudflare 보안 레이어**: WAF, DDoS 보호, SSL/TLS

**Gemini 명령어 예시:**
```
Create a nano banana style AWS Control Tower governance architecture showing:
- Management Account at the top (crown icon)
- Multiple Organizational Units (OU) branching down
- Service Control Policies (SCP) as policy documents attached to OUs
- Member accounts with different compliance levels
- Guardrails and compliance checks as protective shields
Style: minimalist organizational chart style
Colors: AWS orange (#FF9900), Blue for accounts, Green for compliance
Layout: hierarchical tree structure from top to bottom
Include: Korean labels (관리 계정, 조직 단위, SCP 정책, 멤버 계정)
```

---

### 2. Post-Mortem 시리즈

#### 2-1. Cloudflare 글로벌 장애 대응 일지
**필요한 이미지:**
- [ ] **장애 타임라인**: 시간별 이벤트 흐름
- [ ] **장애 영향 범위 맵**: 전 세계 영향도 시각화
- [ ] **대응 프로세스 흐름도**: 인지 → 조사 → 대응 → 복구
- [ ] **Multi-CDN 아키텍처**: 장애 대응 후 개선 구조

**Gemini 명령어 예시:**
```
Create a nano banana style incident timeline showing:
- Timeline from left to right
- Key events marked with icons (alert, investigation, response, recovery)
- Color coding: Red for incident start, Orange for investigation, Yellow for response, Green for recovery
- Duration indicators showing time spent in each phase
Style: minimalist timeline illustration
Colors: Red (#CC0000), Orange (#FF6600), Yellow (#FFCC00), Green (#00AA44)
Layout: horizontal timeline
Include: Korean labels (인지, 조사, 대응, 복구)
```

#### 2-2. Karpenter v1.5.3 노드 통합 장애 분석
**필요한 이미지:**
- [ ] **Kubernetes 클러스터 아키텍처**: 노드 통합 전/후 비교
- [ ] **장애 발생 시퀀스**: Pod 재시작 → 서비스 장애 흐름
- [ ] **해결 방안 다이어그램**: PodDisruptionBudget 설정 구조
- [ ] **모니터링 대시보드**: 장애 지표 시각화

**Gemini 명령어 예시:**
```
Create a nano banana style Kubernetes cluster diagram showing:
- Control Plane at the top
- Multiple worker nodes with pods
- Karpenter controller managing node lifecycle
- PodDisruptionBudget as protective barriers around pod groups
- Before/After comparison: Aggressive consolidation vs Safe gradual consolidation
Style: minimalist Kubernetes architecture
Colors: Kubernetes blue (#326CE5), Red for pods being terminated, Green for stable pods
Layout: vertical cluster structure
Include: Korean labels (컨트롤 플레인, 워커 노드, 파드, PDB)
```

---

### 3. 보안 가이드 시리즈

#### 3-1. AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기
**필요한 이미지:**
- [ ] **네트워크 아키텍처**: NLB + Security Group 구조
- [ ] **Zero Trust 접근 흐름도**: 인증 → 승인 → 접근
- [ ] **보안 레이어 스택**: 다중 방어 계층
- [ ] **Terraform 인프라 코드 구조**: IaC 구조도

**Gemini 명령어 예시:**
```
Create a nano banana style Zero Trust database gateway architecture showing:
- Users/Applications on the left
- Network Load Balancer (NLB) in the middle as gateway
- Security Groups as multiple protective layers
- Database cluster on the right (RDS icon)
- Authentication and authorization checks at each layer
- Encrypted connections (lock icons)
Style: minimalist network security architecture
Colors: Blue for networking, Green for security, Orange for AWS services
Layout: horizontal flow from left (users) to right (database)
Include: Korean labels (사용자, NLB 게이트웨이, 보안 그룹, 데이터베이스)
```

#### 3-2. Zscaler 완벽 가이드
**필요한 이미지:**
- [ ] **Zscaler 아키텍처**: 클라우드 보안 게이트웨이 구조
- [ ] **트래픽 흐름도**: 사용자 → Zscaler → 인터넷
- [ ] **보안 정책 스택**: SSL 검사 → 샌드박스 → 필터링
- [ ] **ZTNA 접근 모델**: Zero Trust 네트워크 접근

**Gemini 명령어 예시:**
```
Create a nano banana style Zscaler cloud security architecture showing:
- Users/devices on the left (laptop, mobile icons)
- Zscaler Cloud Gateway in the center (cloud with shield)
- Security policies: SSL inspection, sandbox, web filtering, AI threat detection
- Internet/Applications on the right
- Encrypted tunnels connecting users to Zscaler
Style: minimalist cloud security illustration
Colors: Zscaler blue (#0066CC), Green for security, Gray for users
Layout: horizontal flow showing traffic path
Include: Korean labels (사용자, Zscaler 게이트웨이, 보안 정책, 인터넷)
```

#### 3-3. 이메일 발송 신뢰도 높이기: SendGrid SPF, DKIM, DMARC 설정
**필요한 이미지:**
- [ ] **이메일 인증 프로세스**: SPF → DKIM → DMARC 검증 흐름
- [ ] **DNS 레코드 설정 구조**: 각 레코드 타입별 설명
- [ ] **인증 실패/성공 시나리오**: 차단 vs 통과 흐름
- [ ] **신뢰도 점수 시각화**: 인증 전/후 비교

**Gemini 명령어 예시:**
```
Create a nano banana style email authentication flow diagram showing:
- Email sender on the left
- Three authentication steps: SPF check (shield with S), DKIM signature (key icon), DMARC policy (document)
- Email receiver on the right
- Pass/Fail indicators for each check
- Trust score meter showing authentication status
Style: minimalist email security illustration
Colors: Green for pass, Red for fail, Blue for email flow
Layout: horizontal flow from sender to receiver
Include: Korean labels (발신자, SPF 검증, DKIM 서명, DMARC 정책, 수신자)
```

#### 3-4. SKT 보안 이슈 완벽 대응 가이드
**필요한 이미지:**
- [ ] **보안 위협 시나리오**: IMEI 탈취 → SIM 교체 공격 흐름
- [ ] **대응 프로세스**: 확인 → 차단 → 복구 단계
- [ ] **MFA 중요성**: 단일 인증 vs 다중 인증 비교
- [ ] **보안 체크리스트**: 단계별 확인 사항

**Gemini 명령어 예시:**
```
Create a nano banana style security threat scenario showing:
- Attacker attempting SIM swap attack
- IMEI verification as first defense layer
- MFA (Multi-Factor Authentication) as second defense layer
- User receiving security alerts
- Account protection shield
Style: minimalist security threat illustration
Colors: Red for threats, Green for security measures, Yellow for alerts
Layout: vertical defense layers
Include: Korean labels (공격자, IMEI 확인, MFA, 보안 알림)
```

---

### 4. 인프라 구축 가이드

#### 4-1. Kubernetes Minikube & K9s 실습 가이드
**필요한 이미지:**
- [ ] **Minikube 아키텍처**: 로컬 Kubernetes 구조
- [ ] **문제 해결 프로세스**: 에러 → 진단 → 해결 흐름
- [ ] **K9s 대시보드**: 주요 기능 시각화
- [ ] **실습 환경 구성도**: 개발 환경 구조

**Gemini 명령어 예시:**
```
Create a nano banana style Minikube local Kubernetes architecture showing:
- Docker Desktop/VM at the bottom
- Minikube cluster with control plane and worker nodes
- K9s terminal UI showing pods, services, deployments
- Common issues and solutions as troubleshooting tips
Style: minimalist Kubernetes local development illustration
Colors: Kubernetes blue (#326CE5), Terminal green (#00FF00), Error red (#CC0000)
Layout: vertical stack showing local environment
Include: Korean labels (Docker, Minikube 클러스터, K9s 대시보드)
```

---

### 5. 컨퍼런스 회고

#### 5-1. 12월 컨퍼런스 회고: AWSKRUG, OWASP, Datadog
**필요한 이미지:**
- [ ] **컨퍼런스 비교표**: 각 컨퍼런스 특징 비교
- [ ] **트렌드 타임라인**: 2025년 기술 트렌드
- [ ] **AI와 보안 융합**: 두 영역의 교차점 시각화
- [ ] **주요 인사이트**: 핵심 내용 요약

**Gemini 명령어 예시:**
```
Create a nano banana style conference comparison infographic showing:
- Three conference logos: AWSKRUG, OWASP, Datadog
- Key topics for each: AI IDE, Security, Monitoring
- 2025 trends timeline at the bottom
- AI and Security intersection highlighted in the center
Style: minimalist infographic style
Colors: Different colors for each conference, Highlight color for trends
Layout: three-column comparison with timeline below
Include: Korean labels (컨퍼런스, 주요 주제, 트렌드)
```

---

### 6. 보안 침해 분석

#### 6-1. NPM "Shai-Hulud" 공급망 공격 완전 분석
**필요한 이미지:**
- [ ] **공격 벡터 다이어그램**: 공격 경로 시각화
- [ ] **감염 전파 흐름도**: 패키지 → 의존성 → 감염 확산
- [ ] **대응 프로세스**: 탐지 → 격리 → 복구
- [ ] **영향 범위**: 감염된 패키지 수 및 영향도

**Gemini 명령어 예시:**
```
Create a nano banana style supply chain attack diagram showing:
- Malicious package at the top (red warning icon)
- Dependency tree spreading downward
- Infected packages marked in red
- Security scanner detecting threats (shield with alert)
- Remediation steps: Remove → Update → Verify
Style: minimalist security threat visualization
Colors: Red for malicious/infected, Green for safe, Yellow for warnings
Layout: tree structure showing attack propagation
Include: Korean labels (악성 패키지, 의존성, 감염 확산, 보안 스캔)
```

---

### 7. 블록체인 및 암호화폐 보안

#### 7-1. 블록체인 암호화폐 보안 완벽 가이드
**필요한 이미지:**
- [ ] **블록체인 보안 위협 다이어그램**: 주요 위협 유형 시각화
- [ ] **스마트 컨트랙트 보안 분석 도구 비교**: Slither, Mythril, Securify 비교
- [ ] **DevSecOps 파이프라인 통합**: CI/CD에 보안 검사 통합 흐름도
- [ ] **스마트 컨트랙트 취약점 예시**: Reentrancy, Integer Overflow 등
- [ ] **지갑 보안 아키텍처**: 콜드/핫 월렛 구조 및 키 관리
- [ ] **거래소 보안 레이어**: 다중 방어 계층 구조

**Gemini 명령어 예시:**

**블록체인 보안 위협 다이어그램:**
```
Create a nano banana style blockchain security threats diagram showing:
- Blockchain network at the center (chain of blocks)
- Smart contract vulnerabilities (red warning icons): Reentrancy, Integer Overflow, Access Control
- Network-level threats (orange icons): 51% Attack, Sybil Attack, DDoS
- Wallet threats (yellow icons): Private Key Leak, Phishing, Social Engineering
- Exchange threats (purple icons): Hot Wallet Hacking, Insider Attack, API Key Leak
- Security tools protecting the network (green shields): Slither, Mythril, Securify
Style: minimalist blockchain security illustration
Colors: Red (#CC0000) for vulnerabilities, Orange (#FF6600) for network threats, Yellow (#FFCC00) for wallet threats, Purple (#9966CC) for exchange threats, Green (#00AA44) for security tools
Layout: central blockchain with threats surrounding it
Include: Korean labels (블록체인, 스마트 컨트랙트 취약점, 네트워크 위협, 지갑 위협, 거래소 위협, 보안 도구)
```

**DevSecOps 파이프라인 통합:**
```
Create a nano banana style DevSecOps pipeline diagram showing:
- Step 1: Code Commit (developer icon)
- Step 2: Static Analysis with Slither (shield with S icon)
- Step 3: Symbolic Execution with Mythril (shield with M icon)
- Step 4: Dependency Audit (package icon with checkmark)
- Step 5: Security Testing (test tube icon)
- Step 6: Deployment (rocket icon)
- Security gates at each step (red/green indicators)
- GitHub Actions workflow integration
Style: minimalist CI/CD pipeline illustration
Colors: Blue (#0066CC) for pipeline, Green (#00AA44) for passed checks, Red (#CC0000) for failed checks
Layout: horizontal flow from left to right
Include: Korean labels (코드 커밋, 정적 분석, 심볼릭 실행, 의존성 검사, 보안 테스트, 배포)
```

**스마트 컨트랙트 보안 도구 비교:**
```
Create a nano banana style comparison infographic showing three security tools:
- Slither (left): Static analysis tool, 90+ vulnerability patterns, Fast scanning, CI/CD integration
- Mythril (center): Symbolic execution, Deep analysis, Reentrancy detection, Gas optimization
- Securify 2.0 (right): Pattern matching + Data flow, 37+ security patterns, Web interface, High accuracy
Each tool with its logo, key features, and use cases
Style: minimalist comparison chart
Colors: Different colors for each tool (Blue, Green, Orange)
Layout: three-column comparison
Include: Korean labels (Slither, Mythril, Securify, 정적 분석, 심볼릭 실행, 패턴 매칭)
```

**지갑 보안 아키텍처:**
```
Create a nano banana style wallet security architecture showing:
- User at the top (person icon)
- Hot Wallet (orange wallet icon): Small amount, Multi-signature, Online
- Cold Wallet (blue wallet icon): Large amount, Hardware wallet, Offline
- Key Management System (key icon): Encrypted storage, Key splitting, Backup
- Security Layers: Encryption, Multi-signature, HSM (Hardware Security Module)
- Connection arrows showing secure paths
Style: minimalist wallet security illustration
Colors: Orange (#FF6600) for hot wallet, Blue (#0066CC) for cold wallet, Green (#00AA44) for security
Layout: vertical hierarchy from user to wallets
Include: Korean labels (사용자, 핫 월렛, 콜드 월렛, 키 관리, 암호화, 다중 서명)
```

**스마트 컨트랙트 취약점 예시:**
```
Create a nano banana style smart contract vulnerability examples showing:
- Reentrancy Attack: Function call loop with attacker exploiting reentry
- Integer Overflow: Number calculation exceeding limit causing wrap-around
- Access Control: Unauthorized user accessing admin function
- Oracle Manipulation: External data source being manipulated
Each vulnerability with visual representation and prevention method
Style: minimalist security vulnerability illustration
Colors: Red (#CC0000) for vulnerabilities, Green (#00AA44) for prevention
Layout: four-panel grid showing each vulnerability
Include: Korean labels (재진입 공격, 정수 오버플로우, 접근 제어, 오라클 조작)
```

**거래소 보안 레이어:**
```
Create a nano banana style exchange security layers diagram showing:
- External users/applications at the top
- Layer 1: DDoS Protection (shield icon)
- Layer 2: WAF (Web Application Firewall) (firewall icon)
- Layer 3: Authentication & Authorization (lock icon with key)
- Layer 4: API Security (API icon with shield)
- Layer 5: Hot Wallet (small amount, orange)
- Layer 6: Cold Wallet (large amount, blue, offline)
- Monitoring and alerting system surrounding all layers
Style: minimalist layered security architecture
Colors: Different colors for each layer (Red, Orange, Yellow, Green, Blue, Purple)
Layout: vertical layers from top (users) to bottom (cold wallet)
Include: Korean labels (사용자, DDoS 방어, WAF, 인증/인가, API 보안, 핫 월렛, 콜드 월렛, 모니터링)
```

---

## 공통 시각화 요소

### 아키텍처 다이어그램 템플릿
```
Create a nano banana style [서비스명] architecture diagram showing:
- [주요 컴포넌트 1] with [설명]
- [주요 컴포넌트 2] with [설명]
- [연결 관계] between components
- [보안 레이어] as protective elements
Style: minimalist [카테고리] architecture illustration
Colors: [색상 팔레트]
Layout: [레이아웃 타입]
Include: Korean labels ([한글 라벨])
```

### 흐름도 템플릿
```
Create a nano banana style [프로세스명] workflow diagram showing:
- Step 1: [단계 1] (icon)
- Step 2: [단계 2] (icon)
- Step 3: [단계 3] (icon)
- Decision points with yes/no branches
- Final outcome
Style: minimalist process flow illustration
Colors: [단계별 색상]
Layout: horizontal/vertical flow
Include: Korean labels ([한글 라벨])
```

### 비교표 템플릿
```
Create a nano banana style comparison infographic showing:
- [항목 A] vs [항목 B] side by side
- Key differences highlighted
- Pros and cons for each
- Recommendation indicator
Style: minimalist comparison chart
Colors: [각 항목별 색상]
Layout: side-by-side comparison
Include: Korean labels ([한글 라벨])
```

### 타임라인 템플릿
```
Create a nano banana style timeline showing:
- Timeline from [시작] to [종료]
- Key milestones marked with icons
- Color coding by [카테고리]
- Duration indicators
Style: minimalist timeline illustration
Colors: [단계별 색상]
Layout: horizontal timeline
Include: Korean labels ([한글 라벨])
```

---

## 이미지 파일 명명 규칙

### 파일명 형식
```
[날짜]-[포스팅-제목]-[이미지-타입]-[번호].png
```

### 예시
```
2025-12-24-aws-control-tower-architecture-01.png
2025-12-24-aws-control-tower-scp-flow-02.png
2025-11-19-cloudflare-incident-timeline-01.png
```

### 이미지 타입 약어
- `architecture`: 아키텍처 다이어그램
- `flow`: 흐름도
- `timeline`: 타임라인
- `comparison`: 비교표/인포그래픽
- `diagram`: 일반 다이어그램
- `process`: 프로세스도

---

## 체크리스트

각 포스팅 작성 시 확인 사항:

- [ ] 포스팅 주제에 맞는 아키텍처 다이어그램 생성
- [ ] 복잡한 프로세스는 흐름도로 시각화
- [ ] 비교가 필요한 내용은 비교표/인포그래픽 생성
- [ ] 시간 순서가 중요한 내용은 타임라인 생성
- [ ] 핵심 내용은 요약 박스/인포그래픽으로 강조
- [ ] 모든 이미지에 한글 라벨 포함
- [ ] 이미지 파일명 규칙 준수
- [ ] 포스팅 내용과 이미지 일관성 확인

---

## 참고 사항

1. **이미지 크기**: 블로그 포스팅에 최적화된 가로형 (1200x800px 권장)
2. **해상도**: 고해상도 (300 DPI)로 생성하여 선명도 확보
3. **스타일 일관성**: 모든 이미지가 nano banana 스타일로 통일
4. **색상 팔레트**: 보안/기술 블로그에 맞는 전문적인 색상 사용
5. **접근성**: 색상만으로 구분하지 않고 아이콘/라벨 병행

---

**마지막 업데이트**: 2026-01-08
