// Service Worker for Offline Support and Caching
// 버전 업데이트 시 CACHE_NAME 변경하여 캐시 무효화
const CACHE_NAME = 'tech-blog-v2';
const STATIC_CACHE = 'tech-blog-static-v2';
const DYNAMIC_CACHE = 'tech-blog-dynamic-v2';

// 캐시할 정적 리소스
const STATIC_ASSETS = [
  '/',
  '/assets/css/main.css',
  '/assets/js/main.js',
  '/assets/js/chat-widget.js',
  '/assets/js/image-optimizer.js',
  '/assets/images/favicon.png'
];

// 설치: 정적 리소스 캐시
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
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
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // 모든 클라이언트에 즉시 적용
      return self.clients.claim();
    })
  );
});

// 메시지 리스너: 즉시 활성화 요청
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
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

  // 캐시 가능한 리소스만 처리
  event.respondWith(
    fetch(request)
      .then((response) => {
        // GET 요청이고 성공한 경우에만 캐시
        // POST, PUT, DELETE 등은 절대 캐시하지 않음
        if (request.method === 'GET' && response.status === 200) {
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
              cache.put(request, responseClone).catch(() => {
                // 캐시 저장 실패 시 무시
              });
            }).catch(() => {
              // 캐시 열기 실패 시 무시
            });
          }
        }
        return response;
      })
      .catch(() => {
        // 네트워크 실패 시 캐시에서 반환 (GET 요청만)
        if (request.method === 'GET') {
          return caches.match(request).then((cachedResponse) => {
            return cachedResponse || new Response('Offline', { 
              status: 503,
              headers: { 'Content-Type': 'text/plain' }
            });
          });
        }
        // POST 등은 네트워크 오류 그대로 반환 (캐시하지 않음)
        return new Response('Network error', { 
          status: 503,
          headers: { 'Content-Type': 'text/plain' }
        });
      })
  );
});
