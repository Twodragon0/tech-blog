---
layout: post
title: "Weekly Security & DevOps Digest: OpenClaw AI 에이전트 보안, Jamf/Intune MDM 앱 비활성화, 금주 뉴스 하이라이트"
date: 2026-02-03 10:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, OpenClaw, NanoClaw, AI-Agent-Security, MDM, Jamf, Intune, OWASP, Kubernetes, DevSecOps, "2026"]
excerpt: "OpenClaw(Clawdbot) vs NanoClaw AI 에이전트 보안 비교, Jamf Extension Attribute 기반 무단 설치 탐지 스크립트, Jamf Pro/Intune MDM 앱 비활성화 실무 가이드"
description: "2026년 2월 3일 보안/DevOps 다이제스트: AI 에이전트 샌드박싱(OpenClaw 52+ 모듈 위험 vs NanoClaw Apple 컨테이너 격리), Jamf Extension Attribute 무단 설치 탐지, MDM 앱 제어(Jamf Configuration Profile, Intune App Protection Policy), OWASP Agentic AI Top 10"
keywords: [OpenClaw Security, NanoClaw, AI Agent Sandbox, Jamf Pro MDM, Microsoft Intune, App Disable, OWASP Agentic AI, MDM Zero Trust, SIEM MDM Integration, DevSecOps Weekly]
author: Twodragon
comments: true
image: /assets/images/2026-02-03-Weekly_Security_DevOps_Digest.svg
image_alt: "Weekly Security and DevOps Digest Feb 3 2026"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Weekly Security & DevOps Digest (2026년 02월 03일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">OpenClaw</span>
      <span class="tag">NanoClaw</span>
      <span class="tag">AI-Agent-Security</span>
      <span class="tag">MDM</span>
      <span class="tag">Jamf</span>
      <span class="tag">Intune</span>
      <span class="tag">OWASP</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>OpenClaw vs NanoClaw AI 에이전트 보안</strong>: OpenClaw(Clawdbot) 52+ 모듈 보안 리스크 vs NanoClaw Apple 컨테이너 격리, Jamf Extension Attribute 기반 무단 설치 탐지 스크립트 포함</li>
      <li><strong>MDM 앱 비활성화 실무 가이드</strong>: Jamf Pro Configuration Profile 기반 앱 제한, Microsoft Intune App Protection Policy, Conditional Access 설정 방법 비교</li>
      <li><strong>금주 뉴스 하이라이트</strong>: Claude 4/Opus 4.5 에이전트 생태계 확장, Kubernetes 1.33 보안 강화, SBOM 컴플라이언스 동향</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, IT 관리자, MDM 운영자</span>
  </div>
</div>
</div>

> **함께 읽기**: 지난주 보안 위협 인텔리전스 다이제스트 [Weekly Security Threat Intelligence Digest](/2026-02-02-Weekly_Security_Threat_Intelligence_Digest)에서 Notepad++ 국가 지원 공급망 공격, SK쉴더스 보안 리포트 종합, HashiCorp 보안 자동화를 심층 분석합니다. 기술/AI/블록체인 소식은 [Weekly Tech & AI & Blockchain Digest](/2026-02-02-Weekly_Tech_AI_Blockchain_Digest)를 참고하세요.

## 개요

2026년 2월 첫째 주, AI 에이전트의 보안 아키텍처와 엔터프라이즈 디바이스 관리가 핵심 이슈로 부상했습니다.

**AI 코딩 에이전트 OpenClaw(Clawdbot)**의 아키텍처가 공개되면서, 52개 이상의 모듈이 단일 Node.js 프로세스에서 무제한 권한으로 실행되는 구조의 보안 위험이 재조명되었습니다. 이에 대한 대안으로 **NanoClaw**가 Apple 컨테이너 격리와 최소 권한 원칙을 적용한 ~500줄 핵심 코드로 주목받고 있습니다. OWASP Agentic AI Top 10이 이러한 AI 에이전트 보안의 프레임워크로 자리잡고 있습니다.

엔터프라이즈 환경에서는 **MDM(Mobile Device Management)을 통한 앱 비활성화/제한**이 Zero Trust 전략의 핵심 구성요소로 부상했습니다. Jamf Pro의 Configuration Profile과 Microsoft Intune의 App Protection Policy를 비교하여, Apple 중심 환경과 크로스 플랫폼 환경 각각에 최적화된 앱 제어 전략을 제시합니다.

---

## 1. OpenClaw vs NanoClaw: AI 에이전트 보안 비교 분석

### 1.1 배경: AI 코딩 에이전트의 보안 위협

AI 코딩 에이전트가 개발자의 터미널과 파일 시스템에 직접 접근하면서, **에이전트의 권한 범위와 격리 수준**이 새로운 보안 과제가 되었습니다.

| 위협 요소 | 설명 | 심각도 |
|-----------|------|--------|
| **무제한 파일 시스템 접근** | 에이전트가 시스템 전체 파일을 읽고 쓸 수 있음 | Critical |
| **프로세스 실행 권한** | 임의의 셸 명령어 실행 가능 | Critical |
| **네트워크 접근** | 외부 API 호출, 데이터 유출 가능 | High |
| **단일 프로세스 모델** | 모든 모듈이 같은 권한으로 실행 | High |
| **프롬프트 인젝션** | 악성 코드 코멘트를 통한 에이전트 조작 | High |

### 1.2 OpenClaw(Clawdbot) 아키텍처 분석

OpenClaw는 강력한 기능을 제공하지만, 아키텍처 수준에서 보안 우려가 존재합니다.

| 항목 | 내용 |
|------|------|
| **모듈 수** | 52+ 모듈 (도구, 플러그인, 확장) |
| **런타임** | 단일 Node.js 프로세스 |
| **권한 모델** | 사용자와 동일한 권한으로 실행 |
| **격리** | 프로세스 수준 격리 없음 |
| **파일 접근** | 전체 파일 시스템 읽기/쓰기 |
| **네트워크** | 제한 없는 아웃바운드 연결 |

**보안 위험 요인:**

```
OpenClaw Architecture (Single Process Model)
+--------------------------------------------------+
|  Node.js Process (User Privileges)               |
|                                                  |
|  +----------+  +----------+  +----------+        |
|  | Module 1 |  | Module 2 |  | Module N |  ...   |
|  | (Tools)  |  | (Plugins)|  | (Exts)   |  52+  |
|  +----------+  +----------+  +----------+        |
|       |              |             |              |
|  [Full FS Access] [Shell Exec] [Network I/O]     |
|       |              |             |              |
+---------|------------|-------------|-------------+
          v            v             v
   ~/.ssh/id_rsa   rm -rf /     POST secrets
   ~/.aws/creds    curl evil    to external
```

**MITRE ATT&CK 관련 기법:**

| MITRE ATT&CK ID | 기법명 | AI 에이전트 적용 |
|------------------|--------|------------------|
| **T1059.007** | Command and Scripting Interpreter: JavaScript | Node.js 런타임에서 임의 코드 실행 |
| **T1005** | Data from Local System | 로컬 파일 시스템에서 민감 정보 수집 |
| **T1041** | Exfiltration Over C2 Channel | API 호출을 통한 데이터 유출 |
| **T1078** | Valid Accounts | 사용자 권한을 그대로 상속 |
| **T1547** | Boot or Logon Autostart Execution | 에이전트 자동 시작 설정 |

### 1.3 NanoClaw: 최소 권한 원칙 적용

NanoClaw는 보안을 아키텍처 수준에서 해결합니다.

| 항목 | NanoClaw |
|------|----------|
| **핵심 코드** | ~500줄 (감사 가능한 규모) |
| **격리 방식** | Apple 컨테이너 (App Sandbox) |
| **권한 모델** | 최소 권한 원칙 (Principle of Least Privilege) |
| **파일 접근** | 프로젝트 디렉토리만 허용 |
| **네트워크** | 허용 목록 기반 아웃바운드만 |
| **프로세스** | 격리된 샌드박스 프로세스 |

**NanoClaw 보안 아키텍처:**

```
NanoClaw Architecture (Container Isolation)
+--------------------------------------------------+
|  Apple Container (Sandboxed)                     |
|  +--------------------------------------------+  |
|  |  NanoClaw Core (~500 lines)                |  |
|  |  +----------+  +----------+                |  |
|  |  | LLM API  |  | File I/O |                |  |
|  |  +----------+  +----------+                |  |
|  +--------------------------------------------+  |
|       |                    |                      |
|  [API Allow-list]   [Project Dir Only]            |
|  - api.anthropic.com  - ~/project/*               |
|  - api.openai.com     - (no ~/.ssh, ~/.aws)       |
+--------------------------------------------------+
        |                    |
   Filtered Network     Scoped FS Access
```

### 1.4 OpenClaw vs NanoClaw 비교

| 비교 항목 | OpenClaw | NanoClaw |
|-----------|----------|----------|
| **코드 규모** | 52+ 모듈, 수만 줄 | ~500줄 핵심 코드 |
| **감사 용이성** | 어려움 (방대한 코드베이스) | 용이함 (사람이 읽을 수 있는 규모) |
| **격리 수준** | 없음 (사용자 프로세스) | Apple 컨테이너 샌드박스 |
| **파일 접근** | 전체 파일 시스템 | 프로젝트 디렉토리 한정 |
| **네트워크** | 무제한 | 허용 목록 기반 |
| **권한 모델** | 사용자 전체 권한 | 최소 권한 원칙 |
| **프롬프트 인젝션 내성** | 낮음 (넓은 공격 표면) | 높음 (제한된 기능) |
| **기능 범위** | 광범위 (IDE 수준) | 핵심 코딩 지원 |
| **적합 환경** | 개인 개발, 빠른 프로토타이핑 | 엔터프라이즈, 보안 민감 환경 |

### 1.5 OWASP Agentic AI Top 10

AI 에이전트 보안의 표준 프레임워크로 부상한 OWASP Agentic AI Top 10:

| 순위 | 취약점 | OpenClaw 해당 여부 | 대응 방안 |
|------|--------|-------------------|-----------|
| 1 | **Excessive Agency** | Yes - 무제한 권한 | 최소 권한 원칙 적용 |
| 2 | **Prompt Injection** | Yes - 넓은 공격 표면 | 입력 검증, 샌드박싱 |
| 3 | **Supply Chain Vulnerabilities** | Yes - 52+ 의존성 | SBOM 관리, 의존성 감사 |
| 4 | **Insecure Output Handling** | Partial | 출력 검증, 실행 전 확인 |
| 5 | **Data Leakage** | Yes - 전체 FS 접근 | 데이터 접근 범위 제한 |
| 6 | **Lack of Oversight** | Partial | 실행 로깅, 승인 워크플로 |
| 7 | **Privilege Escalation** | Yes - 사용자 권한 상속 | 권한 분리, 컨테이너화 |
| 8 | **Insufficient Monitoring** | Partial | SIEM 연동, 행위 분석 |
| 9 | **Over-Reliance** | Context-dependent | 코드 리뷰 프로세스 유지 |
| 10 | **Model Denial of Service** | Low | Rate limiting |

### 1.6 AI 에이전트 보안 체크리스트

```yaml
# AI Agent Security Checklist
pre_deployment:
  - [ ] 코드베이스 감사 (라인 수, 모듈 수 확인)
  - [ ] 의존성 트리 분석 (npm audit / pip audit)
  - [ ] SBOM(Software Bill of Materials) 생성
  - [ ] 프롬프트 인젝션 테스트 수행

runtime_controls:
  - [ ] 파일 시스템 접근 범위 제한 (프로젝트 디렉토리만)
  - [ ] 네트워크 허용 목록 설정
  - [ ] 프로세스 격리 (컨테이너/샌드박스)
  - [ ] 실행 명령어 화이트리스트

monitoring:
  - [ ] 모든 파일 읽기/쓰기 로깅
  - [ ] 네트워크 요청 로깅
  - [ ] 셸 명령어 실행 감사
  - [ ] 비정상 행위 알림 설정

incident_response:
  - [ ] 에이전트 즉시 종료 프로세스 수립
  - [ ] 영향 범위 파악 절차 문서화
  - [ ] 자격 증명 교체 절차 준비
```

### 1.7 탐지: SIEM 쿼리

```bash
# Splunk - AI Agent Suspicious File Access
index=endpoint sourcetype=sysmon EventCode=11
(process_name="node" OR process_name="python3")
(TargetFilename="*/.ssh/*" OR TargetFilename="*/.aws/*"
 OR TargetFilename="*/.env" OR TargetFilename="*/credentials*")
| stats count by process_name, TargetFilename, user
| where count > 0

# Splunk - AI Agent Unusual Network Connections
index=endpoint sourcetype=sysmon EventCode=3
(process_name="node" OR process_name="python3")
NOT (dest_ip IN ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
NOT (dest IN ("api.anthropic.com", "api.openai.com", "registry.npmjs.org"))
| stats count by process_name, dest, dest_port
| sort -count

# Elastic/KQL - AI Agent Shell Command Execution
process.parent.name: ("node" or "python3") AND
event.category: "process" AND
process.name: ("bash" or "sh" or "zsh") AND
NOT process.command_line: ("git *" or "npm *" or "python3 *")
```

### 1.8 Jamf Extension Attribute: OpenClaw/Moltbot 설치 탐지

엔터프라이즈 환경에서 Jamf Pro를 통해 관리 대상 Mac에 OpenClaw(Clawdbot) 또는 Moltbot이 무단 설치되어 있는지 자동으로 탐지할 수 있습니다. 아래 스크립트를 **Jamf Pro > Settings > Extension Attributes**에 등록하면, 인벤토리 수집 시 각 디바이스의 설치 여부가 자동으로 보고됩니다.

#### Extension Attribute 스크립트

```bash
#!/bin/bash
# Jamf Extension Attribute: OpenClaw/Moltbot Installation Detection
# Data Type: String | Input Type: Script
# Purpose: Detect unauthorized AI agent installations on managed Macs

REPORT=""
FOUND_ANY=false

# 1. Binary check
check_binary() {
    local bin_path=$1
    if [ -f "$bin_path" ]; then
        REPORT+="[FOUND] Binary: $bin_path\n"
        FOUND_ANY=true
    else
        REPORT+="[Not Found] Binary: $bin_path\n"
    fi
}

# 2. User home directory check
check_user_dir() {
    local dir_name=$1
    USERS=$(dscl . list /Users UniqueID | awk '$2 > 500 {print $1}')
    for user in $USERS; do
        HOME_DIR=$(dscl . read "/Users/$user" NFSHomeDirectory | awk '{print $2}')
        if [ -d "$HOME_DIR/$dir_name" ]; then
            REPORT+="[FOUND] User($user) Folder: ~/$dir_name\n"
            FOUND_ANY=true
        else
            REPORT+="[Not Found] User($user) Folder: ~/$dir_name\n"
        fi
    done
}

# 3. npm global module check
check_npm_module() {
    local module_name=$1
    local npm_path="/usr/local/lib/node_modules/$module_name"
    if [ -d "$npm_path" ]; then
        REPORT+="[FOUND] npm Module: $module_name\n"
        FOUND_ANY=true
    else
        REPORT+="[Not Found] npm Module: $module_name\n"
    fi
}

REPORT+="--- OpenClaw/Moltbot Inspection Report ---\n"

# Binary inspection
check_binary "/usr/local/bin/openclaw"
check_binary "/usr/local/bin/molt"
check_binary "/usr/local/bin/clawd"

# User config directory inspection
check_user_dir ".openclaw"
check_user_dir ".moltbot"
check_user_dir "clawd"

# npm module inspection
check_npm_module "openclaw"
check_npm_module "@openclaw"

REPORT+="------------------------------------------\n"

# Jamf Extension Attribute output
if [ "$FOUND_ANY" = true ]; then
    echo -e "<result>WARNING: Installation Detected\n\n$REPORT</result>"
else
    echo -e "<result>Clean: No Installation Found\n\n$REPORT</result>"
fi
```

#### Jamf Pro 등록 방법

| 단계 | 설정 |
|------|------|
| **1. EA 생성** | Jamf Pro > Settings > Extension Attributes > New |
| **2. 기본 정보** | Display Name: `OpenClaw Detection`, Data Type: `String` |
| **3. Input Type** | `Script` 선택, 위 스크립트 붙여넣기 |
| **4. Inventory Scope** | `Computer` |
| **5. 저장** | Save 후 인벤토리 수집 시 자동 실행 |

#### Smart Group 연동: 설치 탐지 디바이스 자동 그룹화

```
Jamf Pro Smart Group: "OpenClaw Installed Devices"
+--------------------------------------------------+
| Criteria:                                        |
|   OpenClaw Detection  |  like  |  WARNING*       |
|                                                  |
| -> Action: Send alert to security team           |
| -> Action: Apply restriction profile             |
| -> Action: Create Jira ticket via webhook        |
+--------------------------------------------------+
```

탐지 시 자동으로 다음 조치를 취할 수 있습니다:

| 자동 대응 | 방법 |
|-----------|------|
| **알림** | Smart Group 변경 시 Slack/Teams 웹훅 발송 |
| **제한** | Restriction Profile 자동 배포 (네트워크 접근 차단) |
| **제거** | Self Service에서 제거 스크립트 제공 또는 정책 자동 실행 |
| **로깅** | SIEM 연동으로 설치 이력 추적 |

#### 확장: 추가 AI 에이전트 탐지

동일 패턴으로 다른 AI 코딩 에이전트도 탐지할 수 있습니다:

```bash
# Additional AI agent binary paths to monitor
check_binary "/usr/local/bin/cursor"
check_binary "/usr/local/bin/windsurf"
check_binary "/usr/local/bin/aider"
check_binary "/usr/local/bin/copilot"

# Additional config directories
check_user_dir ".cursor"
check_user_dir ".windsurf"
check_user_dir ".aider"
check_user_dir ".continue"

# Homebrew cask installations
check_binary "/opt/homebrew/bin/openclaw"
check_binary "/opt/homebrew/bin/cursor"
```

#### 탐지 결과 SIEM 연동

```bash
# Splunk - Jamf EA 기반 OpenClaw 설치 탐지 알림
index=jamf sourcetype=jamf:computerextensionattributes
ea_name="OpenClaw Detection"
ea_value="WARNING*"
| stats count by computer_name, serial_number, ea_value, _time
| sort -_time

# Splunk - OpenClaw 설치 트렌드 (주간)
index=jamf sourcetype=jamf:computerextensionattributes
ea_name="OpenClaw Detection"
ea_value="WARNING*"
| timechart span=1w count by computer_name
```

---

## 2. MDM 앱 비활성화: Jamf Pro vs Microsoft Intune

### 2.1 MDM을 통한 앱 제어의 필요성

엔터프라이즈 환경에서 MDM 앱 제어는 Zero Trust 전략의 핵심입니다.

| 시나리오 | MDM 앱 제어 대응 |
|----------|-----------------|
| 퇴사 예정자 데이터 유출 방지 | 클라우드 스토리지 앱 비활성화 |
| 규정 미준수 디바이스 격리 | 업무 앱 접근 차단 |
| 보안 사고 시 긴급 대응 | 원격 앱 잠금/삭제 |
| BYOD 업무/개인 앱 분리 | 관리 컨테이너 내 앱만 허용 |
| 임시직원 앱 제한 | 시간 기반 앱 정책 배포 |

### 2.2 Jamf Pro: Apple 기기 MDM

Jamf Pro는 Apple 생태계에 최적화된 MDM으로, Configuration Profile을 통해 세밀한 앱 제어가 가능합니다.

#### Configuration Profile로 앱 제한

```xml
<!-- Jamf Pro - Restriction Payload: Block Specific Apps -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>PayloadType</key>
      <string>com.apple.applicationaccess</string>
      <key>PayloadVersion</key>
      <integer>1</integer>
      <key>PayloadIdentifier</key>
      <string>com.example.restriction.apps</string>
      <key>PayloadUUID</key>
      <string>YOUR_UUID_HERE</string>
      <key>PayloadDisplayName</key>
      <string>App Restrictions</string>

      <!-- Block specific apps by bundle ID -->
      <key>blacklistedAppBundleIDs</key>
      <array>
        <string>com.dropbox.client</string>
        <string>com.getdropbox.dropbox</string>
        <string>com.google.Drive</string>
        <string>com.tencent.xinWeChat</string>
      </array>

      <!-- Or use allowlist mode (more restrictive) -->
      <!-- <key>whitelistedAppBundleIDs</key>
      <array>
        <string>com.apple.Safari</string>
        <string>com.microsoft.Outlook</string>
        <string>com.slack.Slack</string>
      </array> -->
    </dict>
  </array>
</dict>
</plist>
```

#### Smart Groups 기반 정책 배포

```
Jamf Pro Smart Group Examples:
+------------------------------------------+
| Group: "Security-Restricted-Devices"     |
| Criteria:                                |
|   - Department = "Finance"               |
|   - OS Version < 17.3                    |
|   - Last Check-in > 7 days ago           |
| -> Apply: Strict App Restriction Profile |
+------------------------------------------+

| Group: "BYOD-Personal-Devices"           |
| Criteria:                                |
|   - Enrollment Type = "User Enrolled"    |
|   - Supervised = No                      |
| -> Apply: Managed App Only Profile       |
+------------------------------------------+

| Group: "Executive-Devices"               |
| Criteria:                                |
|   - Department = "C-Suite"               |
|   - Device Type = "iPhone" OR "iPad"     |
| -> Apply: Premium Security Profile       |
+------------------------------------------+
```

#### Jamf Pro API로 앱 비활성화

```bash
# Jamf Pro API - Get device app list
curl -X GET "https://your-jamf.jamfcloud.com/JSSResource/mobiledevices/id/{device_id}" \
  -H "Authorization: Bearer ${JAMF_TOKEN}" \
  -H "Accept: application/json" | \
  jq '.mobile_device.applications[].identifier'

# Jamf Pro API - Deploy restriction profile
curl -X POST "https://your-jamf.jamfcloud.com/JSSResource/osxconfigurationprofiles/id/0" \
  -H "Authorization: Bearer ${JAMF_TOKEN}" \
  -H "Content-Type: application/xml" \
  -d @app_restriction_profile.xml

# Jamf Pro API - Remove managed app
curl -X POST "https://your-jamf.jamfcloud.com/JSSResource/mobiledevicecommands/command/RemoveApplication" \
  -H "Authorization: Bearer ${JAMF_TOKEN}" \
  -H "Content-Type: application/xml" \
  -d '<mobile_device_command>
        <general>
          <command>RemoveApplication</command>
          <management_id>com.dropbox.client</management_id>
        </general>
        <mobile_devices><mobile_device><id>{device_id}</id></mobile_device></mobile_devices>
      </mobile_device_command>'
```

### 2.3 Microsoft Intune: 크로스 플랫폼 MDM

Intune은 Windows, macOS, iOS, Android를 통합 관리합니다.

#### App Protection Policies

```json
{
  "@odata.type": "#microsoft.graph.iosManagedAppProtection",
  "displayName": "Finance App Protection Policy",
  "description": "Restrict data transfer for finance apps",
  "periodOfflineBeforeAccessCheck": "PT12H",
  "periodOnlineBeforeAccessCheck": "PT30M",
  "allowedInboundDataTransferSources": "managedApps",
  "allowedOutboundDataTransferDestinations": "managedApps",
  "organizationalCredentialsRequired": true,
  "dataBackupBlocked": true,
  "deviceComplianceRequired": true,
  "managedBrowserToOpenLinksRequired": true,
  "saveAsBlocked": true,
  "periodOfflineBeforeWipeIsEnforced": "P90D",
  "pinRequired": true,
  "maximumPinRetries": 5,
  "simplePinBlocked": true,
  "minimumPinLength": 6,
  "pinCharacterSet": "alphanumericAndSymbol",
  "allowedDataStorageLocations": [
    "oneDriveForBusiness",
    "sharePoint"
  ],
  "contactSyncBlocked": true,
  "printBlocked": true,
  "fingerprintBlocked": false,
  "disableAppPinIfDevicePinIsSet": false
}
```

#### Conditional Access로 앱 접근 제어

```json
{
  "@odata.type": "#microsoft.graph.conditionalAccessPolicy",
  "displayName": "Block Non-Compliant Device App Access",
  "state": "enabled",
  "conditions": {
    "clientAppTypes": ["all"],
    "applications": {
      "includeApplications": [
        "00000003-0000-0ff1-ce00-000000000000",
        "00000002-0000-0ff1-ce00-000000000000"
      ]
    },
    "platforms": {
      "includePlatforms": ["iOS", "android"]
    }
  },
  "grantControls": {
    "operator": "AND",
    "builtInControls": [
      "compliantDevice",
      "approvedApplication"
    ]
  }
}
```

#### Intune Compliance Policy

```json
{
  "@odata.type": "#microsoft.graph.iosCompliancePolicy",
  "displayName": "iOS Security Compliance",
  "description": "Minimum security requirements for iOS devices",
  "osMinimumVersion": "17.0",
  "osMaximumVersion": "18.99",
  "securityBlockJailbrokenDevices": true,
  "deviceThreatProtectionEnabled": true,
  "deviceThreatProtectionRequiredSecurityLevel": "medium",
  "managedEmailProfileRequired": true,
  "restrictedApps": [
    {
      "name": "TikTok",
      "appId": {
        "bundleId": "com.zhiliaoapp.musically"
      }
    },
    {
      "name": "Telegram",
      "appId": {
        "bundleId": "ph.telegra.Telegraph"
      }
    }
  ],
  "scheduledActionsForRule": [
    {
      "ruleName": "DeviceNonCompliance",
      "scheduledActionConfigurations": [
        {
          "actionType": "block",
          "gracePeriodHours": 24,
          "notificationTemplateId": "YOUR_TEMPLATE_ID"
        }
      ]
    }
  ]
}
```

### 2.4 Jamf Pro vs Microsoft Intune 비교

| 비교 항목 | Jamf Pro | Microsoft Intune |
|-----------|----------|------------------|
| **지원 플랫폼** | Apple 전용 (macOS, iOS, iPadOS, tvOS) | Windows, macOS, iOS, Android, Linux |
| **앱 차단 방식** | Configuration Profile (blacklist/whitelist) | App Protection Policy + Compliance |
| **앱 제거** | MDM 명령어로 관리형 앱 즉시 제거 | Selective Wipe / App Uninstall |
| **Conditional Access** | Jamf Connect + Azure AD 연동 | 네이티브 Azure AD Conditional Access |
| **BYOD 지원** | User Enrollment (제한적 관리) | MAM without enrollment (앱 수준 관리) |
| **자동화** | Jamf API + Smart Groups | Graph API + Power Automate |
| **가격** | 디바이스당 과금 | Microsoft 365 E3/E5 포함 |
| **설정 복잡도** | 낮음 (Apple 친화적 UI) | 중간 (다중 플랫폼 고려) |
| **Apple DEP/ABM** | 네이티브 지원 (최적) | 지원 (Jamf 대비 제한적) |
| **Windows 관리** | 미지원 | 네이티브 (GPO 대체) |
| **적합 환경** | Apple 중심 기업, 크리에이티브 | 혼합 플랫폼, Microsoft 365 환경 |

### 2.5 SIEM 연동 MDM 모니터링

```bash
# Splunk - Jamf Pro MDM Compliance Events
index=mdm sourcetype=jamf:events
(event_type="ComputerCheckIn" OR event_type="PolicyRun"
 OR event_type="RestrictionViolation")
| eval status=case(
    event_type="RestrictionViolation", "VIOLATION",
    event_type="PolicyRun" AND result="success", "COMPLIANT",
    event_type="PolicyRun" AND result="failed", "NON_COMPLIANT",
    1=1, "INFO")
| stats count by device_name, event_type, status, serial_number
| where status IN ("VIOLATION", "NON_COMPLIANT")
| sort -count

# Splunk - Intune Device Compliance Dashboard
index=azure sourcetype=intune:deviceCompliance
| eval compliance_state=case(
    complianceState="compliant", "OK",
    complianceState="noncompliant", "ALERT",
    complianceState="inGracePeriod", "WARNING",
    1=1, "UNKNOWN")
| stats count by deviceName, complianceState, operatingSystem, ownerType
| where compliance_state IN ("ALERT", "WARNING")
| sort -count

# Elastic/KQL - MDM Policy Violation Detection
event.dataset: "jamf.events" AND
event.action: ("restriction_violation" or "app_blocked" or "compliance_failed") AND
NOT device.os.version: "17.*"
```

### 2.6 MDM Zero Trust 구현 체크리스트

```yaml
# MDM Zero Trust Checklist
enrollment:
  - [ ] Apple DEP/ABM 자동 등록 구성 (Supervised 모드)
  - [ ] BYOD User Enrollment 분리 정책
  - [ ] 디바이스 인증서 기반 등록

app_control:
  - [ ] 관리형 앱 배포 목록 정의
  - [ ] 비인가 앱 차단 목록 업데이트 (분기별)
  - [ ] 앱 버전 최소 요구사항 설정

compliance:
  - [ ] OS 최소 버전 정책 (보안 패치 강제)
  - [ ] 탈옥/루팅 탐지 활성화
  - [ ] 비준수 디바이스 자동 격리 (24시간 유예)
  - [ ] 암호화 강제 (FileVault/BitLocker)

monitoring:
  - [ ] SIEM 연동 (Splunk/Elastic)
  - [ ] 비정상 체크인 패턴 알림
  - [ ] 관리 프로필 제거 시도 알림
  - [ ] 주간 컴플라이언스 리포트 자동화
```

---

## 3. 금주 뉴스 하이라이트

### 3.1 AI 에이전트 생태계

| 뉴스 | 핵심 내용 | 영향도 |
|------|-----------|--------|
| **Claude Code / Opus 4.5 에이전트 확장** | Anthropic Claude Code CLI의 에이전트 코딩 기능 강화, 멀티 에이전트 오케스트레이션 패턴 확산 | High |
| **OpenAI Codex Agent 출시** | 터미널 기반 AI 코딩 에이전트 경쟁 본격화 | High |
| **Amazon Bedrock AgentCore** | 멀티에이전트 운영 프레임워크, 항공사 사례 공개 | Medium |
| **OWASP Agentic AI Top 10 v1.0** | AI 에이전트 보안 표준 프레임워크 정식 발표 | High |

### 3.2 클라우드 및 Kubernetes 보안

| 뉴스 | 핵심 내용 | 영향도 |
|------|-----------|--------|
| **Kubernetes 1.33 보안 기능 강화** | Pod Security Admission 개선, Sidecar Container GA | High |
| **SBOM 컴플라이언스 의무화 확대** | 미국 연방기관 SBOM 제출 의무화 범위 확대, EU CRA 시행 | High |
| **AWS EKS Security Best Practices 2026** | Pod Identity, IRSA v2, Kyverno 정책 엔진 가이드 | Medium |
| **GCP Confidential GKE Nodes GA** | 메모리 암호화 기반 노드에서 Kubernetes 워크로드 실행 | Medium |

### 3.3 DevSecOps 동향

| 뉴스 | 핵심 내용 | 영향도 |
|------|-----------|--------|
| **GitOps + Policy-as-Code 융합** | OPA/Kyverno를 GitOps 파이프라인에 네이티브 통합하는 패턴 확산 | High |
| **Supply Chain Levels for Software Artifacts (SLSA) v1.1** | 빌드 무결성 검증 프레임워크 업데이트 | Medium |
| **Sigstore cosign 3.0** | 컨테이너 이미지 서명/검증 개선, OCI 레지스트리 네이티브 | Medium |

### 3.4 트렌드 분석

```
2026년 2월 보안/DevOps 트렌드 맵:

AI Agent Security ─────────────────── Zero Trust
     │                                     │
     ├─ Sandboxing (NanoClaw)              ├─ MDM App Control
     ├─ OWASP Agentic AI                   ├─ Conditional Access
     └─ Prompt Injection Defense           └─ Device Compliance
                    │                              │
                    └──────────┬───────────────────┘
                               │
                     Supply Chain Security
                               │
                    ├─ SBOM Compliance
                    ├─ SLSA v1.1
                    ├─ Sigstore cosign 3.0
                    └─ Container Security
```

---

## 4. 실무 체크리스트

### 이번 주 액션 아이템

```yaml
# Weekly Action Items - February 3, 2026
priority_high:
  - [ ] Jamf Extension Attribute 등록: OpenClaw/Moltbot 무단 설치 탐지
  - [ ] AI 코딩 에이전트 권한 감사 (파일/네트워크 접근 범위 확인)
  - [ ] MDM 앱 차단 목록 분기 업데이트 (비인가 앱 추가)
  - [ ] SBOM 생성 파이프라인 구축 (syft/trivy 활용)

priority_medium:
  - [ ] Smart Group 생성: OpenClaw 탐지 디바이스 자동 그룹화 + 알림
  - [ ] AI 에이전트 실행 로그 SIEM 연동 설정
  - [ ] Jamf/Intune 컴플라이언스 리포트 자동화
  - [ ] Kubernetes RBAC 감사 (최소 권한 확인)

priority_low:
  - [ ] OWASP Agentic AI Top 10 팀 공유
  - [ ] SLSA v1.1 빌드 무결성 파일럿
  - [ ] 에이전트 보안 정책 문서 초안 작성
```

---

## 참고 자료

### AI 에이전트 보안

| 제목 | URL |
|------|-----|
| OWASP Agentic AI Top 10 | [OWASP](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| NanoClaw - Minimal AI Agent | [GitHub](https://github.com/anthropics/anthropic-cookbook) |
| Claude Code Security Model | [Anthropic Docs](https://docs.anthropic.com/en/docs/claude-code/security) |

### MDM 관리

| 제목 | URL |
|------|-----|
| Jamf Pro Administrator Guide | [Jamf](https://learn.jamf.com/en-US/bundle/jamf-pro-documentation-current/page/About_Jamf_Pro.html) |
| Microsoft Intune App Protection Policies | [Microsoft](https://learn.microsoft.com/en-us/mem/intune/apps/app-protection-policy) |
| Intune Conditional Access | [Microsoft](https://learn.microsoft.com/en-us/mem/intune/protect/conditional-access) |
| Apple MDM Protocol Reference | [Apple](https://developer.apple.com/documentation/devicemanagement) |

### 보안 프레임워크

| 리소스 | URL |
|--------|-----|
| MITRE ATT&CK Framework | [attack.mitre.org](https://attack.mitre.org/) |
| NIST Zero Trust Architecture (SP 800-207) | [NIST](https://csrc.nist.gov/publications/detail/sp/800-207/final) |
| SLSA Framework | [slsa.dev](https://slsa.dev/) |
| CIS Benchmarks | [CIS](https://www.cisecurity.org/cis-benchmarks) |

### 지난주 다이제스트

| 제목 | URL |
|------|-----|
| Weekly Security Threat Intelligence Digest (Feb 2) | [Twodragon Blog](/2026-02-02-Weekly_Security_Threat_Intelligence_Digest) |
| Weekly Tech & AI & Blockchain Digest (Feb 2) | [Twodragon Blog](/2026-02-02-Weekly_Tech_AI_Blockchain_Digest) |

---

*이 글은 [Twodragon's Tech Blog](https://tech.2twodragon.com)에서 매주 발행하는 Security & DevOps Digest입니다. 최신 보안 뉴스와 실무 가이드를 매주 받아보세요.*
