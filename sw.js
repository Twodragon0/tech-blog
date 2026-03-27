// Service Worker for Offline Support and Caching
// Cache version: bump on each deploy or content change
// v21: OG PNG optimization (-7.2MB) + category illustrations (build marker: 20260327)
const STATIC_CACHE = 'tech-blog-static-v21';
const DYNAMIC_CACHE = 'tech-blog-dynamic-v21';

// Dynamic cache settings
const DYNAMIC_CACHE_MAX_ENTRIES = 50;
const DYNAMIC_CACHE_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

// 캐시할 정적 리소스 (CSS는 version param 무시하고 매칭)
const STATIC_ASSETS = [
  '/',
  '/assets/css/main.css',
  '/assets/js/main-core.js',
  '/assets/js/post-page.js',
  '/assets/js/google-translate.js',
  '/assets/js/error-handler.js',
  '/assets/js/toc.js',
  '/assets/js/mermaid-init.js',
  '/assets/js/performance-monitor.js',
  '/assets/js/head-runtime.js',
  '/assets/js/header-runtime.js',
  '/assets/js/footer-runtime.js',
  '/assets/js/console-filter.js',
  '/assets/js/giscus-init.js',
  '/assets/js/sentry-init.js',
  '/assets/js/adsense-init.js',
  '/assets/js/chat-widget-loader.js',
  '/assets/js/subscribe-float.js',
  '/assets/js/support-page.js',
  '/assets/images/favicon.png',
  '/assets/images/news-fallback.svg'
];

// 설치: 정적 리소스 캐시 (개별 캐시로 에러 격리)
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      // 각 리소스를 개별적으로 캐시하여 하나가 실패해도 다른 것들은 계속 캐시
      return Promise.all(
        STATIC_ASSETS.map((url) => {
          return fetch(url, { cache: 'no-store' })
            .then((response) => {
              if (response.ok) {
                return cache.put(url, response);
              }
              // 404 등 실패한 리소스는 무시하고 계속 진행
              return Promise.resolve();
            })
            .catch(() => {
              // 네트워크 에러도 무시하고 계속 진행
              return Promise.resolve();
            });
        })
      );
    }).catch((error) => {
      // 캐시 열기 실패해도 조용히 계속 진행
      return Promise.resolve();
    })
  );
  self.skipWaiting();
});

// 활성화: 오래된 캐시 삭제
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // 현재 버전이 아닌 모든 캐시 삭제
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            return caches.delete(cacheName).catch((error) => {
              // 캐시 삭제 실패 시 로그만 남기고 계속 진행
              console.error('[Service Worker] Cache delete failed:', error);
              return Promise.resolve();
            });
          }
          return Promise.resolve();
        })
      );
    }).then(() => {
      // Remove expired/excess dynamic cache entries
      return cleanupDynamicCache();
    }).then(() => {
      // 모든 클라이언트에 즉시 적용
      return self.clients.claim();
    }).catch((error) => {
      console.error('[Service Worker] Activate failed:', error);
    })
  );
});

// Remove expired and excess entries from dynamic cache
async function cleanupDynamicCache() {
  let cache;
  try {
    cache = await caches.open(DYNAMIC_CACHE);
  } catch (e) {
    return;
  }

  const requests = await cache.keys().catch(() => []);
  const now = Date.now();
  const entries = [];

  for (const request of requests) {
    const response = await cache.match(request).catch(() => null);
    if (!response) continue;

    const dateHeader = response.headers.get('date');
    const cachedAt = dateHeader ? new Date(dateHeader).getTime() : 0;

    if (cachedAt && now - cachedAt > DYNAMIC_CACHE_MAX_AGE_MS) {
      // Expired: remove immediately
      await cache.delete(request).catch(() => {});
    } else {
      entries.push({ request, cachedAt });
    }
  }

  // Enforce max entries limit (remove oldest first)
  if (entries.length > DYNAMIC_CACHE_MAX_ENTRIES) {
    entries.sort((a, b) => a.cachedAt - b.cachedAt);
    const toRemove = entries.slice(0, entries.length - DYNAMIC_CACHE_MAX_ENTRIES);
    for (const { request } of toRemove) {
      await cache.delete(request).catch(() => {});
    }
  }
}

// 메시지 리스너: 즉시 활성화 요청 (클라이언트 출처 검증)
self.addEventListener('message', (event) => {
  if (event.source && event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// 네트워크 우선, 캐시 fallback 전략
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // API 요청은 네트워크만 사용 (캐시하지 않음)
  if (url.pathname.startsWith('/api/')) {
    return; // 네트워크로만 처리
  }

  // POST, PUT, DELETE 등 수정 요청은 캐시하지 않음
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    return; // 네트워크로만 처리
  }

  // 같은 출처만 캐시
  if (url.origin !== location.origin) {
    return;
  }

  // 이미지 요청 시 AVIF/WebP 콘텐츠 협상
  if (url.pathname.match(/\/_og\.png$/)) {
    const accept = request.headers.get('Accept') || '';
    let bestUrl = url.href;
    if (accept.includes('image/avif')) {
      bestUrl = url.href.replace('_og.png', '_og.avif');
    } else if (accept.includes('image/webp')) {
      bestUrl = url.href.replace('_og.png', '_og.webp');
    }
    if (bestUrl !== url.href) {
      event.respondWith(
        fetch(bestUrl).catch(() => fetch(request))
      );
      return;
    }
  }

  // 캐시 가능한 리소스만 처리
  event.respondWith(
    fetch(request)
      .then((response) => {
        // GET 요청이고 성공한 경우에만 캐시
        // POST, PUT, DELETE 등은 절대 캐시하지 않음
        if (request.method === 'GET' && response.status === 200 && response.type === 'basic') {
          // 캐시 가능한 응답인지 확인
          const contentType = response.headers.get('content-type') || '';
          const isCacheable =
            contentType.includes('text/html') ||
            contentType.includes('text/css') ||
            contentType.includes('application/javascript') ||
            contentType.includes('image/') ||
            contentType.includes('font/');

          if (isCacheable) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then((cache) => {
              // 안전하게 캐시 저장 (에러 무시)
              cache.put(request, responseClone).catch((error) => {
                // 캐시 저장 실패 시 로그만 남기고 무시
                if (self.location.hostname === 'localhost' || self.location.hostname === '127.0.0.1') {
                  console.error('[Service Worker] Cache put failed:', error);
                }
              });
            }).catch((error) => {
              // 캐시 열기 실패 시 로그만 남기고 무시
              if (self.location.hostname === 'localhost' || self.location.hostname === '127.0.0.1') {
                console.error('[Service Worker] Cache open failed:', error);
              }
            });
          }
        }
        return response;
      })
      .catch((error) => {
        // 네트워크 실패 시 캐시에서 반환 (GET 요청만)
        if (request.method === 'GET') {
          // CSS는 version query param 무시하고 매칭
          return caches.match(request, { ignoreSearch: url.pathname.endsWith('.css') }).then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // 캐시에도 없으면 오프라인 메시지 반환
            return new Response('Offline', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
          }).catch(() => {
            // 캐시 매칭 실패 시에도 오프라인 메시지 반환
            return new Response('Offline', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
          });
        }
        // POST 등은 네트워크 오류 그대로 반환 (캐시하지 않음)
        return new Response('Network error', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
      })
  );
});
