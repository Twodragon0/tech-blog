---
layout: post
title: "개인정보 보호 및 Passkey 설정 가이드"
date: 2024-12-25 09:49:00 +0900
last_modified_at: 2025-02-27T15:36:14+09:00
categories: [security]
tags: [Passkey, Privacy, Authentication]
excerpt: "공용 PC 사용 후 개인정보를 보호하고 Passkey를 활용하여 안전한 인증 환경을 구축하는 방법을 안내드립니다. Passkey는 비밀번호를 대체하는 차세대 인증 기술로, 사용 편의성과 보안성을 동시에 제공합니다."
description: "공용 PC 사용 후 개인정보를 보호하고 Passkey를 활용하여 안전한 인증 환경을 구축하는 방법을 안내드립니다. Passkey는 비밀번호를 대체하는 차세대 인증 기술로, 사용 편의성과 보안성을 동시에 제공합니다."
keywords: [Passkey, Privacy, Authentication]
author: Twodragon
comments: true
image: /assets/images/2024-12-25-Privacy_Protection_And_Passkey_Setup_Guide.png
image_alt: "Privacy Protection and Passkey Setup Guide"
toc: true
original_url: https://2twodragon.com/passkey/
---

> 이 글은 2twodragon.com(워드프레스)에서 2024-12-25에 처음 게시된 글을 옮긴 것입니다.

공용 PC 사용 후 개인정보를 보호하고 Passkey를 활용하여 안전한 인증 환경을 구축하는 방법을 안내드립니다. Passkey는 비밀번호를 대체하는 차세대 인증 기술로, 사용 편의성과 보안성을 동시에 제공합니다.

**Passkey란?** 🔑

- Passkey는 비밀번호 없이 생체 인증(지문, 얼굴 인식) 또는 장치 PIN을 사용해 계정에 로그인하는 FIDO2 기반 인증 방식입니다.
- 개인 데이터를 보호하고 피싱 및 비밀번호 유출 위험을 줄일 수 있는 차세대 인증 기술입니다.

## Passkey 설정 및 사용 방법

## 1. macOS에서 Passkey 설정 및 사용

1.  Safari에서 Passkey 지원 확인 : macOS Ventura 이상 버전에서 Safari가 Passkey를 지원하는지 확인합니다.
2.  Passkey 설정 : Passkey를 지원하는 웹사이트에서 로그인 또는 회원가입 진행하고, Passkey 설정 시 생체 인증(Face ID, Touch ID) 또는 장치 암호로 등록합니다.
3.  iCloud 키체인 활성화 🔐 : 시스템 설정 \> Apple ID \> iCloud \> 비밀번호 및 키체인을 활성화하여 Passkey를 iCloud에 동기화합니다.
4.  Safari에서 웹사이트 방문 : Passkey를 지원하는 웹사이트로 이동합니다.
5.  Passkey 로그인 선택 : 생체 인증(Touch ID, Face ID) 또는 장치 암호를 입력하여 즉시 로그인합니다.

## 2. Chrome에서 Passkey 설정 및 사용

1.  Chrome 최신 버전 확인 : Chrome이 최신 버전인지 확인하고 업데이트합니다.
2.  Passkey 지원 웹사이트 방문 : Passkey를 지원하는 사이트에서 로그인 또는 회원가입 진행.
3.  Passkey 등록 : 등록 과정에서 생체 인증(Touch ID, Face ID) 또는 장치 PIN을 사용하여 Passkey를 생성합니다.
4.  Passkey 지원 사이트 방문 : Chrome 브라우저에서 해당 사이트로 이동합니다.
5.  Passkey 선택 및 인증 : 로그인 페이지에서 Passkey를 선택하고, 생체 인증(Touch ID, Face ID) 또는 장치 PIN으로 인증합니다.

**지문 인식 보안 가이드** 🖐️

1.  고유성 : 개인의 고유한 지문 패턴을 사용하여 높은 보안을 제공합니다.
2.  편의성 : 비밀번호를 기억하지 않아도 빠르고 간단하게 인증 가능.
3.  빠른 인증 : 지문을 통한 인증은 비밀번호 입력보다 훨씬 빠릅니다.

**지문 인식 사용 시 주의사항** ⚠️

1.  정확한 등록 : 지문 등록 시 손가락이 깨끗하고 다양한 각도로 스캔되었는지 확인하세요.
2.  센서 관리 : 지문 센서를 깨끗하게 유지하고, 손상이 있는 경우 대체 손가락을 등록하세요.
3.  보조 인증 설정 : 지문 인식이 실패할 경우를 대비해 PIN 또는 패턴을 보조 인증 수단으로 설정하세요.

**공용 PC에서 Passkey 및 생체 인증 사용 시 주의사항** ⚠️

1.  Passkey 등록 피하기 : 공용 PC에서는 Passkey를 생성하거나 저장하지 마세요.
2.  자동 로그아웃 확인 : 공용 PC에서 사용 후 자동 로그아웃이 설정되었는지 확인하세요.
3.  로그인 후 흔적 삭제 : 브라우저 방문 기록 및 쿠키를 삭제하여 로그인 정보가 저장되지 않도록 하세요.
4.  로그인 보조 장치 사용 : 공용 PC에서 로그인해야 할 경우 개인 스마트폰 또는 USB 보안 키를 활용하세요.
5.  화면 잠금 활성화 : 자리를 비울 때 화면 잠금을 활성화하여 계정을 보호하세요.
    - Windows: Windows 키 + L
    - macOS: Control + Command + Q

**Passkey의 장점** 🌟

1.  비밀번호 없이 로그인 가능 : 기억할 필요 없이 생체 인증 또는 PIN을 통해 빠르고 안전한 인증 가능.
2.  강력한 보안 : 피싱 및 비밀번호 유출 위험을 크게 줄임.
3.  다양한 장치 간 연동 : macOS, iOS, Android, Chrome 등 여러 기기에서 동일한 Passkey 사용 가능.
4.  Google, Microsoft, Apple 등 주요 서비스에서 Passkey 지원.
5.  지원 사이트는 계속 확장 중이며, Passkey를 지원하는 앱과 웹사이트에서 쉽게 설정 및 사용 가능합니다.

💡 Tip: Passkey는 iCloud와 Google 계정을 통해 동기화되므로, 다른 장치에서도 동일한 인증 정보를 사용할 수 있습니다.

공용 PC 사용 후 개인 정보를 보호하려면 위 가이드를 철저히 따라주세요! 🌟✨
