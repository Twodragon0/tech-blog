// Vercel Serverless Function for DeepSeek Chat API
// 보안: API 키를 서버에서 관리하여 클라이언트에 노출되지 않도록 함
// 프리티어 최적화: 실행 시간, 메모리, Rate limiting 고려
// 
// 사용법:
// 1. Vercel 환경 변수에 DEEPSEEK_API_KEY 설정
// 2. /api/chat 엔드포인트로 POST 요청
// 
// 요청 형식:
// {
//   "message": "질문 내용",
//   "sessionId": "세션 ID (선택사항)"
// }

// 최적화 설정
const CONFIG = {
  // Pro 플랜: 60초 제한, 안전하게 55초로 설정 (DeepSeek API 응답 시간 고려)
  // Hobby 플랜 사용 시: 10초 제한, 9초로 설정 필요
  TIMEOUT_MS: process.env.VERCEL_ENV === 'production' ? 55000 : 9000,
  // Rate limiting (간단한 메모리 기반, 프로덕션에서는 Redis 권장)
  RATE_LIMIT: {
    MAX_REQUESTS: 10, // 세션당 최대 요청 수
    WINDOW_MS: 60000, // 1분 윈도우
  },
  // 메시지 제한
  MAX_MESSAGE_LENGTH: 2000,
  MAX_TOKENS: 1200, // 응답 시간 단축을 위한 토큰 수 제한
};

// 간단한 메모리 기반 Rate Limiter (프리티어용)
// 프로덕션에서는 Redis 또는 Vercel KV 사용 권장
const rateLimitStore = new Map();

function checkRateLimit(sessionId) {
  const now = Date.now();
  const key = sessionId || 'anonymous';
  const record = rateLimitStore.get(key);

  if (!record) {
    rateLimitStore.set(key, { count: 1, resetAt: now + CONFIG.RATE_LIMIT.WINDOW_MS });
    // 메모리 정리: 오래된 레코드 삭제
    if (rateLimitStore.size > 1000) {
      for (const [k, v] of rateLimitStore.entries()) {
        if (v.resetAt < now) {
          rateLimitStore.delete(k);
        }
      }
    }
    return true;
  }

  if (record.resetAt < now) {
    record.count = 1;
    record.resetAt = now + CONFIG.RATE_LIMIT.WINDOW_MS;
    return true;
  }

  if (record.count >= CONFIG.RATE_LIMIT.MAX_REQUESTS) {
    return false;
  }

  record.count++;
  return true;
}

export default async function handler(req, res) {
  const startTime = Date.now();
  
  // 허용된 Origin 목록 (보안 강화)
  const allowedOrigins = [
    'https://tech.2twodragon.com',
    'https://www.tech.2twodragon.com',
    // 개발 환경용 (로컬 개발 시에만 사용)
    ...(process.env.NODE_ENV === 'development' ? ['http://localhost:4000', 'http://127.0.0.1:4000'] : [])
  ];
  
  const origin = req.headers.origin || req.headers.referer;
  const isAllowedOrigin = origin && allowedOrigins.some(allowed => origin.startsWith(allowed));
  
  // CORS 헤더 설정 (보안 강화: 실제 도메인만 허용)
  if (isAllowedOrigin) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Credentials', 'false');
  res.setHeader('Access-Control-Max-Age', '86400'); // 24시간
  
  // 보안 헤더 추가
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  // OPTIONS 요청 처리 (CORS preflight) - 빠른 응답
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  
  // Origin 검증 (POST 요청 시)
  if (req.method === 'POST' && !isAllowedOrigin && process.env.NODE_ENV === 'production') {
    return res.status(403).json({ error: 'Forbidden: Invalid origin' });
  }

  // POST 요청만 허용
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, sessionId } = req.body;

    // 입력 검증 강화
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: '메시지가 필요합니다.' });
    }
    
    const trimmedMessage = message.trim();
    if (trimmedMessage.length === 0) {
      return res.status(400).json({ error: '메시지가 비어있습니다.' });
    }
    
    // 메시지 길이 제한 (보안 및 프리티어 최적화)
    if (trimmedMessage.length > CONFIG.MAX_MESSAGE_LENGTH) {
      return res.status(400).json({ 
        error: `메시지가 너무 깁니다. (최대 ${CONFIG.MAX_MESSAGE_LENGTH}자)` 
      });
    }
    
    // 최소 길이 검증 (스팸 방지)
    if (trimmedMessage.length < 2) {
      return res.status(400).json({ error: '메시지는 최소 2자 이상이어야 합니다.' });
    }
    
    // 위험한 패턴 검증 (기본적인 보안 필터)
    const dangerousPatterns = [
      /<script[^>]*>/i,
      /javascript:/i,
      /on\w+\s*=/i, // onclick, onerror 등
      /data:text\/html/i,
    ];
    
    for (const pattern of dangerousPatterns) {
      if (pattern.test(trimmedMessage)) {
        // 프로덕션에서는 상세 로그 최소화
        if (process.env.NODE_ENV === 'development') {
          console.warn('[Chat API] 위험한 패턴 감지:', pattern);
        }
        return res.status(400).json({ error: '유효하지 않은 메시지 형식입니다.' });
      }
    }

    // Rate limiting 체크
    const sessionKey = sessionId || `session-${Date.now()}`;
    if (!checkRateLimit(sessionKey)) {
      return res.status(429).json({ 
        error: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.',
        retryAfter: 60
      });
    }

    // XSS 방지를 위한 입력 정제
    const sanitizedMessage = sanitizeInput(trimmedMessage);

    // DeepSeek API 키 확인
    const apiKey = process.env.DEEPSEEK_API_KEY;
    if (!apiKey) {
      // 프로덕션에서는 상세 로그 최소화
      if (process.env.NODE_ENV === 'development') {
        console.error('[Chat API] DEEPSEEK_API_KEY가 설정되지 않았습니다.');
      }
      return res.status(503).json({ 
        error: 'AI 서비스가 일시적으로 사용할 수 없습니다. 관리자에게 문의하세요.' 
      });
    }

    // DeepSeek API 호출 (타임아웃 설정: Pro 플랜 55초, Hobby 플랜 9초)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);

    const deepseekResponse = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          {
            role: 'system',
            content: '당신은 DevSecOps, 클라우드 보안, 인프라 자동화 전문가입니다. 기술 블로그의 질문에 친절하고 전문적으로 답변해주세요. 한국어로 답변하세요. 답변은 간결하고 핵심적인 내용으로 작성해주세요.',
          },
          {
            role: 'user',
            content: sanitizedMessage,
          },
        ],
        temperature: 0.7,
        max_tokens: CONFIG.MAX_TOKENS, // 프리티어 최적화: 토큰 수 제한 (응답 시간 단축)
        stream: false,
        // 응답 시간 최적화를 위한 추가 설정
        top_p: 0.95, // 응답 다양성 조절
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!deepseekResponse.ok) {
      const errorData = await deepseekResponse.json().catch(() => ({}));
      
      // 프로덕션에서는 상세 로그 최소화 (보안 및 프리티어 최적화)
      if (process.env.NODE_ENV === 'development') {
        console.error('[Chat API] DeepSeek API 오류:', {
          status: deepseekResponse.status,
          // 민감 정보는 로깅하지 않음
          errorType: errorData.error?.type || 'unknown'
        });
      } else {
        // 프로덕션: 간단한 로그만 (민감 정보 제외)
        console.error(`[Chat API] DeepSeek API Error ${deepseekResponse.status}`);
      }
      
      // Rate limit 오류 처리
      if (deepseekResponse.status === 429) {
        const retryAfter = deepseekResponse.headers.get('retry-after') || '60';
        return res.status(429).json({ 
          error: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.',
          retryAfter: parseInt(retryAfter, 10)
        });
      }
      
      // 401 Unauthorized (API 키 오류)
      if (deepseekResponse.status === 401) {
        // 프로덕션에서는 일반적인 메시지만 반환 (보안)
        return res.status(503).json({ 
          error: 'AI 서비스가 일시적으로 사용할 수 없습니다. 관리자에게 문의하세요.' 
        });
      }

      return res.status(503).json({ 
        error: 'AI 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.' 
      });
    }

    const data = await deepseekResponse.json();

    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      // 프로덕션에서는 상세 로그 최소화
      if (process.env.NODE_ENV === 'development') {
        console.error('[Chat API] DeepSeek API 응답 형식 오류:', data);
      } else {
        console.error('[Chat API] Invalid response format');
      }
      return res.status(500).json({ error: '응답 형식이 올바르지 않습니다.' });
    }

    const response = data.choices[0].message.content;

    // 응답 검증 및 정제
    if (!response || typeof response !== 'string') {
      return res.status(500).json({ error: '응답을 생성할 수 없습니다.' });
    }

    // XSS 방지를 위한 응답 정제
    const sanitizedResponse = sanitizeInput(response);

    // 실행 시간 로깅 (프리티어 모니터링)
    const executionTime = Date.now() - startTime;
    if (process.env.NODE_ENV === 'development' || executionTime > 5000) {
      console.log(`[Chat API] Execution time: ${executionTime}ms`);
    }

    // 성공 응답
    return res.status(200).json({
      response: sanitizedResponse,
      sessionId: sessionKey,
      provider: 'deepseek',
    });

  } catch (error) {
    const executionTime = Date.now() - startTime;
    
    // 프로덕션에서는 상세 로그 최소화 (보안: 민감 정보 노출 방지)
    if (process.env.NODE_ENV === 'development') {
      console.error('[Chat API] 오류:', {
        name: error.name,
        message: error.message,
        executionTime: executionTime
      });
    } else {
      // 프로덕션: 최소한의 정보만 로깅
      console.error(`[Chat API] Error: ${error.name || 'Unknown'} (${executionTime}ms)`);
    }

    // 타임아웃 오류 처리
    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`[Chat API] Timeout after ${executionTime}ms`);
      }
      
      return res.status(504).json({ 
        error: '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 구체적으로 작성하거나 잠시 후 다시 시도해주세요.',
        timeout: true
      });
    }
    
    // 네트워크 오류 처리
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return res.status(503).json({ 
        error: 'AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.' 
      });
    }

    // 기타 오류는 일반적인 메시지로 처리 (보안: 상세 정보 노출 방지)
    return res.status(500).json({ 
      error: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' 
    });
  }
}

// XSS 방지를 위한 입력 정제 함수 (강화)
function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

  // HTML 태그 및 위험한 문자 제거 (XSS 방지 강화)
  // 실제로는 더 강력한 라이브러리(DOMPurify 등)를 사용하는 것이 좋습니다
  return input
    // HTML 태그 제거
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // 따옴표 이스케이프
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    // 슬래시 이스케이프
    .replace(/\//g, '&#x2F;')
    // 추가 위험 문자 제거
    .replace(/&(?!(?:amp|lt|gt|quot|#x27|#x2F);)/g, '&amp;')
    // 제어 문자 제거 (보안 강화)
    .replace(/[\x00-\x1F\x7F]/g, '')
    .trim();
}
