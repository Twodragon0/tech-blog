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
  // 타임아웃 설정: Vercel 플랜에 따라 조정
  // Pro 플랜: 60초 제한, 안전하게 50초로 설정 (안전 마진 확보)
  // Hobby 플랜: 10초 제한, 8초로 설정 (안전 마진 확보)
  // vercel.json의 maxDuration: 60이지만, 실제 플랜이 Hobby일 수 있으므로 보수적으로 설정
  // 환경 변수 VERCEL_ENV가 'production'이어도 Hobby 플랜일 수 있음
  // 따라서 더 보수적으로 설정: 프로덕션에서도 25초로 설정 (Pro/Hobby 모두 대응)
  TIMEOUT_MS: process.env.VERCEL_ENV === 'production' ? 25000 : 8000,
  // Rate limiting (간단한 메모리 기반, 프로덕션에서는 Redis 권장)
  RATE_LIMIT: {
    MAX_REQUESTS: 15, // 세션당 최대 요청 수 (비용 최적화를 위해 증가)
    WINDOW_MS: 60000, // 1분 윈도우
  },
  // 메시지 제한
  MAX_MESSAGE_LENGTH: 2000,
  MAX_TOKENS: 800, // 응답 시간 최적화를 위해 800으로 감소 (타임아웃 방지 우선)
  // 대화 컨텍스트 설정 (비용 최적화: Context Caching 활용)
  MAX_CONVERSATION_HISTORY: 10, // 최대 대화 히스토리 수 (캐시 효율성 고려)
  // Off-peak 시간대 (UTC): 16:30-00:30 (50-75% 할인)
  OFF_PEAK_START_HOUR: 16,
  OFF_PEAK_END_HOUR: 0,
  // 모델 선택: deepseek-chat (일반 작업) 또는 deepseek-reasoner (복잡한 추론 작업)
  // deepseek-chat: DeepSeek-V3.2 기반, 빠른 응답, Function Calling 지원
  // deepseek-reasoner: 깊은 추론 작업용, 최대 64,000 토큰 출력
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
      console.error('[Chat API] 환경 변수 확인 필요: vercel env ls | grep DEEPSEEK_API_KEY');
      return res.status(503).json({ 
        error: 'AI 서비스가 일시적으로 사용할 수 없습니다. 관리자에게 문의하세요.',
        code: 'API_KEY_MISSING'
      });
    }
    
    // API 키 형식 검증 (sk-로 시작하는지 확인)
    if (!apiKey.startsWith('sk-')) {
      console.error('[Chat API] DEEPSEEK_API_KEY 형식이 올바르지 않습니다.');
      console.error('[Chat API] API 키는 sk-로 시작해야 합니다.');
      return res.status(503).json({ 
        error: 'AI 서비스 설정 오류입니다. 관리자에게 문의하세요.',
        code: 'API_KEY_INVALID'
      });
    }
    
    // API 키 길이 검증 (최소 길이 확인)
    if (apiKey.length < 20) {
      console.error('[Chat API] DEEPSEEK_API_KEY가 너무 짧습니다.');
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
    
    // DeepSeek API 호출 (타임아웃 설정: 보수적으로 25초로 설정)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      const elapsed = Date.now() - requestStartTime;
      console.warn(`[Chat API] 타임아웃 발생 (${elapsed}ms 경과, 제한: ${CONFIG.TIMEOUT_MS}ms)`);
      controller.abort();
    }, CONFIG.TIMEOUT_MS);

    // API 요청 로깅 (항상 로깅하여 진단 가능하도록)
    const requestStartTime = Date.now();
    console.log('[Chat API] DeepSeek API 호출 시작:', {
      model: CONFIG.MODEL,
      messageCount: messages.length,
      maxTokens: CONFIG.MAX_TOKENS,
      timeout: CONFIG.TIMEOUT_MS,
      timestamp: new Date().toISOString()
    });

    let deepseekResponse;
    try {
      deepseekResponse = await fetch('https://api.deepseek.com/v1/chat/completions', {
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
    } catch (fetchError) {
      clearTimeout(timeoutId);
      const fetchTime = Date.now() - requestStartTime;
      
      // 타임아웃 오류 처리
      if (fetchError.name === 'AbortError' || fetchError.name === 'TimeoutError') {
        console.warn(`[Chat API] DeepSeek API 타임아웃 (${fetchTime}ms)`);
        return res.status(504).json({ 
          error: '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 구체적으로 작성하거나 잠시 후 다시 시도해주세요.',
          timeout: true,
          executionTime: fetchTime
        });
      }
      
      // 네트워크 오류 처리
      console.error('[Chat API] DeepSeek API 네트워크 오류:', {
        name: fetchError.name,
        message: fetchError.message,
        fetchTime: fetchTime
      });
      return res.status(503).json({ 
        error: 'AI 서비스에 연결할 수 없습니다. 네트워크 연결을 확인하고 잠시 후 다시 시도해주세요.',
        code: 'NETWORK_ERROR'
      });
    }

    clearTimeout(timeoutId);
    const fetchTime = Date.now() - requestStartTime;
    
    // API 응답 시간 로깅 (항상 로깅하여 진단 가능하도록)
    console.log(`[Chat API] DeepSeek API 응답 완료: ${fetchTime}ms (타임아웃 제한: ${CONFIG.TIMEOUT_MS}ms)`);
    
    // 타임아웃에 가까운 경우 경고
    if (fetchTime > CONFIG.TIMEOUT_MS * 0.8) {
      console.warn(`[Chat API] 응답 시간이 타임아웃 제한의 80%를 초과했습니다: ${fetchTime}ms / ${CONFIG.TIMEOUT_MS}ms`);
    }

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

    // 타임아웃 오류 처리 (이미 fetch 단계에서 처리했지만, 추가 안전장치)
    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      console.error(`[Chat API] Timeout after ${executionTime}ms (limit: ${CONFIG.TIMEOUT_MS}ms)`, {
        timeout: CONFIG.TIMEOUT_MS,
        executionTime: executionTime,
        model: CONFIG.MODEL,
        maxTokens: CONFIG.MAX_TOKENS
      });
      
      return res.status(504).json({ 
        error: '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 짧고 구체적으로 작성하거나 잠시 후 다시 시도해주세요.',
        timeout: true,
        executionTime: executionTime,
        timeoutLimit: CONFIG.TIMEOUT_MS,
        code: 'TIMEOUT',
        suggestion: '질문을 더 짧게 작성하거나, 여러 질문으로 나누어 주시면 더 빠르게 답변받을 수 있습니다.'
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
// 보안: 멀티바이트 문자 및 유니코드 정규화 지원
function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return '';
  }

  // 보안: 유니코드 정규화 (NFC) - 멀티바이트 문자 처리
  let sanitized = input.normalize('NFC');
  
  // HTML 태그 및 위험한 문자 제거 (XSS 방지 강화)
  // 실제로는 더 강력한 라이브러리(DOMPurify 등)를 사용하는 것이 좋습니다
  // 하지만 서버리스 환경에서는 의존성 최소화를 위해 기본 함수 사용
  
  // 보안: 멀티바이트 문자를 고려한 완전한 sanitization
  // 모든 위험한 문자를 먼저 이스케이프 처리
  // 멀티바이트 문자 시퀀스를 올바르게 처리하기 위해 정규화된 문자열 사용
  
  // 1단계: 멀티바이트 문자 시퀀스 처리 (유니코드 정규화 후)
  // 위험한 유니코드 조합 문자 제거
  sanitized = sanitized.replace(/[\u200B-\u200D\uFEFF\u202A-\u202E\u2060-\u206F]/g, '');
  
  // 2단계: HTML 특수 문자 이스케이프 (멀티바이트 안전)
  sanitized = sanitized
    // 앰퍼샌드 먼저 처리 (다른 엔티티와 충돌 방지)
    .replace(/&/g, '&amp;')
    // HTML 태그 제거 (더 강력한 패턴) - 멀티바이트 문자 고려
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // 따옴표 이스케이프
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    // 슬래시 이스케이프
    .replace(/\//g, '&#x2F;');
  
  // 3단계: 이미 이스케이프된 엔티티 복원 (중복 이스케이프 방지)
  sanitized = sanitized
    .replace(/&amp;amp;/g, '&amp;')
    .replace(/&amp;lt;/g, '&lt;')
    .replace(/&amp;gt;/g, '&gt;')
    .replace(/&amp;quot;/g, '&quot;')
    .replace(/&amp;#x27;/g, '&#x27;')
    .replace(/&amp;#x2F;/g, '&#x2F;');
  
  // 4단계: 제어 문자 제거 (보안 강화) - 유니코드 제어 문자 포함
  sanitized = sanitized.replace(/[\x00-\x1F\x7F-\x9F]/g, '');
  
  // 5단계: 위험한 패턴 제거 (멀티바이트 고려, 완전한 패턴 매칭)
  // 멀티바이트 문자를 고려하여 모든 변형 패턴 제거
  // 정규화된 문자열에서 위험한 패턴 검사
  const dangerousPatterns = [
    /javascript\s*:/gi,
    /data\s*:\s*text\s*\/\s*html/gi,
    /data\s*:\s*text\s*\/\s*javascript/gi,
    /vbscript\s*:/gi,
    /on\w+\s*=/gi,
    /&lt;\s*script/gi,
    /&lt;\s*iframe/gi,
    /&lt;\s*object/gi,
    /&lt;\s*embed/gi,
    /expression\s*\(/gi,
  ];
  
  for (const pattern of dangerousPatterns) {
    sanitized = sanitized.replace(pattern, '');
  }
  
  sanitized = sanitized.trim();
  
  return sanitized;
}

// URL 검증 함수 (보안 강화)
function validateUrl(url) {
  if (typeof url !== 'string' || !url.trim()) {
    return null;
  }
  
  try {
    // 보안: URL 문자열 자체에 위험한 패턴이 있는지 먼저 검사
    const urlTrimmed = url.trim();
    const urlLower = urlTrimmed.toLowerCase();
    
    // 완전한 스킴 검사: 위험한 스킴이 정확히 시작 부분에 있는지 확인
    // 멀티바이트 문자나 인코딩된 문자를 우회하는 시도 차단
    const dangerousSchemes = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:', 'jar:'];
    for (const scheme of dangerousSchemes) {
      // 정확한 스킴 매칭: 시작 부분에 정확히 일치하는지 확인
      // 공백, 탭, 줄바꿈 등으로 시작하는 경우도 차단
      if (urlLower.startsWith(scheme) || 
          urlLower.match(new RegExp(`^[\\s\\t\\n\\r]*${scheme.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i'))) {
        return null;
      }
      // URL 내부에 위험한 스킴이 포함된 경우도 차단
      if (urlLower.includes(' ' + scheme) || 
          urlLower.includes('\n' + scheme) || 
          urlLower.includes('\t' + scheme) ||
          urlLower.includes('%20' + scheme) ||
          urlLower.includes('%0a' + scheme)) {
        return null;
      }
    }
    
    // 상대 경로를 절대 경로로 변환
    let urlToValidate = urlTrimmed;
    if (!urlToValidate.includes('://')) {
      // 상대 경로인 경우 현재 도메인 기준으로 절대 경로 생성
      urlToValidate = new URL(urlToValidate, 'https://tech.2twodragon.com').href;
    }
    
    const urlObj = new URL(urlToValidate);
    
    // 보안: 허용된 스킴만 허용 (정확한 비교, 대소문자 구분)
    const allowedSchemes = ['http:', 'https:'];
    if (!allowedSchemes.includes(urlObj.protocol.toLowerCase())) {
      return null; // javascript:, data:, vbscript: 등 차단
    }
    
    // 보안: 위험한 호스트명 차단
    const dangerousHosts = ['localhost', '127.0.0.1', '0.0.0.0', '[::1]'];
    if (dangerousHosts.includes(urlObj.hostname.toLowerCase())) {
      return null;
    }
    
    // 보안: 위험한 패턴이 포함된 URL 차단 (모든 구성 요소 검사)
    const dangerousPatterns = [
      /javascript\s*:/i,
      /data\s*:\s*text\s*\/\s*html/i,
      /data\s*:\s*text\s*\/\s*javascript/i,
      /vbscript\s*:/i,
      /on\w+\s*=/i,
      /<script/i,
      /<iframe/i,
      /expression\s*\(/i
    ];
    
    // URL의 모든 구성 요소 검사
    const urlComponents = [
      urlObj.href,
      urlObj.protocol,
      urlObj.hostname,
      urlObj.pathname,
      urlObj.search,
      urlObj.hash
    ];
    
    for (const component of urlComponents) {
      for (const pattern of dangerousPatterns) {
        if (pattern.test(component)) {
          return null;
        }
      }
    }
    
    return urlObj.href;
  } catch (e) {
    // URL 파싱 실패 시 null 반환
    return null;
  }
}
