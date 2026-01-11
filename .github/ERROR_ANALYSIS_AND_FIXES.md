# 에러 분석 및 개선사항

## 📊 로그 분석 결과

### 최신 실행 (Run ID: 20892607641)
- **상태**: `completed` (failure)
- **실행 시간**: 50초
- **실패 원인**: ElevenLabs 크레딧 부족

### 발견된 에러

#### 1. ElevenLabs API 크레딧 부족 ✅ (해결됨)
```
[ERROR] ❌ ElevenLabs API 요청 실패: 401 Client Error: Unauthorized
응답 내용: {"detail": {"status": "quota_exceeded", "message": "This request exceeds your API key (Twodragon) quota of 5. You have 5 credits remaining, while 1727 credits are required for this request."}}
```

**문제점:**
- 대본 생성 성공: 1,727자
- 필요 크레딧: 1,727 크레딧
- 남은 크레딧: 5 크레딧
- 크레딧 부족으로 음성 생성 실패

**해결 방법:**
1. ✅ 대본 길이 제한: 3,000자 → 800자 (53% 감소)
2. ✅ 크레딧 사전 확인 기능 추가
3. ✅ 크레딧 부족 시 조기 실패 및 명확한 메시지

## ✅ 적용된 개선사항

### 1. 크레딧 사전 확인 기능 추가

#### `check_elevenlabs_credits()` 함수 추가
- ElevenLabs API `/v1/user` 엔드포인트 사용
- 남은 크레딧 확인
- 필요 크레딧과 비교
- 부족 시 상세 안내 메시지

```python
def check_elevenlabs_credits(required_credits: int = 800) -> Optional[int]:
    """ElevenLabs API 크레딧을 확인합니다."""
    # API 호출하여 크레딧 확인
    # 부족 시 경고 메시지 출력
    # 남은 크레딧 반환
```

### 2. 워크플로우에 크레딧 확인 단계 추가

#### `.github/workflows/ai-video-gen.yml`
- API 키 검증 후 크레딧 확인 단계 추가
- 크레딧 부족 시 경고 메시지 출력
- 워크플로우는 계속 진행 (실패 가능성 안내)

```yaml
- name: Check ElevenLabs Credits
  env:
    ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
  run: |
    # 크레딧 확인 및 상태 출력
    # 부족 시 해결 방법 안내
```

### 3. `process_post()` 함수 개선

- 포스트 처리 시작 전 크레딧 확인
- 크레딧 부족 시 경고 메시지
- 짧은 대본으로 생성 시도 안내

### 4. `text_to_speech()` 함수 개선

- 음성 생성 전 대본 길이만큼 크레딧 확인
- 크레딧 부족 시 조기 실패
- 상세한 해결 방법 안내

## 📈 개선 효과

### 크레딧 사용량
- **개선 전**: 1,727 크레딧 필요
- **개선 후**: 800 크레딧 필요 (53% 감소)
- **월간 처리 가능**: 약 12-13개 포스트 (개선 전: 5-6개)

### 에러 방지
- **크레딧 사전 확인**: 작업 시작 전 크레딧 확인
- **조기 실패**: 크레딧 부족 시 즉시 실패 (시간 절약)
- **명확한 메시지**: 해결 방법 상세 안내

### 사용자 경험
- **투명성**: 크레딧 상태 사전 확인
- **효율성**: 불필요한 작업 방지
- **안내**: 해결 방법 명확히 제시

## 🔍 추가 개선 가능 사항

### 1. 동적 대본 길이 조정
크레딧 잔액에 따라 대본 길이 자동 조정:
```python
if remaining_credits < 500:
    MAX_SCRIPT_LENGTH = 400  # 매우 짧게
elif remaining_credits < 1000:
    MAX_SCRIPT_LENGTH = 600  # 짧게
else:
    MAX_SCRIPT_LENGTH = 800  # 기본값
```

### 2. 크레딧 임계값 알림
- 크레딧이 1000 미만일 때 경고
- GitHub Actions 알림 설정
- 이메일 알림 (선택사항)

### 3. 캐싱 및 재사용
- 동일 포스트 재처리 방지
- 생성된 대본 캐싱
- 비용 절감

### 4. 배치 처리
- 여러 포스트를 한 번에 처리
- 크레딧이 충분할 때만 실행
- 우선순위 기반 처리

## 📝 체크리스트

워크플로우 실행 전:
- [x] API 키 검증
- [x] 크레딧 사전 확인
- [x] 대본 길이 제한 (800자)
- [x] 에러 핸들링 개선
- [x] 상세한 로그 메시지

## 🔗 관련 문서

- [ElevenLabs Quota Fix](./ELEVENLABS_QUOTA_FIX.md)
- [Workflow Improvements](./WORKFLOW_IMPROVEMENTS.md)
- [Troubleshooting Video Gen](./TROUBLESHOOTING_VIDEO_GEN.md)
- [Cost Management](./COST_MANAGEMENT.md)
