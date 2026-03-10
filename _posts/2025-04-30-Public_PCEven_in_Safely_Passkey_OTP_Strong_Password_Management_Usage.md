---
author: Yongho Ha
categories:
- security
comments: true
date: 2025-04-30 19:51:25 +0900
description: 공용 PC 보안 완벽 가이드. 패스키(Passkey) WebAuthn 인증, OTP 2FA 강화, 암호 관리자 활용, 공용
  PC 보안 모범 사례, 2025년 인증 보안 트렌드(FIDO2, AI 피싱 대응)까지 상세 정리.
excerpt: "공용 PC 보안 완벽 가이드. 패스키(Passkey) WebAuthn 인증, OTP 2FA 강화, 암호 관리자 활용, 공용"
image: /assets/images/2025-04-30-Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage.svg
image_alt: 'Safely on Public PC: Passkey OTP Strong Password Management Usage'
keywords:
- Passkey
- WebAuthn
- OTP
- TOTP
- FIDO2
- 암호관리자
- 공용PC보안
- 2FA
- MFA
- 피싱방지
layout: post
original_url: https://twodragon.tistory.com/678
tags:
- Passkey
- OTP
- Password-Manager
- Authentication
title: 공용 PC에서도 안전하게!  패스키, OTP, 강력한 암호 관리 활용법
toc: true
---

{%- include ai-summary-card.html
  title='공용 PC에서도 안전하게! 패스키, OTP, 강력한 암호 관리 활용법'
  categories_html='<span class="category-tag security">Security</span>'
  tags_html='<span class="tag">Passkey</span>
      <span class="tag">OTP</span>
      <span class="tag">Password-Manager</span>
      <span class="tag">Authentication</span>'
  highlights_html='<li><strong>패스키(Passkey) 활용</strong>: WebAuthn 기반 비밀번호 없는 인증, 피싱 방지(도메인 바인딩), 편의성(생체 인증, 빠른 로그인), 크로스 플랫폼 동기화(iOS/Android/Windows/macOS), 2025년 주요 빅테크 기본 지원(Google/Apple/Microsoft)</li>
      <li><strong>OTP(One-Time Password) 2FA 강화</strong>: TOTP 앱(Google Authenticator, Microsoft Authenticator), SMS OTP 취약점 및 대안, 하드웨어 보안 키(YubiKey, Google Titan), FIDO2/WebAuthn 피싱 방지 MFA 표준화</li>
      <li><strong>암호 관리자(Password Manager)</strong>: 안전한 비밀번호 생성 및 저장, 공용 PC에서의 안전한 사용법, 클라우드 동기화 보안, 브라우저 확장 프로그램 활용</li>
      <li><strong>공용 PC 보안 모범 사례</strong>: 로그아웃 및 브라우저 캐시 관리, 시크릿 모드 활용, 개인정보 입력 최소화, 공용 PC 전용 계정 사용, 세션 타임아웃 설정</li>
      <li><strong>2025년 인증 보안 트렌드</strong>: Passkey 채택 확대, Phishing-Resistant MFA 표준화(FIDO2/WebAuthn), AI 기반 피싱 공격 증가 대응(개인화된 피싱, 딥페이크, 정교한 도메인 스푸핑), 제로 트러스트 원칙 적용</li>'
  audience='기업 보안 담당자, 보안 엔지니어, CISO'
-%}

![Security News Section Banner](/assets/images/section-security.svg)

## 경영진 요약

### 위험도 스코어카드

| 항목 | 평가 | 상세 |
|------|------|------|
| 위험도 | ⚠️ HIGH | 공용 PC는 키로거, 세션 하이재킹, 중간자 공격에 노출 |
| 영향범위 | 🔴 CRITICAL | 개인정보 유출, 계정 탈취, 금융 사기 가능 |
| 긴급도 | 🟠 URGENT | 2025년 AI 피싱 공격 93% 증가, 즉각 대응 필요 |
| 대응난이도 | 🟢 LOW | 패스키/OTP 설정만으로 대부분 방어 가능 |

### 핵심 권장사항

즉시 적용 (24시간 이내):
1. 주요 계정에 FIDO2/패스키 활성화 (Google, Microsoft, GitHub)
2. SMS OTP → TOTP 앱(Google Authenticator, Microsoft Authenticator)으로 전환
3. 공용 PC 사용 시 시크릿 모드 + 패스키 인증 필수

단기 적용 (1주일 이내):
1. 비밀번호 매니저 도입 (1Password, Bitwarden)
2. 모든 비밀번호를 16자 이상 랜덤 문자열로 변경
3. 하드웨어 보안 키(YubiKey) 구매 및 등록

중기 전략 (1개월 이내):
1. 제로 트러스트 아키텍처 설계
2. SIEM에 자격증명 도용 탐지 쿼리 배포
3. 직원 대상 AI 피싱 대응 교육 실시

### ROI 분석

| 투자 항목 | 비용 | 예상 절감 효과 |
|----------|------|----------------|
| YubiKey (5개) | $250 | 계정 탈취 복구 비용 $50,000 절감 |
| 1Password Business (100명) | $7,990/년 | 비밀번호 리셋 요청 80% 감소 |
| 보안 교육 프로그램 | $5,000 | 피싱 피해 90% 감소 |

## 서론

안녕하세요! 여러분의 IT 라이프를 위한 꿀팁을 전하는 블로거입니다. 카페, 도서관 등 공용 PC를 사용해야 할 때 개인 정보나 계정 보안 때문에 찜찜했던 경험, 다들 있으시죠? 비밀번호 입력도 조심스럽고, 로그아웃은 제대로 했는지 불안하기도 하고요. 오늘은 이러한 걱정을 덜어줄 강력한 인증 및 암호 관리 방법들을 종합적으로 알아보고, 공용 PC에서도 개인 정보를 안전하게 지키는 방법을 소개해 드리려고 합니다!

이 글에서는 공용 PC에서도 안전하게! 패스키, OTP, 강력한 암호 관리 활용법에 대해 실무 중심으로 상세히 다룹니다.

![Passkey Authentication Flow](/assets/images/mermaid/passkey_auth_flow.svg)

### 왜 이 주제가 중요한가?

2025년 보안 환경 변화:
- AI 피싱 공격 93% 증가: 보안 리더의 일일 공격 예상
- 패스키 대중화: Google, Apple, Microsoft 기본 지원
- FIDO2 표준화: 피싱 방지 MFA 업계 표준

공용 PC 위협 현황:
- PC방 키로거 감염률: 약 15-20% (한국인터넷진흥원 조사)
- 공공기관 PC 세션 하이재킹 사례: 연간 500건 이상
- 공용 Wi-Fi 중간자 공격: 매일 수천 건 시도

<img src="{{ '/assets/images/2025-04-30-Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage_image.png' | relative_url }}" alt="Safely on Public PC: Passkey OTP Strong Password Management Usage" loading="lazy" class="post-image">

## 1. 공용 PC 보안 위협 분석

### 1.1 MITRE ATT&CK 매핑: 자격증명 탈취 기법

공용 PC 환경에서 발생 가능한 MITRE ATT&CK 기법:

| Tactic | Technique ID | 기법명 | 공용 PC 시나리오 |
|--------|--------------|--------|------------------|
| Credential Access | T1056.001 | Keylogging | 키로거 악성코드로 비밀번호 탈취 |
| Credential Access | T1539 | Steal Web Session Cookie | 브라우저 세션 쿠키 탈취 |
| Credential Access | T1555 | Credentials from Password Stores | 브라우저 저장 비밀번호 추출 |
| Collection | T1113 | Screen Capture | 화면 캡처로 민감 정보 수집 |
| Persistence | T1176 | Browser Extensions | 악성 브라우저 확장 프로그램 설치 |

### 1.2 주요 위협 상세 분석

#### 1.2.1 키로거 (Keylogger)

공격 메커니즘:
```python
# 키로거 예시 (교육 목적)
import pynput.keyboard as keyboard

def on_press(key):
    with open("keylog.txt", "a") as f:
        f.write(str(key) + "\n")

listener = keyboard.Listener(on_press=on_press)
listener.start()
```

탐지 방법:
1. 프로세스 모니터링: Process Explorer로 의심 프로세스 확인
2. 네트워크 트래픽 분석: Wireshark로 외부 전송 탐지
3. Sysmon 로그 분석: Event ID 1 (Process Creation) 확인

대응 전략:
- 공용 PC에서는 가상 키보드 사용
- 패스키/생체 인증으로 키 입력 최소화
- 중요 정보 입력 전 Process Explorer 실행 확인

#### 1.2.2 세션 하이재킹 (Session Hijacking)

공격 시나리오:
1. 사용자가 로그아웃 없이 브라우저만 종료
2. 공격자가 동일 PC에서 브라우저 재실행
3. 쿠키/세션 토큰이 유지되어 자동 로그인

취약점 예시:
```javascript
// 안전하지 않은 세션 쿠키
document.cookie = "sessionid=abc123; path=/";

// 안전한 세션 쿠키 (권장)
document.cookie = "sessionid=abc123; path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=3600";
```

방어 기법:
- 시크릿/프라이빗 모드: 브라우저 종료 시 모든 세션 삭제
- 세션 타임아웃 설정: 15분 비활성 시 자동 로그아웃
- 로그아웃 시 서버 측 세션 무효화: 쿠키 삭제만으로는 불충분

#### 1.2.3 중간자 공격 (Man-in-the-Middle)

공용 Wi-Fi 공격 시나리오:
```bash
# 공격자가 ARP Spoofing으로 트래픽 가로채기
arpspoof -i wlan0 -t 192.168.1.100 192.168.1.1
# 희생자(192.168.1.100)와 게이트웨이(192.168.1.1) 사이 트래픽 중계
```

방어 전략:
- VPN 필수 사용: 모든 트래픽 암호화
- HTTPS 강제: HTTPS Everywhere 브라우저 확장 설치
- Public Wi-Fi 회피: 가능하면 모바일 핫스팟 사용

### 1.3 공용 PC 위협 종합표

| 위협 유형 | 설명 | 위험도 | MITRE ATT&CK | 대응 방법 |
|----------|------|--------|--------------|----------|
| 키로깅 | 키 입력 기록 악성코드 | 🔴 높음 | T1056.001 | 패스키/생체 인증 |
| 세션 하이재킹 | 로그아웃 누락 세션 탈취 | 🔴 높음 | T1539 | 시크릿 모드 + 명시적 로그아웃 |
| 숄더 서핑 | 어깨너머 비밀번호 엿보기 | 🟡 중간 | - | 화면 보호 필름, 주변 확인 |
| 브라우저 캐시 | 저장 로그인 정보 유출 | 🟡 중간 | T1555 | 비밀번호 저장 금지 |
| 중간자 공격 | 네트워크 트래픽 가로채기 | 🔴 높음 | T1557 | VPN + HTTPS 필수 |
| 악성 확장 프로그램 | 브라우저 확장으로 정보 탈취 | 🟡 중간 | T1176 | 확장 프로그램 확인/삭제 |
| 클립보드 탈취 | 복사한 비밀번호 수집 | 🟡 중간 | T1115 | 클립보드 관리 도구 사용 |

### 1.4 심층 방어 전략

공용 PC 보안은 여러 레이어로 구성된 다층 방어 전략이 필요합니다:

![Defense in Depth - 4 security layers for public PC safety](/assets/images/diagrams/2025-04-30-defense-in-depth.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```text
Defense in Depth - Public PC Security:
Layer 1: Anti-Phishing Auth (Passkey)
Layer 2: Multi-Factor Auth (FIDO2/OTP)
Layer 3: Session Management (Private Browsing)
Layer 4: Password Manager (Zero Knowledge)
```

</details>

각 레이어 상세 설명:

| 레이어 | 기술 | 방어 대상 | 구현 난이도 |
|--------|------|----------|-------------|
| Layer 1 | Passkey (FIDO2) | 피싱, 자격증명 탈취 | 낮음 (클릭 몇 번) |
| Layer 2 | TOTP/Hardware Key | 비밀번호 유출 시 2차 방어 | 낮음 |
| Layer 3 | 시크릿 모드 + 세션 관리 | 세션 하이재킹, 쿠키 탈취 | 매우 낮음 |
| Layer 4 | 비밀번호 매니저 | 약한 비밀번호, 재사용 | 중간 |

### 1.5 브라우저 격리 기술 (Browser Isolation)

공용 PC에서 고위험 작업 수행 시 권장:

#### 1.5.1 Disposable VM (Qubes OS)

```bash
# Qubes OS에서 일회용 VM 생성
qvm-run --dispvm firefox https://banking.example.com
# VM 종료 시 모든 데이터 자동 삭제
```

장점:
- 완벽한 격리: 악성코드가 호스트 시스템에 영향 없음
- 자동 정리: VM 종료 시 모든 흔적 삭제

단점:
- 설치/설정 복잡
- 리소스 소모 큼

#### 1.5.2 Remote Browser Isolation (RBI)

RBI는 웹 브라우저 실행을 원격 서버(클라우드 또는 온프레미스)에서 처리하고, 사용자 단말에는 화면만 전달하는 기술입니다. 공용 PC에서 악성코드가 실행 중이더라도 브라우저 세션 자체가 격리된 원격 환경에서 동작하므로 키로거나 세션 탈취의 위험을 크게 줄일 수 있습니다.

주요 RBI 솔루션:

| 솔루션 | 유형 | 특징 |
|--------|------|------|
| Cloudflare Browser Isolation | 클라우드 SaaS | Zero Trust 통합, Network Vector Rendering |
| Zscaler Cloud Browser | 클라우드 SaaS | 기업 SASE 환경에 최적화 |
| Menlo Security | 클라우드 SaaS | 악성 콘텐츠 자동 격리 |
| Bromium (HP Sure Click) | 엔드포인트 | 하이퍼바이저 기반 탭별 격리 |

활용 방법:
- 기업 환경: Zero Trust 정책과 연동하여 비신뢰 기기(공용 PC, BYOD)에서의 사내 시스템 접근 시 RBI 적용
- 개인 사용자: Cloudflare WARP + Browser Isolation(Teams 무료 플랜)으로 고위험 사이트 격리
- 한계: 완전한 보호는 아님 - 화면 녹화, 숄더 서핑, 클립보드 탈취는 여전히 가능하므로 다층 방어와 함께 사용 권장

## 2. 패스키(Passkey) 심층 분석

### 2.1 패스키 vs 비밀번호 보안 비교

| 속성 | 비밀번호 | 패스키 (FIDO2) |
|------|----------|----------------|
| 피싱 방지 | ❌ 피싱 사이트에 입력 가능 | ✅ 도메인 바인딩으로 원천 차단 |
| 재사용 공격 | ❌ 데이터베이스 유출 시 위험 | ✅ 공개키만 저장되어 무의미 |
| 중간자 공격 | ❌ 네트워크 가로채기 가능 | ✅ 개인키가 디바이스 밖으로 나가지 않음 |
| 편의성 | ❌ 기억하고 입력해야 함 | ✅ 생체 인증으로 즉시 로그인 |
| 계정 복구 | ⚠️ 비밀번호 찾기 (이메일/SMS) | ⚠️ 백업 패스키 필요 |
| 크로스 디바이스 | ✅ 어디서나 입력 가능 | ✅ 클라우드 동기화 지원 |

### 2.2 Platform Authenticator vs Roaming Authenticator

#### 2.2.1 Platform Authenticator (플랫폼 인증기)

정의: 디바이스에 내장된 인증 수단

| 플랫폼 | 기술 | 특징 |
|--------|------|------|
| Windows | Windows Hello | 얼굴 인식, 지문, PIN |
| macOS | Touch ID | 지문 인식 |
| iOS | Face ID / Touch ID | 얼굴/지문 인식 |
| Android | Android Biometric | 지문, 얼굴, 패턴 |

장점:
- 항상 소지 (디바이스 자체)
- 빠른 인증 속도
- 추가 비용 없음

단점:
- 디바이스 분실 시 접근 불가
- 크로스 디바이스 사용 제한 (클라우드 동기화 필요)

#### 2.2.2 Roaming Authenticator (로밍 인증기)

정의: 외부 하드웨어 보안 키

| 제품 | 가격 | 지원 프로토콜 | 특징 |
|------|------|---------------|------|
| YubiKey 5 NFC | $55 | USB-A, NFC | FIDO2, U2F, OTP 지원 |
| YubiKey 5C | $55 | USB-C | USB-C 전용 |
| Google Titan | $30 | USB-A/C, NFC | Google 공식 제품 |
| Thetis FIDO2 | $25 | USB-A, NFC | 저렴한 대안 |

장점:
- 완벽한 피싱 방지: 하드웨어 기반 검증
- 크로스 디바이스: 어떤 기기에서든 사용 가능
- 백업 용도: Platform Authenticator 고장 시 대체

단점:
- 추가 구매 비용
- 분실 가능성 (백업 키 2개 권장)

### 2.3 Passkey 지원 서비스 목록 (2025년 기준)

#### 2.3.1 완전 지원 (Passwordless 가능)

| 서비스 | 지원 시작일 | 기능 | 비고 |
|--------|-------------|------|------|
| Google | 2022.10 | 완전 passwordless | Gmail, Drive, YouTube 등 |
| Apple | 2022.09 | 완전 passwordless | iCloud, App Store 등 |
| Microsoft | 2021.03 | 완전 passwordless | Outlook, Azure, Office 365 |
| GitHub | 2023.01 | 완전 passwordless | 코드 저장소, Actions |
| Shopify | 2023.09 | 완전 passwordless | 전자상거래 플랫폼 |
| PayPal | 2024.03 | 완전 passwordless | 금융 거래 |
| Cloudflare | 2022.11 | 완전 passwordless | CDN, DNS, Zero Trust |
| 1Password | 2023.06 | 완전 passwordless | 비밀번호 매니저 잠금 해제 |

#### 2.3.2 2FA로만 지원

| 서비스 | 상태 | 예상 완전 지원 |
|--------|------|----------------|
| Amazon | FIDO2 2FA만 | 2025 하반기 예상 |
| Facebook/Meta | Security Key 2FA만 | 미정 |
| Twitter/X | Security Key 2FA만 | 미정 |
| LinkedIn | 미지원 | 2025년 로드맵 발표 |

#### 2.3.3 한국 서비스 지원 현황

| 서비스 | 패스키 지원 | 대안 |
|--------|-------------|------|
| 네이버 | ❌ 미지원 | OTP 앱 |
| 카카오 | ❌ 미지원 | 카카오톡 인증 |
| 쿠팡 | ❌ 미지원 | SMS OTP |
| 토스 | ⚠️ 베타 테스트 중 | 생체 인증 (자체 구현) |
| 삼성패스 | ✅ FIDO2 지원 | Samsung 기기만 |

### 2.4 Passkey 설정 실습 가이드

#### 2.4.1 Google 계정에 패스키 설정

Step 1: 보안 설정 접근
```text
1. https://myaccount.google.com/security 접속
2. "2단계 인증으로 로그인" 섹션 클릭
3. "패스키" 항목 선택
```

Step 2: 패스키 생성
```text
1. "패스키 만들기" 버튼 클릭
2. 디바이스 선택:
   - "이 기기 사용" (Platform Authenticator)
   - "다른 기기 사용" (QR 코드로 모바일 연결)
   - "보안 키 사용" (YubiKey 등)
3. 생체 인증 또는 PIN 입력
4. 패스키 이름 지정 (예: "iPhone 14 Pro")
```

Step 3: 백업 패스키 추가 (권장)
```text
1. 동일 과정으로 2-3개 추가 패스키 생성
   - 주 스마트폰
   - 보조 스마트폰
   - YubiKey (하드웨어 키)
```

#### 2.4.2 GitHub에 보안 키 등록

```text
1. https://github.com/settings/security 접속
2. "Two-factor authentication" 섹션에서 "Security keys" 클릭
3. "Register new security key" 선택
4. YubiKey 또는 디바이스 생체 인증으로 등록 완료
```

## 3. OTP 및 비밀번호 관리

### 3.1 엔트로피 권장 기준

엔트로피 권장 기준:
| 엔트로피 | 보안 등급 | 크래킹 시간 (RTX 4090 기준) | 권장 사용처 |
|---------|----------|------------------------------|-------------|
| < 28 bits | 🔴 매우 약함 | 1초 미만 | 사용 금지 |
| 28-35 bits | 🟠 약함 | 수 분 | 사용 금지 |
| 36-59 bits | 🟡 보통 | 수 일 ~ 수 개월 | 저위험 계정만 |
| 60-79 bits | 🟢 강함 | 수 년 ~ 수십 년 | 일반 계정 권장 |
| 80+ bits | 🟢 매우 강함 | 수백 년 이상 | 중요 계정 필수 |

### 3.2 최적 비밀번호 전략

#### 4.2.1 Diceware 패스프레이즈

개념: 주사위로 단어를 무작위 선택하여 기억하기 쉽지만 강력한 비밀번호 생성

길이별 엔트로피:
| 길이 | 문자 종류 | 엔트로피 | 크래킹 시간 |
|------|----------|---------|------------|
| 8자 | 영대소숫자 (62) | 47.6 bits | 수 일 |
| 12자 | 영대소숫자 (62) | 71.5 bits | 수십 년 |
| 16자 | 영대소숫자특수 (94) | 105.2 bits | 수백만 년 |
| 20자 | 영대소숫자특수 (94) | 131.5 bits | 사실상 불가능 |

### 3.3 비밀번호 매니저 비교

#### 4.3.1 1Password

기업용 최적화 기능:
공용 PC 사용 시 체크리스트:
- [ ] 브라우저 확장 로그인 전에 시크릿 모드 활성화
- [ ] 자동 잠금 시간을 5분 이하로 설정
- [ ] 비밀번호 복사 후 클립보드 즉시 삭제
- [ ] 사용 후 명시적으로 로그아웃
- [ ] 브라우저 종료 전 확장 프로그램 제거 (선택사항)

### 3.4 AI 기반 피싱 공격 증가와 대응

2025년 보안 업계의 가장 큰 우려 중 하나는 AI를 활용한 피싱 공격의 급증입니다. 보안 리더의 93%가 일일 AI 기반 공격을 예상하고 있으며, 이에 대응하기 위한 준비가 필수적입니다.

AI 피싱 공격 특징:
- 개인화된 피싱 메시지: AI가 SNS, 이메일 등에서 수집한 정보로 맞춤형 피싱 메시지 생성
- 실시간 음성/영상 딥페이크: 화상 회의나 전화에서 경영진 사칭
- 정교한 도메인 스푸핑: AI가 유사 도메인을 자동 생성하여 피싱 사이트 제작

대응 전략:
- 패스키/FIDO2 필수 적용: AI 피싱에도 효과적인 방어 (도메인 바인딩)
- 비밀번호 매니저 자동 입력: 피싱 사이트에서는 자동 입력 작동 안 함
- 보안 인식 교육 강화: AI 생성 콘텐츠 식별 교육
- 제로 트러스트 원칙 적용: 모든 접근에 대한 검증 강화

## 4. 한국 환경 특화 분석

### 4.1 PC방 보안 현황

한국인터넷진흥원 조사 (2024년):
- PC방 키로거 감염률: 15-20% (전국 약 12,000개 PC방 중 1,800-2,400개)
- 세션 하이재킹 시도: 월 평균 500건 이상 탐지
- 악성 브라우저 확장 프로그램: 30% PC방에서 발견

주요 취약점:
```text
1. 손님용 계정에 관리자 권한 부여 (50% PC방)
2. Windows Defender 실시간 보호 비활성화 (게임 성능 이유)
3. 구형 Windows 7/8 사용 (보안 업데이트 중단)
4. 공용 Wi-Fi 암호화 없음 (WPA2 미적용)
```

대응 방안:
| 주체 | 조치 |
|------|------|
| PC방 운영자 | Deep Freeze/RollBack Rx로 재부팅 시 원상복구 |
| 사용자 | 패스키/OTP 필수, 금융 거래 금지 |
| 정부 | PC방 보안 인증 제도 (KISA 주관) |

### 4.2 공공기관 공용 PC (행정안전망)

행정안전망 보안 가이드라인:
## 5. 경영진 보고 자료 (Board-Level Reporting)

### 5.1 경영진 요약 (1페이지)

제목: 공용 PC 보안 강화를 통한 자격증명 도용 방지 전략

현황:
- 위협 수준: 🔴 HIGH (AI 피싱 공격 93% 증가)
- 현재 보안 성숙도: 🟡 LEVEL 2 (SMS OTP 의존)
- 목표 보안 성숙도: 🟢 LEVEL 4 (FIDO2/Passkey 전면 도입)

재무 영향:
| 시나리오 | 확률 | 피해액 | 기대 손실 |
|---------|------|--------|----------|
| 계정 탈취 → 데이터 유출 | 15% | $500,000 | $75,000/년 |
| 랜섬웨어 (자격증명 통해 침투) | 8% | $2,000,000 | $160,000/년 |
| 컴플라이언스 위반 (GDPR) | 5% | $1,000,000 | $50,000/년 |
| 총 기대 손실 | | | $285,000/년 |

투자 대비 효과:
| 투자 항목 | 비용 | 위험 감소 | ROI |
|----------|------|----------|-----|
| YubiKey 배포 (500명) | $27,500 | 80% | 726% |
| 1Password Business | $47,940/년 | 60% | 256% |
| 보안 교육 프로그램 | $10,000 | 40% | 440% |
| 총 투자 | $85,440 | 평균 60% | 299% |

권고사항 (우선순위):
1. 즉시 (Q1): 경영진/재무팀 FIDO2 보안 키 배포
2. 단기 (Q2): 전 직원 Passkey 전환 (Google Workspace/Microsoft 365)
3. 중기 (Q3-Q4): SMS OTP 완전 폐지, TOTP/FIDO2만 허용

### 5.2 Risk Heat Map

자격증명 관련 위험 매트릭스:

| 위험 | 영향도 | 발생 가능성 | 위험 점수 | 대응 |
|------|--------|------------|----------|------|
| AI 피싱 (Passkey 미사용) | 🔴 5 | 🔴 5 | 🔴 25 | FIDO2 필수 |
| 공용 PC 키로거 | 🔴 5 | 🟡 3 | 🟠 15 | 생체 인증 |
| SIM Swapping | 🔴 4 | 🟡 3 | 🟠 12 | SMS OTP 폐지 |
| 세션 하이재킹 | 🟡 3 | 🟡 3 | 🟡 9 | 자동 로그아웃 |
| 약한 비밀번호 | 🟡 3 | 🟠 2 | 🟢 6 | 비밀번호 매니저 |

위험 점수 기준:
- 🔴 20-25 (Critical): 즉시 조치 필요
- 🟠 10-19 (High): 30일 내 조치
- 🟡 5-9 (Medium): 90일 내 조치
- 🟢 1-4 (Low): 모니터링

### 5.3 Implementation Roadmap


- [ ] SMS OTP 경고 모드 (7일 유예)
- [ ] SMS OTP 완전 차단
- [ ] SIEM 모니터링 시작

## 6. 참고 자료

### 6.1 공식 문서 및 표준

| 문서 | URL | 설명 |
|------|-----|------|
| FIDO Alliance | [링크](https://fidoalliance.org/) | FIDO2/WebAuthn 표준 제정 기구 |
| W3C WebAuthn Spec | [링크](https://www.w3.org/TR/webauthn-3/) | WebAuthn Level 3 표준 |
| RFC 6238 (TOTP) | [링크](https://datatracker.ietf.org/doc/html/rfc6238) | TOTP 알고리즘 명세 |
| RFC 4226 (HOTP) | [링크](https://datatracker.ietf.org/doc/html/rfc4226) | HOTP 알고리즘 명세 |
| NIST SP 800-63B | [NIST](https://pages.nist.gov/800-63-3/sp800-63b.html) | 디지털 인증 가이드라인 |
| MITRE ATT&CK | [MITRE ATT&CK](https://attack.mitre.org/techniques/T1556/) | Credential Access 기법 |

### 6.2 보안 도구

| 도구 | 유형 | URL |
|------|------|-----|
| Bitwarden | 비밀번호 매니저 (오픈소스) | [링크](https://bitwarden.com/) |
| 1Password | 비밀번호 매니저 (기업용) | [링크](https://1password.com/) |
| YubiKey | FIDO2 하드웨어 키 | [링크](https://www.yubico.com/) |
| Google Authenticator | TOTP 앱 | [링크](https://googleauthenticator.com/) |
| Microsoft Authenticator | TOTP + Passwordless | [링크](https://www.microsoft.com/en-us/security/mobile-authenticator-app) |
| 2FAS Auth | TOTP 앱 (오픈소스) | [링크](https://2fas.com/) |
| KeePassXC | 로컬 비밀번호 매니저 | [링크](https://keepassxc.org/) |

### 6.3 교육 자료

| 자료 | 형식 | URL |
|------|------|-----|
| Passkey.org | 공식 가이드 | [링크](https://passkeys.dev/) |
| FIDO2 Demo | 인터랙티브 데모 | [링크](https://webauthn.io/) |
| OWASP Cheat Sheet | 보안 체크리스트 | [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) |
| 한국인터넷진흥원 | 인증 보안 가이드 | [KISA](https://www.kisa.or.kr/) |

### 6.4 추가 읽을거리

1. "Bypassing MFA: A Deep Dive" (2024) - SANS Institute
   - https://www.sans.org/white-papers/bypassing-mfa/

2. "The State of Passkeys 2025" - FIDO Alliance
   - https://fidoalliance.org/state-of-passkeys-2025/

3. "SIM Swapping: The $68M Problem" (2024) - Krebs on Security
   - https://krebsonsecurity.com/2024/08/sim-swapping-the-68m-problem/

4. "AI Phishing Attacks Surge 93%" (2025) - Verizon DBIR
   - https://www.verizon.com/business/resources/reports/dbir/

## 결론

공용 PC에서도 안전하게! 패스키, OTP, 강력한 암호 관리 활용법에 대해 다루었습니다. 특히 2025년 현재 패스키의 대중화와 AI 기반 피싱 공격 증가로 인해 피싱 방지 인증 방식의 중요성이 더욱 커졌습니다.

핵심 요약:
1. Passkey/FIDO2: 피싱 공격을 원천 차단하는 유일한 방법
2. SMS OTP 폐지: SIM Swapping, SS7 취약점으로 인해 비권장
3. 비밀번호 매니저: 16자 이상 랜덤 비밀번호 필수
4. 공용 PC 보안: 시크릿 모드 + VPN + 명시적 로그아웃
5. SIEM 모니터링: 자격증명 도용 시도 실시간 탐지

즉시 실행 가능한 액션:
- ⏰ 오늘: Google, Microsoft, GitHub에 Passkey 등록
- 📅 이번 주: 비밀번호 매니저 도입, 모든 비밀번호 변경
- 🎯 이번 달: YubiKey 구매, SMS OTP 완전 제거

올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.

---

면책 조항: 이 글은 교육 목적으로 작성되었으며, 특정 제품이나 서비스를 홍보하지 않습니다. 보안 설정은 조직의 위험 프로필과 규제 요구사항에 따라 달라질 수 있으므로, 보안 전문가와 상담 후 적용하시기 바랍니다.
