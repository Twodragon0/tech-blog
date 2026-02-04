// Modern UI/UX JavaScript for Tech Blog - Core Features
// Build: 2026-02-04 - Split optimization (main-core.js)
(function() {
  'use strict';

  // ============================================
  // Performance Utilities
  // ============================================

  // Performance optimization: Use requestIdleCallback to defer non-critical work
  // This prevents Long Tasks (>50ms) that block the main thread
  const scheduleIdleWork = (callback, timeout = 5000) => {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(callback, { timeout });
    } else {
      // Fallback for browsers without requestIdleCallback
      setTimeout(callback, 1);
    }
  };

  // Yield to main thread to prevent long tasks (breaks up execution)
  const yieldToMain = () => {
    return new Promise(resolve => {
      if ('scheduler' in window && 'yield' in scheduler) {
        // Use scheduler.yield() if available (Chrome 115+)
        scheduler.yield().then(resolve);
      } else {
        // Fallback: setTimeout(0) yields to browser
        setTimeout(resolve, 0);
      }
    });
  };

  // Run tasks in chunks to avoid Long Tasks
  const runInChunks = async (tasks, chunkSize = 5) => {
    for (let i = 0; i < tasks.length; i += chunkSize) {
      const chunk = tasks.slice(i, i + chunkSize);
      chunk.forEach(task => task());
      if (i + chunkSize < tasks.length) {
        await yieldToMain(); // Yield between chunks
      }
    }
  };

  // Expose utilities globally for use by other modules
  window.TechBlog = window.TechBlog || {};
  window.TechBlog.scheduleIdleWork = scheduleIdleWork;
  window.TechBlog.yieldToMain = yieldToMain;
  window.TechBlog.runInChunks = runInChunks;

  // ============================================
  // Theme Toggle
  // ============================================

  // Theme detection (critical for preventing flash)
  // 시스템 설정 우선: localStorage에 'system' 또는 값이 없으면 시스템 설정 따름
  const themeToggle = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)');

  // 테마 결정: 저장된 값이 없거나 'system'이면 시스템 설정 따름
  const getEffectiveTheme = () => {
    if (!savedTheme || savedTheme === 'system') {
      return systemPrefersDark.matches ? 'dark' : 'light';
    }
    return savedTheme;
  };

  const currentTheme = getEffectiveTheme();
  document.documentElement.setAttribute('data-theme', currentTheme);

  // Helper function to update aria-pressed attribute
  const updateThemeToggleAria = (theme) => {
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    }
  };

  // Initialize aria-pressed on page load
  updateThemeToggleAria(currentTheme);

  // 시스템 테마 변경 감지 (실시간 반영) - passive for better FID
  systemPrefersDark.addEventListener('change', (e) => {
    const currentSaved = localStorage.getItem('theme');
    // 저장된 값이 없거나 'system'이면 시스템 변경 따름
    if (!currentSaved || currentSaved === 'system') {
      const newTheme = e.matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', newTheme);
      updateThemeToggleAria(newTheme);
    }
  }, { passive: true });

  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      // 수동 변경 시 해당 테마 저장 (시스템 자동 따르기 해제)
      localStorage.setItem('theme', newTheme);
      updateThemeToggleAria(newTheme);
    });

    // 더블클릭으로 시스템 설정으로 복귀
    themeToggle.addEventListener('dblclick', function() {
      localStorage.setItem('theme', 'system');
      const systemTheme = systemPrefersDark.matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', systemTheme);
      updateThemeToggleAria(systemTheme);
    });
  }

  // ============================================
  // Firebase Dynamic Links Handler
  // ============================================

  // Firebase Dynamic Links URL 파라미터 처리 (Buttondown 확인 이메일에서 Gmail 링크 클릭 시)
  (function() {
    'use strict';

    try {
      const urlParams = new URLSearchParams(window.location.search);
      const linkParam = urlParams.get('link');
      // Security: Use URL parsing instead of substring matching
      const currentHostname = window.location.hostname;
      const isFirebaseDomain = currentHostname === 'app.goo.gl' ||
                               currentHostname.endsWith('.firebaseapp.com');
      const hasFirebaseParams = urlParams.has('link') ||
                                urlParams.has('apn') ||
                                urlParams.has('ibi') ||
                                urlParams.has('isi') ||
                                urlParams.has('efr') ||
                                isFirebaseDomain;

      if (hasFirebaseParams) {
        // Firebase Dynamic Links 파라미터가 있는 경우 처리
        if (linkParam) {
          // link 파라미터에 최종 리디렉션 URL이 있음
          try {
            const decodedLink = decodeURIComponent(linkParam);
            // Security: Validate URL before parsing
            if (!decodedLink || decodedLink.length > 2048) {
              // URL too long or empty - potential attack
              return;
            }

            // 보안: 허용된 도메인만 리디렉션
            const allowedDomains = ['tech.2twodragon.com', 'buttondown.com', 'buttondown.email'];
            const linkUrl = new URL(decodedLink);

            // Security: Validate protocol
            if (!['http:', 'https:'].includes(linkUrl.protocol)) {
              return;
            }

            // Security: Additional validation - check protocol and ensure it's http/https
            const allowedProtocols = ['http:', 'https:'];
            if (!allowedProtocols.includes(linkUrl.protocol)) {
              // Only allow http/https protocols
              return;
            }

            if (allowedDomains.some(domain => linkUrl.hostname === domain || linkUrl.hostname.endsWith('.' + domain))) {
              // Security: Use linkUrl.href (sanitized URL) instead of decodedLink to prevent XSS
              window.location.replace(linkUrl.href);
              return;
            }
          } catch (e) {
            // URL 파싱 실패 시 무시하고 계속 진행
          }
        }

        // Firebase Dynamic Links 파라미터 제거하여 깨끗한 URL로 변경
        const cleanUrl = new URL(window.location.href);
        // Firebase Dynamic Links 관련 파라미터 제거
        const paramsToRemove = ['link', 'apn', 'ibi', 'isi', 'efr', 'ofl', 'afl', 'utm_source', 'utm_medium', 'utm_campaign'];
        paramsToRemove.forEach(param => {
          if (cleanUrl.searchParams.has(param)) {
            cleanUrl.searchParams.delete(param);
          }
        });

        // 깨끗한 URL로 교체 (히스토리 추가하지 않음)
        if (cleanUrl.href !== window.location.href) {
          window.history.replaceState({}, '', cleanUrl.href);
        }
      }
    } catch (e) {
      // URL 파라미터 처리 실패 시 조용히 무시
    }
  })();

  // ============================================
  // Mobile Menu
  // ============================================

  scheduleIdleWork(() => {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileNav = document.getElementById('mobile-nav');

    if (mobileMenuBtn && mobileNav) {
      mobileMenuBtn.addEventListener('click', function() {
        mobileNav.classList.toggle('active');
        const isOpen = mobileNav.classList.contains('active');
        mobileMenuBtn.setAttribute('aria-expanded', isOpen);
      }, { passive: true });

      // Close mobile menu when clicking outside
      document.addEventListener('click', function(event) {
        if (!mobileMenuBtn.contains(event.target) && !mobileNav.contains(event.target)) {
          mobileNav.classList.remove('active');
          mobileMenuBtn.setAttribute('aria-expanded', 'false');
        }
      }, { passive: true });
    }
  });

  // ============================================
  // Smooth Scroll for Anchor Links
  // ============================================

  scheduleIdleWork(() => {
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
          const mobileNav = document.getElementById('mobile-nav');
          const mobileMenuBtn = document.getElementById('mobile-menu-btn');
          if (mobileNav && mobileNav.classList.contains('active')) {
            mobileNav.classList.remove('active');
            mobileMenuBtn.setAttribute('aria-expanded', 'false');
          }
        }
      });
    });
  });

  // ============================================
  // Scroll Animations
  // ============================================

  scheduleIdleWork(() => {
    // Intersection Observer for Scroll Animations (non-critical, defer)
    // CLS 최적화: CSS 클래스 기반 애니메이션 사용 (초기 레이아웃 시프트 방지)
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // CSS 클래스 추가로 애니메이션 (레이아웃 시프트 없음)
          entry.target.classList.add('animate-in');
          observer.unobserve(entry.target); // 한 번만 실행
        }
      });
    }, observerOptions);

    // Observe cards for fade-in animation (CSS 기반)
    document.querySelectorAll('.card, .post-card').forEach(card => {
      // 초기 상태는 CSS에서 처리 (레이아웃 시프트 방지)
      observer.observe(card);
    });
  });

  // ============================================
  // Global Functions
  // ============================================

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

  // ============================================
  // Lazy Loading Images
  // ============================================

  scheduleIdleWork(() => {
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
  });

  console.debug('Tech Blog Core UI initialized');
})();
