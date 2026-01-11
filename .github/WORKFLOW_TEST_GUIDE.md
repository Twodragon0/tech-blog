# 워크플로우 테스트 가이드

## 📋 현재 상태

### ✅ 완료된 설정
- `ELEVENLABS_API_KEY`: GitHub Secrets에 설정 완료
- `ELEVENLABS_VOICE_ID`: GitHub Secrets에 설정 완료 (Voice: "New-Man")
- `DEEPSEEK_API_KEY`: GitHub Secrets에 설정 완료

### ⚠️ 필요한 작업
- 워크플로우 파일 (`.github/workflows/ai-video-gen.yml`) 커밋 및 푸시 필요

## 🚀 테스트 방법

### 방법 1: 로컬 테스트 (권장 - 먼저 진행)

로컬에서 먼저 테스트하여 API 키와 설정이 올바른지 확인합니다.

#### 1. Python 패키지 설치
```bash
cd "/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"
pip3 install -r scripts/requirements.txt
```

#### 2. 환경 변수 설정
```bash
# GitHub Secrets에서 가져온 값으로 설정
export ELEVENLABS_API_KEY='sk_ba9e2442482041d00b7ac7d0ab5af676faf8051157e99f85'
export ELEVENLABS_VOICE_ID='hnRmCiCoPWAjpxiiXEwz'
export DEEPSEEK_API_KEY='your-deepseek-key-here'
```

#### 3. Voice 목록 조회 테스트 (선택사항)
```bash
python3 scripts/generate_audio.py --list-voices
```

#### 4. 오디오 생성 테스트
```bash
# 최신 포스트로 테스트
python3 scripts/generate_audio.py

# 특정 포스트로 테스트
python3 scripts/generate_audio.py _posts/2026-01-10-2026년_DevSecOps_로드맵_완벽_가이드_roadmap.sh_분석.md
```

#### 5. 결과 확인
```bash
# 생성된 오디오 파일 확인
ls -lh output/*.mp3

# 로그 확인
tail -n 50 video_generation_log.txt
```

### 방법 2: GitHub Actions 워크플로우 테스트

#### 1. 워크플로우 파일 커밋 및 푸시
```bash
cd "/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"

# 변경사항 확인
git status

# 워크플로우 파일 추가
git add .github/workflows/ai-video-gen.yml

# 커밋
git commit -m "feat: Add AI video generation workflow with ElevenLabs integration"

# 푸시
git push origin main
```

#### 2. 워크플로우 실행
```bash
# 워크플로우 목록 확인
gh workflow list

# 워크플로우 실행
gh workflow run "Generate AI Video Lecture" \
  --field post_file="" \
  --field video_method="ffmpeg"

# 실행 상태 확인
gh run list --workflow="Generate AI Video Lecture" --limit 1

# 로그 확인 (run-id는 위 명령어 결과에서 확인)
gh run view <run-id> --log
```

## 🔍 문제 해결

### 로컬 테스트 실패 시

1. **패키지 설치 오류**
   ```bash
   pip3 install --upgrade pip
   pip3 install -r scripts/requirements.txt
   ```

2. **API 키 오류**
   - 환경 변수가 올바르게 설정되었는지 확인
   - `echo $ELEVENLABS_API_KEY`로 확인 (보안: 실제 값은 출력되지 않음)

3. **Voice ID 오류**
   - Voice ID 형식 확인: `hnRmCiCoPWAjpxiiXEwz`
   - `--list-voices` 옵션으로 사용 가능한 Voice 확인

### GitHub Actions 실패 시

1. **Secrets 확인**
   ```bash
   gh secret list | grep -i elevenlabs
   ```

2. **워크플로우 파일 확인**
   - `.github/workflows/ai-video-gen.yml` 파일이 올바른지 확인
   - YAML 문법 오류 확인

3. **로그 확인**
   ```bash
   gh run view <run-id> --log
   ```

## 💰 비용 모니터링

### 사용량 확인
- [ElevenLabs Usage](https://elevenlabs.io/app/usage)
- 무료 티어: 월 10,000자 제한

### 비용 절감 팁
1. 테스트 시 짧은 포스트 사용
2. 로컬 테스트로 먼저 검증
3. 크레딧 제한 설정 (ElevenLabs 대시보드)

## 📝 다음 단계

1. ✅ 로컬 테스트 완료
2. ✅ 워크플로우 파일 커밋 및 푸시
3. ✅ GitHub Actions 워크플로우 테스트
4. ✅ 사용량 모니터링 설정

## 🔗 관련 문서

- [ElevenLabs Setup Guide](./ELEVENLABS_SETUP.md)
- [Cost Management](./COST_MANAGEMENT.md)
- [Secrets Management](./SECRETS_MANAGEMENT.md)
