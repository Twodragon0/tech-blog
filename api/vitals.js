// Vercel Serverless Function: first-party Web Vitals collector.
//
// Why this exists instead of shipping the metrics through gtag:
// gtag batches dataLayer pushes behind a ~5s timer (measured 5003-5005ms,
// n=4), but vitals are pushed at page hide. Any session that ends by closing
// the tab or following an internal link — which on a non-SPA blog is almost
// all of them — dies before that timer fires and the events are lost.
// Measured 0/3 delivered at a 2s leave-gap, 3/3 at 5s.
// See notes/ga4-web-vitals-delivery-loss.md.
//
// navigator.sendBeacon survives teardown (verified: captured 1/1 at a 0ms
// leave-gap in the same handler where gtag delivered 0/3), so the browser
// beacons here and this function forwards to GA4 via the Measurement
// Protocol. The api_secret stays server-side; being first-party also means
// ad blockers do not strip the request, removing a second source of bias.
//
// 보안: POST 전용, 동일 출처 검증, 입력 검증, Rate Limiting, 본문 크기 제한.
// api_secret은 환경변수에서만 읽으며 응답/로그에 절대 포함하지 않는다.
//
// 사용법 (클라이언트는 assets/js/performance-monitor.js):
//   navigator.sendBeacon('/api/vitals', Blob(JSON))
//   body: { "p": "/posts/…", "m": [{ "n": "LCP", "v": 1234, "r": "good" }] }
//
// 응답은 항상 204 (fire-and-forget). 실패해도 독자에게 영향이 없어야 하고,
// 내부 상태를 노출하지 않는다.

import { checkRateLimit } from './lib/ratelimit.js';
import { safeLog } from './lib/log-sanitizer.js';

const MP_ENDPOINT = 'https://www.google-analytics.com/mp/collect';

const CONFIG = {
  MEASUREMENT_ID: process.env.GA4_MEASUREMENT_ID || 'G-B29150XJ73',
  MAX_BODY_BYTES: 2048,
  MAX_METRICS: 3,
  MAX_PATH_LENGTH: 200,
  MAX_CAUSE_LENGTH: 100,
  RATE_LIMIT_TIER: 'anonymous',
  SITE_ORIGIN: process.env.SITE_ORIGIN || 'https://tech.2twodragon.com',
};

const METRIC_NAMES = new Set(['LCP', 'INP', 'CLS']);
const RATINGS = new Set(['good', 'needs-improvement', 'poor']);

// LCP/INP are milliseconds, CLS is an unitless 0..1-ish score. One generous
// ceiling per unit keeps obviously-forged values out without second-guessing
// a genuinely terrible page.
const VALUE_MAX = { LCP: 600000, INP: 600000, CLS: 100 };

/** Strips control characters; keeps the value printable and log-safe. */
function clean(value, maxLength) {
  // eslint-disable-next-line no-control-regex
  return String(value).replace(/[\x00-\x1f\x7f]/g, '').slice(0, maxLength);
}

/**
 * GA4 stores the client id in the `_ga` cookie as `GA1.<depth>.<a>.<b>`,
 * where the client id is `<a>.<b>`.
 */
export function clientIdFromCookies(cookieHeader) {
  const match = /(?:^|;\s*)_ga=([^;]+)/.exec(cookieHeader || '');
  if (!match) return null;
  const parts = decodeURIComponent(match[1]).split('.');
  if (parts.length < 4) return null;
  const id = `${parts[2]}.${parts[3]}`;
  return /^\d+\.\d+$/.test(id) ? id : null;
}

/**
 * Session id lives in `_ga_<CONTAINER>`, which has two formats in the wild:
 *   GS2.1.s1745000000$o5$g1$t1745000100$j60   -> after the `s` marker
 *   GS1.1.1745000000.5.1.1745000100.60.0.0    -> third dot-segment
 * Without it the event lands in its own session and page-level joins break.
 */
export function sessionIdFromCookies(cookieHeader, measurementId) {
  // Interpolated into a RegExp below, so keep it to the alphanumerics a real
  // container id uses rather than trusting the configured value.
  const container = String(measurementId || '').replace(/^G-/, '').replace(/[^A-Za-z0-9]/g, '');
  if (!container) return null;
  const re = new RegExp(`(?:^|;\\s*)_ga_${container}=([^;]+)`);
  const match = re.exec(cookieHeader || '');
  if (!match) return null;
  const raw = decodeURIComponent(match[1]);

  const gs2 = /(?:^|[.$])s(\d{6,})/.exec(raw);
  if (gs2) return gs2[1];

  const parts = raw.split('.');
  if (parts.length >= 3 && /^\d{6,}$/.test(parts[2])) return parts[2];
  return null;
}

/**
 * Rejects anything that is not a well-formed vitals report. Returns the
 * normalized metric list, or null when the payload should be dropped.
 */
export function validatePayload(body) {
  if (!body || typeof body !== 'object' || !Array.isArray(body.m)) return null;
  if (body.m.length === 0 || body.m.length > CONFIG.MAX_METRICS) return null;

  const seen = new Set();
  const metrics = [];
  for (const entry of body.m) {
    if (!entry || typeof entry !== 'object') return null;
    if (!METRIC_NAMES.has(entry.n)) return null;
    // One reading per metric per page — a repeat means a forged or buggy send.
    if (seen.has(entry.n)) return null;
    seen.add(entry.n);
    if (!RATINGS.has(entry.r)) return null;
    if (typeof entry.v !== 'number' || !Number.isFinite(entry.v)) return null;
    if (entry.v < 0 || entry.v > VALUE_MAX[entry.n]) return null;

    const metric = { metric_name: entry.n, metric_value: entry.v, metric_rating: entry.r };
    if (entry.c != null) metric.metric_cause = clean(entry.c, CONFIG.MAX_CAUSE_LENGTH);
    metrics.push(metric);
  }

  let path = '/';
  if (typeof body.p === 'string' && body.p.startsWith('/')) {
    path = clean(body.p, CONFIG.MAX_PATH_LENGTH);
  }
  return { metrics, path };
}

/**
 * Only our own pages may post here. Missing Origin AND Referer is rejected.
 *
 * This is NOT a defence against a direct attacker — curl can set any Origin.
 * What it buys is that a third-party site cannot make its visitors' browsers
 * post here. Forged reports are bounded by the validation below and cost
 * nothing but analytics noise, so that is the right level of protection.
 *
 * The client only beacons from the canonical host (performance-monitor.js
 * gates on it), so preview hosts are deliberately NOT allowed — permitting
 * *.vercel.app would admit every project on the platform, not just this one.
 */
function isSameOrigin(req) {
  const origin = req.headers?.origin;
  const referer = req.headers?.referer;
  const candidate = origin || referer;
  if (!candidate) return false;
  try {
    return new URL(candidate).host === new URL(CONFIG.SITE_ORIGIN).host;
  } catch {
    return false;
  }
}

function readBody(req) {
  // Content-Length covers both branches below; the string check alone would
  // miss an oversized body that the platform already parsed into an object.
  const declared = Number(req.headers?.['content-length']);
  if (Number.isFinite(declared) && declared > CONFIG.MAX_BODY_BYTES) return null;

  // Vercel parses application/json into req.body; sendBeacon Blobs arrive
  // that way too. Fall back to the raw string for other runtimes.
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') {
    if (Buffer.byteLength(req.body, 'utf8') > CONFIG.MAX_BODY_BYTES) return null;
    try {
      return JSON.parse(req.body);
    } catch {
      return null;
    }
  }
  return null;
}

function clientIp(req) {
  // x-real-ip is set by Vercel and cannot be spoofed; the first x-forwarded-for
  // entry is client-supplied and can be. Preferring the former is what keeps
  // the rate limiter from being trivially bypassed with a rotating header —
  // same ordering and reasoning as api/chat.js:245-248.
  const realIp = req.headers?.['x-real-ip'];
  if (typeof realIp === 'string' && realIp.length > 0) return realIp;
  const forwarded = req.headers?.['x-forwarded-for'];
  if (typeof forwarded === 'string' && forwarded.length > 0) {
    return forwarded.split(',')[0].trim();
  }
  return req.socket?.remoteAddress || 'unknown';
}

export default async function handler(req, res) {
  // Fire-and-forget: the reader is already gone, so every exit is a 204.
  const done = () => res.status(204).end();

  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).end();
  }
  if (!isSameOrigin(req)) return done();

  const apiSecret = process.env.GA4_API_SECRET;
  if (!apiSecret) {
    // Not configured yet — drop silently rather than erroring on every hide.
    safeLog('warn', '[vitals] GA4_API_SECRET is not set; dropping report');
    return done();
  }

  const rate = await checkRateLimit(clientIp(req), CONFIG.RATE_LIMIT_TIER);
  if (!rate.success) return done();

  const payload = validatePayload(readBody(req));
  if (!payload) return done();

  const cookieHeader = req.headers?.cookie || '';
  const clientId = clientIdFromCookies(cookieHeader);
  const sessionId = sessionIdFromCookies(cookieHeader, CONFIG.MEASUREMENT_ID);

  // No `_ga` cookie means GA never ran for this visitor — exactly the
  // never-interacted session this endpoint exists to recover. The Measurement
  // Protocol still requires a client_id, so we synthesize one and tag the
  // event, because a synthetic id counts as a new user and would otherwise
  // inflate user totals with no way to tell which rows are affected.
  const resolvedClientId = clientId || `${Date.now()}.${Math.floor(Math.random() * 1e10)}`;

  const events = payload.metrics.map((metric) => ({
    name: 'web_vitals',
    params: {
      ...metric,
      page_location: `${CONFIG.SITE_ORIGIN}${payload.path}`,
      // Without this GA4 treats the hit as non-engaged and drops it from most
      // standard reports.
      engagement_time_msec: '1',
      cid_source: clientId ? 'ga_cookie' : 'synthetic',
      ...(sessionId ? { session_id: sessionId } : {}),
    },
  }));

  const url =
    `${MP_ENDPOINT}?measurement_id=${encodeURIComponent(CONFIG.MEASUREMENT_ID)}` +
    `&api_secret=${encodeURIComponent(apiSecret)}`;

  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: resolvedClientId, events }),
    });
  } catch (error) {
    // Never surface upstream failures — the response goes nowhere anyway.
    safeLog('error', '[vitals] Measurement Protocol forward failed', {
      message: error?.message,
    });
  }

  return done();
}
