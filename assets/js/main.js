// Modern UI/UX JavaScript for Tech Blog
(function() {
  'use strict';

  // Console Error Filtering and Enhancement
  // 보안적으로 안전한 에러 메시지 필터링 및 개선
  (function() {
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalLog = console.log;

    // 개발 모드 감지 (URL 파라미터 또는 로컬호스트)
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.search.includes('debug=true');

    // 필터링할 패턴 정의 (보안 확장 프로그램 및 외부 리소스 관련 노이즈)
    const filterPatterns = [
      /📥 Received message.*NmLockState/i,
      /📤 Sending.*NmLockState/i,
      /Duration:.*ms/i,
      /X-Frame-Options may only be set via an HTTP header/i,
      /cache\.agilebits\.com.*404/i,
      /notification\.js.*\[Notification\]/i,
      /giscus\.app.*404.*discussions/i,
      /giscus\.app\/api\/discussions.*404/i,
      /GET.*giscus\.app.*404/i,
      /\[giscus\] Discussion not found/i,
      /Content Security Policy.*connect-src.*violates/i,
      /Refused to connect.*violates.*Content Security Policy/i
    ];

    // 에러 메시지 개선 매핑
    const errorMessageMap = [
      {
        pattern: /DeviceTrust.*access denied.*missing backoffice permission.*missing admin permission/i,
        replacement: {
          message: '⚠️ 보안 확장 프로그램 권한 부족',
          details: 'DeviceTrust 기능을 사용하려면 관리자 권한이 필요합니다. IT 관리자에게 문의하세요.',
          level: 'warn'
        }
      },
      {
        pattern: /DeviceTrust.*access denied/i,
        replacement: {
          message: '⚠️ 보안 확장 프로그램 접근 거부',
          details: '보안 정책에 의해 일부 기능이 제한되었습니다.',
          level: 'warn'
        }
      },
      {
        pattern: /X-Frame-Options may only be set via an HTTP header/i,
        replacement: {
          message: 'ℹ️ 보안 헤더 설정 안내',
          details: 'X-Frame-Options는 서버 HTTP 헤더로만 설정 가능합니다. 메타 태그는 무시됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /Content Security Policy directive.*violates/i,
        replacement: {
          message: 'ℹ️ 콘텐츠 보안 정책',
          details: 'CSP 정책이 적용되어 있습니다. 이는 정상적인 보안 동작입니다.',
          level: 'info'
        }
      },
      {
        pattern: /Refused to connect.*violates.*Content Security Policy/i,
        replacement: {
          message: 'ℹ️ 콘텐츠 보안 정책',
          details: 'CSP 정책에 의해 일부 연결이 차단되었습니다. 이는 정상적인 보안 동작입니다.',
          level: 'info'
        }
      },
      {
        pattern: /\[giscus\] Discussion not found/i,
        replacement: {
          message: 'ℹ️ 댓글 시스템',
          details: '새로운 댓글을 작성하면 자동으로 토론이 생성됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /giscus\.app.*api\/discussions.*404/i,
        replacement: {
          message: 'ℹ️ 댓글 시스템',
          details: '새로운 댓글을 작성하면 자동으로 토론이 생성됩니다.',
          level: 'info'
        }
      }
    ];

    // 메시지가 필터링되어야 하는지 확인
    function shouldFilter(message) {
      if (typeof message !== 'string') return false;
      return filterPatterns.some(pattern => pattern.test(message));
    }

    // 에러 메시지 개선
    function enhanceErrorMessage(message) {
      if (typeof message !== 'string') return null;
      
      for (const { pattern, replacement } of errorMessageMap) {
        if (pattern.test(message)) {
          return replacement;
        }
      }
      return null;
    }

    // 안전한 에러 로깅 (민감 정보 마스킹)
    function safeLog(originalFn, args, level = 'error') {
      const filteredArgs = [];
      let hasEnhancedMessage = false;

      for (const arg of args) {
        // 문자열이 아닌 경우도 체크 (에러 객체 등)
        const messageStr = typeof arg === 'string' ? arg : 
                          (arg?.message || arg?.toString?.() || '');

        if (typeof messageStr === 'string' && messageStr) {
          // 필터링할 메시지는 건너뛰기
          if (shouldFilter(messageStr)) {
            continue;
          }
          
          // 에러 메시지 개선
          const enhanced = enhanceErrorMessage(messageStr);
          if (enhanced) {
            hasEnhancedMessage = true;
            // 개발 환경에서만 상세 정보 표시
            if (isDevelopment) {
              if (enhanced.level === 'info') {
                originalLog(`[${enhanced.message}]`, enhanced.details);
              } else {
                originalWarn(`[${enhanced.message}]`, enhanced.details, '\n원본:', messageStr);
              }
            } else {
              // 프로덕션에서는 중요한 경고만 표시
              if (enhanced.level === 'warn') {
                originalWarn(enhanced.message);
              }
              // info 레벨은 프로덕션에서 표시하지 않음
            }
            continue; // 원본 메시지는 표시하지 않음
          }
        }
        filteredArgs.push(arg);
      }

      // 필터링된 인자가 있거나 개선된 메시지가 없으면 로깅
      if (filteredArgs.length > 0 && !hasEnhancedMessage) {
        originalFn.apply(console, filteredArgs);
      }
    }

    // 콘솔 메서드 오버라이드
    console.error = function(...args) {
      safeLog(originalError, args, 'error');
    };

    console.warn = function(...args) {
      safeLog(originalWarn, args, 'warn');
    };

    // 프로덕션 환경에서 디버그 로그 필터링
    if (!isDevelopment) {
      console.log = function(...args) {
        const filteredArgs = Array.from(args).filter(arg => {
          if (typeof arg === 'string') {
            return !shouldFilter(arg);
          }
          return true;
        });
        if (filteredArgs.length > 0) {
          originalLog.apply(console, filteredArgs);
        }
      };
    }
  })();

  // Theme Toggle
  const themeToggle = document.getElementById('theme-toggle');
  const currentTheme = localStorage.getItem('theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  document.documentElement.setAttribute('data-theme', currentTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
    });
  }

  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileNav = document.getElementById('mobile-nav');

  if (mobileMenuBtn && mobileNav) {
    mobileMenuBtn.addEventListener('click', function() {
      mobileNav.classList.toggle('active');
      const isOpen = mobileNav.classList.contains('active');
      mobileMenuBtn.setAttribute('aria-expanded', isOpen);
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!mobileMenuBtn.contains(event.target) && !mobileNav.contains(event.target)) {
        mobileNav.classList.remove('active');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Smooth Scroll for Anchor Links
  // 숫자로 시작하는 ID를 안전하게 처리하는 헬퍼 함수
  function findElementByHref(href) {
    if (!href || href === '#') return null;
    
    const id = href.substring(1); // '#' 제거
    if (!id) return null;
    
    // getElementById는 숫자로 시작하는 ID도 안전하게 처리
    let target = document.getElementById(id);
    
    // getElementById가 실패한 경우에만 querySelector 시도 (이스케이프 처리)
    if (!target) {
      try {
        // CSS.escape를 사용하여 셀렉터 이스케이프
        if (typeof CSS !== 'undefined' && CSS.escape) {
          target = document.querySelector('#' + CSS.escape(id));
        } else {
          // CSS.escape가 없는 경우 querySelector 시도 (오류 발생 가능)
          target = document.querySelector(href);
        }
      } catch (err) {
        // 셀렉터 오류는 무시 (getElementById가 이미 실패했으므로)
        return null;
      }
    }
    
    return target;
  }

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      const target = findElementByHref(href);
      
      if (target) {
        e.preventDefault();
        const headerHeight = document.querySelector('.site-header')?.offsetHeight || 70;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });

        // Update URL without jumping
        if (history.pushState) {
          history.pushState(null, null, href);
        }

        // Close mobile menu if open
        if (mobileNav && mobileNav.classList.contains('active')) {
          mobileNav.classList.remove('active');
          mobileMenuBtn.setAttribute('aria-expanded', 'false');
        }
      }
    });
  });

  // Search Functionality
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  
  // searchContainer를 안전하게 찾기 (searchInput이 있을 때만)
  let searchContainer = null;
  if (searchInput) {
    searchContainer = searchInput.closest('.search-container');
  }

  if (searchInput && searchResults) {
    let searchData = [];
    let searchDataLoaded = false;

    // Get baseurl dynamically
    function getBaseUrl() {
      // Try to detect from current path
      const pathname = window.location.pathname;
      if (pathname.startsWith('/tech-blog')) {
        return '/tech-blog';
      }
      return '';
    }

    const baseUrl = getBaseUrl();
    const searchJsonUrl = baseUrl + '/search.json';

    // Load search data
    fetch(searchJsonUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        searchData = data;
        searchDataLoaded = true;
      })
      .catch(err => {
        // 개발 환경에서만 상세 에러 표시
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          console.warn('검색 데이터를 불러올 수 없습니다:', err.message);
        }
        // 프로덕션에서는 조용히 실패하고 사용자에게 알림
        searchInput.placeholder = '검색 데이터 로드 실패';
      });

    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.trim().toLowerCase();

      if (query.length < 2) {
        searchResults.innerHTML = '';
        searchResults.style.display = 'none';
        return;
      }

      if (!searchDataLoaded || searchData.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item">검색 데이터를 로드 중...</div>';
        searchResults.style.display = 'block';
        return;
      }

      const results = searchData.filter(item => {
        const title = (item.title || '').toLowerCase();
        const content = (item.content || '').toLowerCase();
        const tags = Array.isArray(item.tags) ? item.tags.join(' ').toLowerCase() : '';
        return title.includes(query) || content.includes(query) || tags.includes(query);
      }).slice(0, 8);

      if (results.length > 0) {
        searchResults.innerHTML = results.map(item => `
          <a href="${item.url}" class="search-result-item">
            <div class="search-result-title">${highlightMatch(item.title, query)}</div>
            <div class="search-result-meta">${item.date || ''} ${item.category ? '· ' + item.category : ''}</div>
            <div class="search-result-excerpt">${(item.content || '').substring(0, 80)}...</div>
          </a>
        `).join('');
        searchResults.style.display = 'block';
      } else {
        searchResults.innerHTML = '<div class="search-result-item no-results">검색 결과가 없습니다.</div>';
        searchResults.style.display = 'block';
      }
    });

    // Highlight matching text
    function highlightMatch(text, query) {
      if (!text || !query) return text;
      const regex = new RegExp(`(${query})`, 'gi');
      return text.replace(regex, '<mark>$1</mark>');
    }

    // Hide search results when clicking outside
    if (searchContainer) {
      document.addEventListener('click', function(event) {
        if (!searchContainer.contains(event.target)) {
          searchResults.style.display = 'none';
        }
      });
    }
  }

  // Intersection Observer for Scroll Animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe cards for fade-in animation
  document.querySelectorAll('.card, .post-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
  });

  // Reading Progress Bar (for post pages)
  const postArticle = document.querySelector('.post-article');
  if (postArticle) {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--color-primary), var(--color-devsecops));
      width: 0%;
      z-index: 9999;
      transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', function() {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const progress = (scrollTop / (documentHeight - windowHeight)) * 100;
      progressBar.style.width = Math.min(progress, 100) + '%';
    });
  }

  // Copy to Clipboard Function
  // KakaoTalk Share Function
  // 카카오톡 공유 함수 (모바일에서는 자동 감지, 데스크톱에서는 링크 복사)
  window.shareKakao = function(url, title, description) {
    // 모바일 환경 감지
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
      // 모바일에서는 카카오톡 링크 공유 (카카오톡 앱이 자동으로 감지)
      // 카카오톡은 Open Graph 메타 태그를 읽어서 미리보기를 표시합니다
      const shareText = `${title}\n\n${description || ''}\n\n${url}`;
      if (navigator.share) {
        navigator.share({
          title: title,
          text: description || '',
          url: url
        }).catch(err => {
          console.log('공유 취소됨:', err);
        });
      } else {
        // Web Share API를 지원하지 않는 경우 링크 복사
        copyToClipboard(url);
        alert('링크가 클립보드에 복사되었습니다. 카카오톡에서 붙여넣기 하세요.');
      }
    } else {
      // 데스크톱에서는 링크 복사 후 안내
      copyToClipboard(url);
      alert('링크가 클립보드에 복사되었습니다.\n카카오톡에서 붙여넣기 하거나, 카카오톡 웹에서 공유하세요.');
    }
  };

  window.copyToClipboard = async function(text) {
    try {
      await navigator.clipboard.writeText(text);
      // Show toast notification
      const toast = document.createElement('div');
      toast.textContent = '링크가 복사되었습니다!';
      toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: var(--color-primary);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: var(--shadow-lg);
        z-index: 10000;
        animation: slideIn 0.3s ease;
      `;
      document.body.appendChild(toast);
      setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Enhanced Code Block with Language Label and Copy Button
  // Use a Set to track processed code blocks and prevent duplicates
  const processedBlocks = new Set();
  
  // Only process .highlight divs to avoid duplicates
  document.querySelectorAll('.highlight').forEach(highlightDiv => {
    // Skip if already processed
    if (processedBlocks.has(highlightDiv)) {
      return;
    }
    
    // Mark as processed
    processedBlocks.add(highlightDiv);
    
    const pre = highlightDiv.querySelector('pre');
    const codeBlock = pre ? pre.querySelector('code') : null;
    
    if (!codeBlock || !pre) return;
    
    // Check if button already exists
    if (highlightDiv.querySelector('.copy-code-btn')) {
      return;
    }

    // Detect language from class names
    // Rouge typically adds classes like: .highlight.python, .highlight .language-python, etc.
    let language = 'code';
    
    // Priority order: highlight div > pre > code
    const highlightClasses = Array.from(highlightDiv.classList);
    const preClasses = Array.from(pre.classList);
    const codeClasses = Array.from(codeBlock.classList);
    
    // Check highlight div classes first (Rouge often adds language class here)
    let langMatch = highlightClasses.find(cls => 
      cls !== 'highlight' && 
      /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
    );
    
    if (!langMatch) {
      // Check pre element classes
      langMatch = preClasses.find(cls => 
        cls !== 'highlight' && 
        /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
      );
    }
    
    if (!langMatch) {
      // Check code element classes (most common: language-xxx)
      langMatch = codeClasses.find(cls => 
        cls.startsWith('language-') || 
        /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
      );
      
      if (langMatch && langMatch.startsWith('language-')) {
        language = langMatch.replace('language-', '').toUpperCase();
      } else if (langMatch) {
        language = langMatch.toUpperCase();
      }
    } else {
      language = langMatch.toUpperCase();
    }

    // Language name mapping for better display
    const langMap = {
      'PYTHON': 'Python',
      'JAVASCRIPT': 'JavaScript',
      'JS': 'JavaScript',
      'BASH': 'Bash',
      'SH': 'Shell',
      'YAML': 'YAML',
      'YML': 'YAML',
      'JSON': 'JSON',
      'HTML': 'HTML',
      'CSS': 'CSS',
      'SQL': 'SQL',
      'GO': 'Go',
      'RUST': 'Rust',
      'JAVA': 'Java',
      'PHP': 'PHP',
      'RUBY': 'Ruby',
      'TYPESCRIPT': 'TypeScript',
      'TS': 'TypeScript',
      'DOCKERFILE': 'Dockerfile',
      'DOCKER': 'Docker',
      'MAKEFILE': 'Makefile',
      'MAKE': 'Make',
      'MARKDOWN': 'Markdown',
      'MD': 'Markdown',
      'XML': 'XML',
      'INI': 'INI',
      'TOML': 'TOML',
      'PROPERTIES': 'Properties',
      'CONF': 'Config',
      'CONFIG': 'Config'
    };
    
    const displayLang = langMap[language] || language;

    // Set language attribute for CSS
    highlightDiv.setAttribute('data-lang', displayLang);
    
    // Ensure highlight div is positioned relatively
    if (!highlightDiv.style.position) {
      highlightDiv.style.position = 'relative';
    }

    // Create copy button
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.setAttribute('type', 'button');
    button.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span class="copy-text">Copy</span>
    `;
    
    highlightDiv.appendChild(button);

    // Copy functionality
    button.addEventListener('click', async (e) => {
      e.stopPropagation();
      e.preventDefault();
      
      const text = codeBlock.textContent || codeBlock.innerText;
      const copyText = button.querySelector('.copy-text');
      const buttonSvg = button.querySelector('svg');
      
      try {
        await navigator.clipboard.writeText(text);
        
        // Update button state - success
        button.classList.add('copied');
        if (copyText) copyText.textContent = 'Copied!';
        if (buttonSvg) {
          buttonSvg.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>';
        }
        
        setTimeout(() => {
          button.classList.remove('copied');
          if (copyText) copyText.textContent = 'Copy';
          if (buttonSvg) {
            buttonSvg.innerHTML = '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>';
          }
        }, 2000);
      } catch (err) {
        console.error('Failed to copy:', err);
        
        // Update button state - error
        button.classList.add('error');
        if (copyText) copyText.textContent = 'Error';
        
        setTimeout(() => {
          button.classList.remove('error');
          if (copyText) copyText.textContent = 'Copy';
        }, 2000);
      }
    });
  });
  
  // Also handle standalone pre code blocks (not wrapped in .highlight)
  document.querySelectorAll('pre code').forEach(codeBlock => {
    const pre = codeBlock.parentElement;
    if (pre.tagName === 'PRE' && !pre.closest('.highlight')) {
      // Check if already processed
      if (processedBlocks.has(pre)) {
        return;
      }
      processedBlocks.add(pre);
      
      // Check if button already exists
      if (pre.querySelector('.copy-code-btn')) {
        return;
      }
      
      // Wrap in highlight div
      const highlightDiv = document.createElement('div');
      highlightDiv.className = 'highlight';
      pre.parentNode.insertBefore(highlightDiv, pre);
      highlightDiv.appendChild(pre);
      
      // Process the newly created highlight div
      const newPre = highlightDiv.querySelector('pre');
      const newCodeBlock = newPre ? newPre.querySelector('code') : null;
      
      if (newCodeBlock && newPre) {
        // Detect language and set up button (reuse logic above)
        let language = 'code';
        const codeClasses = Array.from(newCodeBlock.classList);
        const langMatch = codeClasses.find(cls => 
          cls.startsWith('language-') || 
          /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
        );
        
        if (langMatch) {
          language = langMatch.replace('language-', '').toUpperCase();
        }
        
        const langMap = {
          'PYTHON': 'Python', 'JAVASCRIPT': 'JavaScript', 'JS': 'JavaScript',
          'BASH': 'Bash', 'SH': 'Shell', 'YAML': 'YAML', 'YML': 'YAML',
          'JSON': 'JSON', 'HTML': 'HTML', 'CSS': 'CSS', 'SQL': 'SQL',
          'GO': 'Go', 'RUST': 'Rust', 'JAVA': 'Java', 'PHP': 'PHP',
          'RUBY': 'Ruby', 'TYPESCRIPT': 'TypeScript', 'TS': 'TypeScript',
          'DOCKERFILE': 'Dockerfile', 'DOCKER': 'Docker', 'MAKEFILE': 'Makefile',
          'MAKE': 'Make', 'MARKDOWN': 'Markdown', 'MD': 'Markdown',
          'XML': 'XML', 'INI': 'INI', 'TOML': 'TOML', 'PROPERTIES': 'Properties',
          'CONF': 'Config', 'CONFIG': 'Config'
        };
        
        const displayLang = langMap[language] || language;
        highlightDiv.setAttribute('data-lang', displayLang);
        highlightDiv.style.position = 'relative';
        
        const button = document.createElement('button');
        button.className = 'copy-code-btn';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.setAttribute('type', 'button');
        button.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <span class="copy-text">Copy</span>
        `;
        
        highlightDiv.appendChild(button);
        
        button.addEventListener('click', async (e) => {
          e.stopPropagation();
          e.preventDefault();
          const text = newCodeBlock.textContent || newCodeBlock.innerText;
          const copyText = button.querySelector('.copy-text');
          const buttonSvg = button.querySelector('svg');
          
          try {
            await navigator.clipboard.writeText(text);
            button.classList.add('copied');
            if (copyText) copyText.textContent = 'Copied!';
            if (buttonSvg) {
              buttonSvg.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>';
            }
            setTimeout(() => {
              button.classList.remove('copied');
              if (copyText) copyText.textContent = 'Copy';
              if (buttonSvg) {
                buttonSvg.innerHTML = '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>';
              }
            }, 2000);
          } catch (err) {
            console.error('Failed to copy:', err);
            button.classList.add('error');
            if (copyText) copyText.textContent = 'Error';
            setTimeout(() => {
              button.classList.remove('error');
              if (copyText) copyText.textContent = 'Copy';
            }, 2000);
          }
        });
      }
    }
  });

  // Lazy Loading Images
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
          }
        }
      });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }

  console.log('Tech Blog UI initialized');

  // ============================================
  // Language Dropdown and Translation
  // ============================================
  (function initLanguageDropdown() {
    const langToggle = document.getElementById('lang-toggle');
    const langDropdown = document.getElementById('lang-dropdown');
    const langMenu = document.getElementById('lang-menu');
    const langOptions = document.querySelectorAll('.lang-option[data-lang]');
    const googleTranslateLink = document.getElementById('header-google-translate');

    if (!langToggle || !langDropdown) return;

    // Create toast element for translation status
    let toast = document.querySelector('.translate-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'translate-toast';
      document.body.appendChild(toast);
    }

    // Set Google Translate link
    if (googleTranslateLink) {
      googleTranslateLink.href = `https://translate.google.com/translate?sl=ko&tl=en&u=${encodeURIComponent(window.location.href)}`;
    }

    // Toggle dropdown
    langToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      langDropdown.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!langDropdown.contains(e.target)) {
        langDropdown.classList.remove('active');
      }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        langDropdown.classList.remove('active');
      }
    });

    // Translation state
    let currentLang = 'ko';
    let originalContent = {};
    let translationCache = {};
    let isInitialized = false;

    // Save original content
    function saveOriginalContent() {
      if (isInitialized) return;

      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      if (postContent) originalContent.postContent = postContent.innerHTML;
      if (postTitle) originalContent.postTitle = postTitle.textContent;

      originalContent.cardTitles = [];
      cardTitles.forEach((el, i) => {
        originalContent.cardTitles[i] = el.textContent;
      });

      originalContent.cardExcerpts = [];
      cardExcerpts.forEach((el, i) => {
        originalContent.cardExcerpts[i] = el.textContent;
      });

      isInitialized = true;
    }

    // Show toast notification
    function showToast(message, type) {
      toast.textContent = message;
      toast.className = 'translate-toast show ' + type;

      if (type === 'success' || type === 'error') {
        setTimeout(() => {
          toast.classList.remove('show');
        }, 3000);
      }
    }

    // Get language name
    function getLanguageName(lang) {
      const names = {
        'ko': '한국어',
        'en': 'English',
        'ja': '日本語',
        'zh': '中文'
      };
      return names[lang] || lang;
    }

    // Check if text is already in target language (simple heuristic)
    function isAlreadyInTargetLanguage(text, targetLang) {
      if (targetLang === 'ko') {
        // Check if text contains Korean characters
        return /[가-힣]/.test(text);
      } else if (targetLang === 'en') {
        // Check if text is mostly English (has English words and few Korean characters)
        const koreanChars = (text.match(/[가-힣]/g) || []).length;
        const englishWords = (text.match(/[a-zA-Z]+/g) || []).length;
        return englishWords > koreanChars * 2 && koreanChars < text.length * 0.1;
      }
      return false;
    }

    // Split long text into chunks for translation
    function splitTextIntoChunks(text, maxLength = 500) {
      if (text.length <= maxLength) return [text];
      
      const chunks = [];
      const sentences = text.split(/([.!?]\s+|\.\s+)/);
      let currentChunk = '';
      
      for (let i = 0; i < sentences.length; i++) {
        const sentence = sentences[i];
        if ((currentChunk + sentence).length <= maxLength) {
          currentChunk += sentence;
        } else {
          if (currentChunk) chunks.push(currentChunk.trim());
          currentChunk = sentence;
        }
      }
      if (currentChunk) chunks.push(currentChunk.trim());
      
      return chunks.filter(chunk => chunk.length > 0);
    }

    // Translation cache for individual text chunks
    const textTranslationCache = {};

    // Translate text using MyMemory API with retry logic
    async function translateText(text, sourceLang, targetLang, retries = 2) {
      if (!text || text.trim().length === 0) return text;

      // Skip if already in target language
      if (isAlreadyInTargetLanguage(text, targetLang)) {
        return text;
      }

      // Check cache first
      const cacheKey = `${sourceLang}-${targetLang}-${text}`;
      if (textTranslationCache[cacheKey]) {
        return textTranslationCache[cacheKey];
      }

      const langMap = {
        'en': 'en-US',
        'ja': 'ja-JP',
        'zh': 'zh-CN',
        'ko': 'ko-KR'
      };

      const targetLangCode = langMap[targetLang] || targetLang;
      const sourceLangCode = langMap[sourceLang] || sourceLang;

      // Handle long text by splitting into chunks
      if (text.length > 500) {
        const chunks = splitTextIntoChunks(text, 500);
        const translatedChunks = [];
        
        // Process chunks in parallel for better performance
        const chunkPromises = chunks.map(async (chunk) => {
          const translated = await translateText(chunk, sourceLang, targetLang, retries);
          return translated || chunk;
        });
        
        const results = await Promise.all(chunkPromises);
        const translated = results.join(' ');
        
        // Cache the result
        textTranslationCache[cacheKey] = translated;
        return translated;
      }

      // Translate short text
      for (let attempt = 0; attempt <= retries; attempt++) {
        try {
          // Create abort controller for timeout
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
          
          const response = await fetch(
            `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${sourceLangCode}|${targetLangCode}`,
            {
              method: 'GET',
              headers: {
                'Accept': 'application/json'
              },
              signal: controller.signal
            }
          );
          
          clearTimeout(timeoutId);

          if (!response.ok) {
            if (attempt < retries) {
              await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
              continue;
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const data = await response.json();

          if (data.responseStatus === 200 && data.responseData && data.responseData.translatedText) {
            const translated = data.responseData.translatedText;
            // Check if translation is valid (not same as original for non-English)
            if (translated && translated !== text) {
              // Cache the result
              textTranslationCache[cacheKey] = translated;
              return translated;
            }
          }

          // If translation failed, return original text
          textTranslationCache[cacheKey] = text;
          return text;
        } catch (error) {
          if (attempt < retries && error.name !== 'AbortError') {
            await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
            continue;
          }
          // Only log in development mode
          if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.warn('Translation failed:', error.message, text.substring(0, 50));
          }
          // Cache the original text to avoid repeated failures
          textTranslationCache[cacheKey] = text;
          return text;
        }
      }

      return text;
    }

    // Translate page content
    async function translatePage(targetLang) {
      saveOriginalContent();

      // Check cache
      if (translationCache[targetLang]) {
        applyTranslation(translationCache[targetLang]);
        return;
      }

      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      const translation = {};
      let totalItems = 0;
      let translatedItems = 0;

      // Count items to translate
      if (postTitle && originalContent.postTitle) totalItems++;
      if (postContent && originalContent.postContent) {
        const textElements = postContent.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote');
        totalItems += textElements.length;
      }
      totalItems += cardTitles.length + cardExcerpts.length;

      // Translate title first (priority)
      if (postTitle && originalContent.postTitle) {
        try {
          translation.postTitle = await translateText(originalContent.postTitle, 'ko', targetLang);
          translatedItems++;
          // Apply title immediately for better UX
          if (translation.postTitle && translation.postTitle !== originalContent.postTitle) {
            postTitle.textContent = translation.postTitle;
          }
          showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
        } catch (error) {
          console.warn('Title translation failed:', error);
          translation.postTitle = originalContent.postTitle;
        }
      }

      // Translate post content with batch processing for better performance
      if (postContent && originalContent.postContent) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = originalContent.postContent;
        const textElements = Array.from(tempDiv.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote, code:not(pre code), span:not(.highlight), div:not(.code-block):not(.highlight)')).filter(el => {
          const text = el.textContent.trim();
          // Filter out empty elements, code blocks, and elements with code children
          return text && !el.closest('pre') && !el.closest('code') && !el.querySelector('code');
        });

        // Process in batches for better performance
        const batchSize = 5;
        for (let i = 0; i < textElements.length; i += batchSize) {
          const batch = textElements.slice(i, i + batchSize);
          
          // Process batch in parallel
          const batchPromises = batch.map(async (el) => {
            const text = el.textContent.trim();
            
            // Only translate if it's mostly text content
            const hasOnlyTextChildren = Array.from(el.childNodes).every(node => 
              node.nodeType === Node.TEXT_NODE || 
              (node.nodeType === Node.ELEMENT_NODE && (node.tagName === 'STRONG' || node.tagName === 'EM' || node.tagName === 'B' || node.tagName === 'I' || node.tagName === 'A'))
            );

            if (hasOnlyTextChildren && text.length > 0) {
              try {
                const translated = await translateText(text, 'ko', targetLang);
                if (translated && translated !== text) {
                  // Security: Always use textContent instead of innerHTML to prevent XSS attacks
                  // textContent automatically escapes HTML and prevents script injection
                  if (el.children.length > 0) {
                    // For elements with children, update text content of each child safely
                    const children = Array.from(el.children);
                    // Split translated text by whitespace to distribute to children
                    const words = translated.split(/\s+/);
                    let wordIndex = 0;
                    
                    children.forEach((child) => {
                      if (wordIndex < words.length) {
                        // Security: textContent escapes HTML, preventing XSS
                        child.textContent = words[wordIndex];
                        wordIndex++;
                      }
                    });
                    
                    // If we have remaining words or structure mismatch, update parent textContent
                    if (wordIndex < words.length || children.length === 0) {
                      // Security: textContent is safe - it escapes HTML automatically
                      el.textContent = translated;
                    }
                  } else {
                    // Security: textContent automatically escapes HTML, preventing XSS
                    el.textContent = translated;
                  }
                }
              } catch (error) {
                // Continue on error
              }
            }
          });

          await Promise.all(batchPromises);
          translatedItems += batch.length;
          
          // Update progress every batch
          if (translatedItems % 5 === 0 || i + batchSize >= textElements.length) {
            showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
          }
          
          // Small delay between batches to avoid rate limiting
          if (i + batchSize < textElements.length) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }

        translation.postContent = tempDiv.innerHTML;
      }

      // Translate card titles in parallel
      translation.cardTitles = [];
      if (cardTitles.length > 0 && originalContent.cardTitles) {
        const titlePromises = Array.from(cardTitles).map(async (el, i) => {
          if (originalContent.cardTitles[i]) {
            return await translateText(originalContent.cardTitles[i], 'ko', targetLang);
          }
          return null;
        });
        translation.cardTitles = await Promise.all(titlePromises);
        translatedItems += cardTitles.length;
        showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
      }

      // Translate card excerpts in parallel
      translation.cardExcerpts = [];
      if (cardExcerpts.length > 0 && originalContent.cardExcerpts) {
        const excerptPromises = Array.from(cardExcerpts).map(async (el, i) => {
          if (originalContent.cardExcerpts[i]) {
            return await translateText(originalContent.cardExcerpts[i], 'ko', targetLang);
          }
          return null;
        });
        translation.cardExcerpts = await Promise.all(excerptPromises);
        translatedItems += cardExcerpts.length;
      }

      // Cache and apply translation
      translationCache[targetLang] = translation;
      applyTranslation(translation);
    }

    // Apply translation to page
    function applyTranslation(translation) {
      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      // Apply title translation (ensure it's applied even if already set)
      if (postTitle && translation.postTitle && translation.postTitle !== originalContent.postTitle) {
        postTitle.textContent = translation.postTitle;
      }

      // Apply post content translation
      if (postContent && translation.postContent) {
        postContent.innerHTML = translation.postContent;
      }

      // Apply card titles
      if (translation.cardTitles) {
        cardTitles.forEach((el, i) => {
          if (translation.cardTitles[i] && translation.cardTitles[i] !== originalContent.cardTitles?.[i]) {
            el.textContent = translation.cardTitles[i];
          }
        });
      }

      // Apply card excerpts
      if (translation.cardExcerpts) {
        cardExcerpts.forEach((el, i) => {
          if (translation.cardExcerpts[i] && translation.cardExcerpts[i] !== originalContent.cardExcerpts?.[i]) {
            el.textContent = translation.cardExcerpts[i];
          }
        });
      }
    }

    // Restore original content
    function restoreOriginal() {
      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      if (postContent && originalContent.postContent) {
        postContent.innerHTML = originalContent.postContent;
      }

      if (postTitle && originalContent.postTitle) {
        postTitle.textContent = originalContent.postTitle;
      }

      cardTitles.forEach((el, i) => {
        if (originalContent.cardTitles && originalContent.cardTitles[i]) {
          el.textContent = originalContent.cardTitles[i];
        }
      });

      cardExcerpts.forEach((el, i) => {
        if (originalContent.cardExcerpts && originalContent.cardExcerpts[i]) {
          el.textContent = originalContent.cardExcerpts[i];
        }
      });
    }

    // Language option click handler
    langOptions.forEach(option => {
      option.addEventListener('click', async function() {
        const targetLang = this.dataset.lang;

        if (targetLang === currentLang) {
          langDropdown.classList.remove('active');
          return;
        }

        // Update active state
        langOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');

        // Update post page language selector if exists
        const postLangBtns = document.querySelectorAll('.language-tools .lang-btn');
        postLangBtns.forEach(btn => {
          btn.classList.remove('active');
          if (btn.dataset.lang === targetLang) {
            btn.classList.add('active');
          }
        });

        // Close dropdown
        langDropdown.classList.remove('active');

        // Show loading
        showToast('번역 중...', 'loading');

        try {
          if (targetLang === 'ko') {
            restoreOriginal();
            showToast('원본으로 복원되었습니다', 'success');
          } else {
            await translatePage(targetLang);
            showToast(`${getLanguageName(targetLang)}로 번역되었습니다`, 'success');
          }
          currentLang = targetLang;
        } catch (error) {
          console.error('Translation error:', error);
          showToast('번역 실패. 다시 시도해주세요.', 'error');
        }
      });
    });

    // Sync with post page language selector if exists
    const postLangBtns = document.querySelectorAll('.language-tools .lang-btn');
    postLangBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const targetLang = this.dataset.lang;

        // Update header dropdown active state
        langOptions.forEach(opt => {
          opt.classList.remove('active');
          if (opt.dataset.lang === targetLang) {
            opt.classList.add('active');
          }
        });

        currentLang = targetLang;
      });
    });
  })();

  // Fix Korean image filename URL encoding
  // 한글 파일명을 가진 이미지의 URL 인코딩 문제 해결
  (function() {
    function fixImageUrls() {
      const images = document.querySelectorAll('img.post-image, img[src*="assets/images"]');
      images.forEach(img => {
        const src = img.getAttribute('src');
        if (src && /[가-힣]/.test(src)) {
          // 한글이 포함된 경우 URL 인코딩
          // 상대 경로인 경우 직접 처리
          const pathParts = src.split('/');
          const filename = pathParts[pathParts.length - 1];
          if (filename && /[가-힣]/.test(filename)) {
            // 파일명만 URL 인코딩 (경로는 그대로 유지)
            const encodedFilename = encodeURIComponent(filename);
            pathParts[pathParts.length - 1] = encodedFilename;
            const newSrc = pathParts.join('/');
            // 이미 인코딩된 경우 스킵
            if (newSrc !== src) {
              img.src = newSrc;
            }
          }
        }
      });
    }

    // DOM 로드 후 실행
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fixImageUrls);
    } else {
      fixImageUrls();
    }

    // 동적으로 추가된 이미지도 처리
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
          fixImageUrls();
        }
      });
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  })();
})();
