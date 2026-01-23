# 다음 단계 가이드

## 📊 현재 상태

### ✅ 완료된 작업
1. **DeepSeek API 개선**
   - 타임아웃 증가: 30초 → 120초
   - 재시도 로직 추가: 최대 3회
   - 결과: 대본 생성 성공

2. **ElevenLabs 크레딧 최적화**
   - 대본 길이 제한: 3,000자 → 800자 (53% 감소)
   - 프롬프트 최적화: 간결한 대본 요청
   - 크레딧 부족 오류 처리 개선

3. **코드 개선 및 커밋**
   - 모든 개선사항 적용 완료
   - GitHub에 푸시 완료

## 🔍 ElevenLabs 크레딧 확인

### 방법 1: 웹 대시보드 (권장)
1. [ElevenLabs Usage 페이지](https://elevenlabs.io/app/usage) 접속
2. 로그인 후 크레딧 잔액 확인
3. 월간 사용량 확인

### 방법 2: API를 통한 확인
```bash
curl -X GET "https://api.elevenlabs.io/v1/user" \
  -H "xi-api-key: YOUR_API_KEY"
```

### 크레딧 요구사항
- **최소 필요 크레딧**: 800 크레딧
- **권장 크레딧**: 1,000 크레딧 이상 (여유 확보)

## 🚀 워크플로우 재실행

### 크레딧이 충분한 경우 (800 이상)

```bash
# 워크플로우 실행
gh workflow run "Generate AI Video Lecture" \
  --field post_file="" \
  --field video_method="ffmpeg"

# 실행 상태 확인
gh run list --workflow="Generate AI Video Lecture" --limit 1

# 로그 확인
gh run view <run-id> --log
```

### 크레딧이 부족한 경우

#### 옵션 1: 다음 달까지 대기
- ElevenLabs 무료 티어는 매월 크레딧이 리셋됩니다
- 다음 달 1일에 크레딧이 충전됩니다

#### 옵션 2: 유료 플랜 업그레이드
- **Starter 플랜**: $5/월, 30,000 크레딧
- **Creator 플랜**: $22/월, 100,000 크레딧
- **Pro 플랜**: $99/월, 500,000 크레딧

#### 옵션 3: 대본을 더 짧게 생성
- 현재 설정: 최대 800자
- 더 짧게 하려면 `MAX_SCRIPT_LENGTH`를 500자로 줄일 수 있음

## 📊 예상 크레딧 사용량

### 개선 후 설정
- 대본 길이: 최대 800자
- 필요 크레딧: 800 크레딧
- 월간 처리 가능: 약 12-13개 포스트 (10,000 크레딧 기준)

### 크레딧 관리 팁
1. **짧은 포스트 우선**: 긴 포스트보다 짧은 포스트를 먼저 처리
2. **사용량 모니터링**: 정기적으로 사용량 확인
3. **크레딧 제한 설정**: API Key에 월간 크레딧 제한 설정

## 🔧 추가 개선 가능 사항

### 1. 대본 길이 동적 조정
크레딧 잔액에 따라 대본 길이를 자동 조정:
```python
# 크레딧 확인 후 대본 길이 조정
if remaining_credits < 1000:
    MAX_SCRIPT_LENGTH = 500  # 더 짧게
else:
    MAX_SCRIPT_LENGTH = 800  # 기본값
```

### 2. 크레딧 사전 확인
워크플로우 실행 전 크레딧 확인:
```python
# ElevenLabs API로 크레딧 확인
response = requests.get(
    "https://api.elevenlabs.io/v1/user",
    headers={"xi-api-key": ELEVENLABS_API_KEY}
)
remaining_credits = response.json()["subscription"]["character_limit"]
```

### 3. 캐싱 추가
- 동일 포스트 재처리 시 캐시된 대본 사용
- 비용 절감 및 속도 향상

## 📝 체크리스트

워크플로우 실행 전 확인:
- [ ] ElevenLabs 크레딧 확인 (800 이상)
- [ ] DeepSeek API 키 유효성 확인
- [ ] GitHub Secrets 설정 확인
- [ ] 최신 코드가 푸시되었는지 확인

## 🔗 관련 문서

- [ElevenLabs Setup](./ELEVENLABS_SETUP.md)
- [Cost Management](./COST_MANAGEMENT.md)
- [ElevenLabs Quota Fix](./ELEVENLABS_QUOTA_FIX.md)
- [Workflow Improvements](./WORKFLOW_IMPROVEMENTS.md)
- [Troubleshooting Video Gen](./TROUBLESHOOTING_VIDEO_GEN.md)
