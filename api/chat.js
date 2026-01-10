// Vercel Serverless Function for DeepSeek Chat API
// 보안: API 키를 서버에서 관리하여 클라이언트에 노출되지 않도록 함

export default async function handler(req, res) {
  // CORS 헤더 설정 (필요한 경우)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // OPTIONS 요청 처리 (CORS preflight)
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

    // 메시지 길이 제한 (보안)
    if (message.length > 2000) {
      return res.status(400).json({ error: '메시지가 너무 깁니다. (최대 2000자)' });
    }

    // XSS 방지를 위한 입력 정제
    const sanitizedMessage = sanitizeInput(message);

    // DeepSeek API 키 확인
    const apiKey = process.env.DEEPSEEK_API_KEY;
    if (!apiKey) {
      console.error('DEEPSEEK_API_KEY가 설정되지 않았습니다.');
      return res.status(503).json({ 
        error: 'AI 서비스가 일시적으로 사용할 수 없습니다. 관리자에게 문의하세요.' 
      });
    }

    // Rate limiting을 위한 세션 ID 사용 (간단한 구현)
    // 실제로는 Redis 등을 사용하는 것이 좋습니다
    const sessionKey = sessionId || `session-${Date.now()}`;

    // DeepSeek API 호출
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60초 타임아웃

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
            content: '당신은 DevSecOps, 클라우드 보안, 인프라 자동화 전문가입니다. 기술 블로그의 질문에 친절하고 전문적으로 답변해주세요. 한국어로 답변하세요.',
          },
          {
            role: 'user',
            content: sanitizedMessage,
          },
        ],
        temperature: 0.7,
        max_tokens: 2000,
        stream: false,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!deepseekResponse.ok) {
      const errorData = await deepseekResponse.json().catch(() => ({}));
      console.error('DeepSeek API 오류:', deepseekResponse.status, errorData);
      
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
      console.error('DeepSeek API 응답 형식 오류:', data);
      return res.status(500).json({ error: '응답 형식이 올바르지 않습니다.' });
    }

    const response = data.choices[0].message.content;

    // 응답 검증 및 정제
    if (!response || typeof response !== 'string') {
      return res.status(500).json({ error: '응답을 생성할 수 없습니다.' });
    }

    // XSS 방지를 위한 응답 정제
    const sanitizedResponse = sanitizeInput(response);

    // 성공 응답
    return res.status(200).json({
      response: sanitizedResponse,
      sessionId: sessionKey,
      provider: 'deepseek',
    });

  } catch (error) {
    console.error('Chat API 오류:', error);

    if (error.name === 'AbortError' || error.name === 'TimeoutError') {
      return res.status(504).json({ 
        error: '요청 시간이 초과되었습니다. 네트워크 연결을 확인하고 다시 시도해주세요.' 
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
