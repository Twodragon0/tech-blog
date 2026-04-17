/**
 * Log Sanitizer Utility
 *
 * API 로그에서 민감 정보를 마스킹하는 유틸리티
 * 보안 감사 지적 사항 대응: IP, API 키, JWT, 이메일 노출 방지
 *
 * 지원 패턴:
 * - API 키: sk-*, ghp_*, AIza*, AKIA*
 * - JWT 토큰
 * - 이메일 주소
 * - IPv4 / IPv6 주소
 */

// ── 마스킹 패턴 정의 ─────────────────────────────────────────────────────────

const PATTERNS = [
  // API 키 (DeepSeek, GitHub, Google, AWS)
  // false-positive 최소화: prefix + 최소 8자 이상만 매칭
  { re: /\bsk-[A-Za-z0-9_-]{8,}\b/g,   mask: 'sk-***MASKED***' },
  { re: /\bghp_[A-Za-z0-9]{8,}\b/g,    mask: 'ghp_***MASKED***' },
  { re: /\bAIza[A-Za-z0-9_-]{8,}\b/g,  mask: 'AIza***MASKED***' },
  { re: /\bAKIA[A-Z0-9]{8,}\b/g,        mask: 'AKIA***MASKED***' },

  // JWT: header.payload.signature (각 파트 최소 10자)
  { re: /\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b/g, mask: '[JWT_MASKED]' },

  // 이메일
  { re: /\b[A-Za-z0-9._%+'-]{2,}@[A-Za-z0-9.-]{2,}\.[A-Za-z]{2,}\b/g, mask: '[EMAIL_MASKED]' },

  // IPv4 (공인 IP만: 10.x, 192.168.x, 127.x, 172.16-31.x 사설 대역 제외)
  // false-positive 최소화: 완전한 옥텟 매칭만
  {
    re: /\b(?!(?:10|127|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.)(?:\d{1,3}\.){3}\d{1,3}\b/g,
    mask: '[IP_MASKED]',
  },

  // IPv6 (축약형 포함, 최소 2개 이상의 콜론 구분자)
  { re: /\b(?:[0-9a-fA-F]{1,4}:){2,}(?:[0-9a-fA-F]{0,4}:?)+\b/g, mask: '[IPv6_MASKED]' },
];

// ── 핵심 함수 ────────────────────────────────────────────────────────────────

/**
 * 문자열 값에서 민감 정보를 마스킹한다.
 * 비문자열 값은 그대로 반환한다.
 *
 * @param {unknown} value
 * @returns {unknown}
 */
export function maskSensitive(value) {
  if (typeof value !== 'string') return value;
  let result = value;
  for (const { re, mask } of PATTERNS) {
    // RegExp 상태 초기화 (global flag 사용 시 필요)
    re.lastIndex = 0;
    result = result.replace(re, mask);
  }
  return result;
}

/**
 * 객체/배열/원시값을 재귀적으로 순회하여 모든 문자열 값을 마스킹한다.
 * 순환 참조 방지를 위해 깊이를 10으로 제한한다.
 *
 * @param {unknown} obj
 * @param {number} [depth=0]
 * @returns {unknown}
 */
export function maskDeep(obj, depth = 0) {
  if (depth > 10) return obj;
  if (obj === null || obj === undefined) return obj;
  if (typeof obj === 'string') return maskSensitive(obj);
  if (typeof obj !== 'object') return obj;

  if (Array.isArray(obj)) {
    return obj.map(item => maskDeep(item, depth + 1));
  }

  const masked = {};
  for (const key of Object.keys(obj)) {
    masked[key] = maskDeep(obj[key], depth + 1);
  }
  return masked;
}

/**
 * 안전한 로그 출력 함수.
 * context 객체의 모든 값을 재귀적으로 마스킹한 후 console[level]로 출력한다.
 * 기존 console 호출의 level/message 순서를 유지한다.
 *
 * @param {'log'|'warn'|'error'|'info'|'debug'} level
 * @param {string} message
 * @param {unknown} [context]
 */
export function safeLog(level, message, context) {
  const safeLevel = ['log', 'warn', 'error', 'info', 'debug'].includes(level) ? level : 'log';
  if (context === undefined) {
    console[safeLevel](message);
  } else {
    console[safeLevel](message, maskDeep(context));
  }
}
