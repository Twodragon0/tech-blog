---
layout: post
title: "KISA 보안 공지 분석: 랜섬웨어 예방 가이드와 리눅스 커널 루트킷 점검 방법"
date: 2026-01-22 14:00:00 +0900
categories: [security, devsecops]
tags: [KISA, Ransomware, Linux-Rootkit, Security-Advisory, Incident-Prevention, Backup, Phishing, E-commerce-Security, DevSecOps, "2026"]
excerpt: "랜섬웨어 예방, 리눅스 루트킷 점검, 이커머스 피싱 대응 실무 가이드"
description: "KISA 보호나라 최신 보안 공지: 랜섬웨어 3-2-1 백업 전략, 리눅스 커널 루트킷 점검 가이드(chkrootkit, rkhunter), 이커머스 해킹 피해 악용 스미싱/피싱 주의 권고까지 실무 중심 대응 방안 제공"
keywords: [KISA, Ransomware, Linux-Rootkit, Security-Advisory, 3-2-1-Backup, chkrootkit, rkhunter, Phishing, E-commerce-Security, DevSecOps, Incident-Prevention]
author: Twodragon
comments: true
image: /assets/images/2026-01-22-KISA_Security_Advisory_Ransomware_Linux_Rootkit.svg
image_alt: "KISA Security Advisory - Ransomware Prevention and Linux Rootkit Detection Guide"
toc: true
schema_type: Article
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">KISA 보안 공지 분석: 랜섬웨어 예방 가이드와 리눅스 커널 루트킷 점검 방법</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">KISA</span>
      <span class="tag">Ransomware</span>
      <span class="tag">Linux-Rootkit</span>
      <span class="tag">Security-Advisory</span>
      <span class="tag">Incident-Prevention</span>
      <span class="tag">Backup</span>
      <span class="tag">Phishing</span>
      <span class="tag">E-commerce-Security</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>랜섬웨어 예방</strong>: 3-2-1 백업 규칙, 네트워크 분리, 보안 업데이트 적용 필수</li>
      <li><strong>리눅스 루트킷 점검</strong>: 커널 모듈 검증, 시스템 콜 테이블 무결성 확인, chkrootkit/rkhunter 활용</li>
      <li><strong>이커머스 피싱 주의</strong>: 해킹 피해 악용 스미싱/피싱 공격 증가, 결제 정보 탈취 주의</li>
      <li><strong>DevSecOps 통합</strong>: CI/CD 파이프라인에 보안 점검 자동화 적용</li>
      <li><strong>실무 체크리스트</strong>: KISA 권고 기반 즉시 적용 가능한 보안 조치</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">chkrootkit, rkhunter, AIDE, Lynis, ClamAV, iptables, 3-2-1 Backup</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, 시스템 관리자, DevSecOps 엔지니어, 서버 운영자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

KISA(한국인터넷진흥원) 보호나라에서 최근 발표한 보안 공지들을 분석하여 실무에서 즉시 적용할 수 있는 대응 방안을 정리했습니다. 특히 **랜섬웨어 예방**과 **리눅스 커널 루트킷 점검**은 서버 운영자와 DevSecOps 엔지니어에게 필수적인 내용입니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- 랜섬웨어 악성코드 감염 예방을 위한 보안 강화 권고
- 리눅스 커널 루트킷 점검 가이드
- 이커머스 해킹 피해 악용 스미싱/피싱 주의 권고
- DevSecOps 관점에서의 보안 자동화 방안

## 📊 빠른 참조

### KISA 최신 보안 공지 요약 (2025년 11-12월)

| 공지 | 날짜 | 위협 유형 | 심각도 | 대응 우선순위 |
|------|------|----------|--------|--------------|
| **랜섬웨어 감염 예방 권고** | 2025-12-06 | 랜섬웨어 | 높음 | 즉시 |
| **리눅스 루트킷 점검 가이드** | 2025-12-11 | 루트킷 | 높음 | 높음 |
| **이커머스 해킹 피싱 주의** | 2025-12-19 | 피싱/스미싱 | 중간 | 중간 |

> **참고**: [KISA 보호나라 보안공지](https://www.boho.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133)

---

## 1. 랜섬웨어 악성코드 감염 예방

### 1.1 KISA 권고 배경

KISA는 랜섬웨어 감염 피해가 지속적으로 발생함에 따라 보안 강화를 권고했습니다. 특히 **연말연시 기간**에 보안 담당자 부재를 노린 공격이 증가하는 추세입니다.

| 위협 | 설명 | 영향 |
|------|------|------|
| **파일 암호화** | 중요 문서/데이터 암호화 | 업무 마비 |
| **이중 갈취** | 데이터 유출 협박 | 평판 손상, 규제 위반 |
| **공급망 감염** | 협력업체를 통한 전파 | 광범위한 피해 |

### 1.2 3-2-1 백업 규칙

랜섬웨어 대응의 핵심은 **백업**입니다:

![3-2-1 Backup Rule](/assets/images/2026-01-22-3_2_1_Backup_Rule_Architecture.svg)
*3-2-1 백업 규칙 - 랜섬웨어 방어 전략*

**규칙 요약:**
- **3 Copies**: 최소 3개의 데이터 복사본 유지 (원본 + 백업1 + 백업2)
- **2 Media Types**: 최소 2개의 서로 다른 저장 매체 사용 (로컬 디스크 + NAS/테이프)
- **1 Offsite**: 최소 1개는 오프사이트(원격지) 보관 (클라우드 또는 물리적 별도 위치)
- **Bonus**: Air-Gap 백업 권장 (네트워크 분리된 백업으로 랜섬웨어 접근 차단)

### 1.3 백업 스크립트 예시

```bash
#!/bin/bash
# ransomware_backup.sh - 랜섬웨어 대응 백업 스크립트

# 설정
BACKUP_SOURCE="/var/www /home /etc"
BACKUP_DEST="/backup/$(date +%Y%m%d)"
REMOTE_DEST="s3://company-backup/daily/$(date +%Y%m%d)"
RETENTION_DAYS=30

# 로컬 백업
echo "[$(date)] Starting local backup..."
mkdir -p "$BACKUP_DEST"
tar -czf "$BACKUP_DEST/full_backup.tar.gz" $BACKUP_SOURCE 2>/dev/null

# 무결성 검증
sha256sum "$BACKUP_DEST/full_backup.tar.gz" > "$BACKUP_DEST/checksum.sha256"

# 원격 백업 (Air-Gap 대안)
if command -v aws &> /dev/null; then
    echo "[$(date)] Uploading to S3..."
    aws s3 cp "$BACKUP_DEST/full_backup.tar.gz" "$REMOTE_DEST/" --storage-class GLACIER_IR
    aws s3 cp "$BACKUP_DEST/checksum.sha256" "$REMOTE_DEST/"
fi

# 오래된 백업 정리
find /backup -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null

echo "[$(date)] Backup completed."
```

### 1.4 네트워크 분리 권장 사항

![Network Segmentation Architecture](/assets/images/2026-01-22-Network_Segmentation_Architecture.svg)
*네트워크 세그멘테이션 아키텍처*

**Zone 구성:**
- **DMZ Zone**: 인터넷 노출 서비스 (Web Server, Proxy)
- **App Zone**: 비즈니스 로직 (App Server, API Gateway)
- **Data Zone**: 민감 데이터 (Database, Backup)

**방화벽 규칙:**
- DMZ → App: HTTPS만 허용 (443, 8080)
- App → Data: 데이터베이스 포트만 허용 (5432, 3306, 1433)
- **Data → Internet: 모든 트래픽 차단** (랜섬웨어 데이터 유출 방지)

---

## 2. 리눅스 커널 루트킷 점검 가이드

### 2.1 KISA 권고 배경

KISA는 리눅스 서버를 대상으로 한 루트킷 공격에 대응하기 위한 점검 가이드를 배포했습니다. 루트킷은 **커널 레벨에서 동작**하여 탐지가 어렵습니다.

| 루트킷 유형 | 특징 | 탐지 난이도 |
|------------|------|------------|
| **유저스페이스 루트킷** | 바이너리 교체, LD_PRELOAD 악용 | 중간 |
| **커널 모듈 루트킷** | LKM을 통한 시스템 콜 후킹 | 높음 |
| **부트킷** | 부트로더/MBR 감염 | 매우 높음 |

![Linux Rootkit Detection Flow](/assets/images/2026-01-22-Linux_Rootkit_Detection_Flow.svg)
*리눅스 루트킷 탐지 파이프라인*

### 2.2 루트킷 점검 도구

#### 2.2.1 chkrootkit 사용

```bash
# chkrootkit 설치 (Debian/Ubuntu)
sudo apt update && sudo apt install chkrootkit -y

# chkrootkit 설치 (RHEL/CentOS)
sudo dnf install epel-release -y
sudo dnf install chkrootkit -y

# 점검 실행
sudo chkrootkit

# 상세 출력
sudo chkrootkit -q  # 감염 의심 항목만 출력

# 특정 점검 실행
sudo chkrootkit lkm  # LKM 루트킷 점검
sudo chkrootkit bindshell  # 백도어 점검
```

#### 2.2.2 rkhunter 사용

```bash
# rkhunter 설치
sudo apt install rkhunter -y  # Debian/Ubuntu
sudo dnf install rkhunter -y  # RHEL/CentOS

# 데이터베이스 업데이트
sudo rkhunter --update
sudo rkhunter --propupd  # 현재 시스템 상태를 기준으로 설정

# 전체 점검 실행
sudo rkhunter --check --skip-keypress

# 경고만 출력
sudo rkhunter --check --report-warnings-only
```

### 2.3 커널 모듈 무결성 점검

```bash
#!/bin/bash
# kernel_integrity_check.sh - 커널 모듈 무결성 점검

echo "=== 커널 모듈 무결성 점검 ==="
echo "점검 시간: $(date)"
echo ""

# 1. 로드된 커널 모듈 확인
echo "[1] 현재 로드된 커널 모듈:"
lsmod | head -20
echo "... (총 $(lsmod | wc -l) 개 모듈)"
echo ""

# 2. 숨겨진 모듈 탐지 시도
echo "[2] /sys/module과 lsmod 비교:"
LSMOD_COUNT=$(lsmod | tail -n +2 | wc -l)
SYSMOD_COUNT=$(ls /sys/module | wc -l)
echo "  lsmod 모듈 수: $LSMOD_COUNT"
echo "  /sys/module 수: $SYSMOD_COUNT"
if [ $SYSMOD_COUNT -gt $LSMOD_COUNT ]; then
    echo "  ⚠️  경고: 숨겨진 모듈이 있을 수 있습니다"
fi
echo ""

# 3. 시스템 콜 테이블 주소 확인
echo "[3] 시스템 콜 테이블 확인:"
if [ -f /proc/kallsyms ]; then
    grep sys_call_table /proc/kallsyms 2>/dev/null || echo "  접근 제한됨 (정상)"
fi
echo ""

# 4. 의심스러운 네트워크 연결
echo "[4] 의심스러운 네트워크 연결:"
netstat -tlnp 2>/dev/null | grep -v "127.0.0.1\|::1" | head -10
echo ""

# 5. SUID/SGID 바이너리 확인
echo "[5] 최근 변경된 SUID 바이너리:"
find /usr /bin /sbin -perm -4000 -mtime -7 2>/dev/null | head -10
echo ""

echo "=== 점검 완료 ==="
```

### 2.4 AIDE를 통한 파일 무결성 모니터링

```bash
# AIDE 설치
sudo apt install aide -y

# 초기 데이터베이스 생성
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# 무결성 점검 실행
sudo aide --check

# 크론잡으로 자동화
echo "0 3 * * * root /usr/bin/aide --check | mail -s 'AIDE Report' security@company.com" | sudo tee /etc/cron.d/aide-check
```

### 2.5 자동화된 보안 점검 스크립트

```bash
#!/bin/bash
# security_audit.sh - 종합 보안 점검 스크립트

LOG_FILE="/var/log/security_audit_$(date +%Y%m%d).log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "=========================================="
echo "보안 점검 시작: $(date)"
echo "=========================================="

# 1. 루트킷 점검
echo -e "\n[1/5] 루트킷 점검..."
if command -v chkrootkit &> /dev/null; then
    chkrootkit -q 2>/dev/null
else
    echo "chkrootkit 미설치"
fi

if command -v rkhunter &> /dev/null; then
    rkhunter --check --skip-keypress --report-warnings-only 2>/dev/null
else
    echo "rkhunter 미설치"
fi

# 2. 보안 업데이트 확인
echo -e "\n[2/5] 보안 업데이트 확인..."
if command -v apt &> /dev/null; then
    apt list --upgradable 2>/dev/null | grep -i security
elif command -v dnf &> /dev/null; then
    dnf check-update --security 2>/dev/null | head -20
fi

# 3. 실패한 로그인 시도
echo -e "\n[3/5] 최근 실패한 로그인 시도..."
grep "Failed password" /var/log/auth.log 2>/dev/null | tail -10

# 4. 열린 포트 확인
echo -e "\n[4/5] 열린 포트..."
ss -tlnp | grep LISTEN

# 5. 디스크 사용량 (이상 탐지용)
echo -e "\n[5/5] 디스크 사용량..."
df -h | grep -v "tmpfs\|udev"

echo -e "\n=========================================="
echo "점검 완료: $(date)"
echo "로그 파일: $LOG_FILE"
echo "=========================================="
```

---

## 3. 이커머스 해킹 피싱 주의 권고

### 3.1 KISA 권고 배경

최근 이커머스 플랫폼 해킹 피해를 악용한 스미싱/피싱 공격이 증가하고 있습니다. 공격자들은 **유출된 개인정보**를 활용하여 정교한 사회공학 공격을 수행합니다.

| 공격 유형 | 특징 | 피해 |
|----------|------|------|
| **스미싱** | 배송/결제 알림 위장 문자 | 악성앱 설치, 개인정보 탈취 |
| **피싱 이메일** | 이커머스 사이트 위장 | 로그인 정보 탈취 |
| **가짜 고객센터** | 피해 보상 위장 전화 | 금융정보 탈취 |

### 3.2 사용자 대응 가이드

![Phishing Detection Checklist - SMS, Email, and Phone scam indicators](/assets/images/diagrams/2026-01-22-phishing-detection-checklist.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```
Phishing Detection Checklist:
SMS Phishing (Smishing):
- Sender number differs from official number
- Contains shortened URLs (bit.ly, tinyurl, etc.)
- Demands urgent action ("verify immediately", "urgent")
- Prompts app installation

Phishing Email:
- Sender domain differs from official domain
- Login page URL differs from legitimate URL
- Grammar/spelling errors
- Requests to run attachments

Fake Customer Service:
- They call you first (normal: customer initiates)
- Requests remote control software installation
- Asks for personal/financial information
```

</details>

### 3.3 기업 대응 가이드

```yaml
# 이메일 보안 설정 (SPF, DKIM, DMARC)
# DNS TXT 레코드 예시

# SPF 레코드
_spf.company.com:
  type: TXT
  value: "v=spf1 include:_spf.google.com include:amazonses.com -all"

# DKIM 레코드  
selector1._domainkey.company.com:
  type: TXT
  value: "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBA..."

# DMARC 레코드
_dmarc.company.com:
  type: TXT
  value: "v=DMARC1; p=quarantine; rua=mailto:dmarc@company.com; pct=100"
```

---

## 4. DevSecOps 보안 자동화 통합

### 4.1 CI/CD 파이프라인 보안 점검

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 2 * * *'  # 매일 새벽 2시

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Run Checkov IaC scanner
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: all
          soft_fail: false
      
      - name: Run Gitleaks secrets scanner
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

### 4.2 인프라 보안 모니터링

```yaml
# kubernetes/security-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: falco-rules
  namespace: security
data:
  custom-rules.yaml: |
    - rule: Detect Rootkit Activity
      desc: Detect potential rootkit installation
      condition: >
        spawned_process and
        proc.name in (insmod, modprobe) and
        not proc.pname in (systemd, init)
      output: >
        Potential rootkit module loading
        (user=%user.name command=%proc.cmdline)
      priority: CRITICAL
      tags: [rootkit, mitre_persistence]

    - rule: Detect Ransomware Behavior
      desc: Detect mass file encryption patterns
      condition: >
        open_write and
        fd.name endswith (".encrypted" or ".locked" or ".crypted") and
        evt.count > 100
      output: >
        Potential ransomware activity
        (user=%user.name file=%fd.name count=%evt.count)
      priority: CRITICAL
      tags: [ransomware, mitre_impact]
```

### 4.3 자동화된 대응 플레이북

```python
#!/usr/bin/env python3
"""
incident_response.py - 자동화된 인시던트 대응 플레이북
"""

import subprocess
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def isolate_host(hostname: str) -> bool:
    """감염 의심 호스트 네트워크 격리"""
    try:
        # iptables를 통한 네트워크 격리
        commands = [
            f"iptables -I INPUT -s {hostname} -j DROP",
            f"iptables -I OUTPUT -d {hostname} -j DROP",
        ]
        for cmd in commands:
            subprocess.run(cmd.split(), check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def collect_forensics(hostname: str, output_dir: str) -> str:
    """포렌식 데이터 수집"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    forensics_file = f"{output_dir}/forensics_{hostname}_{timestamp}.tar.gz"
    
    commands = [
        "ps auxf",  # 프로세스 목록
        "netstat -tlnp",  # 네트워크 연결
        "lsof -i",  # 열린 파일
        "cat /etc/passwd",  # 사용자 계정
        "last -100",  # 로그인 이력
    ]
    
    output = []
    for cmd in commands:
        result = subprocess.run(
            cmd.split(), 
            capture_output=True, 
            text=True
        )
        output.append(f"=== {cmd} ===\n{result.stdout}")
    
    with open(forensics_file.replace('.tar.gz', '.txt'), 'w') as f:
        f.write('\n'.join(output))
    
    return forensics_file

def notify_security_team(incident_type: str, details: str):
    """보안팀 알림"""
    msg = MIMEText(f"""
인시던트 유형: {incident_type}
발생 시간: {datetime.now()}
상세 내용:
{details}
    """)
    msg['Subject'] = f"[ALERT] Security Incident: {incident_type}"
    msg['From'] = "security-bot@company.com"
    msg['To'] = "security-team@company.com"
    
    # SMTP 전송 (실제 환경에서는 설정 필요)
    # with smtplib.SMTP('smtp.company.com') as server:
    #     server.send_message(msg)
    print(f"Alert sent: {incident_type}")

# 사용 예시
if __name__ == "__main__":
    # 랜섬웨어 탐지 시
    notify_security_team(
        "Ransomware Detected",
        "Host: web-server-01\nFiles encrypted: 150+"
    )
```

---

## 5. 실무 체크리스트

### 5.1 즉시 적용 가능한 보안 조치

#### 랜섬웨어 예방

- [ ] **백업 검증**: 3-2-1 규칙 준수 여부 확인
- [ ] **백업 복구 테스트**: 분기별 복구 테스트 수행
- [ ] **네트워크 분리**: 백업 서버 네트워크 격리
- [ ] **보안 업데이트**: OS/애플리케이션 최신 패치 적용
- [ ] **이메일 필터링**: 악성 첨부파일 차단 정책

#### 루트킷 점검

- [ ] **도구 설치**: chkrootkit, rkhunter 설치
- [ ] **정기 점검**: 주간/월간 자동 점검 스케줄
- [ ] **AIDE 구성**: 파일 무결성 모니터링 활성화
- [ ] **커널 모듈 감사**: 승인된 모듈만 로드 허용
- [ ] **로그 모니터링**: 의심스러운 활동 알림 설정

#### 피싱 대응

- [ ] **SPF/DKIM/DMARC**: 이메일 인증 설정
- [ ] **사용자 교육**: 피싱 인식 훈련 실시
- [ ] **MFA 적용**: 모든 관리자 계정 2단계 인증
- [ ] **URL 필터링**: 악성 URL 차단 시스템

### 5.2 KISA 참고 자료

| 자료 | 링크 |
|------|------|
| 랜섬웨어 예방 권고 | [KISA 보안공지](https://www.boho.or.kr/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId=71914) |
| 리눅스 루트킷 점검 가이드 | [KISA 보안공지](https://www.boho.or.kr/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId=71917) |
| 이커머스 피싱 주의 | [KISA 보안공지](https://www.boho.or.kr/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId=71925) |
| 보호나라 | [https://www.boho.or.kr](https://www.boho.or.kr) |

---

## 결론

KISA의 최신 보안 공지는 **랜섬웨어, 루트킷, 피싱**이라는 세 가지 주요 위협에 대한 실질적인 대응 방안을 제시합니다. 특히 DevSecOps 환경에서는 이러한 보안 점검을 **자동화**하여 지속적인 보안 모니터링 체계를 구축하는 것이 중요합니다.

핵심 권고 사항:
1. **3-2-1 백업 규칙** 준수 및 정기적인 복구 테스트
2. **루트킷 탐지 도구** 설치 및 자동화된 정기 점검
3. **이메일 인증(SPF/DKIM/DMARC)** 설정으로 피싱 방어
4. **CI/CD 파이프라인**에 보안 스캔 통합

다음 포스팅에서는 AWS와 GCP의 최신 서비스 업데이트를 다루겠습니다.

---

## 참고 문헌

1. KISA 보호나라. (2025). "랜섬웨어 악성코드 감염피해 예방을 위한 보안강화 권고". [Link](https://www.boho.or.kr/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId=71914)
2. KISA 보호나라. (2025). "리눅스 커널 루트킷 점검 가이드 배포". [Link](https://www.boho.or.kr/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId=71917)
3. KISA 보호나라. (2025). "(사례) 이커머스 해킹 피해 악용 스미싱·피싱 주의권고". [Link](https://www.boho.or.kr/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId=71925)
4. chkrootkit 공식 사이트. [http://www.chkrootkit.org/](http://www.chkrootkit.org/)
5. rkhunter 공식 사이트. [http://rkhunter.sourceforge.net/](http://rkhunter.sourceforge.net/)
