# DeepSeek Chat API 문제 해결 가이드

## 🔍 빠른 진단

진단 스크립트를 실행하여 전체 상태를 확인하세요:

```bash
./scripts/diagnose-chat-api.sh
```

## ✅ 확인 사항

### 1. Vercel 환경 변수 확인

#### 방법 1: Vercel 대시보드
1. https://vercel.com/dashboard 접속
2. `tech-blog` 프로젝트 선택
3. **Settings** → **Environment Variables** 클릭
4. `DEEPSEEK_API_KEY` 확인:
   - ✅ **Production**, **Preview**, **Development** 모두에 설정되어 있어야 함
   - ✅ 값이 `sk-`로 시작해야 함
   - ✅ **Encrypted** 상태여야 함

#### 방법 2: Vercel CLI
```bash
# 환경 변수 목록 확인
vercel env ls

# 특정 환경 변수 확인
vercel env ls | grep DEEPSEEK_API_KEY

# 환경 변수 값 확인 (로컬 개발용)
vercel env pull .env.local
cat .env.local | grep DEEPSEEK_API_KEY
```

### 2. Vercel 로그 확인

#### 실시간 로그 확인
```bash
# 실시간 로그 스트리밍
vercel logs https://tech.2twodragon.com --follow

# 최근 로그 확인 (1시간)
vercel logs https://tech.2twodragon.com --since 1h

# JSON 형식으로 확인
vercel logs https://tech.2twodragon.com --json | jq

# Chat API 관련 로그만 필터링
vercel logs https://tech.2twodragon.com --since 1h | grep -i "chat\|deepseek\|api"
```

#### 로그에서 확인할 사항
- ✅ API 호출 성공: `[Chat API] DeepSeek API 호출`
- ✅ 응답 성공: `Execution time: XXXms`
- ❌ API 키 오류: `DEEPSEEK_API_KEY가 설정되지 않았습니다`
- ❌ Rate Limit: `요청이 너무 많습니다`
- ❌ 타임아웃: `Timeout after XXXms`

### 3. 브라우저 콘솔 확인

#### 개발자 도구 열기
1. 브라우저에서 `https://tech.2twodragon.com` 접속
2. **F12** 또는 **우클릭 → 검사** 클릭
3. **Console** 탭 확인

#### 확인할 사항

**Console 탭:**
- ❌ 에러 메시지 확인
  - `Failed to fetch`: 네트워크 오류
  - `403 Forbidden`: Origin 검증 실패
  - `503 Service Unavailable`: API 키 문제 또는 서비스 오류
  - `429 Too Many Requests`: Rate Limit 초과

**Network 탭:**
1. **Network** 탭 클릭
2. 페이지 새로고침 (F5)
3. 채팅 위젯에서 메시지 전송
4. `/api/chat` 요청 찾기
5. 요청 클릭하여 확인:
   - **Headers**: 요청 헤더 확인
     - `Origin`: `https://tech.2twodragon.com` 확인
     - `Content-Type`: `application/json` 확인
   - **Payload**: 요청 본문 확인
     - `message`: 전송한 메시지 확인
     - `sessionId`: 세션 ID 확인
   - **Response**: 응답 확인
     - `200 OK`: 정상 응답
     - `response`: AI 응답 내용 확인

## 🔧 일반적인 문제 해결

### 문제 1: API 키가 설정되지 않음

**증상:**
- 로그: `DEEPSEEK_API_KEY가 설정되지 않았습니다`
- 응답: `503 Service Unavailable`

**해결 방법:**

1. **Vercel 대시보드에서 추가:**
   ```
   1. https://vercel.com/dashboard 접속
   2. tech-blog 프로젝트 선택
   3. Settings → Environment Variables
   4. Add New → Key: DEEPSEEK_API_KEY
   5. Value: sk-로 시작하는 API 키 입력
   6. Environment: Production, Preview, Development 모두 선택
   7. Save
   ```

2. **Vercel CLI로 추가:**
   ```bash
   vercel env add DEEPSEEK_API_KEY
   # 프롬프트에 API 키 입력
   # Environment: Production, Preview, Development 모두 선택
   ```

3. **다른 프로젝트에서 복사:**
   ```bash
   ./scripts/add-deepseek-key.sh
   ```

4. **재배포:**
   ```bash
   git commit -m "fix: Add DEEPSEEK_API_KEY"
   git push
   ```

### 문제 2: Rate Limit 초과

**증상:**
- 응답: `429 Too Many Requests`
- 메시지: `요청이 너무 많습니다`

**해결 방법:**
- ⏳ **60초 대기 후 재시도**
- 🔄 **브라우저 새로고침**
- 💡 **Rate Limit 설정 확인:**
  - 현재: 세션당 15회/분
  - `api/chat.js`의 `RATE_LIMIT` 설정 확인

### 문제 3: Origin 검증 실패

**증상:**
- 응답: `403 Forbidden`
- 메시지: `Forbidden: Invalid origin`

**해결 방법:**
1. **요청 Origin 확인:**
   - 브라우저 Network 탭에서 `/api/chat` 요청의 `Origin` 헤더 확인
   - `https://tech.2twodragon.com` 또는 `https://www.tech.2twodragon.com`이어야 함

2. **허용된 Origin 확인:**
   - `api/chat.js`의 `allowedOrigins` 배열 확인
   - 필요시 도메인 추가

### 문제 4: 타임아웃

**증상:**
- 응답: `504 Gateway Timeout`
- 메시지: `응답 생성에 시간이 오래 걸리고 있습니다`

**해결 방법:**
- ⏱️ **타임아웃 설정 확인:**
  - 프로덕션: 55초 (Pro 플랜)
  - 개발: 9초 (Hobby 플랜)
- 💡 **질문을 더 구체적으로 작성**
- 🔄 **잠시 후 재시도**

### 문제 5: 응답이 비어있음

**증상:**
- 응답: `200 OK`이지만 응답 내용이 없음
- 메시지: `응답을 생성할 수 없습니다`

**해결 방법:**
1. **로그 확인:**
   ```bash
   vercel logs https://tech.2twodragon.com --since 1h | grep -i "response\|error"
   ```

2. **DeepSeek API 상태 확인:**
   - https://platform.deepseek.com 접속
   - API 상태 확인

3. **모델 설정 확인:**
   - `api/chat.js`의 `CONFIG.MODEL` 확인
   - 기본값: `deepseek-chat`
   - 환경 변수 `DEEPSEEK_MODEL`로 변경 가능

## 📊 모니터링

### 로그 모니터링 스크립트
```bash
# 실시간 로그 모니터링
./scripts/check-vercel-logs.sh

# Chat API 전용 로그
vercel logs https://tech.2twodragon.com --follow | grep -i "chat\|deepseek"
```

### 주요 메트릭 확인
- ✅ **응답 시간**: `Execution time: XXXms`
- ✅ **토큰 사용량**: `Token usage - Prompt: XXX, Completion: XXX`
- ✅ **캐시 히트율**: `Cache hit rate: XX%`
- ✅ **Off-peak 시간대**: `Off-peak hours (UTC XX:00)`

## 🚀 테스트

### 로컬 테스트 (개발 환경)
```bash
# 환경 변수 설정
vercel env pull .env.local

# 로컬 서버 실행
bundle exec jekyll serve

# 브라우저에서 테스트
# http://localhost:4000
```

### 프로덕션 테스트
1. **브라우저에서 테스트:**
   - https://tech.2twodragon.com 접속
   - 채팅 위젯 열기 (우측 하단)
   - 테스트 메시지 전송

2. **API 직접 테스트:**
   ```bash
   curl -X POST https://tech.2twodragon.com/api/chat \
     -H "Content-Type: application/json" \
     -H "Origin: https://tech.2twodragon.com" \
     -d '{"message":"안녕하세요"}'
   ```

## 📝 체크리스트

진단 시 다음 항목을 확인하세요:

- [ ] Vercel CLI 설치 및 로그인 확인
- [ ] `DEEPSEEK_API_KEY` 환경 변수 설정 확인 (Production, Preview, Development)
- [ ] API 키 형식 확인 (`sk-`로 시작)
- [ ] 최근 배포 상태 확인
- [ ] API 엔드포인트 응답 확인 (200 OK)
- [ ] 브라우저 콘솔 에러 확인
- [ ] Network 탭에서 요청/응답 확인
- [ ] Vercel 로그에서 에러 확인

## 🔗 관련 문서

- [README_CHAT_WIDGET.md](./README_CHAT_WIDGET.md) - 채팅 위젯 설정 가이드
- [api/chat.js](./api/chat.js) - API 엔드포인트 코드
- [assets/js/chat-widget.js](./assets/js/chat-widget.js) - 클라이언트 코드

## 💬 지원

문제가 지속되면:
1. Vercel 로그 확인
2. 브라우저 콘솔 에러 확인
3. 진단 스크립트 실행: `./scripts/diagnose-chat-api.sh`
4. 로그와 에러 메시지를 함께 확인
