# 비용 관리 가이드

이 문서는 GitHub Actions와 외부 API 사용 시 비용을 효율적으로 관리하는 방법을 제공합니다.

## 💰 ElevenLabs 비용 관리

### 무료 티어 제한
- **월 10,000자** 제한
- 초과 시 유료 플랜 필요
- 사용량 확인: [ElevenLabs Usage](https://elevenlabs.io/app/usage)

### 비용 절감 전략

#### 1. 크레딧 제한 설정
API Key 생성 시 월간 크레딧 제한을 설정하여 예상치 못한 사용을 방지합니다.

**설정 방법:**
1. ElevenLabs Creative Platform → Developers → API Keys
2. API Key 생성 또는 편집
3. **Credit Limit** → **Monthly** 설정
4. 예상 사용량보다 여유있게 설정 (예: 5,000자)

#### 2. 포스트 요약
긴 포스트는 DeepSeek AI로 요약하여 사용량을 절감합니다.

```python
# scripts/generate_enhanced_audio.py에서 자동으로 처리
MAX_SCRIPT_LENGTH = 3000  # 최대 대본 길이 (약 5분 분량)
```

#### 3. 수동 실행만 허용
워크플로우는 `workflow_dispatch`로만 실행하여 자동 실행을 방지합니다.

```yaml
# .github/workflows/ai-video-gen.yml
on:
  workflow_dispatch:  # 수동 실행만 허용
  # push 이벤트는 주석 처리 (비용 관리)
```

#### 4. 사용량 모니터링
정기적으로 사용량을 확인하고 알림을 설정합니다.

**모니터링 방법:**
- ElevenLabs 대시보드: **Developers** → **Usage**
- GitHub Actions 로그에서 생성된 파일 크기 확인
- 월간 사용량 리포트 확인

### 비용 예측

| 항목 | 예상 비용 |
|------|----------|
| 무료 티어 | 월 10,000자 (무료) |
| Starter 플랜 | $5/월 (30,000자) |
| Creator 플랜 | $22/월 (100,000자) |
| Pro 플랜 | $99/월 (500,000자) |

**비용 계산:**
- 평균 포스트 길이: 3,000자 (요약 후)
- 월간 포스트 수: 약 3개
- 예상 사용량: 9,000자/월 (무료 티어 내)

## 🔒 보안을 통한 비용 보호

### 1. API Key 권한 제한
최소 권한 원칙을 적용하여 불필요한 API 호출을 방지합니다.

**권장 설정:**
- ✅ Text to Speech: **Access** (필수)
- ❌ 나머지 권한: **No Access**

### 2. 크레딧 제한
API Key 레벨에서 크레딧 제한을 설정하여 예상치 못한 사용을 방지합니다.

### 3. Secrets 보안
API Key가 유출되지 않도록 주의합니다.

- 절대 Git에 커밋하지 않기
- 로그에 API Key 값 출력하지 않기
- 정기적으로 키 로테이션

## 📊 사용량 추적

### ElevenLabs 사용량 확인

1. **대시보드 확인**
   - [ElevenLabs Usage](https://elevenlabs.io/app/usage)
   - 월간 사용량 및 크레딧 잔액 확인

2. **API를 통한 확인**
   ```bash
   curl -X GET "https://api.elevenlabs.io/v1/user" \
     -H "xi-api-key: YOUR_API_KEY"
   ```

3. **GitHub Actions 로그**
   - 워크플로우 실행 후 생성된 파일 크기 확인
   - 로그에서 사용된 문자 수 확인

### 알림 설정

1. **ElevenLabs 대시보드**
   - 사용량 임계값 설정
   - 크레딧 부족 시 이메일 알림

2. **GitHub Actions**
   - 워크플로우 실패 시 알림
   - 사용량 초과 시 워크플로우 중단

## 🎯 최적화 팁

### 1. 포스트 선택
- 긴 포스트는 요약 후 사용
- 중요한 포스트만 영상으로 변환
- 시리즈 포스트는 통합 고려

### 2. 대본 최적화
- 불필요한 문장 제거
- 반복되는 내용 축약
- 핵심 내용만 포함

### 3. Voice 설정
- 적절한 Voice 선택으로 재생성 방지
- Voice Cloning으로 일관성 유지

## 📈 비용 모니터링 체크리스트

- [ ] 월간 사용량 확인 (매월 1일)
- [ ] 크레딧 제한 설정 확인
- [ ] 예상 사용량 대비 실제 사용량 비교
- [ ] 비용 초과 시 플랜 업그레이드 고려
- [ ] 사용하지 않는 API Key 삭제
- [ ] 워크플로우 로그 정기 확인

## 🔗 관련 문서

- [ElevenLabs Setup Guide](./ELEVENLABS_SETUP.md)
- [Secrets Management](./SECRETS_MANAGEMENT.md)
- [ElevenLabs Platform Guide](../scripts/ELEVENLABS_PLATFORM_GUIDE.md)
