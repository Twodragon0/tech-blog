# Vercel DeepSeek API 키 확인 가이드

## 🔍 현재 상태

### ✅ 확인 완료
- **Vercel**: `DEEPSEEK_API_KEY` 설정됨 (Development, Preview, Production)
- **GitHub Secrets**: `DEEPSEEK_API_KEY` 설정됨 (2026-01-11)

### ⚠️ 주의사항
Vercel CLI는 보안상의 이유로 암호화된 환경 변수의 실제 값을 다운로드하지 않습니다.
`vercel env pull` 명령으로 가져온 `.env.local` 파일에는 값이 비어있습니다.

## 📋 값 확인 방법

### 방법 1: Vercel 대시보드 (권장)

1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. 프로젝트 **tech-blog** 선택
3. **Settings** → **Environment Variables** 이동
4. `DEEPSEEK_API_KEY` 찾기
5. **눈 아이콘** 클릭하여 값 확인
6. 값 복사

### 방법 2: GitHub Secrets 값 검증

현재 GitHub Secrets에 설정된 값이 올바른지 로컬에서 테스트:

```bash
# Vercel 대시보드에서 확인한 값으로 설정
export DEEPSEEK_API_KEY='vercel에서-확인한-값'
export ELEVENLABS_API_KEY='sk_ba9e2442482041d00b7ac7d0ab5af676faf8051157e99f85'
export ELEVENLABS_VOICE_ID='hnRmCiCoPWAjpxiiXEwz'

# 테스트 실행
python3 scripts/generate_audio.py --list-voices
```

성공하면 GitHub Secrets의 값이 올바른 것입니다.

## 🔄 동기화 절차

### Vercel 값과 GitHub Secrets 값이 다른 경우

1. **Vercel 대시보드에서 값 확인** (위 방법 1 참고)

2. **GitHub Secrets 업데이트**
   ```bash
   gh secret set DEEPSEEK_API_KEY --body "vercel에서-확인한-값"
   ```

3. **확인**
   ```bash
   gh secret list | grep -i deepseek
   ```

4. **워크플로우 재실행**
   ```bash
   gh workflow run "Generate AI Video Lecture" \
     --field post_file="" \
     --field video_method="ffmpeg"
   ```

## 🧪 로컬 테스트

GitHub Secrets의 값이 올바른지 확인하려면:

```bash
# 환경 변수 설정 (Vercel 대시보드에서 확인한 값 사용)
export DEEPSEEK_API_KEY='your-api-key-from-vercel'
export ELEVENLABS_API_KEY='sk_ba9e2442482041d00b7ac7d0ab5af676faf8051157e99f85'
export ELEVENLABS_VOICE_ID='hnRmCiCoPWAjpxiiXEwz'

# 간단한 테스트
python3 scripts/generate_audio.py --list-voices

# 또는 전체 테스트
python3 scripts/generate_audio.py
```

## ⚠️ 문제 해결

### 401 Unauthorized 오류 발생 시

1. **Vercel 대시보드에서 값 확인**
   - 값이 올바른지 확인
   - `sk-`로 시작하는지 확인

2. **GitHub Secrets 업데이트**
   ```bash
   gh secret set DEEPSEEK_API_KEY --body "올바른-api-key-값"
   ```

3. **로컬 테스트로 검증**
   ```bash
   export DEEPSEEK_API_KEY='올바른-api-key-값'
   python3 scripts/generate_audio.py --list-voices
   ```

4. **워크플로우 재실행**

## 📚 관련 문서

- [Vercel GitHub Secrets Sync](./VERCEL_GITHUB_SECRETS_SYNC.md)
- [Troubleshooting Video Gen](./TROUBLESHOOTING_VIDEO_GEN.md)
- [Secrets Management](./SECRETS_MANAGEMENT.md)
