# LinkedIn 앱 생성 가이드 (DevSecOps 관점)

## 📋 개요

LinkedIn Developer Portal에서 앱을 생성할 때 필요한 정보와 보안 고려사항을 정리한 가이드입니다.

## 🔐 필수 입력 항목

### 1. App Name (앱 이름) ⚠️ 필수

**설명:**
- LinkedIn에서 사용자에게 표시될 앱 이름
- 한 번 저장하면 변경 불가 (주의 필요)

**보안 고려사항:**
- 앱 이름에 회사명이나 브랜드명을 포함하여 신뢰성 확보
- 사용자가 앱을 식별할 수 있는 명확한 이름 사용
- 예: `[회사명] Analytics App`, `[서비스명] Integration`

**권장 형식:**
```
[회사명/서비스명] - [기능 설명]
예: "TechCorp - Social Media Analytics"
```

---

### 2. LinkedIn Page (LinkedIn 페이지) ⚠️ 필수

**설명:**
- 앱과 연결될 LinkedIn Company Page
- 개인 프로필 페이지는 사용 불가
- Enterprise/Third Party 개발자는 회사 페이지 선택 필요
- Individual 개발자는 기본 Company Page 사용

**보안 고려사항:**
- **페이지 관리 권한 확인**: 앱 생성자는 해당 페이지의 Admin 권한이 있어야 함
- **검증 프로세스**: LinkedIn에서 페이지 소유권을 검증함 (Enterprise 개발자 필수)
- **기본 페이지 사용 시**: Individual 개발자는 제한된 API 제품만 사용 가능

**선택 옵션:**
1. **기존 페이지 선택**: 드롭다운에서 회사 페이지 선택
2. **새 페이지 생성**: "Create a new LinkedIn Page" 클릭

**⚠️ 주의사항:**
- 이 작업은 되돌릴 수 없음 (Once saved, cannot be undone)
- 잘못된 페이지 선택 시 앱을 삭제하고 재생성해야 함
- **Enterprise 개발자**: 앱 생성 후 회사 페이지 검증(Company Verification) 필수
  - 검증 URL을 Page Admin에게 전달하여 승인 받아야 함
  - 검증 완료 후 취소 불가

---

### 3. Privacy Policy URL (개인정보 처리방침 URL) ⚠️ 필수

**설명:**
- 앱이 수집하는 데이터와 사용 목적을 명시한 개인정보 처리방침 페이지 URL
- OAuth 인증 시 사용자에게 표시됨

**보안 고려사항:**
- **HTTPS 필수**: HTTP는 사용 불가 (보안 정책 위반)
- **접근 가능성**: 공개적으로 접근 가능한 URL이어야 함
- **GDPR/개인정보보호법 준수**: 다음 내용 포함 필수:
  - 수집하는 데이터 유형
  - 데이터 사용 목적
  - 데이터 보관 기간
  - 사용자 권리 (삭제, 수정, 열람)
  - 데이터 공유 정책
  - 연락처 정보

**권장 내용:**
```markdown
# 개인정보 처리방침 예시 구조

1. 수집하는 정보
   - LinkedIn 프로필 정보 (이름, 이메일, 프로필 사진)
   - 게시물 데이터 (공개 게시물만)
   - 연결 정보 (연결된 사용자 목록)

2. 사용 목적
   - 소셜 미디어 분석
   - 콘텐츠 추천
   - 사용자 경험 개선

3. 데이터 보관
   - 보관 기간: [기간]
   - 보관 방법: 암호화 저장

4. 사용자 권리
   - 데이터 삭제 요청
   - 데이터 수정 요청
   - 데이터 열람 요청

5. 연락처
   - 이메일: privacy@yourcompany.com
```

**URL 예시:**
```
https://yourcompany.com/privacy-policy
https://app.yourcompany.com/privacy
```

---

### 4. App Logo (앱 로고) 📷 선택

**설명:**
- OAuth 인증 화면에서 사용자에게 표시될 앱 로고
- 사용자가 앱을 식별하는 데 사용

**기술 요구사항:**
- **형식**: PNG, JPG, SVG
- **크기**: 정사각형 권장 (Square image)
- **최소 크기**: 최소 한 변이 100px 이상
- **권장 크기**: 512x512px 또는 1024x1024px

**보안 고려사항:**
- **로고 검증**: 악성 코드가 포함된 이미지 파일 업로드 방지
- **파일 크기 제한**: 과도하게 큰 파일은 업로드 거부될 수 있음
- **브랜드 일관성**: 회사 브랜드 가이드라인 준수

**권장 사항:**
- 고해상도 이미지 사용 (Retina 디스플레이 대응)
- 투명 배경 PNG 사용 (다양한 배경에 대응)
- 간단하고 명확한 디자인 (작은 크기에서도 식별 가능)

---

### 5. Legal Agreement (법적 동의) ⚠️ 필수

**설명:**
- LinkedIn API Terms of Use에 동의하는 체크박스
- 체크하지 않으면 앱 생성 불가

**보안/법적 고려사항:**
- **API 사용 제한**: LinkedIn API 사용 정책 준수 필수
- **데이터 사용 규칙**: 
  - 사용자 동의 없이 데이터 재판매 금지
  - 데이터 저장 및 사용 목적 제한
  - GDPR, CCPA 등 개인정보보호법 준수
- **Rate Limiting**: API 호출 제한 준수
- **사용자 권리**: 사용자가 언제든지 앱 연결 해제 가능

**LinkedIn API Terms of Use 주요 내용:**
1. **데이터 보호**: 사용자 데이터를 안전하게 보호해야 함
2. **사용 목적 제한**: 승인된 목적 외 사용 금지
3. **재판매 금지**: 데이터를 제3자에게 판매 불가
4. **보안 요구사항**: 적절한 보안 조치 구현 필수
5. **정기 감사**: LinkedIn이 앱 사용을 감사할 수 있음

**⚠️ 중요:**
- Terms of Use를 읽고 이해한 후 동의
- 위반 시 앱이 정지되거나 계정이 제한될 수 있음

---

## 🔒 보안 체크리스트

앱 생성 전 다음 항목을 확인하세요:

### Pre-Creation (생성 전)
- [ ] Privacy Policy URL이 HTTPS로 접근 가능한가?
- [ ] Privacy Policy에 GDPR/개인정보보호법 요구사항이 포함되어 있는가?
- [ ] LinkedIn Page Admin 권한이 있는가?
- [ ] 앱 이름이 명확하고 신뢰할 수 있는가?
- [ ] API Terms of Use를 읽고 이해했는가?

### Post-Creation (생성 후)
- [ ] **회사 페이지 검증 완료** (Enterprise 개발자 필수)
- [ ] 검증 URL을 Page Admin에게 안전하게 전달했는가?
- [ ] Client ID와 Client Secret을 안전하게 저장했는가?
- [ ] Client Secret을 Git에 커밋하지 않았는가?
- [ ] 환경 변수나 시크릿 관리 도구를 사용하는가?
- [ ] 필요한 API 권한만 요청했는가? (최소 권한 원칙)
- [ ] OAuth Redirect URI를 제한적으로 설정했는가?

---

## 🛡️ 보안 모범 사례

### 1. 자격 증명 관리

**❌ 나쁜 예:**
```python
# 하드코딩된 Client Secret (절대 금지!)
CLIENT_SECRET = "abc123xyz789"
```

**✅ 좋은 예:**
```python
import os
from aws_secretsmanager import get_secret

# 환경 변수 사용
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')

# 또는 AWS Secrets Manager 사용
CLIENT_SECRET = get_secret('linkedin/client-secret')
```

### 2. OAuth Redirect URI 설정

**보안 원칙:**
- 정확한 도메인과 경로 지정
- 와일드카드 사용 최소화
- 개발/프로덕션 환경 분리

**예시:**
```
https://app.yourcompany.com/auth/linkedin/callback
https://staging.yourcompany.com/auth/linkedin/callback
```

**❌ 피해야 할 설정:**
```
http://localhost:3000/callback  # HTTP 사용 금지
https://*.yourcompany.com/*      # 과도한 와일드카드
```

### 3. API 권한 요청

**최소 권한 원칙 적용:**
- 필요한 권한만 요청
- 사용자에게 명확한 권한 설명 제공
- 불필요한 데이터 수집 금지

**권한 예시:**
- `r_liteprofile`: 기본 프로필 정보 (이름, 프로필 사진)
- `r_emailaddress`: 이메일 주소
- `w_member_social`: 게시물 작성 (필요한 경우만)

### 4. 데이터 저장 및 암호화

**요구사항:**
- 수집한 데이터는 암호화하여 저장
- 전송 시 TLS 1.2+ 사용
- 데이터 보관 기간 최소화
- 사용자 요청 시 데이터 삭제 기능 제공

**예시:**
```python
# 데이터 암호화 저장
from cryptography.fernet import Fernet

def encrypt_user_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# AWS KMS 사용 예시
import boto3
kms = boto3.client('kms')
encrypted = kms.encrypt(
    KeyId='your-kms-key-id',
    Plaintext=user_data
)
```

---

## 📝 앱 생성 후 다음 단계

> **💡 빠른 참조: 회사 페이지 검증 프로세스**
> 
> 1. LinkedIn Developer Portal → 앱 선택 → "Verification URL" 복사
> 2. Page Admin에게 검증 URL 전달 (이메일 템플릿 사용)
> 3. Page Admin이 URL 접속 → 로그인 → 승인
> 4. 앱 대시보드에서 "Verified" 상태 확인
> 
> **현재 검증 URL (Twodragon 페이지):**
> ```
> https://www.linkedin.com/developers/apps/verification/5bc6ae9a-23f8-46f1-ab6f-7883d13bd01d
> ```
> 
> ⚠️ **중요**: 검증 완료 후 취소 불가! 신중하게 진행하세요.

---

### 1. 회사 페이지 검증 (Company Verification) ⚠️ 필수

**설명:**
- Enterprise/Third Party 개발자는 앱과 회사 페이지의 연관성을 검증해야 함
- 페이지가 앱에 대한 책임을 지며, Page Admin이 이 연관성을 확인할 수 있게 됨
- **검증 완료 전까지 일부 API 기능이 제한될 수 있음**

**⚠️ 중요 사항:**
- **되돌릴 수 없음**: 검증 완료 후 취소 불가 (Once verification is complete, it cannot be undone)
- **책임 전가**: 페이지가 앱에 대한 책임을 지게 됨
- **관리자 권한**: Page Admin만 검증 프로세스를 완료할 수 있음

---

#### 단계 1: 검증 URL 확인 및 복사

1. **LinkedIn Developer Portal 접속**
   - [LinkedIn Developer Portal](https://www.linkedin.com/developers/)에 로그인
   - 생성한 앱 선택

2. **검증 페이지 접근**
   - 앱 대시보드에서 "Verify company" 또는 "Company verification" 섹션 확인
   - "Verification URL" 섹션에서 URL 확인

3. **검증 URL 복사**
   - "Copy URL" 버튼 클릭하여 URL 복사
   - 예시 형식: `https://www.linkedin.com/developers/apps/verification/[UUID]`

**검증 URL 예시:**
```
https://www.linkedin.com/developers/apps/verification/5bc6ae9a-23f8-46f1-ab6f-7883d13bd01d
```

**현재 검증 URL (Twodragon 페이지용):**
```
https://www.linkedin.com/developers/apps/verification/5bc6ae9a-23f8-46f1-ab6f-7883d13bd01d
```

---

#### 단계 2: Page Admin 확인 및 연락

**Page Admin 확인 방법:**
1. LinkedIn에서 회사 페이지로 이동
2. "Admin tools" 또는 "관리 도구" 클릭
3. "Admins" 또는 "관리자" 탭에서 Admin 목록 확인
4. 적절한 Admin 선택 (보통 마케팅, IT, 또는 개발팀 담당자)

**Page Admin에게 보낼 이메일 템플릿:**

```markdown
제목: Twodragon LinkedIn 앱 검증 요청 - 긴급

안녕하세요 [Page Admin 이름]님,

LinkedIn Developer Portal에서 Twodragon 기술 블로그 앱을 생성했으며, 
회사 페이지와의 연관성을 검증하기 위해 승인이 필요합니다.

[검증 절차]
1. 아래 검증 URL을 클릭하세요
2. LinkedIn에 로그인하세요
3. 앱 정보를 확인하고 "Approve" 또는 "승인" 버튼을 클릭하세요

[검증 URL]
https://www.linkedin.com/developers/apps/verification/5bc6ae9a-23f8-46f1-ab6f-7883d13bd01d

[주의사항]
- 검증 완료 후 취소할 수 없습니다
- 검증 과정에서 제 이름, 프로필, 직책, 회사명이 표시됩니다
- 승인 시 회사 페이지가 앱에 대한 책임을 지게 됩니다

[문의]
검증 과정에 대한 질문이 있으시면 언제든지 연락주세요.

감사합니다.
[이름]
[부서/직책]
[연락처]
```

**실제 사용 예시 (Twodragon 페이지용):**

```markdown
제목: Twodragon LinkedIn 앱 검증 요청

안녕하세요,

LinkedIn Developer Portal에서 기술 블로그 자동 공유를 위한 앱을 생성했습니다.
Twodragon 페이지와의 연관성을 검증하기 위해 승인이 필요합니다.

[검증 URL]
https://www.linkedin.com/developers/apps/verification/5bc6ae9a-23f8-46f1-ab6f-7883d13bd01d

위 URL을 클릭하여 검증을 완료해주시기 바랍니다.

감사합니다.
```

---

#### 단계 3: 검증 승인 프로세스 (Page Admin 작업)

Page Admin이 검증 URL에 접속하면 다음 단계를 따릅니다:

1. **LinkedIn 로그인**
   - 검증 URL 클릭 시 LinkedIn 로그인 페이지로 이동
   - Page Admin 계정으로 로그인

2. **앱 정보 확인**
   - 다음 정보가 표시됨:
     - 앱 생성자 이름
     - 프로필 이미지
     - 현재 직책 (Current Title)
     - 현재 회사명 (Current Company Name)
     - 연결 상태 (Connection)

3. **승인 완료**
   - "Approve" 또는 "승인" 버튼 클릭
   - 확인 메시지 표시

**⚠️ Page Admin 주의사항:**
- 검증 전에 앱의 목적과 사용 목적을 확인하세요
- 앱 생성자가 회사 직원인지 확인하세요
- 검증 완료 후 취소할 수 없습니다

---

#### 단계 4: 검증 완료 확인

1. **앱 상태 확인**
   - LinkedIn Developer Portal에서 앱 대시보드 확인
   - "Company verification" 상태가 "Verified" 또는 "검증 완료"로 변경되었는지 확인

2. **API 제품 사용 가능 여부 확인**
   - 일부 API 제품은 검증 완료 후에만 사용 가능
   - 필요한 API 제품이 활성화되었는지 확인

3. **문서화**
   - 검증 완료 날짜 기록
   - 검증을 승인한 Page Admin 정보 기록
   - 검증 URL 보관 (보안상 안전한 곳에)

---

#### 문제 해결 (Troubleshooting)

**문제 1: 검증 URL이 표시되지 않음**
- 앱이 제대로 생성되었는지 확인
- Enterprise/Third Party 개발자 계정인지 확인
- Individual 개발자는 검증이 필요 없을 수 있음

**문제 2: Page Admin이 검증 URL에 접근할 수 없음**
- URL이 올바르게 복사되었는지 확인
- URL이 만료되지 않았는지 확인 (일반적으로 만료되지 않음)
- Page Admin 권한이 있는지 확인

**문제 3: 검증 후에도 API가 사용 불가**
- 검증 완료 후 몇 분 정도 기다려보기
- 브라우저 캐시 삭제 후 다시 시도
- LinkedIn Developer Portal에서 앱 상태 재확인

**문제 4: 잘못된 페이지로 검증됨**
- ⚠️ 검증 완료 후 취소 불가
- 앱을 삭제하고 재생성해야 함
- 올바른 페이지로 다시 검증 필요

---

#### 보안 고려사항

- **검증 URL 보안**: 
  - 검증 URL은 민감한 정보이므로 안전한 채널로 전달
  - 공개 채팅이나 이메일 그룹에 공유하지 않기
  - 필요시 암호화된 메시지로 전달

- **권한 확인**: 
  - Page Admin 권한이 있는지 사전 확인
  - 회사 정책에 따라 승인 프로세스 확인

- **프로세스 문서화**: 
  - 검증 과정을 문서화하여 추적 가능하도록 관리
  - 검증 완료 후 관련 문서 보관

---

#### 체크리스트

**앱 생성자 체크리스트:**
- [ ] 검증 URL이 생성되었는가?
- [ ] Page Admin 목록을 확인했는가?
- [ ] 적절한 Page Admin을 식별했는가?
- [ ] Page Admin에게 검증 요청 이메일을 보냈는가?
- [ ] 검증 완료 확인을 요청했는가?
- [ ] 검증 완료 후 앱 상태가 "Verified"로 변경되었는가?
- [ ] 필요한 API 제품이 활성화되었는가?
- [ ] 검증 관련 문서를 보관했는가?

**Page Admin 체크리스트:**
- [ ] 검증 URL을 받았는가?
- [ ] 앱 생성자가 회사 직원인지 확인했는가?
- [ ] 앱의 목적과 사용 목적을 이해했는가?
- [ ] 검증을 승인했는가?
- [ ] 검증 완료 확인을 앱 생성자에게 알렸는가?

---

### 2. API 제품 선택
- 필요한 API 제품 선택 (Marketing Developer Platform, Talent Solutions 등)
- 각 제품별 요구사항 확인

### 3. OAuth 2.0 설정
- Redirect URI 등록
- 필요한 스코프(권한) 선택

### 4. 테스트 환경 구성
- 개발 환경에서 OAuth 플로우 테스트
- 에러 처리 및 로깅 구현

### 5. 프로덕션 배포
- 보안 스캔 완료
- 모니터링 및 알림 설정
- 문서화 완료

---

## 🔗 참고 자료

- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
- [LinkedIn API Terms of Use](https://www.linkedin.com/legal/api-terms-of-use)
- [OAuth 2.0 Best Practices](https://oauth.net/2/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

---

## ⚠️ 주의사항

1. **되돌릴 수 없는 작업**: 
   - 앱 생성 후 일부 설정은 변경 불가
   - **회사 페이지 검증 완료 후 취소 불가** (매우 중요!)

2. **검증 필요**: 
   - Enterprise/Third Party 개발자는 회사 페이지 검증 필수
   - 검증 완료 전까지 일부 API 기능 제한 가능

3. **API 제한**: 
   - Individual 개발자는 제한된 API만 사용 가능
   - 기본 Company Page만 사용 가능

4. **정책 준수**: 
   - Terms of Use 위반 시 앱 정지 가능
   - 정기적인 감사에 협조 필요

5. **검증 프로세스**: 
   - Page Admin 권한이 있는 담당자에게 검증 URL 전달 필요
   - 검증 과정에서 개인정보(이름, 프로필, 직책 등)가 Page Admin에게 노출됨

---

**Last Updated**: 2026-01-08  
**Maintainer**: DevSecOps Team
