# Vercel과 GitHub Secrets 동기화 가이드

## 🔄 Vercel과 GitHub Secrets의 관계

**중요**: Vercel 환경 변수와 GitHub Secrets는 **자동으로 동기화되지 않습니다**. 각각 별도로 관리해야 합니다.

### Vercel 환경 변수
- **용도**: Vercel 배포 환경에서 사용 (Serverless Functions, Edge Functions 등)
- **설정 위치**: Vercel 대시보드 → 프로젝트 → Settings → Environment Variables
- **사용처**: `api/chat.js` 등 Vercel Serverless Functions

### GitHub Secrets
- **용도**: GitHub Actions 워크플로우에서 사용
- **설정 위치**: GitHub 저장소 → Settings → Secrets and variables → Actions
- **사용처**: `.github/workflows/*.yml` 워크플로우 파일

## 📋 동기화 필요 항목

### DeepSeek API Key
- **Vercel**: `DEEPSEEK_API_KEY` (Vercel 대시보드에서 설정)
- **GitHub Secrets**: `DEEPSEEK_API_KEY` (GitHub Actions에서 사용)

**동기화 방법:**
1. Vercel 대시보드에서 `DEEPSEEK_API_KEY` 값 확인
2. GitHub Secrets에 동일한 값 설정

```bash
# Vercel에서 값 확인 (Vercel CLI 사용)
vercel env ls

# GitHub Secrets에 설정
gh secret set DEEPSEEK_API_KEY --body "vercel에서-확인한-api-key-값"
```

## ✅ 확인 방법

### 1. GitHub Secrets 확인
```bash
gh secret list | grep -i deepseek
```

### 2. Vercel 환경 변수 확인

#### 방법 A: Vercel CLI 사용
```bash
# Vercel CLI 설치 (없는 경우)
npm install -g vercel

# 프로젝트 디렉토리에서
cd /path/to/tech-blog  # 실제 프로젝트 경로로 교체 필요
vercel env ls
```

#### 방법 B: Vercel 대시보드 사용
1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. 프로젝트 선택
3. **Settings** → **Environment Variables**
4. `DEEPSEEK_API_KEY` 확인

### 3. 값 비교

두 값이 동일한지 확인:
- Vercel: Vercel 대시보드에서 확인
- GitHub Secrets: `gh secret list`로 존재 여부 확인 (값은 보안상 표시되지 않음)

## 🔧 동기화 절차

### DeepSeek API Key 동기화

1. **Vercel에서 값 확인**
   ```bash
   # Vercel CLI 사용
   vercel env pull .env.local
   cat .env.local | grep DEEPSEEK_API_KEY
   ```
   
   또는 Vercel 대시보드에서 직접 확인

2. **GitHub Secrets 업데이트**
   ```bash
   gh secret set DEEPSEEK_API_KEY --body "vercel에서-확인한-값"
   ```

3. **확인**
   ```bash
   gh secret list | grep -i deepseek
   ```

## ⚠️ 주의사항

1. **값 일치**: Vercel과 GitHub Secrets의 값이 동일해야 합니다
2. **보안**: API 키 값은 절대 공개하지 마세요
3. **업데이트**: 한쪽에서 변경 시 다른 쪽도 업데이트 필요
4. **형식**: DeepSeek API 키는 `sk-`로 시작해야 합니다

## 🔍 문제 해결

### GitHub Actions에서 401 오류 발생 시

1. **GitHub Secrets 확인**
   ```bash
   gh secret list | grep DEEPSEEK_API_KEY
   ```

2. **Vercel 값과 비교**
   - Vercel 대시보드에서 값 확인
   - GitHub Secrets에 동일한 값 설정

3. **로컬 테스트**
   ```bash
   export DEEPSEEK_API_KEY='vercel에서-확인한-값'
   python3 scripts/generate_enhanced_audio.py --list-voices
   ```

4. **워크플로우 재실행**
   - GitHub Actions에서 워크플로우 다시 실행

## 📚 관련 문서

- [Secrets Management](./SECRETS_MANAGEMENT.md)
- [Troubleshooting Video Gen](./TROUBLESHOOTING_VIDEO_GEN.md)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
