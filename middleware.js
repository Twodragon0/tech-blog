/**
 * Vercel Edge Middleware — SEO Bot Passthrough (best-effort)
 *
 * 목적: 검색 엔진 봇을 식별하여 캐시 친화적 응답 헤더를 추가.
 *
 * 한계 (IMPORTANT):
 *   Vercel Attack Challenge Mode는 Edge Middleware보다 먼저 실행된다.
 *   따라서 Challenge Mode가 활성화된 상태에서 이 middleware는
 *   차단된 요청에 도달하지 못한다. Challenge Mode를 완전히 우회하려면
 *   Vercel Dashboard > Firewall / Bot Protection 에서 직접 OFF 해야 한다.
 *
 *   이 파일은 Challenge Mode가 비활성화된 상태 또는 캐시 HIT 경로에서만
 *   의미 있는 효과를 낸다.
 *
 * Jekyll 정적 사이트 호환:
 *   next/server 의존성 없이 Web Standard API(Request/Response)만 사용.
 *   Vercel Edge Runtime은 Next.js 없이도 이 형식을 지원한다.
 *
 * @see https://vercel.com/docs/functions/edge-middleware
 */

const SEO_BOT_RE =
  /googlebot|bingbot|yandexbot|baiduspider|duckduckbot|slurp|applebot|facebookexternalhit|twitterbot|linkedinbot|rogerbot|semrushbot|ahrefsbot/i;

// Path filtering happens inside middleware() — Vercel's config.matcher uses
// path-to-regexp which does NOT support negative lookahead `(?!...)`.
// An earlier `matcher: '/((?!assets|...).*)'` triggered
// `Error: Unhandled type: "ColonToken" :` and broke every deploy after
// commit aaad1f9f. With matcher removed, Vercel runs middleware on every
// request; we cheaply early-return for static assets.
const SKIP_PREFIXES = [
  '/assets/',
  '/_next/',
  '/api/',
];

const SKIP_EXACT = new Set([
  '/favicon.ico',
  '/robots.txt',
  '/sitemap.xml',
]);

function shouldSkip(pathname) {
  if (SKIP_EXACT.has(pathname)) return true;
  for (const prefix of SKIP_PREFIXES) {
    if (pathname.startsWith(prefix)) return true;
  }
  return false;
}

export default function middleware(request) {
  const url = new URL(request.url);
  if (shouldSkip(url.pathname)) {
    return;
  }

  const ua = request.headers.get('user-agent') || '';
  if (!SEO_BOT_RE.test(ua)) {
    // 일반 사용자: passthrough (헤더 변경 없음)
    return;
  }

  // 봇 감지: vercel.json의 has matcher 룰이 응답 헤더를 추가한다.
  // Edge Middleware에서 정적 파일 body를 재구성하지 않고 통과시키려면
  // undefined 반환이 가장 안전하다. 이전에는 `new Request(...)` 를
  // 반환했지만 Vercel은 Request 반환을 무시하므로 의미 없는 동작이었다.
  return;
}
