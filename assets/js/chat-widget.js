// DeepSeek Chat Widget JavaScript
(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    apiEndpoint: '/api/chat', // Vercel Serverless Function 엔드포인트
    maxRetries: 2, // 프리티어 최적화: 재시도 횟수 감소
    timeout: 10000, // 프리티어 최적화: 10초 (서버 타임아웃 8초 + 여유)
    showIconDelay: 5000, // 5 seconds
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
      // Vercel Serverless Function을 통한 API 호출 (보안)
      const response = await fetch(CONFIG.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          sessionId: sessionId,
        }),
        signal: AbortSignal.timeout(CONFIG.timeout),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        
        // Rate limit 오류 처리
        if (response.status === 429) {
          const retryAfter = errorData.retryAfter || 60;
          throw new Error(`요청이 너무 많습니다. ${retryAfter}초 후 다시 시도해주세요.`);
        }
        
        // 서비스 사용 불가 오류
        if (response.status === 503) {
          throw new Error(errorData.error || '서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.');
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
      } else {
        throw new Error('응답 형식이 올바르지 않습니다.');
      }
    } catch (error) {
      removeLoading();
      let errorMessage = '죄송합니다. 답변을 생성하는 중에 문제가 발생했습니다.';
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMessage = '요청 시간이 초과되었습니다. 네트워크 연결을 확인하고 다시 시도해주세요.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      addMessage(`❌ ${errorMessage}`, 'assistant');
    } finally {
      isLoading = false;
      chatInput.disabled = false;
      chatSend.disabled = false;
      chatInput.focus();
    }
  }


  // Handle form submission
  function handleSubmit(e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message || isLoading) return;
    
    chatInput.value = '';
    sendMessage(message);
  }

  // Event Listeners
  chatToggle.addEventListener('click', toggleChat);
  chatClose.addEventListener('click', toggleChat);
  chatForm.addEventListener('submit', handleSubmit);
  
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
