# 오디오 생성 상태 및 가이드

## 현재 상태

- **총 개선된 대본**: 34개
- **생성 완료**: 16개
- **생성 필요**: 18개

## 생성된 오디오 파일

다음 오디오 파일들이 IT 전문가용 남자 목소리(Rasalgethi)로 생성되었습니다:

1. ✅ 2025-04-29-SKT_보안_이슈... (110KB)
2. ✅ 2025-04-30-공용_PC에서도... (379KB)
3. ✅ 2025-05-02-Kandji로... (102KB)
4. ✅ 2025-05-02-클라우드_시큐리티_과정_7기_-_3주차... (173KB)
5. ✅ 2025-05-09-클라우드_보안_과정_7기_-_4주차... (1.3MB)
6. ✅ 2025-05-23-클라우드_시큐리티_과정_7기_-_6주차... (1.2MB)
7. ✅ 2026-01-08-클라우드_보안_과정_8기... (486KB)
8. ✅ 2026-01-11-AI_Music_Video_Generation... (727KB)

## 나머지 오디오 생성 방법

### 방법 1: 배치 생성 (권장)

모든 개선된 대본을 자동으로 처리합니다:

```bash
# 백그라운드로 실행 (시간이 오래 걸릴 수 있음)
python scripts/generate_audio_batch.py > /tmp/audio_batch.log 2>&1 &

# 진행 상황 확인
tail -f /tmp/audio_batch.log
```

### 방법 2: 개별 생성

특정 파일만 선택하여 생성:

```bash
# 파일명만 지정 (output/ 접두사 없이)
python scripts/generate_audio_from_improved_split.py 2025-05-16-클라우드_시큐리티_과정_7기_-_5주차_AWS_Control_Tower_및_ZTNA_script_improved.txt

# 또는 전체 경로
python scripts/generate_audio_from_improved_split.py output/2025-06-05-이메일_발송_신뢰도_높이기_SendGrid_SPF_DKIM_DMARC_설정_완벽_가이드_script_improved.txt
```

### 방법 3: 상태 확인 후 선택적 생성

```bash
# 현재 상태 확인
python scripts/check_audio_generation_status.py

# 필요한 파일만 선택하여 생성
```

## 생성 필요 파일 목록

다음 파일들의 오디오가 아직 생성되지 않았습니다:

1. 2025-05-16-클라우드_시큐리티_과정_7기_-_5주차_AWS_Control_Tower_및_ZTNA_script_improved.txt
2. 2025-05-24-Amazon_Q_Developer와_GitHub_Advanced_Security..._script_improved.txt
3. 2025-05-30-Kubernetes_Minikube_ampamp_K9s_실습_가이드..._script_improved.txt
4. 2025-05-30-클라우드_시큐리티_과정_7기_-_7주차_Docker_및_Kubernetes_이해_script_improved.txt
5. 2025-06-05-이메일_발송_신뢰도_높이기_SendGrid_SPF_DKIM_DMARC_설정_완벽_가이드_script_improved.txt
6. 2025-06-06-클라우드_시큐리티_과정_7기_-_8주차_CICD와_Kubernetes_보안_실전_가이드_script_improved.txt
7. 2025-06-13-클라우드_시큐리티_과정_7기_-_9주차_DevSecOps_통합_정리_script_improved.txt
8. 2025-09-10-긴급_npm_생태계_대규모_보안_침해..._script_improved.txt
9. 2025-09-16-AWS_reInforce_2025_클라우드_보안의_현재와_미래__script_improved.txt
... 외 9개

## 특징

### 생성된 오디오
- **Voice**: Rasalgethi (IT 전문가용 남자 목소리)
- **속도**: 1.5배속 재생 지원
- **품질**: 개선된 대본 기반 고품질 오디오
- **동기화**: Remotion 구간 정보 포함

### 파일 위치
- 오디오: `output/*_audio_improved.mp3`
- 대본: `output/*_improved.txt`
- 구간 정보: `output/*_segments.json`

## 문제 해결

### 타임아웃 오류
- 긴 대본은 자동으로 분할 처리됩니다
- 각 부분 생성에 약 1-2분 소요
- 전체 생성은 시간이 오래 걸릴 수 있습니다

### API 키 오류
- `.env` 파일에 `GEMINI_API_KEY` 확인
- API 할당량 확인

### 진행 상황 확인
```bash
# 진행 상황 파일 확인
cat output/.audio_generation_progress.json

# 생성된 파일 확인
ls -lh output/*audio_improved.mp3
```

## 다음 단계

1. **배치 생성 실행**: `python scripts/generate_audio_batch.py`
2. **상태 확인**: `python scripts/check_audio_generation_status.py`
3. **필요한 파일만 선택 생성**: 개별 파일 지정

모든 오디오 생성이 완료되면 Remotion을 사용하여 영상 제작을 진행할 수 있습니다.
