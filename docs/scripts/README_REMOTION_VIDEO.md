# Remotion을 활용한 블로그 영상 생성 가이드

이 가이드는 Remotion을 사용하여 블로그 포스팅을 자동으로 영상으로 변환하는 방법을 설명합니다.

## 개요

이 시스템은 다음 단계로 작동합니다:

1. **포스팅 파일 파싱**: Jekyll 포스팅 파일에서 메타데이터와 이미지 경로 추출
2. **대본 파싱**: 생성된 대본 파일을 시퀀스로 나누기
3. **이미지 매핑**: 각 시퀀스에 맞는 이미지 할당
4. **Remotion 렌더링**: React 기반 Remotion을 사용하여 영상 생성

## 사전 요구사항

### 1. Python 의존성

```bash
pip install python-frontmatter mutagen
```

### 2. Node.js 및 Remotion 의존성

```bash
cd video-generator
npm install
```

## 사용 방법

### 1단계: 오디오 및 대본 생성

먼저 `generate_enhanced_audio.py`를 실행하여 오디오와 대본을 생성합니다:

```bash
python scripts/generate_enhanced_audio.py _posts/2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.md
```

이 스크립트는 다음 파일을 생성합니다:
- `output/{post_basename}_script.txt`: 대본 파일
- `output/{post_basename}_audio.mp3`: 오디오 파일

### 2단계: 영상 생성

생성된 대본과 오디오를 사용하여 영상을 생성합니다:

```bash
python scripts/generate_video_with_remotion.py 2026-01-11-AI_Music_Video_Generation_Complete_Guide_DevSecOps_Perspective.md
```

이 스크립트는 다음 작업을 수행합니다:

1. 포스팅 메타데이터 추출 (제목, 이미지 경로 등)
2. 대본 파일 파싱 및 시퀀스 분할
3. 오디오 길이 확인
4. 각 시퀀스에 이미지 매핑
5. Remotion 설정 파일 생성 (`video-generator/public/video-config.json`)
6. 에셋 복사 (이미지, 오디오)
7. Remotion을 사용하여 영상 렌더링

생성된 영상은 `output/{post_basename}_video.mp4`에 저장됩니다.

## 프로젝트 구조

```
tech-blog/
├── scripts/
│   ├── generate_enhanced_audio.py      # 오디오 및 대본 생성
│   └── generate_video_with_remotion.py # 영상 생성
├── video-generator/
│   ├── src/
│   │   ├── Root.tsx                    # Remotion 루트 컴포넌트
│   │   ├── BlogVideo.tsx               # 블로그 영상 컴포넌트
│   │   └── index.tsx
│   ├── public/
│   │   ├── video-config.json           # 동적 생성되는 설정 파일
│   │   ├── {image}.png                 # 복사된 이미지
│   │   └── {audio}.mp3                  # 복사된 오디오
│   └── package.json
└── output/
    ├── {post_basename}_script.txt
    ├── {post_basename}_audio.mp3
    └── {post_basename}_video.mp4
```

## Remotion 컴포넌트 구조

### BlogVideo.tsx

주요 기능:
- 제목 표시 (처음 3초)
- 대본 시퀀스 표시 (페이드 인/아웃 효과)
- 배경 이미지 (시퀀스별 또는 기본 이미지)
- 진행 바
- 오디오 재생

### 시퀀스 구조

각 시퀀스는 다음 정보를 포함합니다:

```json
{
  "text": "시퀀스 텍스트",
  "startTime": 3.0,      // 시작 시간 (초)
  "duration": 5.0,       // 지속 시간 (초)
  "image": "image.png"   // 배경 이미지 (선택사항)
}
```

## 커스터마이징

### 시퀀스 분할 설정

`generate_video_with_remotion.py`의 `split_script_into_segments` 함수에서 다음 파라미터를 조정할 수 있습니다:

- `min_segment_duration`: 최소 시퀀스 길이 (기본값: 3.0초)
- `max_segment_duration`: 최대 시퀀스 길이 (기본값: 10.0초)
- 읽기 속도: 현재 4.5자/초 (1.5배속 기준)

### 영상 스타일

`BlogVideo.tsx`에서 다음을 커스터마이징할 수 있습니다:

- 폰트 크기 및 스타일
- 색상 및 그라데이션
- 애니메이션 효과
- 레이아웃

### Remotion 설정

`remotion.config.ts`에서 렌더링 설정을 조정할 수 있습니다:

- 비디오 코덱
- 이미지 포맷
- 픽셀 포맷

## 문제 해결

### 오디오 길이 추출 실패

`mutagen` 라이브러리가 설치되어 있는지 확인하세요:

```bash
pip install mutagen
```

### Remotion 렌더링 실패

1. `video-generator` 디렉토리에서 의존성이 설치되어 있는지 확인:
   ```bash
   cd video-generator
   npm install
   ```

2. 설정 파일이 올바르게 생성되었는지 확인:
   ```bash
   cat video-generator/public/video-config.json
   ```

3. 에셋 파일이 올바르게 복사되었는지 확인:
   ```bash
   ls -la video-generator/public/
   ```

### 이미지를 찾을 수 없음

포스팅 파일의 frontmatter에 `image` 필드가 올바르게 설정되어 있는지 확인하세요:

```yaml
---
image: /assets/images/your-image.png
---
```

## 보안 고려사항

- 모든 파일 경로는 검증됩니다
- 입력 파일은 존재 여부를 확인합니다
- 에러 메시지는 민감한 정보를 포함하지 않습니다
- 로그 파일에는 민감한 정보가 기록되지 않습니다

## 성능 최적화

- 대본 파싱은 캐싱되지 않습니다 (매번 새로 생성)
- 이미지 복사는 필요할 때만 수행됩니다
- Remotion 렌더링은 병렬화되지 않습니다 (순차 처리)

## 향후 개선 사항

- [ ] 키워드 기반 이미지 자동 매핑
- [ ] 여러 이미지를 시퀀스에 할당
- [ ] 자막 파일 생성 (SRT, VTT)
- [ ] 영상 품질 설정 옵션
- [ ] 배치 처리 지원 (여러 포스팅 동시 처리)
- [ ] 클라우드 렌더링 지원 (Remotion Lambda)

## 참고 자료

- [Remotion 공식 문서](https://www.remotion.dev/docs)
- [Remotion GitHub](https://github.com/remotion-dev/remotion)
- [Jekyll Front Matter](https://jekyllrb.com/docs/front-matter/)
