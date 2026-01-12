# TTS 오픈소스 통합 완료 요약

## ✅ 완료된 작업

### 1. TTS 오픈소스 라이브러리 통합

#### Edge-TTS (1순위 - 무료)
- ✅ Microsoft Edge TTS 통합
- ✅ API 키 불필요
- ✅ 한국어 지원
- ✅ 오디오 속도 조정 지원 (FFmpeg)

#### Coqui TTS (2순위 - 로컬 무료)
- ✅ Coqui TTS 통합
- ✅ 로컬 실행 가능
- ✅ 한국어 모델 지원
- ✅ 오디오 속도 조정 지원 (FFmpeg)

### 2. AWS/보안 아키텍처 다이어그램 자동 감지

#### 자동 감지 로직 개선
- ✅ AWS 키워드 2개 이상 감지 → Python Diagrams 사용
- ✅ 보안 키워드 2개 이상 감지 → Python Diagrams 사용
- ✅ 포스팅 image 필드 자동 업데이트

#### 지원 키워드 확장
- AWS 키워드: EC2, ECS, EKS, Lambda, S3, RDS, DynamoDB, VPC, IAM, WAF 등
- 보안 키워드: 보안, Security, WAF, Shield, IAM, 인증, 방화벽, ZTNA 등

### 3. 문서 업데이트

- ✅ `CONTENT_WORKFLOW.md` - TTS 옵션 업데이트
- ✅ `TTS_OPENSOURCE_GUIDE.md` - 상세 가이드 작성
- ✅ `requirements.txt` - TTS 라이브러리 추가

---

## 📦 설치 방법

### 필수 라이브러리 설치

```bash
# TTS 오픈소스 라이브러리
pip install edge-tts TTS

# AWS 다이어그램 생성
pip install diagrams graphviz

# 전체 의존성 설치
pip install -r scripts/requirements.txt
```

### 시스템 의존성 (macOS)

```bash
# Graphviz 설치 (diagrams 의존성)
brew install graphviz

# FFmpeg 설치 (오디오 속도 조정)
brew install ffmpeg
```

---

## 🚀 사용 방법

### 전체 워크플로우 실행

```bash
# 전체 파이프라인 (포스팅 → 이미지 → 대본 → TTS → 영상)
python3 scripts/generate_complete_content.py _posts/2026-01-12-Post.md
```

### TTS만 생성

```bash
# Edge-TTS 사용 (자동 선택)
python3 scripts/generate_enhanced_audio.py _posts/2026-01-12-Post.md

# 특정 TTS 방법 강제 사용
export PREFER_EDGE_TTS="true"
python3 scripts/generate_enhanced_audio.py _posts/2026-01-12-Post.md
```

### AWS 다이어그램 생성

```bash
# 자동 감지
python3 scripts/generate_aws_diagram.py _posts/2026-01-12-AWS_Security.md

# 특정 유형 지정
python3 scripts/generate_aws_diagram.py --type security _posts/2026-01-12-WAF.md
```

---

## 💰 비용 최적화 결과

### TTS 비용 절감

| 이전 | 이후 | 절감 |
|------|------|------|
| ElevenLabs (유료) | Edge-TTS (무료) | **100% 절감** |
| Gemini TTS (유료) | Coqui TTS (무료) | **100% 절감** |

### 이미지 생성 비용 절감

| 콘텐츠 유형 | 이전 | 이후 | 절감 |
|------------|------|------|------|
| AWS 아키텍처 | Gemini API (유료) | Python Diagrams (무료) | **100% 절감** |
| 보안 아키텍처 | Gemini API (유료) | Python Diagrams (무료) | **100% 절감** |

---

## 📊 TTS 우선순위

1. **Edge-TTS** (무료, API 키 불필요) ⭐ **권장**
2. **Coqui TTS** (로컬, 완전 무료)
3. **ElevenLabs** (유료, 최고 품질)
4. **Gemini TTS** (유료, 폴백)

---

## 🔍 자동 감지 예시

### AWS 아키텍처 자동 감지

```markdown
---
title: "AWS VPC 보안 아키텍처"
tags: [AWS, Security, VPC, IAM]
---

본문에 AWS, EC2, S3, RDS 등이 언급되면...
→ 자동으로 Python Diagrams 사용
```

### 보안 아키텍처 자동 감지

```markdown
---
title: "WAF와 Shield를 활용한 보안 방어"
tags: [Security, WAF, Shield, IAM]
---

본문에 보안, WAF, Shield, IAM 등이 언급되면...
→ 자동으로 Python Diagrams 사용
```

---

## 📝 변경된 파일

1. `scripts/generate_enhanced_audio.py`
   - Edge-TTS 통합
   - Coqui TTS 통합
   - 오디오 속도 조정 기능

2. `scripts/generate_complete_content.py`
   - AWS/보안 키워드 감지 개선
   - 포스팅 image 필드 자동 업데이트

3. `scripts/generate_aws_diagram.py`
   - 포스팅 image 필드 기반 경로 생성

4. `scripts/CONTENT_WORKFLOW.md`
   - TTS 옵션 업데이트
   - 비용 최적화 전략 업데이트

5. `scripts/requirements.txt`
   - edge-tts 추가
   - TTS 추가
   - diagrams 추가

6. `scripts/TTS_OPENSOURCE_GUIDE.md` (신규)
   - 상세 TTS 가이드

---

## ✅ 다음 단계

1. **테스트 실행**
   ```bash
   # Edge-TTS 테스트
   edge-tts --text "안녕하세요" --write-media test.mp3
   
   # 전체 워크플로우 테스트
   python3 scripts/generate_complete_content.py _posts/[최신포스트].md
   ```

2. **환경 변수 설정** (선택사항)
   ```bash
   # Edge-TTS 우선 사용
   export PREFER_EDGE_TTS="true"
   
   # Coqui TTS 우선 사용
   export PREFER_COQUI_TTS="true"
   ```

3. **모니터링**
   - TTS 생성 로그 확인
   - 비용 절감 효과 확인
   - 품질 검증

---

## 🎯 주요 개선 사항

1. **비용 절감**: TTS 비용 100% 절감 (무료 오픈소스 사용)
2. **자동화**: AWS/보안 아키텍처 자동 감지 및 다이어그램 생성
3. **품질 유지**: Edge-TTS와 Coqui TTS 모두 우수한 한국어 지원
4. **유연성**: 여러 TTS 옵션 제공으로 폴백 가능

---

## 📚 참고 문서

- [TTS 오픈소스 가이드](TTS_OPENSOURCE_GUIDE.md)
- [콘텐츠 워크플로우 가이드](CONTENT_WORKFLOW.md)
- [AWS 다이어그램 생성 가이드](generate_aws_diagram.py)
