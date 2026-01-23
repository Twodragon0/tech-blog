# PDCA: 알림/공유 기능

> SNS 공유, 이메일 뉴스레터, 알림 시스템

## 현황

| 항목 | 값 |
|------|-----|
| **워크플로우** | `sns-share.yml`, `buttondown-notify.yml` |
| **트리거** | push (main, _posts/**) |
| **플랫폼** | Twitter/X, Facebook, LinkedIn, Buttondown |
| **상태** | Active |

---

## Plan (계획)

### 목표
- 새 포스트 자동 SNS 공유
- 이메일 뉴스레터 자동 발송
- 구독자 참여도 향상

### KPI
| 지표 | 목표 | 현재 |
|------|------|------|
| SNS 공유 성공률 | 99%+ | - |
| 이메일 발송 성공률 | 99%+ | - |
| 이메일 오픈율 | 20%+ | - |

### 알림 아키텍처
```
┌─────────────┐
│  New Post   │
│   (Push)    │
└──────┬──────┘
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
┌─────────────┐                          ┌─────────────┐
│  SNS Share  │                          │  Buttondown │
│  Workflow   │                          │  Notify     │
└──────┬──────┘                          └──────┬──────┘
       │                                        │
       ├──────┬──────┬──────┐                   ▼
       ▼      ▼      ▼      ▼           ┌─────────────┐
   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │  Subscribers │
   │ X/  │ │ FB  │ │ LI  │ │More │     │   (Email)    │
   │Twit │ │     │ │     │ │     │     └─────────────┘
   └─────┘ └─────┘ └─────┘ └─────┘
```

---

## Do (실행)

### 1. SNS 공유 (sns-share.yml)

**트리거:**
```yaml
on:
  push:
    branches: [main]
    paths:
      - '_posts/**'  # 포스트 변경 시에만
```

**지원 플랫폼:**
| 플랫폼 | API | Secret 키 |
|--------|-----|-----------|
| Twitter/X | Tweepy v2 | TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET |
| Facebook | Graph API | FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN |
| LinkedIn | UGC Posts API | LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID |

**실행 스크립트:**
```bash
python scripts/share_sns.py "$LATEST_POST"
```

### 2. 이메일 뉴스레터 (buttondown-notify.yml)

**트리거:**
```yaml
on:
  push:
    branches: [main]
    paths:
      - '_posts/**'
```

**특징:**
- 새 포스트만 발송 (--diff-filter=A)
- 수정된 포스트는 제외
- 배치 처리 지원

**실행 스크립트:**
```bash
python3 scripts/buttondown_notify_batch.py
```

**이메일 템플릿:**
```markdown
## {포스트 제목}

📅 {발행일}
🔒 {카테고리}
🏷️ {태그들}

📋 요약
{excerpt 또는 첫 단락}

[📖 전체 내용 읽기]({포스트 URL})
```

### 3. 관련 스크립트

```bash
# 이메일 미리보기
python3 scripts/preview_buttondown_email.py _posts/YYYY-MM-DD-Title.md

# 발송 테스트 (Dry Run)
python3 scripts/test_buttondown_email_send.py _posts/YYYY-MM-DD-Title.md --dry-run
```

---

## Check (점검)

### 모니터링 항목

#### SNS 공유 상태
```bash
# 최근 워크플로우 실행 확인
gh run list --workflow=sns-share.yml --limit=5
```

#### 이메일 발송 상태
```bash
# 최근 워크플로우 실행 확인
gh run list --workflow=buttondown-notify.yml --limit=5
```

#### Buttondown 대시보드
- 구독자 수
- 이메일 오픈율
- 클릭률
- 구독 취소율

### 점검 체크리스트
- [ ] SNS 공유 성공 여부
- [ ] 이메일 발송 성공 여부
- [ ] 포맷/링크 정상 동작
- [ ] API 키 만료 확인

### 장애 대응
| 상황 | 대응 |
|------|------|
| API 키 만료 | GitHub Secrets 갱신 |
| Rate Limit | 재시도 로직 확인 |
| 발송 실패 | 수동 재실행 |

---

## Act (개선)

### 식별된 개선점
1. **플랫폼 추가**: Threads, Mastodon 지원
2. **스케줄링**: 최적 시간대 공유
3. **A/B 테스트**: 제목/내용 최적화

### 개선 이력
| 날짜 | 개선 내용 | 결과 |
|------|----------|------|
| - | - | - |

### 다음 사이클 계획
- [ ] 새 SNS 플랫폼 연동 검토
- [ ] 이메일 템플릿 개선
- [ ] 공유 시간대 최적화

---

## 비용 관리

### API 사용량
| 서비스 | 무료 티어 | 현재 사용 |
|--------|----------|----------|
| Twitter API | 기본 무료 | - |
| Facebook API | 무료 | - |
| LinkedIn API | 무료 | - |
| Buttondown | 100 구독자 | - |

### 비용 절감 팁
1. 조건부 실행 (새 포스트만)
2. 배치 처리 (여러 포스트 통합)
3. 실패 재시도 제한

---

## 관련 문서

- [Pipeline 전체 흐름](../pipeline/README.md)
- [SNS 공유 스크립트](../../scripts/share_sns.py)
- [Buttondown 설정](../setup/buttondown.md)
