# Vercel 배포 최적화 가이드

Vercel의 추천사항을 적용하여 빌드 성능과 배포 효율성을 향상시킵니다.

## 적용된 최적화

### 1. Build Multiple Deployments Simultaneously
**목적**: 여러 배포를 동시에 빌드하여 대기 시간 제거 및 빌드 속도 최대 40% 향상

**설정 방법**:
1. Vercel 대시보드 접속
2. 프로젝트 선택 → **Settings** → **Build & Development Settings**
3. **On-Demand Concurrent Builds** 섹션에서 다음 중 선택:
   - ✅ **Run all builds immediately** (권장): 모든 빌드를 즉시 병렬 실행
   - **Run up to one build per branch**: 브랜치당 하나의 빌드만 실행

**효과**:
- 빌드 대기 시간 제거
- 여러 브랜치의 프리뷰 배포가 동시에 진행
- 프로덕션 배포 우선순위 유지

**주의사항**:
- Pro 플랜 이상에서 최대 12개의 동시 빌드 지원
- Hobby 플랜은 1개의 동시 빌드만 지원 (업그레이드 필요)

### 2. Switch to a Bigger Build Machine
**목적**: 더 큰 빌드 머신으로 전환하여 빌드 성능 향상

**설정 방법**:
1. Vercel 대시보드 접속
2. 프로젝트 선택 → **Settings** → **Build & Development Settings**
3. **Build Settings** 섹션에서 확인:
   - **Node.js Version**: 최신 LTS 버전 사용 (권장)
   - **Root Directory**: 프로젝트 루트 디렉토리 확인
   - **Build Command**: 최적화된 빌드 명령어 사용

**vercel.json 최적화**:
```json
{
  "build": {
    "env": {
      "BUNDLE_JOBS": "4",           // 병렬 빌드 작업 수
      "BUNDLE_WITHOUT": "development:test",  // 불필요한 의존성 제외
      "BUNDLE_PATH": "vendor/bundle"  // 번들 경로 최적화
    }
  }
}
```

**효과**:
- 더 빠른 의존성 설치
- 병렬 빌드로 빌드 시간 단축
- 불필요한 의존성 제외로 빌드 크기 감소

**업그레이드 옵션**:
- **Pro 플랜**: 더 큰 빌드 머신 및 더 많은 리소스
- **Enterprise 플랜**: 커스텀 빌드 머신 설정 가능

### 3. Prevent Frontend-Backend Mismatches
**목적**: 클라이언트와 서버 버전을 자동 동기화하여 배포 충돌 방지

**현재 프로젝트 구조**:
- **Frontend**: Jekyll 정적 사이트 (`_site` 디렉토리)
- **Backend**: Vercel Serverless Functions (`api/chat.js`)

**적용 방법**:

#### 방법 1: 빌드 ID 기반 버전 동기화
`vercel.json`에 빌드 메타데이터 추가:
```json
{
  "build": {
    "env": {
      "BUILD_ID": "$VERCEL_GIT_COMMIT_SHA",
      "BUILD_TIME": "$VERCEL_BUILD_TIME",
      "DEPLOYMENT_URL": "$VERCEL_URL"
    }
  }
}
```

#### 방법 2: @vercel/related-projects 사용 (프론트엔드-백엔드 분리 시)
프로젝트가 분리되어 있는 경우:
```bash
npm install @vercel/related-projects
```

```javascript
// api/chat.js 또는 프론트엔드 코드
import { withRelatedProject } from '@vercel/related-projects';

const apiUrl = withRelatedProject({
  projectName: "api-project",
  defaultHost: process.env.API_URL || "https://tech.2twodragon.com",
});
```

#### 방법 3: 환경 변수 기반 버전 관리
Vercel 환경 변수에 버전 정보 추가:
- **Production**: `APP_VERSION=1.0.0`
- **Preview**: `APP_VERSION=preview-{COMMIT_SHA}`

**효과**:
- 프리뷰 배포 시 해당하는 백엔드 버전 자동 참조
- 프로덕션 배포 시 안정적인 버전 유지
- 버전 불일치로 인한 오류 방지

## vercel.json 최적화 설정

현재 적용된 최적화:

```json
{
  "build": {
    "env": {
      "BUNDLE_WITHOUT": "development:test",  // 개발/테스트 의존성 제외
      "BUNDLE_JOBS": "4",                    // 병렬 빌드 작업
      "BUNDLE_PATH": "vendor/bundle"        // 번들 경로 최적화
    }
  },
  "git": {
    "deploymentEnabled": {
      "production": true,
      "preview": true,
      "development": true
    }
  }
}
```

## 대시보드 설정 체크리스트

### Build & Development Settings
- [ ] **On-Demand Concurrent Builds**: "Run all builds immediately" 활성화
- [ ] **Node.js Version**: 최신 LTS 버전 확인
- [ ] **Build Command**: 최적화된 명령어 확인
- [ ] **Install Command**: `bundle install` 확인
- [ ] **Output Directory**: `_site` 확인
- [ ] **Root Directory**: 프로젝트 루트 확인

### Environment Variables
- [ ] **BUILD_ID**: `$VERCEL_GIT_COMMIT_SHA` 설정 (자동)
- [ ] **BUILD_TIME**: `$VERCEL_BUILD_TIME` 설정 (자동)
- [ ] **DEPLOYMENT_URL**: `$VERCEL_URL` 설정 (자동)
- [ ] **APP_VERSION**: 필요시 수동 설정

### Git Integration
- [ ] **Production Branch**: `main` 또는 `master` 확인
- [ ] **Preview Deployments**: 활성화 확인
- [ ] **Automatic Deployments**: 활성화 확인

## 성능 모니터링

### 빌드 시간 추적
```bash
# Vercel CLI로 빌드 로그 확인
vercel logs --follow

# 특정 배포 확인
vercel inspect [DEPLOYMENT_URL]
```

### 주요 메트릭
- **빌드 시간**: 목표 < 2분
- **동시 빌드 수**: Pro 플랜 기준 최대 12개
- **배포 성공률**: 목표 > 99%

## 문제 해결

### 빌드 대기 시간이 긴 경우
1. **On-Demand Concurrent Builds** 활성화 확인
2. Pro 플랜 업그레이드 고려 (Hobby 플랜은 1개만 지원)
3. 불필요한 빌드 트리거 확인

### 빌드 실패 시
1. 빌드 로그 확인: `vercel logs`
2. Node.js 버전 확인
3. 의존성 설치 오류 확인: `bundle install` 로컬 테스트

### 버전 불일치 오류
1. 환경 변수 확인: `vercel env ls`
2. 빌드 ID 확인: `$VERCEL_GIT_COMMIT_SHA`
3. 프리뷰 배포 시 해당 커밋의 백엔드 버전 확인

## 비용 고려사항

### Hobby (무료) 플랜
- ✅ 1개 동시 빌드
- ✅ 기본 빌드 머신
- ⚠️ 빌드 대기 시간 발생 가능

### Pro 플랜 ($20/월)
- ✅ 최대 12개 동시 빌드
- ✅ 더 큰 빌드 머신
- ✅ 빌드 대기 시간 최소화
- ✅ 우선순위 지원

### Enterprise 플랜
- ✅ 무제한 동시 빌드
- ✅ 커스텀 빌드 머신
- ✅ 전용 리소스

## 참고 자료

- [Vercel Build Settings](https://vercel.com/docs/builds/managing-builds)
- [Vercel Concurrent Builds](https://vercel.com/docs/builds/build-queues)
- [Vercel Related Projects](https://vercel.com/changelog/sync-projects-with-vercel-related-projects)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Vercel Pricing](https://vercel.com/pricing)

## 다음 단계

1. ✅ `vercel.json` 최적화 설정 적용 완료
2. ⏳ Vercel 대시보드에서 **On-Demand Concurrent Builds** 활성화
3. ⏳ 빌드 성능 모니터링 및 최적화
4. ⏳ 필요시 Pro 플랜 업그레이드 고려
