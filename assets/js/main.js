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

  // Copy Code Block Button
  document.querySelectorAll('pre code').forEach(codeBlock => {
    const pre = codeBlock.parentElement;
    if (pre.tagName === 'PRE') {
      const button = document.createElement('button');
      button.className = 'copy-code-btn';
      button.innerHTML = 'Copy';
      button.setAttribute('aria-label', 'Copy code');
      button.style.cssText = `
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        padding: 0.25rem 0.5rem;
        background: var(--color-bg-secondary);
        border: 1px solid var(--color-border);
        border-radius: 4px;
        font-size: 0.75rem;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.2s;
      `;
      
      pre.style.position = 'relative';
      pre.appendChild(button);

      pre.addEventListener('mouseenter', () => {
        button.style.opacity = '1';
      });

      pre.addEventListener('mouseleave', () => {
        button.style.opacity = '0';
      });

      button.addEventListener('click', async () => {
        const text = codeBlock.textContent;
        try {
          await navigator.clipboard.writeText(text);
          button.textContent = 'Copied!';
          setTimeout(() => {
            button.textContent = 'Copy';
          }, 2000);
        } catch (err) {
          console.error('Failed to copy:', err);
        }
      });
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
})();
