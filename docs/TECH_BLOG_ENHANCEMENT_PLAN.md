# Tech-Blog 플랫폼 고도화 기획서

## 📋 목차
1. [현재 상태 분석](#현재-상태-분석)
2. [멀티 플랫폼 통합 전략](#멀티-플랫폼-통합-전략)
3. [핵심 기능 추가](#핵심-기능-추가)
4. [사용자 경험 개선](#사용자-경험-개선)
5. [수익화 전략](#수익화-전략)
6. [기술 구현 계획](#기술-구현-계획)
7. [마이그레이션 전략](#마이그레이션-전략)
8. [로드맵](#로드맵)

---

## 현재 상태 분석

### ✅ 현재 구현된 기능
- **정적 블로그**: Jekyll 기반 정적 사이트 생성
- **콘텐츠 관리**: Markdown 기반 포스트 작성
- **카테고리 시스템**: 7개 카테고리 (Security, DevSecOps, DevOps, Cloud, Kubernetes, FinOps, Incident, Certifications)
- **자격증 관리**: 6개 자격증 정보 페이지
- **댓글 시스템**: Giscus (GitHub Discussions 연동)
- **검색 기능**: 클라이언트 사이드 검색 (search.json)
- **SEO 최적화**: Open Graph, Sitemap, RSS Feed
- **광고 연동**: Google AdSense
- **소셜 공유**: 기본 소셜 공유 기능

### ⚠️ 현재 제한사항
- **사용자 인증 없음**: 개인화 기능 불가
- **동적 기능 부족**: 정적 사이트로 인한 제약
- **통계 추적 제한**: 기본 조회수만 추적 가능
- **플랫폼 간 연동 없음**: online-course와의 연결 부재
- **프리미엄 콘텐츠 없음**: 수익화 옵션 제한적
- **외부 API 연동 미흡**: GitHub, LinkedIn 연동 없음

---

## 멀티 플랫폼 통합 전략

### 1. 아키텍처 전환 전략

#### Option A: 하이브리드 아키텍처 (권장) ⭐
**Jekyll 정적 사이트 + Next.js API 레이어**

```
┌─────────────────────────────────────────┐
│         Vercel Edge Network             │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Jekyll  │  │ Next.js  │  │  Shared  │
│  Static  │  │   API    │  │    DB    │
│  Site    │  │  Layer   │  │          │
└──────────┘  └──────────┘  └──────────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
                   │
                   ▼
            ┌──────────┐
            │online-   │
            │course    │
            └──────────┘
```

**장점**:
- 기존 Jekyll 콘텐츠 유지 (마이그레이션 비용 최소화)
- 점진적 전환 가능
- 정적 사이트의 SEO 이점 유지
- 동적 기능은 Next.js API로 처리

**구현 방식**:
- Jekyll 빌드 결과물을 Next.js의 `public/` 디렉토리에 배치
- Next.js API Routes로 동적 기능 처리
- 공유 데이터베이스와 연동

#### Option B: 완전 전환 (장기)
**Next.js 14 App Router로 완전 전환**

**장점**:
- 완전한 동적 기능
- 통합된 개발 환경
- 더 나은 성능 최적화

**단점**:
- 마이그레이션 비용 높음
- 기존 SEO 영향 가능

---

### 2. 플랫폼 간 콘텐츠 연결

#### 2.1 online-course와의 통합

**연결 시나리오**:

1. **블로그 포스트 → 코스 연결**
   ```
   블로그 포스트: "AWS 보안 아키텍처 완벽 가이드"
   ↓
   관련 코스: "AWS 보안 실전 코스"
   ↓
   사용자 경험: 블로그 포스트 하단에 "관련 코스 보기" 버튼
   ```

2. **코스 → 블로그 포스트 연결**
   ```
   코스: "클라우드 시큐리티 8기"
   ↓
   관련 블로그 포스트: "클라우드 시큐리티 8기 3주차"
   ↓
   사용자 경험: 코스 페이지에 "관련 블로그 포스트" 섹션
   ```

**구현 방법**:
```typescript
// lib/sync-client.ts
interface ContentLink {
  sourcePlatform: 'tech-blog' | 'online-course';
  sourceContentId: string;
  targetPlatform: 'tech-blog' | 'online-course';
  targetContentId: string;
  linkType: 'related' | 'prerequisite' | 'follow-up';
}

// 블로그 포스트에 관련 코스 표시
async function getRelatedCourses(postId: string): Promise<Course[]> {
  const links = await syncClient.getContentLinks({
    sourcePlatform: 'tech-blog',
    sourceContentId: postId,
    targetPlatform: 'online-course',
  });
  
  return links.map(link => getCourse(link.targetContentId));
}
```

#### 2.2 전자제품/IT 제품 제휴 마케팅

**연계 전략**:
tech-blog의 기술 콘텐츠와 자연스럽게 연계되는 전자제품 및 IT 제품을 추천하고 제휴 수익을 창출합니다.

**연계 시나리오**:

1. **하드웨어 제품 추천**
   ```
   포스트: "Kubernetes 클러스터 구축 가이드"
   ↓
   추천 제품: 
   - 서버/워크스테이션 (Dell, HP, Lenovo)
   - 네트워크 장비 (Ubiquiti, TP-Link)
   - 스토리지 솔루션 (Synology, QNAP)
   ↓
   사용자 경험: 포스트 내 "추천 하드웨어" 섹션
   ```

2. **개발 도구 및 소프트웨어**
   ```
   포스트: "DevSecOps 파이프라인 구축"
   ↓
   추천 제품:
   - IDE/에디터 (JetBrains, VS Code 확장)
   - 모니터링 도구 (Datadog, New Relic)
   - 보안 도구 (Snyk, SonarQube)
   ↓
   사용자 경험: 관련 도구 비교 및 추천 섹션
   ```

3. **클라우드 서비스 및 도구**
   ```
   포스트: "AWS 보안 아키텍처"
   ↓
   추천 제품:
   - AWS 서비스 (공식 제휴 프로그램)
   - 클라우드 관리 도구 (Terraform, Ansible)
   - 보안 솔루션 (Cloudflare, AWS WAF)
   ↓
   사용자 경험: "이 포스트에서 사용한 도구" 섹션
   ```

4. **전자제품 (개발 환경 최적화)**
   ```
   포스트: "원격 개발 환경 구축"
   ↓
   추천 제품:
   - 모니터 (다중 모니터 설정)
   - 키보드/마우스 (기계식 키보드, 트랙볼)
   - 웹캠/마이크 (화상 회의용)
   - 노트북/데스크톱 (개발용 사양)
   ↓
   사용자 경험: "개발 환경 추천" 섹션
   ```

**제휴 파트너 후보**:
- **아마존 제휴 프로그램**: AWS 서비스, 전자제품
- **쿠팡 파트너스**: 전자제품, IT 제품
- **네이버 제휴 프로그램**: 전자제품, IT 제품
- **직접 제휴**: 
  - JetBrains (개발 도구)
  - Datadog (모니터링)
  - Cloudflare (보안/CDN)
  - Synology/QNAP (NAS)
  - Dell/HP/Lenovo (서버/워크스테이션)

**구현 방법**:
```typescript
// lib/affiliate.ts
interface ProductRecommendation {
  productId: string;
  name: string;
  category: 'hardware' | 'software' | 'cloud' | 'tool';
  price?: number;
  affiliateUrl: string;
  imageUrl?: string;
  description: string;
  relevanceScore: number; // 포스트와의 관련도
}

// 포스트와 관련된 제품 추천
async function getRecommendedProducts(
  postId: string,
  category?: string
): Promise<ProductRecommendation[]> {
  const post = await getPost(postId);
  
  // 포스트 카테고리/태그 기반 제품 매칭
  const products = await matchProducts({
    category: post.category,
    tags: post.tags,
    content: post.content,
  });
  
  // 관련도 점수로 정렬
  return products.sort((a, b) => b.relevanceScore - a.relevanceScore);
}

// 제휴 링크 생성
export function getAffiliateLink(
  url: string,
  platform: 'amazon' | 'coupang' | 'naver' | 'direct',
  productId?: string
): string {
  const affiliateIds = {
    amazon: process.env.AMAZON_ASSOCIATE_ID,
    coupang: process.env.COUPANG_PARTNER_ID,
    naver: process.env.NAVER_PARTNER_ID,
    aws: process.env.AWS_AFFILIATE_ID,
    jetbrains: process.env.JETBRAINS_AFFILIATE_ID,
    datadog: process.env.DATADOG_AFFILIATE_ID,
    cloudflare: process.env.CLOUDFLARE_AFFILIATE_ID,
  };
  
  return addAffiliateParams(url, affiliateIds[platform], productId);
}
```

**제품 추천 UI 컴포넌트**:
```typescript
// components/product-recommendations.tsx
export function ProductRecommendations({ postId }: { postId: string }) {
  const products = await getRecommendedProducts(postId);
  
  return (
    <section className="product-recommendations">
      <h3>이 포스트에서 추천하는 제품</h3>
      <div className="product-grid">
        {products.map(product => (
          <ProductCard
            key={product.productId}
            product={product}
            affiliateUrl={getAffiliateLink(
              product.affiliateUrl,
              product.platform,
              product.productId
            )}
          />
        ))}
      </div>
      <p className="disclosure">
        * 제휴 링크를 통해 구매하시면 소정의 수수료를 받을 수 있습니다.
      </p>
    </section>
  );
}
```

**추적 및 분석**:
```typescript
// 제휴 링크 클릭 추적
export function trackAffiliateClick(
  productId: string,
  platform: string,
  postId: string
) {
  analytics.track('affiliate_click', {
    productId,
    platform,
    postId,
    timestamp: new Date(),
  });
}

// 제휴 수익 분석
export async function getAffiliateStats(period: 'day' | 'week' | 'month') {
  return await db.affiliateClick.groupBy({
    by: ['platform', 'productId'],
    where: {
      createdAt: {
        gte: getPeriodStart(period),
      },
    },
    _count: {
      id: true,
    },
    _sum: {
      revenue: true,
    },
  });
}
```

---

## 핵심 기능 추가

### 1. 사용자 인증 및 프로필 시스템

#### 1.1 인증 시스템
```typescript
// lib/auth.ts
import { NextAuth } from 'next-auth';
import { PrismaAdapter } from '@next-auth/prisma-adapter';

export const authOptions = {
  adapter: PrismaAdapter(sharedDb),
  providers: [
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],
  callbacks: {
    async session({ session, user }) {
      // 플랫폼 간 사용자 정보 싱크
      await syncUserProfile(user.id);
      return session;
    },
  },
};
```

#### 1.2 사용자 프로필 페이지
**기능**:
- 읽은 포스트 목록
- 북마크한 포스트
- 좋아요한 포스트
- 학습 진행도 (online-course 연동)
- 자격증 정보
- 활동 통계

**구현**:
```typescript
// app/profile/[userId]/page.tsx
export default async function ProfilePage({ params }) {
  const user = await getUser(params.userId);
  const stats = await getUserStats(params.userId);
  const bookmarks = await getUserBookmarks(params.userId);
  const courseProgress = await getCourseProgress(params.userId);
  
  return (
    <div>
      <UserProfileHeader user={user} stats={stats} />
      <BookmarksSection bookmarks={bookmarks} />
      <CourseProgressSection progress={courseProgress} />
      <CertificationsSection certifications={user.certifications} />
    </div>
  );
}
```

### 2. 고급 검색 및 필터링

#### 2.1 검색 기능 강화
**현재**: 클라이언트 사이드 기본 검색
**개선**: 서버 사이드 고급 검색

**기능**:
- 풀텍스트 검색 (PostgreSQL Full-Text Search 또는 Algolia)
- 카테고리별 필터링
- 태그별 필터링
- 날짜 범위 필터링
- 자격증별 필터링
- 인기순/최신순 정렬

**구현**:
```typescript
// app/api/search/route.ts
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('q');
  const category = searchParams.get('category');
  const tags = searchParams.get('tags')?.split(',');
  const sort = searchParams.get('sort') || 'recent';
  
  const results = await searchPosts({
    query,
    category,
    tags,
    sort,
  });
  
  return Response.json(results);
}
```

#### 2.2 AI 기반 검색 (선택사항)
- DeepSeek API를 활용한 의미 기반 검색
- 자연어 질문 처리 ("AWS 보안 관련 최신 포스트")

### 3. 통계 및 분석 강화

#### 3.1 포스트 통계
**추적 항목**:
- 조회수 (페이지뷰)
- 독특한 방문자 수
- 평균 읽기 시간
- 이탈률
- 소셜 공유 횟수
- 댓글 수
- 좋아요 수

**구현**:
```typescript
// app/api/posts/[slug]/stats/route.ts
export async function POST(request: Request, { params }) {
  const { event, userId } = await request.json();
  
  await trackPostEvent({
    postSlug: params.slug,
    event, // 'view', 'like', 'share', 'comment'
    userId,
    timestamp: new Date(),
  });
  
  return Response.json({ success: true });
}
```

#### 3.2 대시보드
**작성자 대시보드**:
- 포스트별 상세 통계
- 인기 포스트 분석
- 카테고리별 성과
- 트래픽 소스 분석
- 사용자 참여도 분석

### 4. 소셜 기능 강화

#### 4.1 좋아요 시스템
```typescript
// app/api/posts/[slug]/like/route.ts
export async function POST(request: Request, { params }) {
  const session = await getServerSession();
  if (!session) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  
  await toggleLike({
    postSlug: params.slug,
    userId: session.user.id,
  });
  
  return Response.json({ success: true });
}
```

#### 4.2 북마크 시스템
- 사용자가 포스트를 북마크
- 북마크한 포스트 목록 페이지
- 북마크 카테고리 관리

#### 4.3 팔로우 시스템
- 작성자 팔로우
- 팔로우한 작성자의 새 포스트 알림

### 5. 외부 플랫폼 연동

#### 5.1 GitHub 연동
**기능**:
- GitHub 프로필 표시
- GitHub 저장소 연결
- 코드 스니펫 자동 임베드
- GitHub Stars 표시

**구현**:
```typescript
// lib/github.ts
export async function getGitHubProfile(username: string) {
  const response = await fetch(`https://api.github.com/users/${username}`, {
    headers: {
      'Authorization': `token ${process.env.GITHUB_TOKEN}`,
    },
  });
  
  return response.json();
}

export async function getGitHubRepos(username: string) {
  const response = await fetch(`https://api.github.com/users/${username}/repos`, {
    headers: {
      'Authorization': `token ${process.env.GITHUB_TOKEN}`,
    },
  });
  
  return response.json();
}
```

#### 5.2 LinkedIn 연동
**기능**:
- LinkedIn 프로필 표시
- 자격증 자동 인증 (LinkedIn Credentials API)
- 경력 정보 표시

#### 5.3 RSS 피드 강화
- 카테고리별 RSS 피드
- 자격증별 RSS 피드
- 사용자 맞춤형 RSS 피드

### 6. 콘텐츠 개선 기능

#### 6.1 읽기 시간 계산
```typescript
// lib/reading-time.ts
export function calculateReadingTime(content: string): number {
  const wordsPerMinute = 200;
  const words = content.split(/\s+/).length;
  return Math.ceil(words / wordsPerMinute);
}
```

#### 6.2 목차 (TOC) 자동 생성
- 현재: 수동 TOC
- 개선: 자동 TOC 생성 및 스크롤 하이라이트

#### 6.3 코드 스니펫 개선
- 구문 강조 개선
- 코드 복사 버튼
- 실행 가능한 코드 스니펫 (CodeSandbox 연동)

#### 6.4 이미지 최적화
- WebP 자동 변환
- Lazy loading
- 반응형 이미지
- 이미지 갤러리

### 7. 댓글 시스템 개선

#### 7.1 현재: Giscus (GitHub Discussions)
**유지하되 추가 기능**:
- 댓글 좋아요
- 댓글 답글 스레드
- 댓글 알림
- 댓글 통계

#### 7.2 대안: 자체 댓글 시스템 (선택사항)
- 데이터베이스 기반 댓글
- 실시간 댓글 업데이트
- 스팸 필터링

---

## 사용자 경험 개선

### 1. 개인화 기능

#### 1.1 맞춤형 홈페이지
- 관심 카테고리 기반 포스트 추천
- 읽은 포스트 제외
- 선호하는 작성자 우선 표시

#### 1.2 다크 모드
- 시스템 설정 감지
- 수동 토글
- 설정 저장 (로컬 스토리지 또는 사용자 프로필)

#### 1.3 읽기 모드
- 깔끔한 읽기 전용 뷰
- 폰트 크기 조절
- 줄 간격 조절

### 2. 네비게이션 개선

#### 2.1 크로스 플랫폼 네비게이션
```html
<!-- 헤더에 플랫폼 전환 메뉴 추가 -->
<nav class="platform-nav">
  <a href="https://tech.2twodragon.com" class="active">Tech Blog</a>
  <a href="https://edu.2twodragon.com">Online Course</a>
</nav>
```

#### 2.2 브레드크럼 네비게이션
- 현재 위치 표시
- 빠른 이동

#### 2.3 관련 포스트 추천
- AI 기반 관련 포스트 추천
- 카테고리별 관련 포스트
- 태그 기반 관련 포스트

### 3. 모바일 경험 개선

#### 3.1 반응형 디자인 강화
- 모바일 터치 최적화
- 스와이프 제스처
- 모바일 메뉴 개선

#### 3.2 PWA (Progressive Web App)
- 오프라인 읽기
- 홈 화면 추가
- 푸시 알림 (새 포스트 알림)

---

## 수익화 전략

### 1. 프리미엄 콘텐츠

#### 1.1 프리미엄 포스트
**모델**:
- 기본 포스트: 무료 (현재와 동일)
- 프리미엄 포스트: 구독자 전용 또는 일회성 결제

**구현**:
```typescript
// app/posts/[slug]/page.tsx
export default async function PostPage({ params }) {
  const post = await getPost(params.slug);
  const session = await getServerSession();
  
  const isPremium = post.premium;
  const hasAccess = session?.user?.subscription?.status === 'active';
  
  if (isPremium && !hasAccess) {
    return <PremiumPostLocked post={post} />;
  }
  
  return <PostContent post={post} />;
}
```

#### 1.2 프리미엄 기능
- 고급 검색
- PDF 다운로드
- 오프라인 읽기
- 광고 제거
- 우선 고객 지원

### 2. 제휴 마케팅 (전자제품/IT 제품 중심)

#### 2.1 제품 추천 전략

**카테고리별 추천 제품**:

1. **하드웨어 제품**
   - 서버/워크스테이션: Dell PowerEdge, HP ProLiant, Lenovo ThinkServer
   - NAS/스토리지: Synology, QNAP
   - 네트워크 장비: Ubiquiti, TP-Link, Netgear
   - 모니터: Dell UltraSharp, LG UltraFine
   - 키보드/마우스: 기계식 키보드, 로지텍 마우스

2. **소프트웨어/도구**
   - IDE: JetBrains (IntelliJ, PyCharm, WebStorm)
   - 모니터링: Datadog, New Relic, Grafana Cloud
   - 보안 도구: Snyk, SonarQube, Checkmarx
   - 클라우드 관리: Terraform Cloud, Ansible Tower

3. **클라우드 서비스**
   - AWS: 공식 제휴 프로그램
   - Cloudflare: CDN 및 보안 서비스
   - Vercel: 호스팅 서비스
   - GitHub: 코드 저장소 및 협업 도구

4. **교육 플랫폼**
   - Udemy: 온라인 강의
   - Pluralsight: 기술 교육
   - A Cloud Guru: 클라우드 교육

#### 2.2 제휴 링크 관리 시스템

```typescript
// lib/affiliate.ts
export interface AffiliatePlatform {
  amazon: 'amazon';
  coupang: 'coupang';
  naver: 'naver';
  aws: 'aws';
  jetbrains: 'jetbrains';
  datadog: 'datadog';
  cloudflare: 'cloudflare';
  direct: 'direct';
}

export function getAffiliateLink(
  url: string,
  platform: keyof AffiliatePlatform,
  productId?: string
): string {
  const affiliateIds = {
    amazon: process.env.AMAZON_ASSOCIATE_ID,
    coupang: process.env.COUPANG_PARTNER_ID,
    naver: process.env.NAVER_PARTNER_ID,
    aws: process.env.AWS_AFFILIATE_ID,
    jetbrains: process.env.JETBRAINS_AFFILIATE_ID,
    datadog: process.env.DATADOG_AFFILIATE_ID,
    cloudflare: process.env.CLOUDFLARE_AFFILIATE_ID,
    udemy: process.env.UDEMY_AFFILIATE_ID,
  };
  
  return addAffiliateParams(url, affiliateIds[platform], productId);
}

// 제품 추천 자동 매칭
export async function matchProductsToPost(postId: string) {
  const post = await getPost(postId);
  const keywords = extractKeywords(post.content);
  
  // 키워드 기반 제품 매칭
  const products = await db.product.findMany({
    where: {
      OR: [
        { tags: { hasSome: keywords } },
        { category: post.category },
        { relatedCategories: { has: post.category } },
      ],
    },
    orderBy: { relevanceScore: 'desc' },
    take: 5,
  });
  
  return products;
}
```

#### 2.3 제품 추천 UI 컴포넌트

**포스트 내 제품 추천 섹션**:
- 포스트 하단에 "추천 제품" 섹션 자동 표시
- 카테고리별 제품 그룹화
- 가격 비교 및 스펙 정보
- 사용자 리뷰 연동 (아마존, 쿠팡)

**제품 비교 페이지**:
- 유사 제품 비교 기능
- 가격 히스토리 추적
- 할인 정보 알림

#### 2.4 제휴 수익 추적

```typescript
// 제휴 클릭 및 수익 추적
export async function trackAffiliateClick(
  productId: string,
  platform: string,
  postId: string,
  userId?: string
) {
  await db.affiliateClick.create({
    data: {
      productId,
      platform,
      postId,
      userId,
      timestamp: new Date(),
    },
  });
  
  // 실시간 분석 업데이트
  await updateAffiliateStats(productId, platform);
}

// 제휴 수익 대시보드
export async function getAffiliateDashboard(period: 'day' | 'week' | 'month') {
  const stats = await db.affiliateClick.groupBy({
    by: ['platform', 'productId'],
    where: {
      createdAt: { gte: getPeriodStart(period) },
    },
    _count: { id: true },
    _sum: { estimatedRevenue: true },
  });
  
  return {
    totalClicks: stats.reduce((sum, s) => sum + s._count.id, 0),
    estimatedRevenue: stats.reduce((sum, s) => sum + (s._sum.estimatedRevenue || 0), 0),
    topProducts: stats.sort((a, b) => b._count.id - a._count.id).slice(0, 10),
    platformBreakdown: stats.reduce((acc, s) => {
      acc[s.platform] = (acc[s.platform] || 0) + s._count.id;
      return acc;
    }, {} as Record<string, number>),
  };
}
```

### 3. 스폰서 콘텐츠

#### 3.1 스폰서 포스트
- 명확한 스폰서 표시
- 스폰서 포스트 필터링 옵션

#### 3.2 배너 광고
- Google AdSense (현재)
- 직접 광고 계약
- 네이티브 광고

### 4. 구독 모델

#### 4.1 무료 티어
- 기본 포스트 읽기
- 제한된 검색
- 기본 통계

#### 4.2 Pro 구독 ($9/월 또는 $90/년)
- 모든 프리미엄 포스트
- 고급 검색
- PDF 다운로드
- 광고 제거
- 우선 고객 지원

#### 4.3 통합 구독 (online-course와 연동)
- tech-blog Pro + online-course Pro: $29/월 (개별 $38/월 대비 할인)
- 플랫폼 간 할인 혜택

---

## 기술 구현 계획

### Phase 1: 기반 구조 구축 (1-2개월)

#### 1.1 Next.js API 레이어 추가
```bash
# 프로젝트 구조
tech-blog/
├── _site/              # Jekyll 빌드 결과물
├── app/                # Next.js App Router
│   ├── api/            # API Routes
│   │   ├── auth/       # 인증 API
│   │   ├── posts/      # 포스트 API
│   │   ├── sync/       # 싱크 API
│   │   └── stats/      # 통계 API
│   ├── profile/        # 프로필 페이지
│   └── dashboard/       # 대시보드
├── lib/                # 공유 라이브러리
│   ├── auth.ts
│   ├── sync-client.ts
│   ├── db.ts
│   └── github.ts
└── _config.yml         # Jekyll 설정 (유지)
```

#### 1.2 데이터베이스 스키마 설정
```prisma
// prisma/schema.prisma
model TechBlogProfile {
  id            String   @id @default(cuid())
  userId        String   @unique
  user          User     @relation(fields: [userId], references: [id])
  
  bio           String?
  githubUrl     String?
  linkedinUrl   String?
  websiteUrl    String?
  
  posts         Post[]
  bookmarks     Bookmark[]
  likes         Like[]
  affiliateClicks AffiliateClick[]
  
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
}

model Post {
  id            String   @id @default(cuid())
  slug          String   @unique
  title         String
  content       String   @db.Text
  excerpt       String?
  
  authorId      String
  author        TechBlogProfile @relation(fields: [authorId], references: [id])
  
  category      String?
  tags          String[]
  published     Boolean  @default(false)
  publishedAt   DateTime?
  premium       Boolean  @default(false)
  
  views         Int      @default(0)
  likes         Int      @default(0)
  comments      Int      @default(0)
  
  // 싱크 정보
  syncId        String?  @unique
  crossPlatformLinks CrossPlatformContent[]
  
  // 통계
  stats         PostStats?
  
  // 제품 추천
  productRecommendations ProductRecommendation[]
  affiliateClicks        AffiliateClick[]
  
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  
  @@index([authorId])
  @@index([slug])
  @@index([published, publishedAt])
  @@index([category])
}

model PostStats {
  id            String   @id @default(cuid())
  postId        String   @unique
  post          Post     @relation(fields: [postId], references: [id])
  
  views         Int      @default(0)
  uniqueViews   Int      @default(0)
  avgReadTime   Int?     // 초 단위
  bounceRate    Float?
  shares        Int      @default(0)
  
  updatedAt     DateTime @updatedAt
}

model Bookmark {
  id            String   @id @default(cuid())
  userId        String
  user          TechBlogProfile @relation(fields: [userId], references: [id])
  postId        String
  post          Post     @relation(fields: [postId], references: [id])
  
  category      String?  // 사용자 정의 카테고리
  notes         String?  @db.Text
  
  createdAt     DateTime @default(now())
  
  @@unique([userId, postId])
  @@index([userId])
}

model Like {
  id            String   @id @default(cuid())
  userId        String
  user          TechBlogProfile @relation(fields: [userId], references: [id])
  postId        String
  post          Post     @relation(fields: [postId], references: [id])
  
  createdAt     DateTime @default(now())
  
  @@unique([userId, postId])
  @@index([userId])
}

model Product {
  id                String   @id @default(cuid())
  name              String
  description       String?   @db.Text
  category          String   // 'hardware' | 'software' | 'cloud' | 'tool' | 'education'
  subcategory       String?   // 'server' | 'nas' | 'monitor' | 'keyboard' 등
  
  // 제품 정보
  price             Float?
  currency          String   @default("KRW")
  imageUrl          String?
  brand             String?
  
  // 제휴 정보
  affiliateUrl      String
  platform          String   // 'amazon' | 'coupang' | 'naver' | 'aws' | 'direct'
  affiliateId       String?
  
  // 매칭 정보
  tags              String[]
  relatedCategories String[] // 관련 블로그 카테고리
  keywords          String[] // 검색 키워드
  
  // 통계
  clickCount        Int      @default(0)
  estimatedRevenue  Float    @default(0)
  relevanceScore    Float    @default(0) // 포스트와의 관련도
  
  // 연결
  recommendations   ProductRecommendation[]
  clicks            AffiliateClick[]
  
  active            Boolean  @default(true)
  
  createdAt         DateTime @default(now())
  updatedAt         DateTime @updatedAt
  
  @@index([category])
  @@index([platform])
  @@index([active, relevanceScore])
}

model ProductRecommendation {
  id            String   @id @default(cuid())
  postId        String
  post          Post     @relation(fields: [postId], references: [id])
  productId     String
  product       Product  @relation(fields: [productId], references: [id])
  
  position      Int      // 포스트 내 표시 순서
  section       String?  // 'top' | 'middle' | 'bottom' | 'sidebar'
  relevanceScore Float    // 이 포스트와의 관련도
  
  createdAt     DateTime @default(now())
  
  @@unique([postId, productId])
  @@index([postId])
  @@index([productId])
}

model AffiliateClick {
  id            String   @id @default(cuid())
  productId     String
  product       Product  @relation(fields: [productId], references: [id])
  postId        String?
  post          Post?    @relation(fields: [postId], references: [id])
  userId        String?
  user          TechBlogProfile? @relation(fields: [userId], references: [id])
  
  platform      String
  affiliateId   String?
  
  // 수익 정보
  estimatedRevenue Float?  // 예상 수익
  
  // 추적 정보
  userAgent     String?
  ipAddress     String?
  referrer      String?
  
  timestamp     DateTime @default(now())
  
  @@index([productId])
  @@index([postId])
  @@index([userId])
  @@index([platform])
  @@index([timestamp])
}
```

#### 1.3 인증 시스템 구축
- NextAuth.js 설정
- GitHub OAuth 연동
- Google OAuth 연동
- 세션 관리

### Phase 2: 핵심 기능 구현 (2-3개월)

#### 2.1 사용자 프로필 시스템
- 프로필 페이지
- 북마크 기능
- 좋아요 기능
- 활동 통계

#### 2.2 검색 기능 강화
- 서버 사이드 검색
- 필터링 기능
- 정렬 기능

#### 2.3 통계 시스템
- 조회수 추적
- 이벤트 추적
- 대시보드

#### 2.4 플랫폼 간 싱크
- sync-client 라이브러리 통합
- online-course와 콘텐츠 연결
- 크로스 플랫폼 네비게이션

### Phase 3: 고급 기능 및 최적화 (1-2개월)

#### 3.1 외부 플랫폼 연동
- GitHub API 연동
- LinkedIn API 연동
- RSS 피드 강화

#### 3.2 개인화 기능
- 맞춤형 홈페이지
- 추천 시스템
- 다크 모드

#### 3.3 성능 최적화
- 이미지 최적화
- 캐싱 전략
- CDN 통합

### Phase 4: 수익화 기능 (1개월)

#### 4.1 프리미엄 콘텐츠
- 구독 시스템
- 결제 연동 (Stripe)
- 접근 제어

#### 4.2 제품 추천 시스템
- 제품 데이터베이스 구축
- 포스트-제품 자동 매칭
- 제품 추천 UI 컴포넌트
- 제휴 링크 관리
- 클릭 추적 시스템
- 수익 분석 대시보드

---

## 마이그레이션 전략

### 1. 점진적 마이그레이션

#### Step 1: Next.js 프로젝트 초기화
```bash
# Next.js 프로젝트 생성
npx create-next-app@latest tech-blog-nextjs --typescript --tailwind --app

# 기존 Jekyll 빌드 결과물을 public/에 복사
cp -r _site/* public/
```

#### Step 2: API 레이어 추가
- 인증 API
- 포스트 API
- 통계 API

#### Step 3: 동적 페이지 추가
- 프로필 페이지
- 대시보드
- 검색 페이지

#### Step 4: Jekyll 콘텐츠 마이그레이션
- Markdown 파일을 데이터베이스로 마이그레이션
- 또는 Jekyll 빌드 결과물을 그대로 사용

### 2. 데이터 마이그레이션

#### 2.1 포스트 마이그레이션
```typescript
// scripts/migrate-posts.ts
import { readdir, readFile } from 'fs/promises';
import { parseFrontMatter } from 'gray-matter';
import { db } from '../lib/db';

async function migratePosts() {
  const postsDir = '_posts';
  const files = await readdir(postsDir);
  
  for (const file of files) {
    const content = await readFile(`${postsDir}/${file}`, 'utf-8');
    const { data, content: body } = parseFrontMatter(content);
    
    await db.post.create({
      data: {
        slug: data.slug || file.replace('.md', ''),
        title: data.title,
        content: body,
        excerpt: data.excerpt,
        category: data.category,
        tags: data.tags || [],
        published: data.published !== false,
        publishedAt: data.date ? new Date(data.date) : new Date(),
      },
    });
  }
}
```

### 3. SEO 유지 전략

#### 3.1 URL 구조 유지
- 기존 URL 구조 유지
- 301 리다이렉트 설정 (필요 시)

#### 3.2 메타데이터 유지
- Open Graph 태그 유지
- 구조화된 데이터 유지

#### 3.3 사이트맵 업데이트
- 동적 사이트맵 생성
- 검색 엔진 제출

---

## 로드맵

### Q1 2026: 기반 구조 구축
- [ ] Next.js API 레이어 추가
- [ ] 데이터베이스 스키마 설정
- [ ] 인증 시스템 구축
- [ ] 기본 프로필 기능

### Q2 2026: 핵심 기능 구현
- [ ] 검색 기능 강화
- [ ] 통계 시스템
- [ ] 북마크/좋아요 기능
- [ ] 플랫폼 간 싱크

### Q3 2026: 고급 기능 및 최적화
- [ ] 외부 플랫폼 연동
- [ ] 개인화 기능
- [ ] 성능 최적화
- [ ] 모바일 경험 개선

### Q4 2026: 수익화 및 확장
- [ ] 프리미엄 콘텐츠
- [ ] 구독 시스템
- [ ] 제품 추천 시스템 구축
- [ ] 제휴 마케팅 (전자제품/IT 제품)
- [ ] 제휴 수익 추적 및 분석
- [ ] 마케팅 및 홍보

---

## 예상 비용

### Phase 1-2 (초기 3-5개월)
```
Vercel Hobby:           $0/월
Vercel Postgres Hobby:  $0/월 (초기)
Upstash Redis Free:     $0/월
Sentry Free:            $0/월
──────────────────────────────
총 비용:                $0-20/월
```

### Phase 3-4 (성장기)
```
Vercel Pro:             $20/월
Vercel Postgres Pro:    $20/월
Upstash Redis Pro:      $10/월
Stripe (수수료):        거래의 2.9% + $0.30
Sentry Team:            $26/월 (선택)
──────────────────────────────
총 비용:                $76+/월
```

---

## 예상 수익 (제품 제휴 마케팅)

### 제휴 수익 모델

#### 1. 제휴 프로그램별 수수료율
- **아마존 제휴**: 1-10% (카테고리별 상이)
  - 전자제품: 4-8%
  - IT 제품: 1-4%
  - 소프트웨어: 1-2%
- **쿠팡 파트너스**: 0.5-5% (카테고리별 상이)
- **네이버 제휴**: 1-3%
- **AWS 제휴**: 5-10% (서비스별 상이)
- **JetBrains**: 20-30% (구독 첫 해)
- **Datadog/Cloudflare**: 직접 협상 (보통 10-20%)

#### 2. 예상 수익 시나리오

**Phase 1 (초기 3-6개월)**:
```
월간 페이지뷰: 5,000-10,000
제품 추천 노출: 2,000-4,000회
제품 링크 클릭: 100-200회 (CTR: 5%)
전환율: 5-10%
평균 주문 금액: 100,000원
평균 수수료율: 3%

월간 제휴 수익 = 150회 × 100,000원 × 3% = 450,000원/월
연간 예상: 5,400,000원
```

**Phase 2 (6-12개월)**:
```
월간 페이지뷰: 20,000-50,000
제품 추천 노출: 10,000-25,000회
제품 링크 클릭: 500-1,250회 (CTR: 5%)
전환율: 8-12%
평균 주문 금액: 150,000원
평균 수수료율: 4%

월간 제휴 수익 = 875회 × 150,000원 × 4% = 5,250,000원/월
연간 예상: 63,000,000원
```

**Phase 3 (12-24개월)**:
```
월간 페이지뷰: 50,000-100,000
제품 추천 노출: 25,000-50,000회
제품 링크 클릭: 1,250-2,500회 (CTR: 5%)
전환율: 10-15%
평균 주문 금액: 200,000원
평균 수수료율: 5%

월간 제휴 수익 = 1,875회 × 200,000원 × 5% = 18,750,000원/월
연간 예상: 225,000,000원
```

#### 3. 제품 카테고리별 수익 기여도 예측

**하드웨어 제품 (40%)**:
- 서버/워크스테이션: 높은 수수료율 (5-8%), 낮은 전환율
- NAS/스토리지: 중간 수수료율 (3-5%), 중간 전환율
- 모니터/주변기기: 낮은 수수료율 (1-3%), 높은 전환율

**소프트웨어/도구 (30%)**:
- JetBrains: 높은 수수료율 (20-30%), 중간 전환율
- 모니터링 도구: 중간 수수료율 (10-20%), 낮은 전환율
- 보안 도구: 중간 수수료율 (5-15%), 낮은 전환율

**클라우드 서비스 (20%)**:
- AWS: 높은 수수료율 (5-10%), 낮은 전환율 (B2B 특성)
- Cloudflare: 중간 수수료율 (10-15%), 중간 전환율

**교육 플랫폼 (10%)**:
- Udemy: 중간 수수료율 (5-10%), 높은 전환율
- Pluralsight: 높은 수수료율 (10-20%), 중간 전환율

#### 4. 수익 최적화 전략

**콘텐츠 최적화**:
- 인기 포스트에 고수익 제품 우선 배치
- 제품 비교 포스트 작성 (SEO 최적화)
- 사용자 리뷰 및 추천 강화

**제품 매칭 개선**:
- AI 기반 관련도 점수 향상
- 사용자 피드백 기반 매칭 개선
- 계절성 제품 추천 (블랙프라이데이, 연말 등)

**전환율 향상**:
- 제품 정보 상세화 (스펙, 가격, 리뷰)
- 할인 정보 실시간 표시
- 구매 전환 유도 메시지 최적화

---

## 성공 지표 (KPI)

### 사용자 참여
- 월간 활성 사용자 (MAU)
- 평균 세션 시간
- 페이지뷰
- 이탈률

### 콘텐츠 성과
- 포스트별 조회수
- 평균 읽기 시간
- 공유 횟수
- 댓글 수

### 수익
- 구독자 수
- 월간 반복 수익 (MRR)
- 제휴 수익 (전자제품/IT 제품)
  - 제품별 클릭률 (CTR)
  - 전환율 (Conversion Rate)
  - 평균 주문 금액 (AOV)
  - 제휴 수수료율
- 광고 수익 (Google AdSense)

### 플랫폼 간 연동
- 크로스 플랫폼 전환율
- online-course로의 전환율
- 싱크 성공률

---

## 리스크 및 대응 방안

### 기술적 리스크
1. **마이그레이션 중 다운타임**
   - 대응: 점진적 마이그레이션, 카나리 배포

2. **SEO 영향**
   - 대응: URL 구조 유지, 301 리다이렉트

3. **성능 저하**
   - 대응: 캐싱 전략, CDN 활용

### 비즈니스 리스크
1. **사용자 이탈**
   - 대응: 점진적 변경, 사용자 피드백 수집

2. **비용 증가**
   - 대응: 사용량 모니터링, 비용 알림 설정

3. **경쟁 플랫폼**
   - 대응: 차별화된 기능, 고품질 콘텐츠

---

## 다음 단계

1. **기획 검토**: 이 기획서 검토 및 피드백 수집
2. **프로토타입 개발**: Next.js API 레이어 프로토타입
3. **POC (Proof of Concept)**: 핵심 기능 프로토타입
4. **사용자 테스트**: 베타 테스터 모집 및 피드백 수집
5. **단계적 롤아웃**: 점진적 기능 출시

---

**작성일**: 2026-01-22  
**버전**: 1.0  
**작성자**: AI Assistant (DevSecOps Engineer)  
**상태**: 초안
