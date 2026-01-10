// Vercel Serverless Function for DeepSeek Chat API
// 보안: API 키를 서버에서 관리하여 클라이언트에 노출되지 않도록 함
// 비용 최적화: Context Caching 활용, Off-peak 시간대 활용, 토큰 사용량 모니터링
// 효율성: 대화 컨텍스트 유지, 응답 시간 최적화
// 
// 사용법:
// 1. Vercel 환경 변수에 DEEPSEEK_API_KEY 설정
// 2. /api/chat 엔드포인트로 POST 요청
// 
// 요청 형식:
// {
//   "message": "질문 내용",
//   "sessionId": "세션 ID (선택사항)",
//   "conversationHistory": [{"role": "user", "content": "..."}, ...] (선택사항)
// }

// 최적화 설정
const CONFIG = {
  // 타임아웃 설정: 성능 최적화를 위해 30초로 단축
  // Pro 플랜: 60초 제한, 안전하게 30초로 설정 (응답 시간 최적화)
  // Hobby 플랜 사용 시: 10초 제한, 9초로 설정 필요
  TIMEOUT_MS: process.env.VERCEL_ENV === 'production' ? 30000 : 9000,
  // Rate limiting (간단한 메모리 기반, 프로덕션에서는 Redis 권장)
  RATE_LIMIT: {
    MAX_REQUESTS: 15, // 세션당 최대 요청 수 (비용 최적화를 위해 증가)
    WINDOW_MS: 60000, // 1분 윈도우
  },
  // 메시지 제한
  MAX_MESSAGE_LENGTH: 2000,
  MAX_TOKENS: 1000, // 응답 시간 최적화를 위해 1000으로 감소 (품질은 Context Caching으로 보완)
  // 대화 컨텍스트 설정 (비용 최적화: Context Caching 활용)
  MAX_CONVERSATION_HISTORY: 10, // 최대 대화 히스토리 수 (캐시 효율성 고려)
  // Off-peak 시간대 (UTC): 16:30-00:30 (50-75% 할인)
  OFF_PEAK_START_HOUR: 16,
  OFF_PEAK_END_HOUR: 0,
  // 모델 선택: deepseek-chat (일반 작업) 또는 deepseek-chat-v3 (최신 모델)
  // 기본값: deepseek-chat (안정적이고 비용 효율적)
  MODEL: process.env.DEEPSEEK_MODEL || 'deepseek-chat', // 환경 변수로 모델 선택 가능
  // 성능 모니터링 임계값
  SLOW_REQUEST_THRESHOLD_MS: 5000, // 5초 이상인 경우만 로깅
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
    const { message, sessionId, conversationHistory } = req.body;

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
    
    // 위험한 패턴 검증 (기본적인 보안 필터) - 강화
    const dangerousPatterns = [
      /<script[^>]*>/i,
      /javascript:/i,
      /on\w+\s*=/i, // onclick, onerror 등
      /data:text\/html/i,
      /vbscript:/i,
      /<iframe[^>]*>/i,
      /<object[^>]*>/i,
      /<embed[^>]*>/i,
      /expression\s*\(/i, // CSS expression
      /@import/i, // CSS injection
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

    // 대화 히스토리 검증 (보안 강화)
    let validatedHistory = [];
    if (conversationHistory && Array.isArray(conversationHistory)) {
      // 최대 히스토리 수 제한 (비용 최적화 및 보안)
      const limitedHistory = conversationHistory.slice(-CONFIG.MAX_CONVERSATION_HISTORY);
      
      for (const msg of limitedHistory) {
        if (msg && typeof msg === 'object' && 
            typeof msg.role === 'string' && 
            typeof msg.content === 'string' &&
            (msg.role === 'user' || msg.role === 'assistant')) {
          // 각 히스토리 메시지도 검증 및 정제
          const sanitizedContent = sanitizeInput(msg.content);
          if (sanitizedContent.length > 0 && sanitizedContent.length <= CONFIG.MAX_MESSAGE_LENGTH) {
            validatedHistory.push({
              role: msg.role,
              content: sanitizedContent
            });
          }
        }
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
      console.error('[Chat API] DEEPSEEK_API_KEY가 설정되지 않았습니다.');
      return res.status(503).json({ 
        error: 'AI 서비스가 일시적으로 사용할 수 없습니다. 관리자에게 문의하세요.',
        code: 'API_KEY_MISSING'
      });
    }
    
    // API 키 형식 검증 (sk-로 시작하는지 확인)
    if (!apiKey.startsWith('sk-')) {
      console.error('[Chat API] DEEPSEEK_API_KEY 형식이 올바르지 않습니다.');
      return res.status(503).json({ 
        error: 'AI 서비스 설정 오류입니다. 관리자에게 문의하세요.',
        code: 'API_KEY_INVALID'
      });
    }

    // 시스템 메시지 (Context Caching 최적화: 재사용 가능하도록 일관된 형식 유지)
    const systemMessage = {
      role: 'system',
      content: '당신은 DevSecOps, 클라우드 보안, 인프라 자동화 전문가입니다. 기술 블로그의 질문에 친절하고 전문적으로 답변해주세요. 한국어로 답변하세요. 답변은 간결하고 핵심적인 내용으로 작성해주세요.',
    };

    // 메시지 배열 구성 (Context Caching 최적화: 시스템 메시지 재사용)
    const messages = [systemMessage];
    
    // 대화 히스토리 추가 (Context Caching 활용: 이전 대화 재사용)
    if (validatedHistory.length > 0) {
      messages.push(...validatedHistory);
    }
    
    // 현재 사용자 메시지 추가
    messages.push({
      role: 'user',
      content: sanitizedMessage,
    });

    // Off-peak 시간대 확인 (비용 최적화: 16:30-00:30 UTC, 50-75% 할인)
    const now = new Date();
    const utcHour = now.getUTCHours();
    const isOffPeak = utcHour >= CONFIG.OFF_PEAK_START_HOUR || utcHour < CONFIG.OFF_PEAK_END_HOUR;
    
    // DeepSeek API 호출 (타임아웃 설정: Pro 플랜 55초, Hobby 플랜 9초)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT_MS);

    // API 요청 로깅 (개발 환경에서만 상세 로깅)
    if (process.env.NODE_ENV === 'development') {
      console.log('[Chat API] DeepSeek API 호출:', {
        model: CONFIG.MODEL,
        messageCount: messages.length,
        hasApiKey: !!apiKey,
        apiKeyPrefix: apiKey ? apiKey.substring(0, 7) + '...' : 'missing'
      });
    }

    const deepseekResponse = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: CONFIG.MODEL,
        messages: messages,
        temperature: 0.7,
        max_tokens: CONFIG.MAX_TOKENS,
        stream: false,
        // 응답 시간 최적화를 위한 추가 설정
        top_p: 0.9, // 응답 다양성 조절 (0.95 → 0.9로 감소하여 응답 생성 속도 향상)
        // Context Caching은 자동으로 작동하므로 별도 설정 불필요
        // 하지만 일관된 시스템 메시지와 대화 히스토리를 유지하면 캐시 히트율 향상
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!deepseekResponse.ok) {
      let errorData = {};
      try {
        errorData = await deepseekResponse.json();
      } catch (e) {
        const responseText = await deepseekResponse.text().catch(() => 'Unable to read response');
        console.error('[Chat API] DeepSeek API 오류 응답 파싱 실패:', {
          status: deepseekResponse.status,
          responsePreview: responseText.substring(0, 200)
        });
      }
      
      // 상세 로그 (보안: 민감 정보 제외)
      console.error('[Chat API] DeepSeek API 오류:', {
        status: deepseekResponse.status,
        statusText: deepseekResponse.statusText,
        errorType: errorData.error?.type || 'unknown',
        errorMessage: errorData.error?.message || 'No error message'
      });
      
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

    let data;
    try {
      data = await deepseekResponse.json();
    } catch (parseError) {
      console.error('[Chat API] DeepSeek API 응답 파싱 오류:', parseError.message);
      const responseText = await deepseekResponse.text().catch(() => 'Unable to read response');
      console.error('[Chat API] Raw response:', responseText.substring(0, 500));
      return res.status(500).json({ 
        error: 'AI 서비스 응답을 처리할 수 없습니다. 잠시 후 다시 시도해주세요.',
        code: 'RESPONSE_PARSE_ERROR'
      });
    }

    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      console.error('[Chat API] DeepSeek API 응답 형식 오류:', {
        hasChoices: !!data.choices,
        choicesLength: data.choices?.length,
        hasMessage: !!data.choices?.[0]?.message,
        error: data.error
      });
      return res.status(500).json({ 
        error: '응답 형식이 올바르지 않습니다.',
        code: 'INVALID_RESPONSE_FORMAT'
      });
    }

    const response = data.choices[0].message.content;

    // 응답 검증 및 정제
    if (!response || typeof response !== 'string') {
      console.error('[Chat API] 응답 내용이 없거나 문자열이 아닙니다:', {
        responseType: typeof response,
        responseValue: response
      });
      return res.status(500).json({ 
        error: '응답을 생성할 수 없습니다.',
        code: 'EMPTY_RESPONSE'
      });
    }

    // XSS 방지를 위한 응답 정제
    const sanitizedResponse = sanitizeInput(response);

    // 실행 시간 로깅 (성능 모니터링)
    const executionTime = Date.now() - startTime;
    
    // 비용 최적화 모니터링: 캐시 히트율 및 토큰 사용량 로깅
    const cacheHitTokens = data.usage?.prompt_cache_hit_tokens || 0;
    const cacheMissTokens = data.usage?.prompt_cache_miss_tokens || 0;
    const totalPromptTokens = data.usage?.prompt_tokens || 0;
    const totalCompletionTokens = data.usage?.completion_tokens || 0;
    const cacheHitRate = totalPromptTokens > 0 ? (cacheHitTokens / totalPromptTokens * 100).toFixed(1) : 0;
    
    // 성능 모니터링: 느린 요청만 로깅 (프로덕션 최적화)
    if (executionTime > CONFIG.SLOW_REQUEST_THRESHOLD_MS) {
      console.log(`[Chat API] Execution time: ${executionTime}ms`);
      console.log(`[Chat API] Token usage - Prompt: ${totalPromptTokens} (Cache hit: ${cacheHitTokens}, Miss: ${cacheMissTokens}), Completion: ${totalCompletionTokens}, Cache hit rate: ${cacheHitRate}%`);
      if (isOffPeak) {
        console.log(`[Chat API] Off-peak hours (UTC ${utcHour}:00) - 50-75% discount applied`);
      }
    } else if (process.env.NODE_ENV === 'development') {
      // 개발 환경에서는 모든 요청 로깅
      console.log(`[Chat API] Execution time: ${executionTime}ms`);
      console.log(`[Chat API] Token usage - Prompt: ${totalPromptTokens} (Cache hit: ${cacheHitTokens}, Miss: ${cacheMissTokens}), Completion: ${totalCompletionTokens}, Cache hit rate: ${cacheHitRate}%`);
      if (isOffPeak) {
        console.log(`[Chat API] Off-peak hours (UTC ${utcHour}:00) - 50-75% discount applied`);
      }
    }

    // 성공 응답 (비용 최적화 정보 포함)
    return res.status(200).json({
      response: sanitizedResponse,
      sessionId: sessionKey,
      provider: 'deepseek',
      // 비용 최적화 정보 (선택적, 개발 환경에서만 상세 정보 제공)
      ...(process.env.NODE_ENV === 'development' ? {
        usage: {
          promptTokens: totalPromptTokens,
          completionTokens: totalCompletionTokens,
          cacheHitTokens: cacheHitTokens,
          cacheMissTokens: cacheMissTokens,
          cacheHitRate: `${cacheHitRate}%`,
          isOffPeak: isOffPeak,
        }
      } : {}),
    });

  } catch (error) {
    const executionTime = Date.now() - startTime;
    
    // 상세 로그 (보안: 민감 정보 제외)
    console.error('[Chat API] 오류:', {
      name: error.name,
      message: error.message,
      stack: error.stack?.split('\n').slice(0, 3).join('\n'), // 스택 트레이스 일부만
      executionTime: executionTime
    });

    // 타임아웃 오류 처리
    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      console.warn(`[Chat API] Timeout after ${executionTime}ms (limit: ${CONFIG.TIMEOUT_MS}ms)`);
      
      return res.status(504).json({ 
        error: '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 구체적으로 작성하거나 잠시 후 다시 시도해주세요.',
        timeout: true,
        executionTime: executionTime
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
  // 하지만 서버리스 환경에서는 의존성 최소화를 위해 기본 함수 사용
  return input
    // HTML 태그 제거 (더 강력한 패턴)
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
    // 추가 보안: 위험한 패턴 제거
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/data:text\/html/gi, '')
    .trim();
}
