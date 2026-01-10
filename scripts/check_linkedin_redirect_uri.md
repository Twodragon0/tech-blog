# LinkedIn Redirect URI 설정 확인 가이드

## 문제 해결: "Bummer, something went wrong" 오류

이 오류는 주로 **Redirect URI가 LinkedIn Developer Portal에 등록되지 않았거나 일치하지 않을 때** 발생합니다.

## 해결 방법

### 1. LinkedIn Developer Portal에서 Redirect URI 확인 및 등록

1. [LinkedIn Developer Portal](https://www.linkedin.com/developers/) 접속
2. 생성한 앱 선택
3. **"Auth" 탭** 클릭
4. **"Authorized redirect URLs for your app"** 섹션 확인

### 2. Redirect URI 추가

다음 URL을 정확히 추가하세요:

```
http://localhost:8000/auth/linkedin/callback
```

**중요:**
- URL은 정확히 일치해야 합니다 (대소문자, 슬래시, 포트 번호 포함)
- `http://`와 `https://`는 다른 것으로 간주됩니다
- 마지막 슬래시(`/`)도 중요합니다

### 3. 여러 Redirect URI 사용 시

개발/프로덕션 환경을 분리하려면 다음을 모두 추가할 수 있습니다:

```
http://localhost:8000/auth/linkedin/callback
http://localhost:3000/auth/linkedin/callback
https://tech.2twodragon.com/auth/linkedin/callback
```

### 4. 변경사항 저장

- "Update" 또는 "Save" 버튼 클릭
- 변경사항이 적용되는 데 몇 분이 걸릴 수 있습니다

## 대안: 다른 Redirect URI 사용

만약 `localhost:8000`이 문제가 된다면, 다른 포트나 도메인을 사용할 수 있습니다:

### 옵션 1: 다른 포트 사용

`.env` 파일 수정:
```bash
LINKEDIN_REDIRECT_URI=http://localhost:3000/auth/linkedin/callback
```

LinkedIn Developer Portal에도 동일한 URL 등록

### 옵션 2: 실제 도메인 사용 (프로덕션)

`.env` 파일 수정:
```bash
LINKEDIN_REDIRECT_URI=https://tech.2twodragon.com/auth/linkedin/callback
```

LinkedIn Developer Portal에도 동일한 URL 등록

## 스코프 문제 해결

LinkedIn API가 변경되어 일부 스코프가 deprecated되었습니다.

### 최신 스코프 (권장)

```
openid
profile
email
w_member_social
```

### 이전 스코프 (deprecated)

```
r_liteprofile  ❌ 더 이상 사용 불가
r_emailaddress ❌ email로 대체
```

스크립트는 이미 최신 스코프로 업데이트되었습니다.

## 확인 체크리스트

- [ ] LinkedIn Developer Portal에 Redirect URI가 등록되어 있는가?
- [ ] Redirect URI가 `.env` 파일의 값과 정확히 일치하는가?
- [ ] URL에 오타나 공백이 없는가?
- [ ] `http://`와 `https://`가 올바른가?
- [ ] 포트 번호가 올바른가?
- [ ] 변경사항을 저장했는가?

## 테스트

1. LinkedIn Developer Portal에서 Redirect URI 확인
2. `.env` 파일의 `LINKEDIN_REDIRECT_URI` 값 확인
3. 두 값이 정확히 일치하는지 확인
4. OAuth 인증 스크립트 재실행:
   ```bash
   python3 scripts/linkedin_oauth.py
   ```

## 추가 도움말

- [LinkedIn OAuth 2.0 문서](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
