// Regression tests for api/vitals.js — the first-party Web Vitals collector.
//
// This endpoint exists because gtag batches dataLayer pushes behind a ~5s
// timer while vitals are pushed at page hide, so sessions ending in a tab
// close or an internal link lost them entirely (measured 0/3 at a 2s
// leave-gap). See notes/ga4-web-vitals-delivery-loss.md.
//
// It is a public, unauthenticated POST endpoint that forwards to GA4 with a
// server-side api_secret, so the things worth pinning are the ones that keep
// it from becoming an open event-injection hole: same-origin enforcement,
// strict payload validation, and never echoing the secret.
//
// These live under tests/js/ rather than api/__tests__/ because vitest.config
// only includes tests/js/**; nothing runs api/__tests__/ today.

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

const MODULE = '../../api/vitals.js';

// The endpoint calls checkRateLimit, which would reach for Upstash.
vi.mock('../../api/lib/ratelimit.js', () => ({
  checkRateLimit: vi.fn(async () => ({ success: true, headers: {} })),
  setRateLimitHeaders: vi.fn(),
}));

const SECRET = 'test-secret-value';
const ORIGIN = 'https://tech.2twodragon.com';

function makeRes() {
  const res = {
    statusCode: null,
    headers: {},
    ended: false,
    setHeader(k, v) { this.headers[k] = v; },
    status(code) { this.statusCode = code; return this; },
    end(body) { this.ended = true; this.body = body; return this; },
  };
  return res;
}

function makeReq(overrides = {}) {
  return {
    method: 'POST',
    headers: { origin: ORIGIN, ...(overrides.headers || {}) },
    body: overrides.body !== undefined
      ? overrides.body
      : { p: '/posts/foo/', m: [{ n: 'LCP', v: 1200, r: 'good' }] },
    socket: { remoteAddress: '203.0.113.7' },
    ...(overrides.method ? { method: overrides.method } : {}),
  };
}

let fetchMock;

beforeEach(async () => {
  vi.resetModules();
  process.env.GA4_API_SECRET = SECRET;
  process.env.GA4_MEASUREMENT_ID = 'G-B29150XJ73';
  process.env.SITE_ORIGIN = ORIGIN;
  fetchMock = vi.fn(async () => ({ ok: true, status: 204 }));
  vi.stubGlobal('fetch', fetchMock);
  const { checkRateLimit } = await import('../../api/lib/ratelimit.js');
  checkRateLimit.mockResolvedValue({ success: true, headers: {} });
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete process.env.GA4_API_SECRET;
  delete process.env.GA4_MEASUREMENT_ID;
  delete process.env.SITE_ORIGIN;
});

async function load() {
  return import(MODULE);
}

/** The JSON body handed to the Measurement Protocol, or null if never called. */
function forwardedBody() {
  if (fetchMock.mock.calls.length === 0) return null;
  return JSON.parse(fetchMock.mock.calls[0][1].body);
}

describe('api/vitals — cookie parsing', () => {
  it('extracts the GA client id from the _ga cookie', async () => {
    const { clientIdFromCookies } = await load();
    expect(clientIdFromCookies('_ga=GA1.1.1234567890.1700000000; other=x'))
      .toBe('1234567890.1700000000');
  });

  it('returns null when _ga is absent or malformed', async () => {
    const { clientIdFromCookies } = await load();
    expect(clientIdFromCookies('')).toBeNull();
    expect(clientIdFromCookies('_ga=GA1.1')).toBeNull();
    expect(clientIdFromCookies('_ga=GA1.1.abc.def')).toBeNull();
  });

  it('reads the session id from the GS2 cookie format', async () => {
    const { sessionIdFromCookies } = await load();
    const cookie = '_ga_B29150XJ73=GS2.1.s1745000000$o5$g1$t1745000100$j60$l0$h0';
    expect(sessionIdFromCookies(cookie, 'G-B29150XJ73')).toBe('1745000000');
  });

  it('reads the session id from the older GS1 cookie format', async () => {
    const { sessionIdFromCookies } = await load();
    const cookie = '_ga_B29150XJ73=GS1.1.1745000000.5.1.1745000100.60.0.0';
    expect(sessionIdFromCookies(cookie, 'G-B29150XJ73')).toBe('1745000000');
  });

  it('returns null when the container cookie is for a different property', async () => {
    const { sessionIdFromCookies } = await load();
    const cookie = '_ga_SOMETHINGELSE=GS2.1.s1745000000$o5';
    expect(sessionIdFromCookies(cookie, 'G-B29150XJ73')).toBeNull();
  });
});

describe('api/vitals — payload validation', () => {
  it('accepts a well-formed report', async () => {
    const { validatePayload } = await load();
    const out = validatePayload({ p: '/posts/foo/', m: [{ n: 'CLS', v: 0.05, r: 'good' }] });
    expect(out.path).toBe('/posts/foo/');
    expect(out.metrics).toEqual([
      { metric_name: 'CLS', metric_value: 0.05, metric_rating: 'good' },
    ]);
  });

  it('rejects unknown metric names', async () => {
    const { validatePayload } = await load();
    expect(validatePayload({ m: [{ n: 'FID', v: 10, r: 'good' }] })).toBeNull();
  });

  it('rejects unknown ratings', async () => {
    const { validatePayload } = await load();
    expect(validatePayload({ m: [{ n: 'LCP', v: 10, r: 'excellent' }] })).toBeNull();
  });

  it('rejects non-finite and out-of-range values', async () => {
    const { validatePayload } = await load();
    expect(validatePayload({ m: [{ n: 'LCP', v: NaN, r: 'good' }] })).toBeNull();
    expect(validatePayload({ m: [{ n: 'LCP', v: -1, r: 'good' }] })).toBeNull();
    expect(validatePayload({ m: [{ n: 'LCP', v: 1e9, r: 'good' }] })).toBeNull();
    expect(validatePayload({ m: [{ n: 'CLS', v: 1000, r: 'poor' }] })).toBeNull();
    expect(validatePayload({ m: [{ n: 'LCP', v: '1200', r: 'good' }] })).toBeNull();
  });

  it('rejects a duplicated metric — one reading per metric per page', async () => {
    const { validatePayload } = await load();
    expect(validatePayload({
      m: [{ n: 'LCP', v: 10, r: 'good' }, { n: 'LCP', v: 20, r: 'good' }],
    })).toBeNull();
  });

  it('rejects an empty or oversized metric list', async () => {
    const { validatePayload } = await load();
    expect(validatePayload({ m: [] })).toBeNull();
    expect(validatePayload({
      m: [
        { n: 'LCP', v: 1, r: 'good' }, { n: 'INP', v: 1, r: 'good' },
        { n: 'CLS', v: 1, r: 'good' }, { n: 'LCP', v: 1, r: 'good' },
      ],
    })).toBeNull();
  });

  it('rejects a body that is not a metric envelope', async () => {
    const { validatePayload } = await load();
    expect(validatePayload(null)).toBeNull();
    expect(validatePayload({})).toBeNull();
    expect(validatePayload({ m: 'LCP' })).toBeNull();
    expect(validatePayload({ m: [null] })).toBeNull();
  });

  it('strips control characters from metric_cause and caps its length', async () => {
    const { validatePayload } = await load();
    const cause = `Image: a\x00b\x1fc${'x'.repeat(200)}`;
    const out = validatePayload({ m: [{ n: 'CLS', v: 0.2, r: 'needs-improvement', c: cause }] });
    expect(out.metrics[0].metric_cause).not.toMatch(/[\x00-\x1f]/);
    expect(out.metrics[0].metric_cause.length).toBeLessThanOrEqual(100);
  });

  it('falls back to "/" for a path that is not an absolute path', async () => {
    const { validatePayload } = await load();
    expect(validatePayload({ p: 'https://evil.test/x', m: [{ n: 'LCP', v: 1, r: 'good' }] }).path)
      .toBe('/');
  });
});

describe('api/vitals — handler', () => {
  it('rejects non-POST with 405', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({ method: 'GET' }), res);
    expect(res.statusCode).toBe(405);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('forwards a valid report to the Measurement Protocol', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({
      headers: { origin: ORIGIN, cookie: '_ga=GA1.1.111.222; _ga_B29150XJ73=GS2.1.s1745000000$o3' },
    }), res);

    expect(res.statusCode).toBe(204);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const body = forwardedBody();
    expect(body.client_id).toBe('111.222');
    expect(body.events).toHaveLength(1);
    expect(body.events[0].name).toBe('web_vitals');
    expect(body.events[0].params).toMatchObject({
      metric_name: 'LCP',
      metric_value: 1200,
      metric_rating: 'good',
      session_id: '1745000000',
      cid_source: 'ga_cookie',
      engagement_time_msec: '1',
      page_location: `${ORIGIN}/posts/foo/`,
    });
  });

  it('marks a synthesized client id so inflated user counts stay detectable', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    // No _ga cookie: GA never ran for this visitor. That is precisely the
    // session this endpoint exists to recover, but the id is not a real user.
    await handler(makeReq({ headers: { origin: ORIGIN } }), res);
    expect(forwardedBody().events[0].params.cid_source).toBe('synthetic');
  });

  it('drops cross-origin posts without forwarding', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({ headers: { origin: 'https://evil.test' } }), res);
    expect(res.statusCode).toBe(204);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('drops posts with neither Origin nor Referer', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    const req = makeReq();
    req.headers = {};
    await handler(req, res);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects preview hosts — *.vercel.app would admit every project on the platform', async () => {
    // The client only beacons from the canonical host, so there is no traffic
    // to lose here, and allowing the suffix would let any vercel.app site post.
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({ headers: { origin: 'https://tech-blog-abc123.vercel.app' } }), res);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('prefers x-real-ip over the spoofable x-forwarded-for for rate limiting', async () => {
    const { checkRateLimit } = await import('../../api/lib/ratelimit.js');
    checkRateLimit.mockClear();
    const { default: handler } = await load();
    await handler(makeReq({
      headers: { origin: ORIGIN, 'x-real-ip': '198.51.100.9', 'x-forwarded-for': '1.2.3.4' },
    }), makeRes());
    expect(checkRateLimit).toHaveBeenCalledWith('198.51.100.9', 'anonymous');
  });

  it('rejects an oversized body even when the platform pre-parsed it', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({ headers: { origin: ORIGIN, 'content-length': '999999' } }), res);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('drops the report when GA4_API_SECRET is not configured', async () => {
    delete process.env.GA4_API_SECRET;
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq(), res);
    expect(res.statusCode).toBe(204);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('never echoes the api_secret in the response', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq(), res);
    expect(JSON.stringify(res.body ?? '')).not.toContain(SECRET);
    expect(JSON.stringify(res.headers)).not.toContain(SECRET);
  });

  it('drops an invalid payload without forwarding', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({ body: { m: [{ n: 'BOGUS', v: 1, r: 'good' }] } }), res);
    expect(res.statusCode).toBe(204);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('drops when rate limited', async () => {
    const { checkRateLimit } = await import('../../api/lib/ratelimit.js');
    checkRateLimit.mockResolvedValueOnce({ success: false, headers: {} });
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq(), res);
    expect(res.statusCode).toBe(204);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('parses a raw JSON string body (sendBeacon text/plain path)', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({
      body: JSON.stringify({ p: '/x/', m: [{ n: 'INP', v: 250, r: 'needs-improvement' }] }),
    }), res);
    expect(forwardedBody().events[0].params.metric_name).toBe('INP');
  });

  it('rejects an oversized raw body', async () => {
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq({ body: 'x'.repeat(5000) }), res);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('still answers 204 when the upstream forward throws', async () => {
    fetchMock.mockRejectedValueOnce(new Error('network down'));
    vi.spyOn(console, 'error').mockImplementation(() => {});
    const { default: handler } = await load();
    const res = makeRes();
    await handler(makeReq(), res);
    expect(res.statusCode).toBe(204);
  });
});
