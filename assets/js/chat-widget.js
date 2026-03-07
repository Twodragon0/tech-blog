// DeepSeek Chat Widget JavaScript
(function() {
  'use strict';

  // Configuration
  const CONFIG = {
    // 엔드포인트: trailing slash 없이 사용 (Vercel이 자동으로 처리)
    apiEndpoint: '/api/chat',
    maxRetries: 1, // 재시도 횟수 (타임아웃 시 재시도는 비효율적)
    timeout: 30000, // 30초 (서버 타임아웃 25초 + 네트워크 여유 5초)
    retryDelay: 2000, // 재시도 전 대기 시간 (ms)
    maxMessageLength: 2000, // 서버와 동일한 제한
  };

  // State
  let isOpen = false;
  let isLoading = false;
  let messages = [];
  let sessionId = null;

  // Development environment detection (browser-compatible)
  const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

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

  // CRITICAL: Force close window immediately on script load
  // This must happen BEFORE any other initialization to prevent auto-opening
  if (chatWindow) {
    // REMOVE inline display style completely (external scripts may add it)
    chatWindow.style.removeProperty('display');
    chatWindow.removeAttribute('style');

    // Remove all opening classes
    chatWindow.classList.remove('chat-widget-window-open');
    chatWindow.classList.remove('chat-widget-user-opened');

    // CRITICAL: Ensure hidden attribute is present (prevents auto-opening)
    chatWindow.setAttribute('hidden', '');
    chatWindow.setAttribute('aria-hidden', 'true');

    isOpen = false;
    if (chatToggle) {
      chatToggle.setAttribute('aria-expanded', 'false');
    }

    // AGGRESSIVE MutationObserver: Block ALL attempts to open window without user action
    // This watches for ANY attempts to modify display, add opening classes, or remove hidden attribute
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'style') {
          // If window is closed, REMOVE any inline display style (external scripts)
          if (!isOpen && chatWindow.hasAttribute('style')) {
            const currentStyle = chatWindow.getAttribute('style');
            if (currentStyle && currentStyle.includes('display')) {
              // Remove entire style attribute to prevent inline style override
              chatWindow.removeAttribute('style');
            }
          }
        }
        if (mutation.attributeName === 'class') {
          // If window is not supposed to be open but opening class was added
          if (!isOpen && (chatWindow.classList.contains('chat-widget-window-open') ||
                          chatWindow.classList.contains('chat-widget-user-opened'))) {
            chatWindow.classList.remove('chat-widget-window-open');
            chatWindow.classList.remove('chat-widget-user-opened');
            if (chatToggle) {
              chatToggle.setAttribute('aria-expanded', 'false');
            }
          }
        }
        if (mutation.attributeName === 'hidden') {
          // If window is closed but hidden attribute was removed, restore it
          if (!isOpen && !chatWindow.hasAttribute('hidden')) {
            chatWindow.setAttribute('hidden', '');
            chatWindow.setAttribute('aria-hidden', 'true');
          }
        }
      });
    });
    // Watch ALL attribute changes, not just style and class
    observer.observe(chatWindow, { attributes: true });
  }

  // Initialize session ID
  function initSession() {
    sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
      sessionId = Date.now().toString();
      localStorage.setItem('chatSessionId', sessionId);
    }
  }

  // Ensure chat icon is visible (CSS handles initial appearance animation)
  function showChatIcon() {
    if (chatToggle) {
      chatToggle.classList.add('chat-widget-toggle-visible');
    }
  }

  // Prevent body scroll when chat is open on mobile
  function preventBodyScroll(prevent) {
    if (typeof window === 'undefined') return;
    if (prevent) {
      document.body.style.overflow = 'hidden';
      document.body.style.paddingRight = '0px'; // Prevent layout shift
    } else {
      document.body.style.overflow = '';
      document.body.style.paddingRight = '';
    }
  }

  // Toggle chat window (NEVER use inline styles - CSS classes only)
  function toggleChat() {
    const wasOpen = isOpen;
    isOpen = !isOpen;

    if (isOpen) {
      // CRITICAL: Remove hidden attribute FIRST to allow CSS to show window
      chatWindow.removeAttribute('hidden');
      chatWindow.setAttribute('aria-hidden', 'false');

      // CRITICAL: Add BOTH classes required by CSS (no inline styles)
      // CSS rule requires: .chat-widget-window.chat-widget-window-open.chat-widget-user-opened:not([hidden])
      requestAnimationFrame(() => {
        chatWindow.classList.add('chat-widget-window-open');
        chatWindow.classList.add('chat-widget-user-opened'); // Requires explicit user action
        chatInput.focus();
        // Scroll to bottom with smooth animation
        setTimeout(() => {
          scrollToBottom();
        }, 100);
      });
      // Prevent body scroll on mobile
      if (window.innerWidth <= 768) {
        preventBodyScroll(true);
      }
    } else {
      // Remove BOTH classes
      chatWindow.classList.remove('chat-widget-window-open');
      chatWindow.classList.remove('chat-widget-user-opened');

      // CRITICAL: Add hidden attribute AFTER removing classes to ensure window is hidden
      chatWindow.setAttribute('hidden', '');
      chatWindow.setAttribute('aria-hidden', 'true');

      // Update toggle button state
      if (chatToggle) {
        chatToggle.setAttribute('aria-expanded', 'false');
      }
      // Restore body scroll on mobile
      if (window.innerWidth <= 768 && wasOpen) {
        setTimeout(() => {
          preventBodyScroll(false);
        }, 300);
      }
    }
    // Update ARIA attributes
    if (chatToggle) {
      chatToggle.setAttribute('aria-expanded', isOpen.toString());
    }
  }

  // Scroll to bottom of messages with smooth animation
  function scrollToBottom(smooth = true) {
    if (!chatMessages) return;
    if (smooth) {
      chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
      });
    } else {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
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
    // XSS prevention: sanitize HTML before innerHTML assignment
    if (typeof DOMPurify !== 'undefined') {
      contentEl.innerHTML = DOMPurify.sanitize(formattedContent, {
        ALLOWED_TAGS: ['h1','h2','h3','h4','h5','h6','p','br','hr','strong','em','del',
          'code','pre','blockquote','ul','ol','li','table','thead','tbody','tr','th','td','div','a','span','mark','svg','polyline','line','path','rect'],
        ALLOWED_ATTR: ['class','href','target','rel','width','height','viewBox','fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','style','d','x1','y1','x2','y2','points','aria-hidden'],
      });
    } else {
      // Fallback: strip all HTML tags when DOMPurify is unavailable (security-first)
      contentEl.textContent = formattedContent.replace(/<[^>]*>/g, '');
    }
    
    const timeEl = document.createElement('div');
    timeEl.className = 'chat-message-time';
    timeEl.textContent = formatTime(message.timestamp);
    
    messageEl.appendChild(contentEl);
    messageEl.appendChild(timeEl);
    
    chatMessages.appendChild(messageEl);
    scrollToBottom();
    
    return messageEl;
  }

  // Format message content (enhanced markdown)
  function formatMessage(content) {
    if (!content) return '';
    
    // Enhanced HTML entity decoding (더 정확한 디코딩)
    // 보안: innerHTML 사용을 피하고 DOMParser 사용
    const decodeHtml = (text) => {
      if (!text || typeof text !== 'string') return '';
      
      // 먼저 숫자 엔티티 디코딩 (&#x2F; 같은 형태)
      text = text.replace(/&#x([0-9A-Fa-f]+);/g, (match, hex) => {
        const code = parseInt(hex, 16);
        // 보안: 제어 문자 및 위험한 문자 범위 제한
        if (code < 0x20 || (code >= 0x7F && code < 0xA0)) {
          return '';
        }
        return String.fromCharCode(code);
      });
      // 10진수 엔티티 디코딩 (&#47; 같은 형태)
      text = text.replace(/&#(\d+);/g, (match, dec) => {
        const code = parseInt(dec, 10);
        // 보안: 제어 문자 및 위험한 문자 범위 제한
        if (code < 0x20 || (code >= 0x7F && code < 0xA0)) {
          return '';
        }
        return String.fromCharCode(code);
      });
      
      // 보안: DOMParser를 사용하지 않고 안전하게 HTML 엔티티 디코딩
      // HTML 파싱을 완전히 방지하여 XSS 공격 차단
      // textContent를 사용하여 안전하게 엔티티 디코딩
      try {
        // 보안: DOMParser의 HTML 파싱 모드를 사용하지 않고, textContent만 사용
        // 이렇게 하면 HTML이 실행되지 않고 텍스트로만 처리됨
        const tempDiv = document.createElement('div');
        // textContent로 설정하면 HTML 엔티티가 자동으로 디코딩되지만 HTML은 실행되지 않음
        tempDiv.textContent = text;
        const decoded = tempDiv.textContent || text;
        
        // 추가 보안: 디코딩된 텍스트에 위험한 패턴이 있는지 확인
        // HTML 태그나 스크립트가 포함되어 있으면 원본 반환
        if (/<[a-z][\s\S]*>/i.test(decoded)) {
          // HTML 태그가 감지되면 원본 반환 (이미 숫자 엔티티는 디코딩됨)
          return text;
        }
        
        return decoded;
      } catch (e) {
        // 파싱 실패 시 원본 반환 (이미 숫자 엔티티는 디코딩됨)
      }
      
      // DOMParser 실패 시 수동으로 일반 엔티티 디코딩
      const entityMap = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#x27;': "'",
        '&#x2F;': '/',
        '&apos;': "'"
      };
      return text.replace(/&(?:amp|lt|gt|quot|#x27|#x2F|apos);/g, (match) => {
        return entityMap[match] || match;
      });
    };
    
    // Escape HTML to prevent XSS (마크다운 파싱 후 최종 적용)
    const escapeHtml = (text) => {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    };
    
    // HTML 엔티티 디코딩 (API 응답에서 올 수 있는 엔티티 처리)
    let formatted = decodeHtml(content);
    
    // XSS 방지를 위해 다시 이스케이프 (마크다운 파싱 전)
    formatted = escapeHtml(formatted);
    
    // Horizontal rules: --- or ***
    formatted = formatted.replace(/^(\*\*\*|---)$/gm, '<hr>');
    
    // Headings: # ## ### #### ##### ######
    formatted = formatted.replace(/^###### (.*)$/gm, '<h6>$1</h6>');
    formatted = formatted.replace(/^##### (.*)$/gm, '<h5>$1</h5>');
    formatted = formatted.replace(/^#### (.*)$/gm, '<h4>$1</h4>');
    formatted = formatted.replace(/^### (.*)$/gm, '<h3>$1</h3>');
    formatted = formatted.replace(/^## (.*)$/gm, '<h2>$1</h2>');
    formatted = formatted.replace(/^# (.*)$/gm, '<h1>$1</h1>');
    
    // Code blocks: ```language\ncode\n```
    formatted = formatted.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
      const escapedCode = escapeHtml(code.trim());
      return `<pre class="code-block"><code class="language-${lang || 'text'}">${escapedCode}</code></pre>`;
    });
    
    // Inline code: `code` (code blocks 이후에 처리)
    formatted = formatted.replace(/`([^`\n]+)`/g, '<code class="inline-code">$1</code>');
    
    // Bold text: **text** or __text__
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // Italic text: *text* or _text_ (bold 이후에 처리, 단독으로만)
    formatted = formatted.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '<em>$1</em>');
    formatted = formatted.replace(/(?<!_)_([^_\n]+?)_(?!_)/g, '<em>$1</em>');
    
    // Strikethrough: ~~text~~
    formatted = formatted.replace(/~~(.*?)~~/g, '<del>$1</del>');
    
    // Blockquotes: > text
    formatted = formatted.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>');
    
    // Markdown tables: | A | B | \n |---|---| \n | 1 | 2 |
    // UI/UX: 챗봇 답변에서 표를 가독성 있게 렌더링 (모바일 가로 스크롤 지원은 CSS에서)
    formatted = formatted.replace(/(^|\n)(\|[^\n]+\|)\n(\|[-:\s|]+\|)\n((?:\|[^\n]+\|\n?)+)/g, function(_, before, headerRow, _sep, bodyBlock) {
      var parseRow = function(row) {
        return row.split('|').map(function(c) { return c.trim(); }).filter(function(c) { return c.length > 0; });
      };
      var thead = parseRow(headerRow);
      var bodyRows = bodyBlock.trim().split('\n').map(function(r) { return parseRow(r); }).filter(function(arr) { return arr.length > 0; });
      if (thead.length === 0) return before + headerRow + '\n' + _sep + '\n' + bodyBlock;
      var html = '<div class="chat-table-wrap"><table class="chat-table"><thead><tr>';
      thead.forEach(function(c) { html += '<th>' + c + '</th>'; });
      html += '</tr></thead><tbody>';
      bodyRows.forEach(function(row) {
        html += '<tr>';
        for (var i = 0; i < thead.length; i++) {
          html += '<td>' + (row[i] || '') + '</td>';
        }
        html += '</tr>';
      });
      html += '</tbody></table></div>';
      return before + html;
    });
    
    // Lists processing: 먼저 줄 단위로 처리
    const lines = formatted.split('\n');
    const processedLines = [];
    let inUnorderedList = false;
    let inOrderedList = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      
      // Unordered list item: - * +
      if (/^[\-\*\+] (.+)$/.test(trimmed)) {
        if (!inUnorderedList) {
          if (inOrderedList) {
            processedLines.push('</ol>');
            inOrderedList = false;
          }
          processedLines.push('<ul>');
          inUnorderedList = true;
        }
        processedLines.push('<li>' + trimmed.replace(/^[\-\*\+] /, '') + '</li>');
      }
      // Ordered list item: 1. 2. etc.
      else if (/^\d+\. (.+)$/.test(trimmed)) {
        if (!inOrderedList) {
          if (inUnorderedList) {
            processedLines.push('</ul>');
            inUnorderedList = false;
          }
          processedLines.push('<ol>');
          inOrderedList = true;
        }
        processedLines.push('<li>' + trimmed.replace(/^\d+\. /, '') + '</li>');
      }
      // Not a list item
      else {
        if (inUnorderedList) {
          processedLines.push('</ul>');
          inUnorderedList = false;
        }
        if (inOrderedList) {
          processedLines.push('</ol>');
          inOrderedList = false;
        }
        processedLines.push(line);
      }
    }
    
    // Close any open lists
    if (inUnorderedList) {
      processedLines.push('</ul>');
    }
    if (inOrderedList) {
      processedLines.push('</ol>');
    }
    
    formatted = processedLines.join('\n');
    
    // Links: [text](url) - 버튼 스타일로 개선
    // 보안: URL 검증 강화
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
      // Validate URL
      try {
        // URL 디코딩 (엔티티가 포함된 경우)
        const decodedUrl = decodeHtml(url);
        
        // 보안: 위험한 스킴 차단
        const dangerousSchemes = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:'];
        const urlLower = decodedUrl.toLowerCase().trim();
        for (const scheme of dangerousSchemes) {
          if (urlLower.startsWith(scheme)) {
            // 위험한 스킴이면 텍스트만 반환
            return escapeHtml(text);
          }
        }
        
        // 상대 경로를 절대 경로로 변환
        let urlToValidate = decodedUrl.trim();
        if (!urlToValidate.includes('://')) {
          // 상대 경로인 경우 현재 도메인 기준으로 절대 경로 생성
          try {
            urlToValidate = new URL(urlToValidate, window.location.origin).href;
          } catch (e) {
            // 상대 경로 파싱 실패 시 텍스트만 반환
            return escapeHtml(text);
          }
        }
        
        const urlObj = new URL(urlToValidate);
        
        // 보안: 허용된 스킴만 허용
        if (urlObj.protocol !== 'http:' && urlObj.protocol !== 'https:') {
          return escapeHtml(text);
        }
        
        // 보안: 위험한 호스트명 차단
        const dangerousHosts = ['localhost', '127.0.0.1', '0.0.0.0', '[::1]'];
        if (dangerousHosts.includes(urlObj.hostname.toLowerCase())) {
          return escapeHtml(text);
        }
        
        // 보안: URL에 위험한 패턴이 포함되어 있는지 확인
        const dangerousPatterns = [
          /javascript:/i,
          /data:text\/html/i,
          /data:text\/javascript/i,
          /vbscript:/i,
          /on\w+\s*=/i
        ];
        
        for (const pattern of dangerousPatterns) {
          if (pattern.test(urlObj.href)) {
            return escapeHtml(text);
          }
        }
        
        // 외부 링크는 아이콘과 함께 버튼 스타일로 표시
        const isExternal = urlObj.hostname !== window.location.hostname;
        const linkClass = isExternal ? 'chat-link-external' : 'chat-link-internal';
        const icon = isExternal ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle; margin-left: 4px;"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>' : '';
        return `<a href="${escapeHtml(urlObj.href)}" target="_blank" rel="noopener noreferrer" class="${linkClass}">${escapeHtml(text)}${icon}</a>`;
      } catch (e) {
        // Invalid URL, return text only
      }
      return escapeHtml(text);
    });
    
    // Paragraphs: 연속된 텍스트를 <p>로 감싸기 (헤딩, 리스트, 코드 블록 제외)
    const paraLines = formatted.split('\n');
    const processed = [];
    let currentParagraph = [];
    
    for (let i = 0; i < paraLines.length; i++) {
      const line = paraLines[i];
      const trimmed = line.trim();
      
      // 블록 요소들은 그대로 유지 (표, 코드, 리스트, 제목 등)
      if (trimmed.startsWith('<h') || 
          trimmed.startsWith('<ul') || trimmed.startsWith('</ul') ||
          trimmed.startsWith('<ol') || trimmed.startsWith('</ol') ||
          trimmed.startsWith('<li') || trimmed.startsWith('</li') ||
          trimmed.startsWith('<pre') || trimmed.includes('</pre>') ||
          trimmed.startsWith('<blockquote') || trimmed.includes('</blockquote>') ||
          trimmed.startsWith('<hr') || trimmed.includes('chat-table-wrap') ||
          trimmed === '') {
        // 현재 단락이 있으면 닫기
        if (currentParagraph.length > 0) {
          const paraText = currentParagraph.join(' ').trim();
          if (paraText) {
            processed.push('<p>' + paraText + '</p>');
          }
          currentParagraph = [];
        }
        if (trimmed !== '') {
          processed.push(line);
        }
      } else {
        currentParagraph.push(line);
      }
    }
    
    // 마지막 단락 처리
    if (currentParagraph.length > 0) {
      const paraText = currentParagraph.join(' ').trim();
      if (paraText) {
        processed.push('<p>' + paraText + '</p>');
      }
    }
    
    formatted = processed.join('\n');
    
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
        signal: (() => {
          if (typeof AbortSignal.timeout === 'function') {
            return AbortSignal.timeout(CONFIG.timeout);
          }
          const controller = new AbortController();
          setTimeout(() => controller.abort(), CONFIG.timeout);
          return controller.signal;
        })(),
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
          const timeoutError = new Error(errorData.error || '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 구체적으로 작성하거나 잠시 후 다시 시도해주세요.');
          timeoutError.timeoutData = errorData; // 추가 정보 저장
          throw timeoutError;
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
        if (data.usage && isDev) {
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
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError' || error.message.includes('시간이 오래 걸리고')) {
        // 서버에서 더 자세한 메시지를 받은 경우 사용
        const timeoutData = error.timeoutData;
        if (timeoutData && timeoutData.suggestion) {
          errorMessage = timeoutData.error + '\n\n💡 ' + timeoutData.suggestion;
        } else {
          errorMessage = '응답 생성에 시간이 오래 걸리고 있습니다. 질문을 더 짧고 구체적으로 작성하거나 잠시 후 다시 시도해주세요.';
        }
        // 타임아웃은 재시도하지 않음 (비효율적)
        shouldRetry = false;
      } else if (error.message) {
        errorMessage = error.message;
        // 네트워크 오류는 재시도 고려
        if (error.message.includes('네트워크') || error.message.includes('fetch') || error.message.includes('연결')) {
          shouldRetry = true;
        }
        // 타임아웃 관련 메시지도 재시도하지 않음
        if (error.message.includes('시간이 오래 걸리고') || error.message.includes('타임아웃')) {
          shouldRetry = false;
        }
      }

      // 콘솔에 상세 오류 로깅 (디버깅용)
      if (isDev) {
        console.error('[Chat Widget] 오류 발생:', {
          name: error.name,
          message: error.message,
          stack: error.stack
        });
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
  
  // Focus trap for modal dialog accessibility
  function handleFocusTrap(e) {
    if (!isOpen) return;

    // Get all focusable elements within the chat window
    const focusableElements = chatWindow.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0]; // Close button
    const lastFocusable = focusableElements[focusableElements.length - 1]; // Send button

    // Handle Tab key
    if (e.key === 'Tab') {
      // Shift + Tab on first element -> wrap to last
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
      // Tab on last element -> wrap to first
      else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  }

  // Close on Escape key and manage focus trap
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      e.preventDefault();
      toggleChat();
    }

    // Activate focus trap when chat is open
    handleFocusTrap(e);
  });

  // Close when clicking outside (optional) - improved with better event handling
  if (chatWindow) {
    chatWindow.addEventListener('click', (e) => {
      // Only close if clicking directly on the window background, not on children
      if (e.target === chatWindow) {
        toggleChat();
      }
    });
  }

  // Initialize
  initSession();
  showChatIcon();

  // Add welcome message if no messages
  if (messages.length === 0) {
    // Welcome message is already in HTML
  }
})();
