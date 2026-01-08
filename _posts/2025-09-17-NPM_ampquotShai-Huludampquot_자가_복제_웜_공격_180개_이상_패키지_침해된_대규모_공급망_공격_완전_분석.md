---
layout: post
title: "NPM &amp;quot;Shai-Hulud&amp;quot; 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석"
date: 2025-09-17 16:20:06 +0900
categories: incident
tags: [npm, Supply-Chain-Attack, Worm, Security-Incident]
excerpt: "사건 개요 2025년 9월, NPM 생태계 역사상 최초의 자가 복제 웜 형태의 공급망 공격이 발생했습니다. "Shai-Hulud"(듄의 거대 샌드웜에서 유래)로 명명된 이 공격은 @ctrl/tinycolor를 포함한 180개 이상의 NPM 패키지를 감염시켰으며, 개발자 인증 정보를 탈취하여 자동으로 다른 패키지로 전파되는 특징을 보였습니다. 공격 영향 분석"
comments: true
original_url: https://twodragon.tistory.com/694
image: /assets/images/2025-09-17-NPM_ampquotShai-Huludampquot_자가_복제_웜_공격_180개_이상_패키지_침해된_대규모_공급망_공격_완전_분석.svg
---
## 📋 포스팅 요약

> **제목**: NPM "Shai-Hulud" 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석
> 
> **카테고리**: incident
> 
> **태그**: npm, Supply-Chain-Attack, Worm, Security-Incident
> 
> **핵심 내용**: 사건 개요 2025년 9월, NPM 생태계 역사상 최초의 자가 복제 웜 형태의 공급망 공격이 발생했습니다. "Shai-Hulud"(듄의 거대 샌드웜에서 유래)로 명명된 이 공격은 @ctrl/tinycolor를 포함한 180개 이상의 NPM 패키지를 감염시켰으며, 개발자 인증 정보를 탈취하여 자동으로 다른 패키지로 전파되는 특징을 보였습니다. 공격 영향 분석
> 
> ---
> 
> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


사건 개요
2025년 9월, NPM 생태계 역사상 최초의 자가 복제 웜 형태의 공급망 공격이 발생했습니다. "Shai-Hulud"(듄의 거대 샌드웜에서 유래)로 명명된 이 공격은 @ctrl/tinycolor를 포함한 180개 이상의 NPM 패키지를 감염시켰으며, 개발자 인증 정보를 탈취하여 자동으로 다른 패키지로 전파되는 특징을 보였습니다.

 공격 영향 분석
 타임라인

9월 15일 03:46 UTC: 최초 ..

원본 포스트: [https://twodragon.tistory.com/694](https://twodragon.tistory.com/694)
