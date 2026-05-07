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

export const config = {
  /**
   * 정적 에셋(css, js, images, fonts) 및 Vercel 내부 경로는
   * middleware 실행에서 제외하여 불필요한 오버헤드 방지.
   */
  matcher: '/((?!assets|_next/static|_next/image|favicon\\.ico|api).*)',
};

export default function middleware(request) {
  const ua = request.headers.get('user-agent') || '';

  if (!SEO_BOT_RE.test(ua)) {
    // 일반 사용자: passthrough (헤더 변경 없음)
    return;
  }

  // 봇 감지: 캐시 힌트 + 식별 헤더 추가
  // NextResponse 없이 Response 헤더를 조작하는 Vercel Edge 방식.
  // undefined를 반환하면 Vercel이 원래 요청을 그대로 처리하므로
  // 헤더 오버라이드는 vercel.json의 has matcher 룰에 위임한다.
  //
  // 참고: Edge Middleware에서 헤더를 추가하려면 Response를 직접 반환해야 하지만
  // static 파일 서빙에서 body를 재구성하는 것은 불가능하므로
  // 여기서는 식별 로그용 헤더만 request에 주입하는 방식을 사용한다.
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-seo-bot-ua', ua.slice(0, 100));

  return new Request(request.url, {
    method: request.method,
    headers: requestHeaders,
    body: request.body,
    redirect: request.redirect,
  });
}
