// DeepSeek Chat Widget JavaScript
(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    // 엔드포인트: trailing slash 없이 사용 (Vercel이 자동으로 처리)
    apiEndpoint: '/api/chat',
    maxRetries: 1, // 재시도 횟수 (타임아웃 시 재시도는 비효율적)
    timeout: 12000, // 12초 (서버 타임아웃 9초 + 네트워크 여유)
    showIconDelay: 5000, // 5 seconds
    retryDelay: 2000, // 재시도 전 대기 시간 (ms)
    maxMessageLength: 2000, // 서버와 동일한 제한
  };

  // State
  let isOpen = false;
  let isLoading = false;
  let messages = [];
  let sessionId = null;

  // DOM Elements
  const chatWidget = document.getElementById('deepseek-chat-widget');
  const chatToggle = document.getElementById('chat-widget-toggle');
  const chatWindow = document.getElementById('chat-widget-window');
  const chatClose = document.getElementById('chat-widget-close');
  const chatMessages = document.getElementById('chat-widget-messages');
  const chatForm = document.getElementById('chat-widget-form');
  const chatInput = document.getElementById('chat-widget-input');
  const chatSend = document.getElementById('chat-widget-send');

  if (!chatWidget || !chatToggle || !chatWindow) {
    return; // Widget not found, exit
  }

  // Initialize session ID
  function initSession() {
    sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
      sessionId = Date.now().toString();
      localStorage.setItem('chatSessionId', sessionId);
    }
  }

  // Show chat icon with delay
  function showChatIcon() {
    setTimeout(() => {
      chatToggle.style.display = 'flex';
      chatToggle.classList.add('chat-widget-toggle-visible');
    }, CONFIG.showIconDelay);
  }

  // Toggle chat window
  function toggleChat() {
    isOpen = !isOpen;
    if (isOpen) {
      chatWindow.style.display = 'flex';
      chatWindow.classList.add('chat-widget-window-open');
      chatInput.focus();
      // Scroll to bottom
      scrollToBottom();
    } else {
      chatWindow.classList.remove('chat-widget-window-open');
      setTimeout(() => {
        chatWindow.style.display = 'none';
      }, 300);
    }
  }

  // Scroll to bottom of messages
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Add message to chat
  function addMessage(content, role = 'assistant', timestamp = null) {
    const messageId = Date.now().toString();
    const message = {
      id: messageId,
      content,
      role,
      timestamp: timestamp || new Date(),
    };
    messages.push(message);

    const messageEl = document.createElement('div');
    messageEl.className = `chat-message chat-message-${role}`;
    messageEl.id = `message-${messageId}`;
    
    const contentEl = document.createElement('div');
    contentEl.className = 'chat-message-content';
    
    // Format message content (basic markdown support)
    const formattedContent = formatMessage(content);
    contentEl.innerHTML = formattedContent;
    
    const timeEl = document.createElement('div');
    timeEl.className = 'chat-message-time';
    timeEl.textContent = formatTime(message.timestamp);
    
    messageEl.appendChild(contentEl);
    messageEl.appendChild(timeEl);
    
    chatMessages.appendChild(messageEl);
    scrollToBottom();
    
    return messageEl;
  }

  // Format message content (basic markdown)
  function formatMessage(content) {
    if (!content) return '';
    
    // Escape HTML to prevent XSS
    const escapeHtml = (text) => {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    };
    
    let formatted = escapeHtml(content);
    
    // Bold text: **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Code blocks: ```code```
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    // Inline code: `code`
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Links: [text](url)
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
      // Validate URL
      try {
        const urlObj = new URL(url);
        if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
          return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(text)}</a>`;
        }
      } catch (e) {
        // Invalid URL, return text only
      }
      return escapeHtml(text);
    });
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
  }

  // Format timestamp
  function formatTime(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    
    if (diff < 60000) { // Less than 1 minute
      return '방금 전';
    } else if (diff < 3600000) { // Less than 1 hour
      return Math.floor(diff / 60000) + '분 전';
    } else if (diff < 86400000) { // Less than 1 day
      return Math.floor(diff / 3600000) + '시간 전';
    } else {
      return time.toLocaleDateString('ko-KR');
    }
  }

  // Show loading indicator
  function showLoading() {
    const loadingEl = document.createElement('div');
    loadingEl.className = 'chat-message chat-message-assistant chat-message-loading';
    loadingEl.id = 'chat-loading';
    loadingEl.innerHTML = `
      <div class="chat-message-content">
        <div class="chat-loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <p>답변을 생성하고 있습니다...</p>
      </div>
    `;
    chatMessages.appendChild(loadingEl);
    scrollToBottom();
  }

  // Remove loading indicator
  function removeLoading() {
    const loadingEl = document.getElementById('chat-loading');
    if (loadingEl) {
      loadingEl.remove();
    }
  }

  // 대화 컨텍스트를 API 형식으로 변환 (비용 최적화: Context Caching 활용)
  function getConversationHistory() {
    // 시스템 메시지 제외하고 최근 대화만 전송 (비용 최적화)
    const history = messages
      .filter(msg => msg.role === 'user' || msg.role === 'assistant')
      .slice(-10) // 최근 10개 메시지만 (서버 설정과 일치)
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }));
    return history;
  }

  // Send message to DeepSeek API
  async function sendMessage(message) {
    if (isLoading) return;
    
    isLoading = true;
    chatInput.disabled = true;
    chatSend.disabled = true;
    
    // Add user message
    addMessage(message, 'user');
    
    // Show loading
    showLoading();
    
    try {
      // 대화 컨텍스트 가져오기 (비용 최적화: Context Caching 활용)
      const conversationHistory = getConversationHistory();
      
      // Vercel Serverless Function을 통한 API 호출 (보안)
      // 엔드포인트는 trailing slash 없이 사용 (Vercel이 자동으로 처리)
      const response = await fetch(CONFIG.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'omit', // 쿠키 전송 방지 (보안)
        body: JSON.stringify({
          message: message,
          sessionId: sessionId,
          conversationHistory: conversationHistory.length > 0 ? conversationHistory : undefined, // 빈 배열은 전송하지 않음
        }),
        signal: AbortSignal.timeout(CONFIG.timeout),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // 403 Forbidden (Origin 검증 실패)
        if (response.status === 403) {
          throw new Error('요청이 거부되었습니다. 페이지를 새로고침해주세요.');
        }
        
        // Rate limit 오류 처리
        if (response.status === 429) {
          const retryAfter = errorData.retryAfter || 60;
          throw new Error(`요청이 너무 많습니다. ${retryAfter}초 후 다시 시도해주세요.`);
        }
        
        // 서비스 사용 불가 오류
        if (response.status === 503) {
          throw new Error(errorData.error || '서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.');
        }
        
        // 타임아웃 오류
        if (response.status === 504) {
          throw new Error(errorData.error || '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 구체적으로 작성하거나 잠시 후 다시 시도해주세요.');
        }
        
        // 400 Bad Request (입력 검증 실패)
        if (response.status === 400) {
          throw new Error(errorData.error || '입력 형식이 올바르지 않습니다.');
        }
        
        throw new Error(errorData.error || `서버 오류 (${response.status})`);
      }
      
      const data = await response.json();
      removeLoading();
      
      if (data.response && typeof data.response === 'string') {
        addMessage(data.response, 'assistant');
        // 세션 ID 업데이트
        if (data.sessionId) {
          sessionId = data.sessionId;
          localStorage.setItem('chatSessionId', sessionId);
        }
        
        // 개발 환경에서 비용 최적화 정보 표시 (선택적)
        if (data.usage && process.env.NODE_ENV === 'development') {
          console.log('[Chat Widget] Usage:', {
            promptTokens: data.usage.promptTokens,
            completionTokens: data.usage.completionTokens,
            cacheHitRate: data.usage.cacheHitRate,
            isOffPeak: data.usage.isOffPeak,
          });
        }
      } else {
        throw new Error('응답 형식이 올바르지 않습니다.');
      }
    } catch (error) {
      removeLoading();
      let errorMessage = '죄송합니다. 답변을 생성하는 중에 문제가 발생했습니다.';
      let shouldRetry = false;
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMessage = '응답 생성에 시간이 오래 걸리고 있습니다. 잠시 후 다시 시도해주세요.';
        // 타임아웃은 재시도하지 않음 (비효율적)
        shouldRetry = false;
      } else if (error.message) {
        errorMessage = error.message;
        // 네트워크 오류는 재시도 고려
        if (error.message.includes('네트워크') || error.message.includes('fetch')) {
          shouldRetry = true;
        }
      }
      
      addMessage(`❌ ${errorMessage}`, 'assistant');
      
      // 재시도 제안 (타임아웃이 아닌 경우)
      if (shouldRetry && !errorMessage.includes('너무 많습니다')) {
        const retryButton = document.createElement('button');
        retryButton.className = 'chat-retry-button';
        retryButton.textContent = '🔄 다시 시도';
        retryButton.style.cssText = 'margin-top: 0.5rem; padding: 0.5rem 1rem; background: var(--color-primary); color: white; border: none; border-radius: 0.5rem; cursor: pointer;';
        retryButton.onclick = () => {
          retryButton.remove();
          sendMessage(message);
        };
        
        const lastMessage = chatMessages.lastElementChild;
        if (lastMessage) {
          lastMessage.querySelector('.chat-message-content')?.appendChild(retryButton);
        }
      }
    } finally {
      isLoading = false;
      chatInput.disabled = false;
      chatSend.disabled = false;
      chatInput.focus();
    }
  }


  // Debounce function for input events (performance optimization)
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Handle form submission
  function handleSubmit(e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    
    // 클라이언트 측 검증 강화
    if (!message || isLoading) return;
    
    // 최소 길이 검증
    if (message.length < 2) {
      addMessage('❌ 메시지는 최소 2자 이상이어야 합니다.', 'assistant');
      return;
    }
    
    // 최대 길이 검증
    if (message.length > CONFIG.maxMessageLength) {
      addMessage(`❌ 메시지가 너무 깁니다. (최대 ${CONFIG.maxMessageLength}자)`, 'assistant');
      return;
    }
    
    chatInput.value = '';
    sendMessage(message);
  }

  // Optimized input handler with debounce for better INP
  const debouncedInputHandler = debounce(function() {
    // Any input-related side effects can go here
    // Currently just prevents blocking the main thread
  }, 100);

  // Event Listeners
  if (chatToggle) {
    chatToggle.addEventListener('click', toggleChat, { passive: true });
  }
  if (chatClose) {
    chatClose.addEventListener('click', toggleChat, { passive: true });
  }
  if (chatForm) {
    chatForm.addEventListener('submit', handleSubmit);
  }
  
  // Optimize input events for better INP score
  if (chatInput) {
    // Use passive listeners where possible
    chatInput.addEventListener('input', debouncedInputHandler, { passive: true });
    
    // Optimize focus events
    chatInput.addEventListener('focus', function() {
      // Use requestAnimationFrame to avoid blocking
      requestAnimationFrame(() => {
        // Any focus-related initialization
      });
    }, { passive: true });
  }
  
  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      toggleChat();
    }
  });

  // Close when clicking outside (optional)
  chatWindow.addEventListener('click', (e) => {
    if (e.target === chatWindow) {
      toggleChat();
    }
  });

  // Initialize
  initSession();
  showChatIcon();
  
  // Add welcome message if no messages
  if (messages.length === 0) {
    // Welcome message is already in HTML
  }
})();
