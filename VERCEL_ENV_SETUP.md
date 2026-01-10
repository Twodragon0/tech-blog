# Vercel 환경 변수 설정 가이드

tech-blog 프로젝트에 필요한 Vercel 환경 변수 설정 가이드입니다.

## DeepSeek API 키 설정

### 방법 1: Vercel 대시보드에서 설정 (권장)

1. [Vercel 대시보드](https://vercel.com/dashboard) 접속
2. `tech-blog` 프로젝트 선택
3. **Settings** → **Environment Variables** 이동
4. 다음 변수 추가:
   - **Key**: `DEEPSEEK_API_KEY`
   - **Value**: `sk-46c21143b44f412b8f420f06df8693cd`
   - **Environment**: 
     - ✅ Production
     - ✅ Preview  
     - ✅ Development
5. **Save** 클릭

### 방법 2: Vercel CLI 사용

```bash
cd "/Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내 드라이브/tech-blog"

# Production 환경
vercel env add DEEPSEEK_API_KEY production
# 프롬프트에 키 입력: sk-46c21143b44f412b8f420f06df8693cd

# Preview 환경
vercel env add DEEPSEEK_API_KEY preview
# 프롬프트에 키 입력: sk-46c21143b44f412b8f420f06df8693cd

# Development 환경
vercel env add DEEPSEEK_API_KEY development
# 프롬프트에 키 입력: sk-46c21143b44f412b8f420f06df8693cd
```

### 확인

환경 변수가 제대로 설정되었는지 확인:

```bash
vercel env ls
```

다음과 같이 표시되어야 합니다:

```
DEEPSEEK_API_KEY    Encrypted    Development, Preview, Production
```

## 참고사항

- **보안**: API 키는 Vercel에서 암호화되어 저장됩니다
- **동기화**: online-course 프로젝트와 동일한 DeepSeek API 키를 사용합니다
- **재배포**: 환경 변수 추가 후 자동으로 재배포되거나, 수동으로 재배포가 필요할 수 있습니다

## 문제 해결

### 환경 변수가 적용되지 않는 경우

1. **재배포 확인**: 환경 변수 추가 후 프로젝트가 재배포되었는지 확인
2. **환경 확인**: Production, Preview, Development 모두 설정되었는지 확인
3. **로컬 테스트**: 로컬에서 테스트하려면 `.env.local` 파일에 추가:
   ```bash
   DEEPSEEK_API_KEY=sk-46c21143b44f412b8f420f06df8693cd
   ```

### API 오류가 발생하는 경우

- **503 오류**: API 키가 설정되지 않았거나 잘못된 경우
- **429 오류**: Rate limit 초과 (잠시 후 재시도)
- **401 오류**: API 키가 유효하지 않은 경우 (키 확인 필요)
