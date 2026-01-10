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

// 프리티어 최적화 설정
const CONFIG = {
  // 프리티어 고려: Hobby 플랜은 10초, 안전하게 9초로 설정 (DeepSeek API 응답 시간 고려)
  TIMEOUT_MS: 9000, // 9초 (프리티어 안전 마진 + API 응답 시간 고려)
  // Rate limiting (간단한 메모리 기반, 프로덕션에서는 Redis 권장)
  RATE_LIMIT: {
    MAX_REQUESTS: 10, // 세션당 최대 요청 수
    WINDOW_MS: 60000, // 1분 윈도우
  },
  // 메시지 제한
  MAX_MESSAGE_LENGTH: 2000,
  MAX_TOKENS: 1200, // 프리티어 최적화: 토큰 수 제한 (응답 시간 단축)
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
  
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // OPTIONS 요청 처리 (CORS preflight) - 빠른 응답
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // POST 요청만 허용
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message, sessionId } = req.body;

    // 입력 검증
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return res.status(400).json({ error: '메시지가 필요합니다.' });
    }

    // 메시지 길이 제한 (보안 및 프리티어 최적화)
    if (message.length > CONFIG.MAX_MESSAGE_LENGTH) {
      return res.status(400).json({ 
        error: `메시지가 너무 깁니다. (최대 ${CONFIG.MAX_MESSAGE_LENGTH}자)` 
      });
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
    const sanitizedMessage = sanitizeInput(message);

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

    // DeepSeek API 호출 (프리티어 최적화: 타임아웃 8초)
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
      
      // 프로덕션에서는 상세 로그 최소화 (프리티어 최적화)
      if (process.env.NODE_ENV === 'development') {
        console.error('[Chat API] DeepSeek API 오류:', deepseekResponse.status, errorData);
      } else {
        // 프로덕션: 간단한 로그만
        console.error(`[Chat API] Error ${deepseekResponse.status}`);
      }
      
      // Rate limit 오류 처리
      if (deepseekResponse.status === 429) {
        const retryAfter = deepseekResponse.headers.get('retry-after') || '60';
        return res.status(429).json({ 
          error: '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.',
          retryAfter: parseInt(retryAfter, 10)
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
    // 프로덕션에서는 상세 로그 최소화
    if (process.env.NODE_ENV === 'development') {
      console.error('[Chat API] 오류:', error);
    } else {
      console.error(`[Chat API] Error: ${error.name || 'Unknown'}`);
    }

    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      // 실행 시간 로깅
      const executionTime = Date.now() - startTime;
      if (process.env.NODE_ENV === 'development') {
        console.warn(`[Chat API] Timeout after ${executionTime}ms`);
      }
      
      return res.status(504).json({ 
        error: '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 구체적으로 작성하거나 잠시 후 다시 시도해주세요.',
        timeout: true,
        executionTime: executionTime
      });
    }

    return res.status(500).json({ 
      error: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.' 
    });
  }
}

// XSS 방지를 위한 입력 정제 함수
function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

  // HTML 태그 제거 (기본적인 XSS 방지)
  // 실제로는 더 강력한 라이브러리(DOMPurify 등)를 사용하는 것이 좋습니다
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
    .trim();
}
