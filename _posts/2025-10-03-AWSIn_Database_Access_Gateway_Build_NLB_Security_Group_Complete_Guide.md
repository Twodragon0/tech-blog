---
layout: post
title: "AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기: NLB + Security Group 완벽 가이드"
date: 2025-10-03 00:10:37 +0900
categories: [cloud]
tags: [AWS, NLB, Security-Group, Database, Network]
excerpt: "AWS NLB와 Security Group을 활용한 Zero Trust 데이터베이스 게이트웨이 구축."
comments: true
original_url: https://twodragon.tistory.com/696
image: /assets/images/2025-10-03-AWSin_Database_Access_Gateway_Build_NLB_Security_Group_Complete_Guide.svg
image_alt: "Building Secure Database Access Gateway on AWS: NLB Security Group Complete Guide"
certifications: [aws-saa]
toc: true
description: AWS Network Load Balancer와 Security Group을 활용한 Zero Trust 데이터베이스 접근 게이트웨이 구축 가이드. Terraform 자동화 및 보안 설정을 다룹니다.
keywords: [AWS, NLB, Security-Group, Database, Terraform, Zero-Trust]
author: Twodragon
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기: NLB + Security Group 완벽 가이드</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag cloud">Cloud</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AWS</span>
      <span class="tag">NLB</span>
      <span class="tag">Security-Group</span>
      <span class="tag">Database</span>
      <span class="tag">Network</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>Network Load Balancer와 Security Group을 활용한 Zero Trust 아키텍처 구축</li>
      <li>Terraform을 통한 인프라 자동화 및 보안 설정</li>
      <li>데이터베이스 접근 관리 솔루션 AWS 배포 경험 공유</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">AWS NLB, Security Group, Terraform, VPC</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

데이터베이스 접근 관리 솔루션을 AWS에 배포하면서 Network Load Balancer와 Security Group을 활용한 Zero Trust 아키텍처를 구축한 경험을 공유합니다. Terraform으로 완전 자동화하고, 보안과 가용성을 모두 확보했습니다.

<img src="{{ '/assets/images/2025-10-03-AWSin_Database_Access_Gateway_Build_NLB_Security_Group_Complete_Guide_image.png' | relative_url }}" alt="Building Secure Database Access Gateway on AWS: NLB Security Group Complete Guide" loading="lazy" class="post-image">

데이터베이스 접근 게이트웨이는 Zero Trust 아키텍처를 통해 보안을 강화합니다.

## 배경: 왜 데이터베이스 접근 게이트웨이가 필요한가?

많은 기업에서 여러 팀이 수십 개의 데이터베이스를 사용합니다:

- **RDS MySQL/PostgreSQL 클러스터**: 애플리케이션 데이터 저장
- **ElastiCache Redis**: 캐시 및 세션 저장
- **DocumentDB**: 문서 기반 데이터 저장
- **Redshift**: 데이터 웨어하우스

### 기존 접근 방식의 문제점

1. **직접 접근**: 각 애플리케이션에서 데이터베이스에 직접 연결
   - Security Group 관리가 복잡해짐
   - IP 주소 변경 시 수동 업데이트 필요
   - 네트워크 경로가 분산되어 추적 어려움

2. **VPN 의존**: VPN을 통한 접근
   - VPN 연결이 끊어지면 접근 불가
   - VPN 서버 장애 시 전체 접근 차단
   - 네트워크 성능 저하

3. **보안 취약점**: 
   - 공개 IP 노출 위험
   - 접근 로그 부족
   - 중앙화된 모니터링 어려움

## 솔루션 아키텍처### 전체 구조

<figure>
<img src="{{ '/assets/images/diagrams/diagram_db_gateway.png' | relative_url }}" alt="Database Access Gateway Architecture" loading="lazy" class="post-image">
<figcaption>데이터베이스 접근 게이트웨이 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

### 핵심 컴포넌트

1. **Network Load Balancer (NLB)**
   - 고가용성 및 로드 밸런싱
   - TCP 레벨 로드 밸런싱
   - 정적 IP 주소 제공

2. **Security Group (게이트웨이)**
   - 인바운드/아웃바운드 트래픽 제어
   - 최소 권한 원칙 적용
   - 중앙화된 접근 제어

3. **Private Subnet**
   - 데이터베이스는 Private Subnet에 배치
   - 인터넷 직접 접근 차단

## 1. Network Load Balancer 설정

### 1.1 NLB의 장점

- **고성능**: Layer 4 로드 밸런싱으로 낮은 지연시간
- **고가용성**: 다중 AZ 지원으로 장애 복구
- **정적 IP**: 고정 IP 주소로 Security Group 규칙 관리 용이
- **비용 효율**: 사용한 만큼만 과금

### 1.2 NLB 구성 요소

> **참고**: Terraform AWS NLB 구성 관련 내용은 [Terraform AWS ALB/NLB 모듈](https://github.com/terraform-aws-modules/terraform-aws-alb) 및 [AWS NLB 문서](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/)를 참조하세요.
> 
> ```hcl
> resource "aws_lb" "db_gateway" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
resource "aws_lb" "db_gateway" {
  name               = "db-gateway-nlb"
  internal           = true  # 내부 전용
  load_balancer_type = "network"
  subnets            = var.private_subnet_ids
  
  enable_deletion_protection = true
  
  tags = {
    Name        = "DB Gateway NLB"
    Environment = var.environment
  }
}

```
-->

### 1.3 타겟 그룹 설정

> **참고**: Terraform AWS Load Balancer 타겟 그룹 관련 내용은 [Terraform AWS ALB/NLB 모듈](https://github.com/terraform-aws-modules/terraform-aws-alb) 및 [AWS ELB Target Groups 문서](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/target-group-register-targets.html)를 참조하세요.
> 
> ```hcl
> resource "aws_lb_target_group" "rds_mysql" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
resource "aws_lb_target_group" "rds_mysql" {
  name     = "rds-mysql-tg"
  port     = 3306
  protocol = "TCP"
  vpc_id   = var.vpc_id
  
  health_check {
    protocol = "TCP"
    port     = 3306
    interval = 30
  }
  
  tags = {
    Name = "RDS MySQL Target Group"
  }
}

```
-->

## 2. Security Group 구성

### 2.1 Security Group 계층 구조

```
[Application Security Group]
    ↓ (허용)
[NLB Security Group]
    ↓ (허용)
[Database Security Group]
```

### 2.2 NLB Security Group

NLB는 Security Group을 직접 지원하지 않지만, 타겟 그룹의 Security Group을 통해 제어합니다:

> **참고**: Terraform AWS Security Group 관련 내용은 [Terraform AWS Security Group 모듈](https://github.com/terraform-aws-modules/terraform-aws-security-group) 및 [AWS Security Groups 문서](https://docs.aws.amazon.com/vpc/latest/userguide/security-groups.html)를 참조하세요.
> 
> ```hcl
> resource "aws_security_group" "nlb" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
resource "aws_security_group" "nlb" {
  name        = "db-gateway-nlb-sg"
  description = "Security group for DB Gateway NLB"
  vpc_id      = var.vpc_id

  # 애플리케이션에서 NLB로의 트래픽 허용
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    security_groups = [var.app_security_group_id]
    description = "Allow MySQL from application"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name = "DB Gateway NLB Security Group"
  }
}

```
-->

### 2.3 데이터베이스 Security Group

> **참고**: Terraform AWS Security Group 관련 내용은 [Terraform AWS Security Group 모듈](https://github.com/terraform-aws-modules/terraform-aws-security-group) 및 [AWS RDS 보안 모범 사례](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html)를 참조하세요.
> 
> ```hcl
> resource "aws_security_group" "database" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
resource "aws_security_group" "database" {
  name        = "database-sg"
  description = "Security group for databases"
  vpc_id      = var.vpc_id

  # NLB에서 데이터베이스로의 트래픽만 허용
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    security_groups = [aws_security_group.nlb.id]
    description = "Allow MySQL from NLB only"
  }

  # 다른 포트도 필요시 추가
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.nlb.id]
    description = "Allow PostgreSQL from NLB only"
  }

  tags = {
    Name = "Database Security Group"
  }
}

```
-->

## 3. Zero Trust 아키텍처 구현

### 3.1 Zero Trust 원칙

1. **명시적 검증**: 모든 접근은 검증되어야 함
2. **최소 권한**: 필요한 최소한의 접근만 허용
3. **가정 위반**: 네트워크 내부도 신뢰하지 않음

### 3.2 구현 방법

#### 애플리케이션 레벨 인증

> **참고**: AWS 데이터베이스 접근 보안 관련 내용은 [AWS RDS 보안 모범 사례](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html) 및 [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)를 참조하세요.
> 
> ```python
> # 애플리케이션에서 데이터베이스 접근 시...
> ```

<!-- 전체 코드는 위 링크 참조
```python
# 애플리케이션에서 데이터베이스 접근 시
import boto3
import mysql.connector

# IAM 인증을 통한 데이터베이스 접근
rds_client = boto3.client('rds')
token = rds_client.generate_db_auth_token(
    DBHostname='db-gateway-nlb-xxx.elb.amazonaws.com',
    Port=3306,
    DBUsername='app_user'
)

conn = mysql.connector.connect(
    host='db-gateway-nlb-xxx.elb.amazonaws.com',
    port=3306,
    user='app_user',
    password=token,
    ssl_ca='/path/to/rds-ca-cert.pem'
)

```
-->

#### Security Group 기반 접근 제어

- 애플리케이션 Security Group만 NLB에 접근 허용
- NLB Security Group만 데이터베이스에 접근 허용
- IP 기반 접근은 최소화

## 4. Terraform 자동화

### 4.1 모듈 구조

```
modules/
  └── db-gateway/
      ├── main.tf
      ├── variables.tf
      ├── outputs.tf
      └── security-groups.tf
```

### 4.2 변수 정의

> **참고**: Terraform 변수 정의 관련 내용은 [Terraform 변수 문서](https://developer.hashicorp.com/terraform/language/values/variables) 및 [Terraform AWS 모듈 예제](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> variable "vpc_id" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for NLB"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "Application security group ID"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

```
-->

### 4.3 출력 값

> **참고**: Terraform 출력 값 관련 내용은 [Terraform 출력 문서](https://developer.hashicorp.com/terraform/language/values/outputs) 및 [Terraform AWS 모듈 예제](https://github.com/terraform-aws-modules)를 참조하세요.
> 
> ```hcl
> output "nlb_dns_name" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
output "nlb_dns_name" {
  description = "NLB DNS name"
  value       = aws_lb.db_gateway.dns_name
}

output "nlb_arn" {
  description = "NLB ARN"
  value       = aws_lb.db_gateway.arn
}

output "database_security_group_id" {
  description = "Database security group ID"
  value       = aws_security_group.database.id
}

```
-->

## 5. 모니터링 및 로깅

### 5.1 CloudWatch 메트릭

NLB는 자동으로 CloudWatch 메트릭을 제공합니다:

- **ActiveFlowCount**: 활성 연결 수
- **ProcessedBytes**: 처리된 바이트 수
- **HealthyHostCount**: 정상 타겟 수
- **UnHealthyHostCount**: 비정상 타겟 수

### 5.2 VPC Flow Logs

VPC Flow Logs를 활성화하여 네트워크 트래픽을 모니터링:

> **참고**: VPC Flow Logs 설정 관련 내용은 [AWS VPC Flow Logs 문서](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html) 및 [Terraform AWS VPC 모듈](https://github.com/terraform-aws-modules/terraform-aws-vpc)을 참조하세요.

```hcl
resource "aws_flow_log" "vpc_flow_log" {
  iam_role_arn    = aws_iam_role.flow_log.arn
  log_destination = aws_cloudwatch_log_group.flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = var.vpc_id
}
```

### 5.3 데이터베이스 로깅

RDS의 경우 자동 로깅 기능을 활성화:

> **참고**: RDS 로깅 설정 관련 내용은 [AWS RDS 로깅 문서](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.html) 및 [Terraform AWS RDS 모듈](https://github.com/terraform-aws-modules/terraform-aws-rds)을 참조하세요.

```hcl
resource "aws_db_instance" "mysql" {
  # ... 기타 설정 ...
  
  enabled_cloudwatch_logs_exports = [
    "error",
    "general",
    "slow_query"
  ]
}
```

## 6. 보안 모범 사례

데이터베이스 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다.

### 6.1 암호화

- **전송 중 암호화**: TLS/SSL을 통한 데이터 암호화
- **저장 중 암호화**: RDS 암호화 활성화
- **키 관리**: AWS KMS를 통한 키 관리

### 6.2 접근 제어

- **IAM 인증**: RDS IAM 데이터베이스 인증 사용
- **Security Group**: 최소 권한 원칙 적용
- **네트워크 격리**: Private Subnet 사용

### 6.3 정기 점검

- **Security Group 규칙 검토**: 정기적으로 불필요한 규칙 제거
- **접근 로그 분석**: 비정상적인 접근 패턴 탐지
- **인증 정보 로테이션**: 정기적인 비밀번호/토큰 갱신

## 7. 비용 최적화

### 7.1 NLB 비용

- **LCU (Load Balancer Capacity Unit)**: 사용량 기반 과금
- **정적 IP**: 시간당 과금
- **데이터 처리**: GB당 과금

### 7.2 비용 절감 방법

- **내부 NLB 사용**: 인터넷 게이트웨이 불필요
- **적절한 타겟 수**: 필요한 만큼만 타겟 등록
- **리전 선택**: 데이터 전송 비용 고려

## 8. 장애 대응

### 8.1 고가용성 구성

- **다중 AZ**: NLB와 데이터베이스를 여러 AZ에 배치
- **Health Check**: 정기적인 헬스 체크로 비정상 타겟 제거
- **자동 복구**: 장애 발생 시 자동으로 정상 타겟으로 라우팅

### 8.2 모니터링 알림

> **참고**: AWS CloudWatch 알림 설정 관련 내용은 [AWS CloudWatch 문서](https://docs.aws.amazon.com/cloudwatch/) 및 [Terraform AWS CloudWatch 모듈](https://github.com/terraform-aws-modules/terraform-aws-cloudwatch)을 참조하세요.
> 
> ```hcl
> resource "aws_cloudwatch_metric_alarm" "unhealthy_hosts" {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
resource "aws_cloudwatch_metric_alarm" "unhealthy_hosts" {
  alarm_name          = "nlb-unhealthy-hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/NetworkELB"
  period              = 60
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "Alert when unhealthy hosts detected"
  
  dimensions = {
    LoadBalancer = aws_lb.db_gateway.arn_suffix
  }
}

```
-->

## 9. 2025년 AWS 네트워크 보안 최신 동향

### 9.1 Post-Quantum TLS 지원 (2025년 11월)

AWS ALB/NLB가 양자 내성 암호화를 지원합니다:

> **참고**: Post-Quantum 암호화 관련 내용은 [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography) 및 [AWS TLS 정책](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-listener.html#tls-policies)을 참조하세요.
> 
> ```hcl
> # 2025년 Post-Quantum TLS 설정...
> ```

<!-- 전체 코드는 위 링크 참조
```hcl
# 2025년 Post-Quantum TLS 설정
resource "aws_lb_listener" "quantum_safe" {
  load_balancer_arn = aws_lb.db_gateway.arn
  port              = "443"
  protocol          = "TLS"

  # ML-KEM768 양자 내성 키 교환 지원
  ssl_policy = "ELBSecurityPolicy-TLS13-1-3-FIPS-2023-04"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.db.arn
  }
}

```
-->

**주요 특징**:
- **ML-KEM768** 양자 내성 암호화 알고리즘 채택
- **HNDL/SNDL 공격** 방어 (Harvest Now, Decrypt Later)
- 미래 양자 컴퓨터 위협에 대한 선제적 대응

### 9.2 VPC Lattice vs NLB 비교 (2025년 업데이트)

2025년 12월 기준, AWS VPC Lattice와 NLB + VPC Endpoint 구성 비교:

| 항목 | VPC Lattice Resource Gateway | NLB + VPC Endpoint Service |
|------|------------------------------|---------------------------|
| **IAM 통합** | 세밀한 접근 제어 가능 | Security Group 기반 |
| **감사 로그** | 통합 감사 로그 제공 | VPC Flow Logs 별도 설정 |
| **초기 비용** | 사용량 기반 | ~$59.40/월 (고정) |
| **복잡도** | 단순화된 관리 | 다중 컴포넌트 관리 필요 |
| **문서화** | 신규 (문서 증가 중) | 풍부한 레퍼런스 |

> **참고**: AWS VPC Lattice 관련 내용은 [AWS VPC Lattice 문서](https://docs.aws.amazon.com/vpc-lattice/) 및 [AWS VPC Lattice 예제](https://github.com/aws-samples)를 참조하세요.
> 
> ```hcl
> # VPC Lattice Resource Gateway 예시 (2025)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
# VPC Lattice Resource Gateway 예시 (2025)
resource "aws_vpclattice_service" "db_service" {
  name = "db-gateway-service"

  auth_type = "AWS_IAM"

  tags = {
    Environment = "production"
    Purpose     = "database-access"
  }
}

resource "aws_vpclattice_auth_policy" "db_policy" {
  resource_identifier = aws_vpclattice_service.db_service.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "vpc-lattice-svcs:Invoke"
        Resource  = "*"
        Condition = {
          StringEquals = {
            "vpc-lattice-svcs:ServiceNetworkArn" = var.service_network_arn
          }
        }
      }
    ]
  })
}

```
-->

### 9.3 NLB Security Group 모범 사례 (2025)

**중요**: NLB 생성 시 Security Group을 연결하지 않으면 나중에 추가할 수 없습니다.

> **참고**: AWS NLB Security Group 설정 관련 내용은 [AWS NLB 문서](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/) 및 [Terraform AWS ALB/NLB 모듈](https://github.com/terraform-aws-modules/terraform-aws-alb)을 참조하세요.
> 
> ```hcl
> # NLB Security Group 필수 설정 (2025 권장사항)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```hcl
# NLB Security Group 필수 설정 (2025 권장사항)
resource "aws_lb" "db_gateway_2025" {
  name               = "db-gateway-nlb-2025"
  internal           = true
  load_balancer_type = "network"
  subnets            = var.private_subnet_ids

  # 반드시 Security Group 연결 (생성 후 추가 불가)
  security_groups = [aws_security_group.nlb_sg.id]

  # PrivateLink 트래픽에 대한 인바운드 규칙 적용 여부
  enable_cross_zone_load_balancing = true

  tags = {
    Name        = "DB Gateway NLB 2025"
    Environment = var.environment
    PostQuantum = "enabled"
  }
}

# QUIC/TCP_QUIC 리스너 사용 시 Security Group 미사용
# 주의: QUIC 프로토콜 사용 시 Security Group 연결 불가

```
-->

### 9.4 Network Firewall Proxy 통합

AWS Network Firewall Proxy와 NLB 통합 시 고려사항:

> **참고**: AWS Network Firewall 및 NLB 통합 관련 내용은 [AWS Network Firewall 문서](https://docs.aws.amazon.com/network-firewall/) 및 [AWS Load Balancer Controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller)를 참조하세요.
> 
> ```yaml
> # Network Firewall + NLB 통합 아키텍처...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Network Firewall + NLB 통합 아키텍처
integration_notes:
  - source_traffic_nated: true
  - original_client_ip: "not_preserved"
  - policy_limitation: "client_ip_based_policies_not_evaluated"

recommended_patterns:
  - vpc_lattice_resource_endpoints
  - nlb_vpc_endpoint_service
  - network_firewall_proxy_mode

```
-->

## 결론

Network Load Balancer와 Security Group을 활용한 데이터베이스 접근 게이트웨이는 Zero Trust 아키텍처를 구현하는 효과적인 방법입니다. 2025년에는 Post-Quantum TLS 지원과 VPC Lattice의 성숙으로 더욱 다양한 선택지가 생겼습니다. 이 아키텍처를 통해:

- **보안 강화**: 중앙화된 접근 제어 및 최소 권한 원칙 적용 + 양자 내성 암호화
- **가용성 향상**: 다중 AZ 및 자동 장애 복구
- **관리 용이성**: Terraform을 통한 인프라 자동화, VPC Lattice로 단순화 가능
- **비용 효율**: 사용량 기반 과금으로 비용 최적화
- **미래 대비**: Post-Quantum TLS로 양자 컴퓨터 위협 선제 대응

올바른 구성과 지속적인 모니터링을 통해 안전하고 효율적인 데이터베이스 접근 환경을 구축할 수 있습니다.