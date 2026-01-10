# DeepSeek Chat Widget 설정 가이드

Jekyll 블로그에 DeepSeek AI 채팅 위젯을 추가했습니다. 이 가이드는 설정 방법을 안내합니다.

## 기능

- 🎯 플로팅 채팅 버튼 (우측 하단)
- 💬 DeepSeek v3 기반 AI 채팅
- 🔒 보안: API 키는 서버에서 관리 (클라이언트에 노출되지 않음)
- 📱 반응형 디자인 (모바일 지원)
- 🌙 다크 모드 지원
- ⚡ 실시간 메시지 전송

## 설정 방법

### 1. DeepSeek API 키 발급

1. [DeepSeek Platform](https://platform.deepseek.com)에 접속
2. 계정 생성 및 로그인
3. API 키 발급 (`sk-`로 시작하는 키)

### 2. Vercel 환경 변수 설정

Vercel 대시보드에서 환경 변수를 설정합니다:

1. Vercel 프로젝트 설정 → Environment Variables
2. 다음 변수 추가:
   - **Key**: `DEEPSEEK_API_KEY`
   - **Value**: `sk-46c21143b44f412b8f420f06df8693cd` (online-course 프로젝트와 동일한 키)
   - **Environment**: Production, Preview, Development 모두 선택

**참고**: online-course 프로젝트에서 동일한 DeepSeek API 키를 사용합니다.

### 3. 배포

변경사항을 커밋하고 푸시하면 자동으로 배포됩니다:

```bash
git add .
git commit -m "feat: DeepSeek 채팅 위젯 추가"
git push
```

## 파일 구조

```
tech-blog/
├── _includes/
│   └── chat-widget.html          # 채팅 위젯 HTML
├── assets/
│   ├── css/
│   │   └── main.css              # 채팅 위젯 스타일 포함
│   └── js/
│       └── chat-widget.js        # 채팅 위젯 JavaScript
├── api/
│   └── chat.js                   # Vercel Serverless Function
└── _layouts/
    └── default.html              # 채팅 위젯 포함
```

## 보안 고려사항

### ✅ 구현된 보안 기능

1. **API 키 보호**: API 키는 서버리스 함수에서만 사용되며 클라이언트에 노출되지 않음
2. **입력 검증**: 메시지 길이 제한 (최대 2000자)
3. **XSS 방지**: 입력 및 출력 정제
4. **Rate Limiting**: 세션 기반 요청 제한 (향후 Redis 등으로 확장 가능)
5. **CORS 설정**: 적절한 CORS 헤더 설정
6. **타임아웃**: 60초 타임아웃으로 무한 대기 방지

### 🔒 추가 보안 권장사항

1. **Rate Limiting 강화**: Redis 등을 사용한 더 정교한 Rate Limiting
2. **입력 정제 강화**: DOMPurify 같은 라이브러리 사용 고려
3. **로그 모니터링**: Vercel 로그를 통한 이상 요청 모니터링
4. **API 키 로테이션**: 정기적인 API 키 교체

## 커스터마이징

### 채팅 위젯 스타일 변경

`assets/css/main.css` 파일의 `/* DeepSeek Chat Widget Styles */` 섹션을 수정하세요.

### 시스템 프롬프트 변경

`api/chat.js` 파일의 시스템 메시지를 수정하세요:

```javascript
{
  role: 'system',
  content: '당신은 DevSecOps, 클라우드 보안, 인프라 자동화 전문가입니다...',
}
```

### 아이콘 표시 지연 시간 변경

`assets/js/chat-widget.js` 파일의 `CONFIG.showIconDelay` 값을 변경하세요:

```javascript
const CONFIG = {
  showIconDelay: 5000, // 5초 → 원하는 시간(밀리초)으로 변경
};
```

## 문제 해결

### 채팅이 작동하지 않는 경우

1. **환경 변수 확인**
   - Vercel 대시보드에서 `DEEPSEEK_API_KEY`가 설정되어 있는지 확인
   - 배포 후 환경 변수가 적용되었는지 확인

2. **브라우저 콘솔 확인**
   - 개발자 도구(F12) → Console 탭에서 오류 메시지 확인
   - Network 탭에서 `/api/chat` 요청 상태 확인

3. **Vercel 로그 확인**
   ```bash
   # 스크립트 사용
   ./scripts/check-vercel-logs.sh
   
   # 또는 직접
   vercel logs https://tech.2twodragon.com
   vercel logs https://tech.2twodragon.com --json
   ```

### API 오류가 발생하는 경우

- **429 오류 (Rate Limit)**: 요청이 너무 많습니다. 잠시 후 다시 시도하세요. (세션당 10회/분 제한)
- **503 오류**: API 키가 설정되지 않았거나 DeepSeek 서비스에 문제가 있습니다.
- **504 오류**: 요청 시간이 초과되었습니다. (프리티어 최적화: 8초 타임아웃)

## 프리티어 최적화

이 채팅 위젯은 Vercel 프리티어 제한 내에서 최적화되었습니다:

- ✅ **실행 시간**: 최대 10초 (타임아웃 8초)
- ✅ **메모리**: 1024MB
- ✅ **Rate Limiting**: 세션당 10회/분
- ✅ **로깅 최소화**: 프로덕션 환경에서 최소한의 로그만 기록

자세한 내용은 [VERCEL_FREE_TIER_OPTIMIZATION.md](./VERCEL_FREE_TIER_OPTIMIZATION.md)를 참고하세요.

## 비용

DeepSeek API는 사용량 기반 과금입니다. 자세한 가격 정보는 [DeepSeek Platform](https://platform.deepseek.com)에서 확인하세요.

## 참고 자료

- [DeepSeek API 문서](https://platform.deepseek.com/api-docs/)
- [Vercel Functions 문서](https://vercel.com/docs/functions)
- [Jekyll 문서](https://jekyllrb.com/)
