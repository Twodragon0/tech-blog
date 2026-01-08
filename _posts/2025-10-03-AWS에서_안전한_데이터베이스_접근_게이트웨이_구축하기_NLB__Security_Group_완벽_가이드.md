---
layout: post
title: "AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기: NLB + Security Group 완벽 가이드"
date: 2025-10-03 00:10:37 +0900
categories: cloud
tags: [AWS, NLB, Security-Group, Database, Network]
excerpt: "데이터베이스 접근 관리 솔루션을 AWS에 배포하면서 Network Load Balancer와 Security Group을 활용한 Zero Trust 아키텍처를 구축한 경험을 공유합니다. Terraform으로 완전 자동화하고, 보안과 가용성을 모두 확보했습니다."
comments: true
original_url: https://twodragon.tistory.com/696
image: /assets/images/2025-10-03-AWS에서_안전한_데이터베이스_접근_게이트웨이_구축하기_NLB__Security_Group_완벽_가이드.svg
---
## 📋 포스팅 요약

> **제목**: AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기: NLB + Security Group 완벽 가이드

> **카테고리**: cloud

> **태그**: AWS, NLB, Security-Group, Database, Network

> **핵심 내용**: 
> - 데이터베이스 접근 관리 솔루션을 AWS에 배포하면서 Network Load Balancer와 Security Group을 활용한 Zero Trust 아키텍처를 구축한 경험을 공유합니다. Terraform으로 완전 자동화하고, 보안과 가용성을 모두 확보했습니다.

> **주요 기술/도구**: AWS, Security, cloud

> **대상 독자**: 클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


## 서론

데이터베이스 접근 관리 솔루션을 AWS에 배포하면서 Network Load Balancer와 Security Group을 활용한 Zero Trust 아키텍처를 구축한 경험을 공유합니다. Terraform으로 완전 자동화하고, 보안과 가용성을 모두 확보했습니다.

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

## 솔루션 아키텍처

### 전체 구조

```
[애플리케이션] 
    ↓
[Network Load Balancer (NLB)]
    ↓
[Security Group (게이트웨이)]
    ↓
[Private Subnet]
    ↓
[RDS / ElastiCache / 기타 DB]
```

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

### 1.3 타겟 그룹 설정

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

### 2.3 데이터베이스 Security Group

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

## 3. Zero Trust 아키텍처 구현

### 3.1 Zero Trust 원칙

1. **명시적 검증**: 모든 접근은 검증되어야 함
2. **최소 권한**: 필요한 최소한의 접근만 허용
3. **가정 위반**: 네트워크 내부도 신뢰하지 않음

### 3.2 구현 방법

#### 애플리케이션 레벨 인증

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

### 4.3 출력 값

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

## 5. 모니터링 및 로깅

### 5.1 CloudWatch 메트릭

NLB는 자동으로 CloudWatch 메트릭을 제공합니다:

- **ActiveFlowCount**: 활성 연결 수
- **ProcessedBytes**: 처리된 바이트 수
- **HealthyHostCount**: 정상 타겟 수
- **UnHealthyHostCount**: 비정상 타겟 수

### 5.2 VPC Flow Logs

VPC Flow Logs를 활성화하여 네트워크 트래픽을 모니터링:

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

## 결론

Network Load Balancer와 Security Group을 활용한 데이터베이스 접근 게이트웨이는 Zero Trust 아키텍처를 구현하는 효과적인 방법입니다. 이 아키텍처를 통해:

- **보안 강화**: 중앙화된 접근 제어 및 최소 권한 원칙 적용
- **가용성 향상**: 다중 AZ 및 자동 장애 복구
- **관리 용이성**: Terraform을 통한 인프라 자동화
- **비용 효율**: 사용량 기반 과금으로 비용 최적화

올바른 구성과 지속적인 모니터링을 통해 안전하고 효율적인 데이터베이스 접근 환경을 구축할 수 있습니다.

---

원본 포스트: [https://twodragon.tistory.com/696](https://twodragon.tistory.com/696)
