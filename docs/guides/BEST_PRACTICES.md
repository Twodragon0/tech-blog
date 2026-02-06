# Tech Blog Best Practices

이 문서는 기술 블로그 운영 및 콘텐츠 작성을 위한 모범 사례와 가이드라인을 정리합니다.

## 📋 목차

1. [포스트 작성 가이드](#포스트-작성-가이드)
2. [코드 작성 규칙](#코드-작성-규칙)
3. [보안 고려사항](#보안-고려사항)
4. [이미지 및 시각화](#이미지-및-시각화)
5. [Git 워크플로우](#git-워크플로우)
6. [품질 관리](#품질-관리)

---

## 포스트 작성 가이드

### 1. 포스트 구조

모든 포스트는 다음 구조를 따릅니다:

```
1. Front Matter (YAML 헤더)
2. 포스팅 요약 섹션
3. 서론
4. 본문 (주제별 섹션)
   - 명확한 제목
   - 코드 예제 (필요시)
   - 이미지/다이어그램 (필요시)
   - 실무 팁 및 주의사항
5. 결론
```

### 2. 제목 작성 원칙

- **명확성**: 제목만으로도 내용을 파악할 수 있어야 함
- **검색 최적화**: 주요 키워드 포함
- **길이**: 50-70자 권장 (너무 길면 요약 형식 사용)
- **형식**: "주제: 부제" 또는 "주제 완벽 가이드" 형식 선호

**좋은 예:**
- "AWS에서 안전한 데이터베이스 접근 게이트웨이 구축하기: NLB + Security Group 완벽 가이드"
- "Zscaler 완벽 가이드: SSL 검사, 샌드박스, AI, 광고, 유해 사이트 완벽 차단"

**나쁜 예:**
- "AWS 설정하기" (너무 모호함)
- "데이터베이스" (주제 불명확)

### 3. 카테고리 및 태그

#### 카테고리 선택
- 하나의 주요 카테고리 선택 (`category` 필드)
- 관련 카테고리는 `categories` 배열에 추가 가능
- `_config.yml`의 `category_list` 참조

#### 태그 작성
- 3-7개의 태그 권장
- 주요 기술/도구/서비스명 포함
- 대문자로 시작, 하이픈으로 단어 구분
- 예: `[AWS, NLB, Security-Group, Database, Zero-Trust]`

### 4. 요약 (Excerpt) 작성

- 150-200자 권장
- 포스트의 핵심 내용을 간결하게 요약
- 독자가 포스트를 읽을지 결정하는 중요한 요소
- 문제 해결 방법이나 주요 인사이트 포함

### 5. 본문 작성 원칙

#### 섹션 구조
- 명확한 제목으로 섹션 구분
- 각 섹션은 독립적으로 읽을 수 있어야 함
- 계층 구조: H2 → H3 → H4 (최대 4단계)

#### 내용 작성
- **실무 중심**: 이론보다 실제 경험과 사례
- **구체성**: 모호한 표현 지양, 구체적인 예제 제공
- **단계별 설명**: 복잡한 내용은 단계별로 나누어 설명
- **문제 해결**: 문제 상황 → 원인 분석 → 해결 방법 → 검증

#### 문체
- 존댓말 사용 (예외: 코드 주석은 간결하게)
- 전문 용어는 첫 사용 시 간단히 설명
- 영어 용어는 한글 병기: "보안 그룹(Security Group)"

---

## 코드 작성 규칙

### 1. 코드 블록 형식

```markdown
```[언어]
# 코드 내용
# 주석으로 설명 추가
```
```

**지원 언어:**
- `bash`, `shell`: 쉘 스크립트, 명령어
- `yaml`, `yml`: YAML 설정 파일
- `json`: JSON 설정 파일
- `python`: Python 스크립트
- `terraform`, `hcl`: Terraform 코드
- `dockerfile`: Dockerfile
- `markdown`: 마크다운 예제

### 2. 코드 예제 모범 사례

#### ✅ 좋은 예

```bash
# RDS 인스턴스 생성
aws rds create-db-instance \
  --db-instance-identifier production-db \
  --db-instance-class db.t3.medium \
  --engine mysql \
  --master-username admin \
  --master-user-password '${DB_PASSWORD}' \
  --allocated-storage 100 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name production-subnet-group
```

**특징:**
- 명확한 주석
- 환경 변수 사용 (`${DB_PASSWORD}`)
- 보안 그룹 ID는 예시 값 사용

#### ❌ 나쁜 예

```bash
aws rds create-db-instance --db-instance-identifier prod --master-username admin --master-user-password MyPassword123!
```

**문제점:**
- 주석 없음
- 하드코딩된 비밀번호
- 보안 취약

### 3. Terraform 코드 작성

#### 변수 사용
```hcl
# variables.tf
variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

# main.tf
resource "aws_db_instance" "main" {
  identifier     = "production-db"
  engine         = "mysql"
  instance_class = "db.t3.medium"
  master_username = "admin"
  master_password = var.db_password  # 변수 사용
  
  # 보안 설정
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  publicly_accessible    = false  # 보안: 외부 접근 차단
}
```

#### 리소스 태깅
```hcl
resource "aws_instance" "web" {
  # ... 기타 설정 ...
  
  tags = {
    Name        = "web-server"
    Environment = "production"
    ManagedBy   = "terraform"
    CostCenter  = "engineering"
  }
}
```

### 4. YAML/JSON 설정 파일

#### 들여쓰기
- YAML: 스페이스 2칸 (탭 사용 금지)
- JSON: 스페이스 2칸

#### 주석 및 설명
```yaml
# Security Group 규칙
# 최소 권한 원칙 적용: 필요한 포트만 허용
security_group_rules:
  - name: "Allow HTTPS"
    port: 443
    protocol: "tcp"
    source: "0.0.0.0/0"  # 프로덕션에서는 특정 IP로 제한 권장
```

---

## 보안 고려사항

### 1. 민감 정보 처리

#### 절대 금지 사항
- ❌ 실제 API 키, 비밀번호, 토큰 하드코딩
- ❌ 실제 IP 주소, 도메인명 (프로덕션 환경)
- ❌ 개인 정보 (이메일, 전화번호 등)

#### 올바른 처리 방법
```bash
# ✅ 환경 변수 사용
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"

# ✅ 시크릿 관리 도구 사용
aws secretsmanager get-secret-value --secret-id db-credentials

# ✅ 예시 값 사용
API_KEY="YOUR_API_KEY_HERE"
DB_PASSWORD="your-secure-password"
```

### 2. 보안 모범 사례 강조

코드 예제에 보안 주석 추가:

```hcl
# 보안: 최소 권한 원칙 적용
resource "aws_security_group_rule" "allow_https" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]  # 프로덕션에서는 특정 IP로 제한 권장
  security_group_id = aws_security_group.web.id
}

# 보안: 암호화 활성화
resource "aws_s3_bucket" "data" {
  bucket = "my-secure-bucket"
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
```

### 3. 보안 경고 박스

중요한 보안 주의사항은 박스로 강조:

```markdown
> **⚠️ 보안 주의사항**
> 
> 이 설정은 개발 환경용입니다. 프로덕션 환경에서는 다음을 고려하세요:
> 
> - Security Group 규칙을 특정 IP로 제한
> - SSL/TLS 인증서 검증 활성화
> - 로그 모니터링 및 알림 설정
> - 정기적인 보안 감사 수행
```

### 4. 취약점 및 대응

보안 취약점을 다룰 때:
- 취약점 설명
- 공격 시나리오
- 영향도 분석
- 대응 방법 (단계별)
- 예방 조치

---

## 이미지 및 시각화

### 1. 이미지 생성 가이드

자세한 내용은 `GEMINI_IMAGE_GUIDE.md` 참조

#### 기본 원칙
- **스타일**: nano banana (미니멀하고 깔끔한 일러스트)
- **크기**: 블로그 포스트용 가로형 레이아웃
- **색상**: 전문적인 색상 팔레트
- **텍스트**: 한글 지원, 명확하고 읽기 쉬운 폰트

#### 이미지 유형
- 🏗️ **Architecture**: 아키텍처 다이어그램
- 🔄 **Flow**: 프로세스 흐름도
- 📅 **Timeline**: 타임라인
- 📊 **Table**: 비교표/데이터 표
- 📈 **Chart**: 차트/그래프
- 🎯 **Summary**: 요약 인포그래픽

### 2. 이미지 파일 관리

#### 파일명 규칙
- 형식: `YYYY-MM-DD-[포스트제목]-[순번].svg`
- 예시: `2025-11-04-Zscaler_완벽_가이드-01.svg`
- 확장자: `.svg` (벡터) 또는 `.png` (래스터)

#### 저장 위치
- 모든 이미지는 `/assets/images/` 디렉토리에 저장
- 포스트별로 하위 디렉토리 생성 가능 (선택사항)

#### 이미지 삽입
```markdown
![이미지 설명](assets/images/2025-11-04-Zscaler_완벽_가이드-01.svg)
*그림 1: Zscaler 아키텍처 구조*
```

### 3. 시각화 체크리스트

포스트 작성 전 `POST_VISUALIZATION_CHECKLIST.md` 확인:
- 필요한 이미지 유형 확인
- Gemini 이미지 생성 명령어 준비
- 이미지 삽입 위치 결정

---

## Git 워크플로우

### 1. 브랜치 전략

```
main (production)
  └── develop (development)
      └── feature/[feature-name]
      └── fix/[bug-name]
```

### 2. 커밋 메시지 규칙

#### 형식
```
[타입] 간단한 제목 (50자 이내)

상세 설명 (선택사항)
- 변경 사항 1
- 변경 사항 2
```

#### 타입
- `feat`: 새 기능 (포스트 추가)
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 포맷팅, 세미콜론 누락 등
- `refactor`: 코드 리팩토링
- `chore`: 빌드 업무 수정, 패키지 매니저 설정 등

#### 예시
```
feat: Zscaler 완벽 가이드 포스트 추가

- SSL 검사 설정 방법 추가
- 샌드박스 정책 구성 가이드 추가
- AI/광고 사이트 차단 정책 추가
- 관련 이미지 3개 추가
```

### 3. Pull Request 규칙

#### PR 제목
- 커밋 메시지와 동일한 형식
- 명확하고 간결하게

#### PR 설명 템플릿
```markdown
## 변경 사항
- [변경 사항 1]
- [변경 사항 2]

## 관련 이슈
- Closes #이슈번호

## 체크리스트
- [ ] 코드/문서 검토 완료
- [ ] 이미지 경로 확인
- [ ] 링크 및 참조 확인
- [ ] 보안 고려사항 확인
```

### 4. 파일 변경 시 주의사항

#### 새 포스트 추가
- `_posts/` 디렉토리에 올바른 파일명으로 생성
- Front matter 형식 확인
- 이미지 파일 함께 커밋

#### 기존 포스트 수정
- 변경 이유 명시
- 기존 링크 및 참조 확인
- 이미지 경로 확인

#### 설정 파일 변경
- `_config.yml` 변경 시 영향도 확인
- 테스트 환경에서 검증 후 커밋

---

## 품질 관리

### 1. 포스트 작성 전 체크리스트

- [ ] 제목이 명확하고 검색 최적화되어 있는가?
- [ ] Front matter 형식이 올바른가?
- [ ] 포스팅 요약 섹션이 포함되어 있는가?
- [ ] 카테고리와 태그가 적절한가?
- [ ] 본문 구조가 명확한가?
- [ ] 필요한 이미지가 준비되었는가?
- [ ] 코드 예제에 보안 고려사항이 포함되어 있는가?
- [ ] 민감한 정보가 제거되었는가?

### 2. 코드 검토 체크리스트

- [ ] 하드코딩된 민감 정보가 없는가?
- [ ] 보안 모범 사례를 따르고 있는가?
- [ ] 주석이 충분하고 명확한가?
- [ ] 변수명이 명확한가?
- [ ] 에러 처리가 적절한가?

### 3. 이미지 검토 체크리스트

- [ ] 이미지 파일명이 규칙을 따르는가?
- [ ] 이미지 경로가 올바른가?
- [ ] 이미지 설명(alt text)이 포함되어 있는가?
- [ ] 이미지가 포스트 내용과 일치하는가?
- [ ] 이미지 품질이 적절한가?

### 4. 최종 검토

#### 내용 검토
- 맞춤법 및 문법 검사
- 기술적 정확성 확인
- 링크 및 참조 확인
- 일관성 확인 (용어, 형식)

#### 형식 검토
- 마크다운 형식 올바름
- 코드 블록 형식 올바름
- 이미지 삽입 형식 올바름
- 표 형식 올바름

#### 보안 검토
- 민감 정보 제거 확인
- 보안 모범 사례 준수 확인
- 보안 경고 박스 포함 확인

---

## 참고 자료

### 프로젝트 문서
- `README.md`: 프로젝트 개요
- `.cursorrules`: Cursor AI 설정 및 규칙
- `GEMINI_IMAGE_GUIDE.md`: 이미지 생성 가이드
- `POST_VISUALIZATION_CHECKLIST.md`: 시각화 체크리스트
- `_config.yml`: Jekyll 설정 및 카테고리 목록

### 외부 자료
- [Jekyll 공식 문서](https://jekyllrb.com/docs/)
- [Markdown 가이드](https://www.markdownguide.org/)
- [AWS 보안 모범 사례](https://aws.amazon.com/security/security-resources/)
- [Terraform 모범 사례](https://www.terraform.io/docs/language/settings/index.html)

---

---

## AI 어시스턴트 활용 최적화

### Opus 4.6 최대한 활용하기

Claude Opus 4.6를 효과적으로 활용하기 위한 가이드라인입니다.

#### 1. 프롬프트 작성 원칙

**✅ 좋은 예시**:
```markdown
"보안을 최우선으로 고려하여 API 키는 환경 변수로 관리하고, 
로그에는 민감 정보가 노출되지 않도록 마스킹을 적용해줘. 
이렇게 하면 실수로 커밋되거나 로그에 노출되는 위험을 방지할 수 있어."
```

**❌ 나쁜 예시**:
```markdown
"API 키는 환경 변수로 관리해줘. 그리고 잊지 말고 로그에는 마스킹을 적용해줘. 
그리고 API 키는 절대 하드코딩하지 말아줘."
```

**핵심 원칙**:
- **반복 지시 불필요**: Opus 4.6는 처음부터 지시사항을 더 꼼꼼하게 따릅니다.
- **의도 설명 포함**: 규칙뿐만 아니라 지시의 의도를 설명하면 넓은 범위에 적용할 수 있습니다.
- **명확한 예시 몇 개면 충분**: Opus 4.6는 그것으로부터 일반화할 수 있습니다.

#### 2. 맥락 제공 전략

**복잡한 작업**:
```markdown
"이 프로젝트는 Jekyll 기반 기술 블로그입니다. 
_posts/ 디렉토리에 마크다운 포스트가 있고, 
assets/images/에 이미지가 저장됩니다. 
이 구조를 이해한 후 새로운 포스트 생성 스크립트를 작성해줘."
```

**간단한 작업**:
```markdown
"이 파일만 봐주세요: scripts/check_posts.py의 50-60줄만 수정해줘. 
넓은 맥락은 건너뛰세요."
```

#### 3. 확인 지점 설정

복잡한 다단계 작업의 경우:
```markdown
"각 주요 단계 후에 확인해줘:
1. 파일 구조 분석 후 확인
2. 개선 로직 설계 후 확인
3. 구현 후 확인"
```

#### 4. 대안 탐색 및 스트레스 테스트

- **대안 탐색**: "이걸 접근하는 세 가지 방법이 뭐가 있을까?"
- **스트레스 테스트**: "이 계획의 문제점은 뭐야?" 또는 "내가 놓치고 있는 게 뭐야?"
- **결정 완료 시**: "대안은 이미 고려했어. 이 접근 방식으로 진행해줘."

#### 5. 글쓰기 스타일 가이드

**예시 제공**:
```markdown
"다음 스타일로 기술 블로그 포스트를 작성해줘:
- 실무 중심의 구체적인 내용
- 보안 모범 사례 강조
- 코드 예제와 설정 파일 포함
- 문제 해결 과정과 트러블슈팅 포함"
```

**제약 명시**:
```markdown
"다음은 피해줘:
- 이론적인 설명만 하는 것
- FAQ 섹션 추가
- 과도한 마케팅 톤"
```

자세한 내용은 `CLAUDE.md`와 `AGENTS.md`의 Opus 4.6 섹션을 참조하세요.

---

**마지막 업데이트**: 2026-02-06
