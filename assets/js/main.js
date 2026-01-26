// Modern UI/UX JavaScript for Tech Blog
(function() {
  'use strict';
  
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
  
  // Critical initialization (runs immediately)
  const initCritical = () => {
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

    document.documentElement.setAttribute('data-theme', getEffectiveTheme());

    // 시스템 테마 변경 감지 (실시간 반영)
    systemPrefersDark.addEventListener('change', (e) => {
      const currentSaved = localStorage.getItem('theme');
      // 저장된 값이 없거나 'system'이면 시스템 변경 따름
      if (!currentSaved || currentSaved === 'system') {
        document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
      }
    });

    if (themeToggle) {
      themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        // 수동 변경 시 해당 테마 저장 (시스템 자동 따르기 해제)
        localStorage.setItem('theme', newTheme);
      });

      // 더블클릭으로 시스템 설정으로 복귀
      themeToggle.addEventListener('dblclick', function() {
        localStorage.setItem('theme', 'system');
        const systemTheme = systemPrefersDark.matches ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', systemTheme);
      });
    }
  };
  
  // Console Error Filtering and Enhancement (runs immediately - critical for error handling)
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
      // Giscus 404 에러 (토론이 아직 생성되지 않은 경우 정상)
      /giscus\.app.*404.*discussions/i,
      /giscus\.app\/api\/discussions.*404/i,
      /GET.*giscus\.app.*404/i,
      /GET.*giscus\.app\/api\/discussions.*404/i,
      /giscus\.app\/api\/discussions.*\b404\b/i,
      /\b404\b.*Not Found.*giscus|giscus.*\b404\b.*Not Found/i,
      /\[giscus\] Discussion not found/i,
      /giscus.*404/i,
      /widget.*giscus.*404/i,
      /Failed to load resource.*giscus.*404/i,
      /giscus\.app.*\d+ms/i,
      /https:\/\/giscus\.app\/.*widget.*\d+ms/i,
      // SES (Secure EcmaScript) - Google AdSense 보안 메커니즘
      /SES Removing unpermitted intrinsics/i,
      /lockdown-install/i,
      /lockdown-install\.js/i,
      // Google AdSense 400 에러 (광고가 없거나 계정 문제일 수 있음)
      /googleads.*400/i,
      /googlesyndication.*400/i,
      /doubleclick.*400/i,
      /doublecl.*400/i,
      /ads\?client.*400/i,
      /pagead\/ads.*400/i,
      /Failed to load resource.*status of 400.*ads/i,
      /Failed to load resource.*status of 400.*googleads/i,
      /Failed to load resource.*status of 400.*doubleclick/i,
      /Failed to load resource.*status of 400.*googlesyndication/i,
      /Content Security Policy.*violates/i,
      /Refused to connect.*violates.*Content Security Policy/i,
      /Refused to load.*violates.*Content Security Policy/i,
      /Loading the script.*violates.*Content Security Policy/i,
      /Framing.*violates.*Content Security Policy/i,
      /frame-ancestors\s*'self'|'self'\s*frame-ancestors/i,
      /report-only.*Content Security Policy|Content Security Policy.*report-only/i,
      /The violation has been logged/i,
      /Unchecked runtime\.lastError/i,
      /The message port closed before a response was received/i,
      /runtime\.lastError.*message port|message port.*response was received/i,
      /Failed to load resource.*404/i,
      /Failed to execute.*postMessage/i,
      /The target origin provided.*does not match/i,
      /favicon\.png.*404/i,
      /favicon.*404/i,
      /apple-touch-icon.*404/i,
      /GET.*favicon/i,
      /GET.*apple-touch-icon/i,
      // Service Worker 정보 메시지 필터링 (에러 아님)
      /\[Service Worker\] New version available/i,
      /Service Worker.*registered/i,
      /Service Worker.*activated/i,
      // 성능 경고 필터링 (외부 리소스 로딩 지연은 정상)
      /\[Performance\] Slow resource/i,
      /Slow resource.*vercel/i,
      /Slow resource.*giscus/i,
      /Slow resource.*googlesyndication/i,
      // Google Ads 403 에러 필터링 (AdSense 계정 문제일 수 있음)
      /adsbygoogle\.js.*403/i,
      /pagead2\.googlesyndication\.com.*403/i,
      /GET.*adsbygoogle.*403/i,
      /GET.*googlesyndication.*403/i,
      /net::ERR_ABORTED.*403.*googlesyndication/i,
      /googlesyndication.*net::ERR_ABORTED/i,
      /adsbygoogle.*Forbidden/i,
      // Vercel Speed Insights 429 에러 필터링 (Rate Limiting)
      /speed-insights.*429/i,
      /vitals.*429/i,
      /_vercel\/speed-insights.*429/i,
      /POST.*speed-insights.*429/i,
      /Too Many Requests.*speed-insights/i,
      /speed-insights.*Too Many Requests/i,
      // Firebase Dynamic Links 오류 필터링 (2025년 8월 25일 서비스 종료로 인한 오류)
      /firebase.*dynamic.*link/i,
      /Invalid dynamic link/i,
      /firebaseapp\.com.*dynamic/i,
      /app\.goo\.gl/i,
      /firebase.*link.*invalid/i,
      // 네트워크 요청에서 Firebase Dynamic Links 오류 필터링
      /Failed to load resource.*firebase/i,
      /Failed to load resource.*app\.goo\.gl/i,
      /Network request failed.*firebase/i,
      /Network request failed.*app\.goo\.gl/i,
      /GET.*firebaseapp\.com/i,
      /GET.*app\.goo\.gl/i,
      // 이미지 404 에러 필터링 (WebP fallback이 처리함)
      /\.webp.*404/i,
      /image.*404.*Not Found/i,
      /Failed to load image/i,
      /\.webp.*404/i,
      /GET.*\.webp.*404/i,
      /assets\/images.*\.webp.*404/i,
      /Failed to load resource.*\.webp/i,
      /Failed to load resource.*\.png.*404/i,
      /diagrams\/.*\.png.*404/i,
      /diagrams\/.*\.webp.*404/i,
      /Download the React DevTools/i,
      /Download the Apollo DevTools/i,
      // Mermaid.js 에러 필터링 (다이어그램 렌더링 실패는 정상일 수 있음)
      /mermaid.*Uncaught.*promise/i,
      /mermaid.*error/i
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
        pattern: /Content Security Policy.*violates/i,
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
        pattern: /Refused to load.*violates.*Content Security Policy/i,
        replacement: {
          message: 'ℹ️ 콘텐츠 보안 정책',
          details: 'CSP 정책에 의해 일부 리소스 로드가 차단되었습니다. 이는 정상적인 보안 동작입니다.',
          level: 'info'
        }
      },
      {
        pattern: /Loading the script.*violates.*Content Security Policy/i,
        replacement: {
          message: 'ℹ️ 콘텐츠 보안 정책',
          details: 'CSP 정책에 의해 일부 스크립트 로드가 차단되었습니다. 이는 정상적인 보안 동작입니다.',
          level: 'info'
        }
      },
      {
        pattern: /Framing.*violates.*Content Security Policy/i,
        replacement: {
          message: 'ℹ️ 콘텐츠 보안 정책',
          details: 'CSP 정책에 의해 일부 프레임 로드가 차단되었습니다. 이는 정상적인 보안 동작입니다.',
          level: 'info'
        }
      },
      {
        pattern: /Failed to execute.*postMessage/i,
        replacement: {
          message: 'ℹ️ 브라우저 보안',
          details: '브라우저 보안 정책에 의한 메시지입니다. 무시해도 됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /The target origin provided.*does not match/i,
        replacement: {
          message: 'ℹ️ 브라우저 보안',
          details: '브라우저 보안 정책에 의한 메시지입니다. 무시해도 됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /Failed to load resource.*404/i,
        replacement: {
          message: 'ℹ️ 리소스 로드',
          details: '일부 리소스를 불러올 수 없습니다. 무시해도 됩니다.',
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
      },
      {
        pattern: /giscus.*404/i,
        replacement: {
          message: 'ℹ️ 댓글 시스템',
          details: '새로운 댓글을 작성하면 자동으로 토론이 생성됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /favicon.*404/i,
        replacement: {
          message: 'ℹ️ 아이콘',
          details: 'Favicon 파일이 없습니다. 기본 아이콘이 사용됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /\.webp.*404|GET.*\.webp.*404|assets\/images.*\.webp.*404|Failed to load resource.*\.webp|diagrams\/.*\.(png|webp).*404/i,
        replacement: {
          message: 'ℹ️ 이미지 최적화 (WebP Fallback)',
          details: 'WebP 이미지가 없어 원본 이미지를 사용합니다. 정상 동작입니다.',
          level: 'info'
        }
      },
      {
        pattern: /apple-touch-icon.*404/i,
        replacement: {
          message: 'ℹ️ 아이콘',
          details: 'Apple touch icon 파일이 없습니다. 무시해도 됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /GET.*favicon/i,
        replacement: {
          message: 'ℹ️ 아이콘',
          details: 'Favicon 요청입니다. 무시해도 됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /Unchecked runtime\.lastError/i,
        replacement: {
          message: 'ℹ️ 브라우저 확장 프로그램',
          details: '브라우저 확장 프로그램 관련 메시지입니다. 무시해도 됩니다.',
          level: 'info'
        }
      },
      {
        pattern: /The message port closed before a response was received/i,
        replacement: {
          message: 'ℹ️ 브라우저 확장 프로그램',
          details: '브라우저 확장 프로그램 통신 관련 메시지입니다. 무시해도 됩니다.',
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

    // 전역 에러 핸들러: Firebase Dynamic Links, Giscus, AdSense 및 기타 무시할 수 있는 오류 처리
    const originalWindowError = window.onerror;
    window.onerror = function(message, source, lineno, colno, error) {
      // 소스 URL도 확인 (네트워크 에러 필터링)
      const sourceStr = source || '';
      const fullMessage = (typeof message === 'string' ? message : String(message)) + ' ' + sourceStr;
      
      // Firebase Dynamic Links 오류 필터링 (2025년 8월 25일 서비스 종료)
      if (typeof message === 'string' && (
        /firebase.*dynamic.*link/i.test(message) ||
        /Invalid dynamic link/i.test(message) ||
        /firebaseapp\.com/i.test(message) ||
        /app\.goo\.gl/i.test(message)
      )) {
        // 조용히 무시 (Firebase Dynamic Links는 서비스가 종료되었으므로 오류는 정상)
        return true; // 에러 처리됨을 표시
      }
      
      // Giscus 404 에러 필터링 (토론이 아직 생성되지 않은 경우 정상)
      if (/giscus\.app/i.test(fullMessage) && /404/i.test(fullMessage)) {
        return true;
      }
      
      // Google AdSense 400 에러 필터링 (광고가 없거나 계정 문제일 수 있음)
      if (/(googleads|googlesyndication|doubleclick|pagead)/i.test(fullMessage) && /400/i.test(fullMessage)) {
        return true;
      }
      
      // SES 경고 필터링 (Google AdSense 보안 메커니즘)
      if (/SES Removing|lockdown-install/i.test(fullMessage)) {
        return true;
      }
      
      // 기타 필터링된 오류도 무시
      if (shouldFilter(fullMessage)) {
        return true;
      }
      
      // 원래 핸들러가 있으면 호출
      if (originalWindowError) {
        return originalWindowError.call(this, message, source, lineno, colno, error);
      }
      
      return false; // 기본 에러 처리 계속
    };

    // Unhandled Promise Rejection 핸들러
    window.addEventListener('unhandledrejection', function(event) {
      const reason = event.reason;
      const reasonStr = reason && typeof reason === 'object' ? reason.toString() : String(reason);
      
      // Firebase Dynamic Links 관련 Promise rejection 필터링
      if (/firebase.*dynamic.*link/i.test(reasonStr) ||
          /Invalid dynamic link/i.test(reasonStr) ||
          /firebaseapp\.com/i.test(reasonStr) ||
          /app\.goo\.gl/i.test(reasonStr)) {
        event.preventDefault(); // 기본 에러 처리 방지
        return;
      }
      
      // Giscus 404 에러 필터링
      if (/giscus\.app/i.test(reasonStr) && /404/i.test(reasonStr)) {
        event.preventDefault();
        return;
      }
      
      // Google AdSense 400 에러 필터링
      if (/(googleads|googlesyndication|doubleclick|pagead)/i.test(reasonStr) && /400/i.test(reasonStr)) {
        event.preventDefault();
        return;
      }
      
      // 기타 필터링된 오류도 무시
      if (shouldFilter(reasonStr)) {
        event.preventDefault();
        return;
      }
    }, { passive: true });

    // 네트워크 요청에서 Firebase Dynamic Links 오류 필터링
    // fetch API 래핑
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
      
      // Firebase Dynamic Links 관련 요청은 조용히 실패 처리
      if (/firebaseapp\.com/i.test(url) || /app\.goo\.gl/i.test(url)) {
        return Promise.reject(new Error('Firebase Dynamic Links service has been discontinued'));
      }
      
      return originalFetch.apply(this, args).catch(function(error) {
        const errorMessage = error?.message || error?.toString() || '';
        const requestUrl = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
        const fullError = errorMessage + ' ' + requestUrl;
        
        // Firebase Dynamic Links 관련 네트워크 오류 필터링
        if (/firebase.*dynamic.*link/i.test(fullError) ||
            /firebaseapp\.com/i.test(fullError) ||
            /app\.goo\.gl/i.test(fullError) ||
            /Invalid dynamic link/i.test(fullError)) {
          // 조용히 무시 (Firebase Dynamic Links는 서비스가 종료되었으므로 오류는 정상)
          return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
        }
        
        // Giscus 404 에러 필터링 (토론이 아직 생성되지 않은 경우 정상)
        if (/giscus\.app/i.test(requestUrl) && (error?.status === 404 || /404/i.test(errorMessage))) {
          return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
        }
        
        // Google AdSense 400 에러 필터링 (광고가 없거나 계정 문제일 수 있음)
        if (/(googleads|googlesyndication|doubleclick|pagead)/i.test(requestUrl) && 
            (error?.status === 400 || /400/i.test(errorMessage))) {
          return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
        }
        
        throw error;
      });
    };

    // XMLHttpRequest 래핑 (레거시 브라우저 지원)
    if (window.XMLHttpRequest) {
      const OriginalXHR = window.XMLHttpRequest;
      window.XMLHttpRequest = function() {
        const xhr = new OriginalXHR();
        const originalOpen = xhr.open;
        
        xhr.open = function(method, url, ...rest) {
          // Firebase Dynamic Links 관련 요청은 조용히 차단
          if (/firebaseapp\.com/i.test(url) || /app\.goo\.gl/i.test(url)) {
            // 빈 응답으로 처리
            xhr.readyState = 4;
            xhr.status = 200;
            xhr.statusText = 'OK';
            xhr.responseText = '';
            return;
          }
          
          // Giscus 404 에러 필터링 (토론이 아직 생성되지 않은 경우 정상)
          if (/giscus\.app/i.test(url)) {
            const originalOnError = xhr.onerror;
            xhr.onerror = function() {
              // 404는 조용히 무시
              if (xhr.status === 404) {
                xhr.readyState = 4;
                xhr.status = 200;
                xhr.statusText = 'OK';
                xhr.responseText = '';
                return;
              }
              if (originalOnError) originalOnError.call(this);
            };
          }
          
          // Google AdSense 400 에러 필터링 (광고가 없거나 계정 문제일 수 있음)
          if (/(googleads|googlesyndication|doubleclick|pagead)/i.test(url)) {
            const originalOnError = xhr.onerror;
            xhr.onerror = function() {
              // 400은 조용히 무시
              if (xhr.status === 400) {
                xhr.readyState = 4;
                xhr.status = 200;
                xhr.statusText = 'OK';
                xhr.responseText = '';
                return;
              }
              if (originalOnError) originalOnError.call(this);
            };
          }
          
          return originalOpen.apply(this, [method, url, ...rest]);
        };
        
        return xhr;
      };
    }
  })();
  
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

  // Run critical initialization immediately
  initCritical();
  
  // Non-critical initialization (runs when idle)
  const initNonCritical = () => {
    // Mobile Menu Toggle
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

    // Search Functionality (deferred)
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

    // Detect language from class names
    // Rouge typically adds classes like: .highlight.python, .highlight .language-python, etc.
    let language = 'code';
    
    // Priority order: highlight div > pre > code
    const highlightClasses = Array.from(highlightDiv.classList);
    const preClasses = Array.from(pre.classList);
    const codeClasses = Array.from(codeBlock.classList);
    
    // Check for Mermaid first (special handling needed)
    const isMermaid = highlightClasses.some(cls => cls === 'mermaid' || cls === 'language-mermaid') ||
                     preClasses.some(cls => cls === 'mermaid' || cls === 'language-mermaid') ||
                     codeClasses.some(cls => cls === 'mermaid' || cls === 'language-mermaid' || cls.startsWith('language-mermaid'));
    
    if (isMermaid) {
      language = 'MERMAID';
    } else {
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
      'CONFIG': 'Config',
      'MERMAID': 'Mermaid'
    };
    
    const displayLang = langMap[language] || language;

    // Set language attribute for CSS
    highlightDiv.setAttribute('data-lang', displayLang);
    
    // Mark Mermaid blocks for special handling
    if (isMermaid) {
      highlightDiv.classList.add('mermaid-block');
    }
    
    // Ensure highlight div is positioned relatively
    if (!highlightDiv.style.position) {
      highlightDiv.style.position = 'relative';
    }

    // Ensure pre element is positioned relatively for button positioning
    if (!pre.style.position) {
      pre.style.position = 'relative';
    }

    // Create copy button with improved UI/UX
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    if (isMermaid) {
      button.classList.add('mermaid-copy-btn');
    }
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.setAttribute('type', 'button');
    button.setAttribute('title', 'Copy');
    button.innerHTML = `
      <svg class="copy-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    `;

    // Append button to highlight div (positioned at top-right via CSS)
    highlightDiv.appendChild(button);

    // Store original code text for Mermaid blocks (before rendering)
    const originalCodeText = codeBlock.textContent || codeBlock.innerText;

    // Copy functionality with visual feedback
    button.addEventListener('click', async (e) => {
      e.stopPropagation();
      e.preventDefault();

      // For Mermaid blocks, use original code text; for others, use current text
      let textToCopy = isMermaid ? originalCodeText : (codeBlock.textContent || codeBlock.innerText || originalCodeText);

      const copyIcon = button.querySelector('.copy-icon');
      const checkIcon = button.querySelector('.check-icon');

      try {
        await navigator.clipboard.writeText(textToCopy);

        // Visual feedback - show check icon
        button.classList.add('copied');
        if (copyIcon) copyIcon.style.display = 'none';
        if (checkIcon) checkIcon.style.display = 'block';
        button.setAttribute('title', 'Copied!');

        setTimeout(() => {
          button.classList.remove('copied');
          if (copyIcon) copyIcon.style.display = 'block';
          if (checkIcon) checkIcon.style.display = 'none';
          button.setAttribute('title', 'Copy');
        }, 2000);
      } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand('copy');
          button.classList.add('copied');
          if (copyIcon) copyIcon.style.display = 'none';
          if (checkIcon) checkIcon.style.display = 'block';
          button.setAttribute('title', 'Copied!');
          setTimeout(() => {
            button.classList.remove('copied');
            if (copyIcon) copyIcon.style.display = 'block';
            if (checkIcon) checkIcon.style.display = 'none';
            button.setAttribute('title', 'Copy');
          }, 2000);
        } catch (fallbackErr) {
          button.classList.add('error');
          button.setAttribute('title', 'Failed to copy');
          setTimeout(() => {
            button.classList.remove('error');
            button.setAttribute('title', 'Copy');
          }, 2000);
        }
        document.body.removeChild(textArea);
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
      
      // Wrap in highlight div
      const highlightDiv = document.createElement('div');
      highlightDiv.className = 'highlight';
      pre.parentNode.insertBefore(highlightDiv, pre);
      highlightDiv.appendChild(pre);
      
      // Process the newly created highlight div
      const newPre = highlightDiv.querySelector('pre');
      const newCodeBlock = newPre ? newPre.querySelector('code') : null;
      
      if (newCodeBlock && newPre) {
        // Detect language for language badge display
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

        // Create copy button for standalone code blocks
        const button = document.createElement('button');
        button.className = 'copy-code-btn';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.setAttribute('type', 'button');
        button.setAttribute('title', 'Copy');
        button.innerHTML = `
          <svg class="copy-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;

        highlightDiv.appendChild(button);

        button.addEventListener('click', async (e) => {
          e.stopPropagation();
          e.preventDefault();
          const text = newCodeBlock.textContent || newCodeBlock.innerText;
          const copyIcon = button.querySelector('.copy-icon');
          const checkIcon = button.querySelector('.check-icon');

          try {
            await navigator.clipboard.writeText(text);
            button.classList.add('copied');
            if (copyIcon) copyIcon.style.display = 'none';
            if (checkIcon) checkIcon.style.display = 'block';
            button.setAttribute('title', 'Copied!');
            setTimeout(() => {
              button.classList.remove('copied');
              if (copyIcon) copyIcon.style.display = 'block';
              if (checkIcon) checkIcon.style.display = 'none';
              button.setAttribute('title', 'Copy');
            }, 2000);
          } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-9999px';
            document.body.appendChild(textArea);
            textArea.select();
            try {
              document.execCommand('copy');
              button.classList.add('copied');
              if (copyIcon) copyIcon.style.display = 'none';
              if (checkIcon) checkIcon.style.display = 'block';
              button.setAttribute('title', 'Copied!');
              setTimeout(() => {
                button.classList.remove('copied');
                if (copyIcon) copyIcon.style.display = 'block';
                if (checkIcon) checkIcon.style.display = 'none';
                button.setAttribute('title', 'Copy');
              }, 2000);
            } catch (fallbackErr) {
              button.classList.add('error');
              button.setAttribute('title', 'Failed to copy');
              setTimeout(() => {
                button.classList.remove('error');
                button.setAttribute('title', 'Copy');
              }, 2000);
            }
            document.body.removeChild(textArea);
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

    console.debug('Tech Blog UI initialized (non-critical)');

  // ============================================
  // Language Dropdown and Translation
  // ============================================
  (function initLanguageDropdown() {
    const langToggle = document.getElementById('lang-toggle');
    const langDropdown = document.getElementById('lang-dropdown');
    const langDropdownOverlay = document.getElementById('lang-dropdown-overlay');
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

    // Function to open dropdown
    function openDropdown() {
      langDropdown.classList.add('active');
      if (langDropdownOverlay) {
        langDropdownOverlay.classList.add('active');
        langDropdownOverlay.setAttribute('aria-hidden', 'false');
      }
      if (langToggle) {
        langToggle.setAttribute('aria-expanded', 'true');
      }
      // Prevent body scroll on mobile when dropdown is open
      if (window.innerWidth <= 768) {
        document.body.style.overflow = 'hidden';
      }
    }

    // Function to close dropdown
    function closeDropdown() {
      langDropdown.classList.remove('active');
      if (langDropdownOverlay) {
        langDropdownOverlay.classList.remove('active');
        langDropdownOverlay.setAttribute('aria-hidden', 'true');
      }
      if (langToggle) {
        langToggle.setAttribute('aria-expanded', 'false');
      }
      // Restore body scroll
      document.body.style.overflow = '';
    }

    // Toggle dropdown
    langToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      if (langDropdown.classList.contains('active')) {
        closeDropdown();
      } else {
        openDropdown();
      }
    });

    // Close dropdown when clicking overlay
    if (langDropdownOverlay) {
      langDropdownOverlay.addEventListener('click', function(e) {
        e.stopPropagation();
        closeDropdown();
      });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!langDropdown.contains(e.target) && 
          !langToggle.contains(e.target) &&
          (!langDropdownOverlay || !langDropdownOverlay.contains(e.target))) {
        closeDropdown();
      }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && langDropdown.classList.contains('active')) {
        closeDropdown();
      }
    });

    let currentLang = 'ko';
    let originalContent = {};
    let translationCache = {};
    let isInitialized = false;

    function stripBrowserTranslationTags(html) {
      if (!html) return html;
      const temp = document.createElement('div');
      temp.innerHTML = html;
      
      temp.querySelectorAll('font').forEach(font => {
        const parent = font.parentNode;
        while (font.firstChild) {
          parent.insertBefore(font.firstChild, font);
        }
        parent.removeChild(font);
      });
      
      temp.querySelectorAll('span[style*="vertical-align: inherit"]').forEach(span => {
        const parent = span.parentNode;
        while (span.firstChild) {
          parent.insertBefore(span.firstChild, span);
        }
        parent.removeChild(span);
      });
      
      return temp.innerHTML;
    }
    
    function extractPureText(el) {
      if (!el) return '';
      const clone = el.cloneNode(true);
      clone.querySelectorAll('font, span[style*="vertical-align: inherit"]').forEach(n => {
        n.replaceWith(...n.childNodes);
      });
      return clone.textContent || '';
    }
    
    // Remove Google injected elements (Knowledge Panel, Topics widgets, etc.)
    // These are <insertion> elements or elements with [data-ved] injected by Google Chrome
    function removeGoogleInjectedElements() {
      const selectors = [
        'insertion',
        '[data-ved]',
        '[data-google-topics]',
        '.kp-wholepage',
        '.kp-blk',
        '.g-blk',
        '.related-question-pair',
        // Google's dynamic recommendation widgets
        '[jscontroller][jsaction][jsname]'
      ];
      
      selectors.forEach(selector => {
        try {
          document.querySelectorAll(selector).forEach(el => {
            // Only remove if it looks like Google injected content (not our own elements)
            if (el.closest('.post-content') || el.closest('.post-article') || el.closest('main')) {
              el.remove();
            }
          });
        } catch (e) {
          // Silently ignore selector errors
        }
      });
    }
    
    // Run cleanup on load and periodically (Google may inject elements dynamically)
    removeGoogleInjectedElements();
    
    // Set up MutationObserver to catch dynamically injected elements
    const googleInjectionObserver = new MutationObserver((mutations) => {
      let shouldClean = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          for (const node of mutation.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.tagName === 'INSERTION' || 
                  node.hasAttribute('data-ved') || 
                  node.hasAttribute('data-google-topics')) {
                shouldClean = true;
                break;
              }
            }
          }
        }
        if (shouldClean) break;
      }
      if (shouldClean) {
        removeGoogleInjectedElements();
      }
    });
    
    // Observe the document body for Google injections
    if (document.body) {
      googleInjectionObserver.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    function saveOriginalContent() {
      if (isInitialized) return;

      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      if (postContent) originalContent.postContent = stripBrowserTranslationTags(postContent.innerHTML);
      if (postTitle) originalContent.postTitle = extractPureText(postTitle);
      
      if (certPage) {
        originalContent.certPage = stripBrowserTranslationTags(certPage.innerHTML);
        if (certTitle) originalContent.certTitle = extractPureText(certTitle);
      }

      originalContent.cardTitles = [];
      cardTitles.forEach((el, i) => {
        originalContent.cardTitles[i] = extractPureText(el);
      });

      originalContent.cardExcerpts = [];
      cardExcerpts.forEach((el, i) => {
        originalContent.cardExcerpts[i] = extractPureText(el);
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

    // Technical terms and patterns that should NOT be translated
    const noTranslatePatterns = [
      /^[A-Z][A-Z0-9_\-\.]+$/,  // ALL_CAPS_CONSTANTS, API-KEY
      /^[a-z]+\.[a-z]+/i,       // file.ext, package.name
      /^\$[a-zA-Z_]+/,          // $variable
      /^@[a-zA-Z]+/,            // @annotation
      /^#[a-zA-Z]+/,            // #hashtag
      /^https?:\/\//,           // URLs
      /^[a-zA-Z_][a-zA-Z0-9_]*\(\)/,  // function()
      /^\d+(\.\d+)?[a-zA-Z]+$/, // 10px, 2rem
      /^[<>\/\[\]{}]+$/,        // HTML/code symbols only
    ];
    
    // Words to preserve (technical terms)
    const preserveWords = new Set([
      'API', 'SDK', 'CLI', 'GUI', 'URL', 'URI', 'DNS', 'CDN', 'SSL', 'TLS', 'HTTP', 'HTTPS',
      'JSON', 'XML', 'YAML', 'CSV', 'HTML', 'CSS', 'SQL', 'NoSQL',
      'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'GitHub', 'GitLab',
      'React', 'Vue', 'Angular', 'Node.js', 'Python', 'Java', 'Go', 'Rust',
      'DevOps', 'DevSecOps', 'FinOps', 'MLOps', 'GitOps', 'SRE',
      'CI/CD', 'IaC', 'IAM', 'VPC', 'EC2', 'S3', 'RDS', 'EKS', 'ECS', 'Lambda',
      'Sentry', 'Cloudflare', 'Vercel', 'Nginx', 'Apache',
      'CRUD', 'REST', 'GraphQL', 'gRPC', 'WebSocket',
      'OAuth', 'JWT', 'SAML', 'SSO', 'MFA', '2FA',
      'SAST', 'DAST', 'IAST', 'SCA', 'WAF', 'DDoS', 'XSS', 'CSRF', 'SQLi',
      'LCP', 'FID', 'CLS', 'TTFB', 'FCP',
    ]);
    
    // Check if text should not be translated
    function shouldSkipTranslation(text) {
      if (!text || text.trim().length === 0) return true;
      if (text.trim().length < 2) return true;
      
      // Skip if it's a technical pattern
      const trimmed = text.trim();
      if (noTranslatePatterns.some(pattern => pattern.test(trimmed))) return true;
      
      // Skip if it's a single preserved word
      if (preserveWords.has(trimmed)) return true;
      
      // Skip if mostly numbers/symbols (less than 30% letters)
      const letters = (trimmed.match(/[a-zA-Z가-힣]/g) || []).length;
      if (letters < trimmed.length * 0.3) return true;
      
      return false;
    }
    
    // Translate text using MyMemory API with retry logic
    async function translateText(text, sourceLang, targetLang, retries = 2) {
      if (!text || text.trim().length === 0) return text;
      
      // Skip technical terms
      if (shouldSkipTranslation(text)) return text;

      // Skip if already in target language
      if (isAlreadyInTargetLanguage(text, targetLang)) {
        return text;
      }

      // Check cache first
      const cacheKey = `${sourceLang}-${targetLang}-${text.substring(0, 100)}`;
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

      // Handle long text by splitting into chunks (MyMemory limit: ~500 chars)
      if (text.length > 400) {
        const chunks = splitTextIntoChunks(text, 400);
        
        // Process chunks sequentially to avoid rate limiting
        const results = [];
        for (const chunk of chunks) {
          const translated = await translateText(chunk, sourceLang, targetLang, retries);
          results.push(translated || chunk);
          // Delay between chunks to avoid rate limiting
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        const translated = results.join(' ');
        textTranslationCache[cacheKey] = translated;
        return translated;
      }

      // Translate short text
      for (let attempt = 0; attempt <= retries; attempt++) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 8000);
          
          const response = await fetch(
            `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${sourceLangCode}|${targetLangCode}`,
            {
              method: 'GET',
              headers: { 'Accept': 'application/json' },
              signal: controller.signal
            }
          );
          
          clearTimeout(timeoutId);

          if (!response.ok) {
            if (response.status === 429) {
              // Rate limited - wait longer and retry
              await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
              continue;
            }
            if (attempt < retries) {
              await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
              continue;
            }
            throw new Error(`HTTP ${response.status}`);
          }

          const data = await response.json();

          // Check for rate limiting in response
          if (data.responseStatus === 429 || 
              (data.responseData && data.responseData.translatedText && 
               data.responseData.translatedText.includes('MYMEMORY WARNING'))) {
            if (attempt < retries) {
              await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
              continue;
            }
            textTranslationCache[cacheKey] = text;
            return text;
          }

          if (data.responseStatus === 200 && data.responseData && data.responseData.translatedText) {
            let translated = data.responseData.translatedText;
            
            // Filter out MyMemory warnings
            if (translated.includes('MYMEMORY WARNING') || 
                translated.includes('PLEASE SELECT') ||
                translated.includes('YOU USED ALL AVAILABLE')) {
              textTranslationCache[cacheKey] = text;
              return text;
            }
            
            // Check if translation is valid
            if (translated && translated !== text && translated.trim().length > 0) {
              textTranslationCache[cacheKey] = translated;
              return translated;
            }
          }

          textTranslationCache[cacheKey] = text;
          return text;
        } catch (error) {
          if (attempt < retries && error.name !== 'AbortError') {
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            continue;
          }
          if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.warn('Translation failed:', error.message);
          }
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
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      const translation = {};
      let totalItems = 0;
      let translatedItems = 0;

      // Count items to translate
      if (postTitle && originalContent.postTitle) totalItems++;
      if (certTitle && originalContent.certTitle) totalItems++;
      if (postContent && originalContent.postContent) {
        const textElements = postContent.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote');
        totalItems += textElements.length;
      }
      if (certPage && originalContent.certPage) {
        const textElements = certPage.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote, span.question-topic, span.question-number');
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
      
      // Translate certification page title
      if (certTitle && originalContent.certTitle) {
        try {
          translation.certTitle = await translateText(originalContent.certTitle, 'ko', targetLang);
          translatedItems++;
          if (translation.certTitle && translation.certTitle !== originalContent.certTitle) {
            certTitle.textContent = translation.certTitle;
          }
          showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
        } catch (error) {
          console.warn('Certification title translation failed:', error);
          translation.certTitle = originalContent.certTitle;
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
                  // Preserve inline formatting by translating only text nodes
                  if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                    el.textContent = translated;
                  } else if (el.children.length === 0) {
                    el.textContent = translated;
                  } else {
                    // Has inline elements - try to preserve structure
                    const textNodes = Array.from(el.childNodes).filter(n => n.nodeType === Node.TEXT_NODE);
                    if (textNodes.length === 1) {
                      textNodes[0].textContent = translated;
                    } else {
                      el.textContent = translated;
                    }
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

      // Translate certification page content
      if (certPage && originalContent.certPage) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = originalContent.certPage;
        const textElements = Array.from(tempDiv.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote, span.question-topic, span.question-number, .question-content, .question-options, .question-answer')).filter(el => {
          const text = el.textContent.trim();
          // Filter out empty elements, code blocks, and elements with code children
          return text && !el.closest('pre') && !el.closest('code') && !el.querySelector('code') && !el.classList.contains('notranslate');
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
                  if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                    el.textContent = translated;
                  } else if (el.children.length === 0) {
                    el.textContent = translated;
                  } else {
                    const textNodes = Array.from(el.childNodes).filter(n => n.nodeType === Node.TEXT_NODE);
                    if (textNodes.length === 1) {
                      textNodes[0].textContent = translated;
                    } else {
                      el.textContent = translated;
                    }
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

        translation.certPage = tempDiv.innerHTML;
      }

      // Cache and apply translation
      translationCache[targetLang] = translation;
      applyTranslation(translation);
    }

    // Apply translation to page
    function applyTranslation(translation) {
      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      // Apply title translation (ensure it's applied even if already set)
      if (postTitle && translation.postTitle && translation.postTitle !== originalContent.postTitle) {
        postTitle.textContent = translation.postTitle;
      }
      
      // Apply certification page title translation
      if (certTitle && translation.certTitle && translation.certTitle !== originalContent.certTitle) {
        certTitle.textContent = translation.certTitle;
      }

      // Apply post content translation
      if (postContent && translation.postContent) {
        postContent.innerHTML = translation.postContent;
      }
      
      // Apply certification page content translation
      if (certPage && translation.certPage) {
        certPage.innerHTML = translation.certPage;
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
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      if (postContent && originalContent.postContent) {
        postContent.innerHTML = originalContent.postContent;
      }

      if (postTitle && originalContent.postTitle) {
        postTitle.textContent = originalContent.postTitle;
      }
      
      // Restore certification page content
      if (certPage && originalContent.certPage) {
        certPage.innerHTML = originalContent.certPage;
      }
      
      if (certTitle && originalContent.certTitle) {
        certTitle.textContent = originalContent.certTitle;
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
          closeDropdown();
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
        closeDropdown();

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

    // Fix Korean image filename URL encoding and handle load errors
    // 한글 파일명을 가진 이미지의 URL 인코딩 문제 해결 및 로드 에러 처리
    (function() {
    /**
     * 경로를 안전하게 검증하고 정제합니다 (XSS 방지)
     * @param {string} path - 검증할 경로
     * @returns {string|null} - 정제된 경로 또는 null (안전하지 않은 경우)
     */
    function sanitizeImagePath(path) {
      if (!path || typeof path !== 'string') {
        return null;
      }
      
      // 위험한 프로토콜 제거 (javascript:, data:, vbscript: 등)
      const dangerousProtocols = /^(javascript|data|vbscript|file|about|chrome):/i;
      if (dangerousProtocols.test(path.trim())) {
        return null;
      }
      
      // HTML 태그나 스크립트 태그 제거
      if (/<[^>]*>/i.test(path)) {
        return null;
      }
      
      // 경로 정규화: 상대 경로 또는 절대 경로만 허용
      // 허용되는 패턴: /path/to/file, ./path, ../path, path/to/file
      const trimmedPath = path.trim();
      
      // 절대 경로인 경우 (/)로 시작
      if (trimmedPath.startsWith('/')) {
        // assets/images로 시작하는 경로만 허용 (보안 강화)
        if (trimmedPath.startsWith('/assets/images/') || 
            trimmedPath.startsWith('/assets/') ||
            trimmedPath.startsWith('/images/')) {
          // 경로에서 위험한 문자 제거
          const sanitized = trimmedPath.replace(/[<>"']/g, '');
          return sanitized;
        }
        return null;
      }
      
      // 상대 경로인 경우
      if (trimmedPath.startsWith('./') || trimmedPath.startsWith('../') || 
          !trimmedPath.includes('://')) {
        // 경로에서 위험한 문자 제거
        const sanitized = trimmedPath.replace(/[<>"']/g, '');
        return sanitized;
      }
      
      // 외부 URL은 허용하지 않음 (보안 정책)
      return null;
    }
    
    function fixImageUrls() {
      const images = document.querySelectorAll('img.post-image, img[src*="assets/images"], img.clickable-image');
      images.forEach(img => {
        const src = img.getAttribute('src');
        const dataFullSrc = img.getAttribute('data-full-src');
        const dataOriginalSrc = img.getAttribute('data-original-src');
        let retryCount = 0;
        const maxRetries = 4;
        
        // 이미지 로드 전에 경로를 미리 수정 - 디코딩된 경로를 먼저 시도
        if (src && !img.complete) {
          try {
            // URL 인코딩된 경로를 디코딩
            const decodedSrc = decodeURIComponent(src);
            
            // 디코딩된 경로에 한글이 있으면, 디코딩된 경로(한글 파일명)로 먼저 시도
            if (decodedSrc !== src && /[가-힣]/.test(decodedSrc)) {
              // 서버가 한글 파일명을 직접 처리할 수 있는 경우를 위해 디코딩된 경로로 먼저 시도
              const sanitized = sanitizeImagePath(decodedSrc);
              if (sanitized) {
                img.src = sanitized;
                if (dataFullSrc) {
                  img.setAttribute('data-full-src', sanitized);
                }
              }
            }
          } catch (e) {
            // 디코딩 실패 시 원본 유지
          }
        }
        
        // 이미지 로드 실패 시 여러 방법으로 재시도
        img.addEventListener('error', function() {
          if (retryCount >= maxRetries) {
            // 모든 재시도 실패 시 조용히 처리
            return;
          }
          
          retryCount++;
          const currentSrc = this.getAttribute('src');
          
          // 방법 1: URL 인코딩된 경로를 완전히 디코딩하여 한글 파일명으로 변환
          if (retryCount === 1) {
            try {
              const decodedSrc = decodeURIComponent(currentSrc);
              if (decodedSrc !== currentSrc && /[가-힣]/.test(decodedSrc)) {
                // 디코딩된 경로로 재시도 (서버가 한글 파일명을 직접 처리할 수 있는 경우)
                const sanitized = sanitizeImagePath(decodedSrc);
                if (sanitized) {
                  this.src = sanitized;
                  if (dataFullSrc) {
                    this.setAttribute('data-full-src', sanitized);
                  }
                  return;
                }
              }
            } catch (e) {
              // 디코딩 실패
            }
          }
          
          // 방법 2: data-original-src가 있으면 원본 경로로 재시도
          if (retryCount === 2 && dataOriginalSrc) {
            // 원본 경로를 그대로 사용 (Jekyll이 생성한 경로)
            const originalPath = dataOriginalSrc.startsWith('/') ? dataOriginalSrc : '/' + dataOriginalSrc;
            const sanitized = sanitizeImagePath(originalPath);
            if (sanitized) {
              this.src = sanitized;
              if (dataFullSrc) {
                this.setAttribute('data-full-src', sanitized);
              }
              return;
            }
          }
          
          // 방법 3: 경로를 분해하여 파일명만 다시 인코딩
          if (retryCount === 3) {
            try {
              const decodedSrc = decodeURIComponent(currentSrc);
              const pathParts = decodedSrc.split('/');
              const filename = pathParts[pathParts.length - 1];
              
              if (filename && /[가-힣]/.test(filename)) {
                // 파일명만 다시 인코딩 (경로는 그대로)
                const encodedFilename = encodeURIComponent(filename);
                pathParts[pathParts.length - 1] = encodedFilename;
                const newSrc = pathParts.join('/');
                const sanitized = sanitizeImagePath(newSrc);
                if (sanitized) {
                  this.src = sanitized;
                  if (dataFullSrc) {
                    this.setAttribute('data-full-src', sanitized);
                  }
                  return;
                }
              }
            } catch (e) {
              // 처리 실패
            }
          }
          
          // 방법 4: data-original-src를 기반으로 상대 경로 재구성
          if (retryCount === 4 && dataOriginalSrc) {
            try {
              // 원본 경로에서 파일명만 추출하여 디코딩된 경로로 재구성
              const pathParts = dataOriginalSrc.split('/');
              const filename = pathParts[pathParts.length - 1];
              if (filename && /[가-힣]/.test(filename)) {
                // 파일명이 한글이면 디코딩된 경로로 재구성
                pathParts[pathParts.length - 1] = filename;
                const newSrc = pathParts.join('/');
                const finalPath = newSrc.startsWith('/') ? newSrc : '/' + newSrc;
                const sanitized = sanitizeImagePath(finalPath);
                if (sanitized) {
                  this.src = sanitized;
                  if (dataFullSrc) {
                    this.setAttribute('data-full-src', sanitized);
                  }
                }
              }
            } catch (e) {
              // 처리 실패
            }
          }
        }, { once: false });
      });
    }

    // DOM 로드 후 실행 (defer to idle time)
    scheduleIdleWork(() => {
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
    });
    })();

    // ========================================
    // Code Block UI Enhancement (언어 뱃지만 추가, 복사 버튼은 기존 것 사용)
    // ========================================
    (function initCodeBlockEnhancement() {
      // Language name mapping for display
      const languageNames = {
        'js': 'JavaScript',
        'javascript': 'JavaScript',
        'ts': 'TypeScript',
        'typescript': 'TypeScript',
        'py': 'Python',
        'python': 'Python',
        'rb': 'Ruby',
        'ruby': 'Ruby',
        'java': 'Java',
        'go': 'Go',
        'golang': 'Go',
        'rs': 'Rust',
        'rust': 'Rust',
        'cpp': 'C++',
        'c': 'C',
        'cs': 'C#',
        'csharp': 'C#',
        'php': 'PHP',
        'swift': 'Swift',
        'kt': 'Kotlin',
        'kotlin': 'Kotlin',
        'sh': 'Shell',
        'bash': 'Bash',
        'shell': 'Shell',
        'zsh': 'Zsh',
        'powershell': 'PowerShell',
        'ps1': 'PowerShell',
        'html': 'HTML',
        'css': 'CSS',
        'scss': 'SCSS',
        'sass': 'Sass',
        'less': 'Less',
        'json': 'JSON',
        'yaml': 'YAML',
        'yml': 'YAML',
        'xml': 'XML',
        'md': 'Markdown',
        'markdown': 'Markdown',
        'sql': 'SQL',
        'graphql': 'GraphQL',
        'dockerfile': 'Dockerfile',
        'docker': 'Docker',
        'nginx': 'Nginx',
        'apache': 'Apache',
        'terraform': 'Terraform',
        'tf': 'Terraform',
        'hcl': 'HCL',
        'toml': 'TOML',
        'ini': 'INI',
        'conf': 'Config',
        'env': 'Environment',
        'plaintext': 'Text',
        'text': 'Text',
        'diff': 'Diff',
        'console': 'Console',
        'log': 'Log'
      };

      // Find all code blocks and add language badges only
      const codeBlocks = document.querySelectorAll('.post-content .highlight, .post-content pre:not(.highlight pre)');

      codeBlocks.forEach((block) => {
        // Skip if already has language badge
        if (block.querySelector('.code-language-badge')) return;

        // Get the code element
        const codeElement = block.querySelector('code');
        if (!codeElement) return;

        // Detect language from class
        let language = '';
        const classes = (codeElement.className + ' ' + (block.className || '')).toLowerCase();
        const langMatch = classes.match(/language-(\w+)|highlight-(\w+)|(\w+)-lang/);
        if (langMatch) {
          language = langMatch[1] || langMatch[2] || langMatch[3];
        }

        // Add language badge if language detected
        if (language && languageNames[language]) {
          const badge = document.createElement('span');
          badge.className = 'code-language-badge';
          badge.textContent = languageNames[language];

          // Make parent relative for badge positioning
          const preElement = block.tagName === 'PRE' ? block : block.querySelector('pre');
          if (preElement) {
            preElement.style.position = 'relative';
            preElement.insertBefore(badge, preElement.firstChild);
          }
        }
      });
    })();

    // Table wrapper for mobile responsiveness with enhanced scroll UX
    (function initTableWrapper() {
      'use strict';
      
      // 스크롤 타이머 ID 저장용
      const scrollTimers = new WeakMap();
      
      // 테이블 래퍼 생성 및 스크롤 이벤트 설정
      const wrapTables = () => {
        const postContent = document.querySelector('.post-content');
        if (!postContent) return;
        
        const tables = postContent.querySelectorAll('table:not(.chat-table)');
        tables.forEach(table => {
          // 이미 래퍼로 감싸져 있으면 스킵
          if (table.parentElement && table.parentElement.classList.contains('table-wrapper')) {
            // 이미 래퍼가 있으면 스크롤 이벤트만 설정
            setupScrollBehavior(table.parentElement);
            return;
          }
          
          // 래퍼 생성
          const wrapper = document.createElement('div');
          wrapper.className = 'table-wrapper';
          
          // 테이블을 래퍼로 이동
          table.parentNode.insertBefore(wrapper, table);
          wrapper.appendChild(table);
          
          // 스크롤 동작 설정
          setupScrollBehavior(wrapper);
        });
      };
      
      // 스크롤 동작 설정 (스크롤 힌트 숨기기/보이기)
      const setupScrollBehavior = (wrapper) => {
        // 이미 설정된 경우 스킵
        if (wrapper.dataset.scrollSetup === 'true') return;
        wrapper.dataset.scrollSetup = 'true';
        
        let scrollTimeout;
        
        // 스크롤 시작 시 힌트 숨김
        wrapper.addEventListener('scroll', () => {
          // 스크롤 중 표시
          wrapper.classList.add('is-scrolling');
          
          // 기존 타이머 클리어
          if (scrollTimeout) {
            clearTimeout(scrollTimeout);
          }
          
          // 스크롤 종료 후 1.5초 뒤 힌트 다시 표시
          scrollTimeout = setTimeout(() => {
            wrapper.classList.remove('is-scrolling');
          }, 1500);
        }, { passive: true });
        
        // 터치 시작 시 힌트 숨김
        wrapper.addEventListener('touchstart', () => {
          wrapper.classList.add('is-scrolling');
        }, { passive: true });
        
        // 터치 종료 후 힌트 다시 표시
        wrapper.addEventListener('touchend', () => {
          if (scrollTimeout) {
            clearTimeout(scrollTimeout);
          }
          scrollTimeout = setTimeout(() => {
            wrapper.classList.remove('is-scrolling');
          }, 1500);
        }, { passive: true });
        
        // 초기 상태: 스크롤 가능 여부 확인 후 힌트 표시/숨김
        const checkScrollable = () => {
          const isScrollable = wrapper.scrollWidth > wrapper.clientWidth;
          if (!isScrollable) {
            wrapper.classList.add('no-scroll-hint');
          } else {
            wrapper.classList.remove('no-scroll-hint');
          }
        };
        
        // 초기 체크 (약간 지연)
        setTimeout(checkScrollable, 100);
        
        // 리사이즈 시 재체크
        window.addEventListener('resize', () => {
          clearTimeout(scrollTimers.get(wrapper));
          scrollTimers.set(wrapper, setTimeout(checkScrollable, 200));
        }, { passive: true });
      };
      
      // 초기 실행
      wrapTables();
      
      // 동적으로 추가된 콘텐츠를 위한 MutationObserver
      const observer = new MutationObserver((mutations) => {
        let shouldWrap = false;
        mutations.forEach((mutation) => {
          if (mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === 1) { // Element node
                if (node.tagName === 'TABLE' || node.querySelector('table')) {
                  shouldWrap = true;
                }
              }
            });
          }
        });
        
        if (shouldWrap) {
          wrapTables();
        }
      });
      
      const postContent = document.querySelector('.post-content');
      if (postContent) {
        observer.observe(postContent, {
          childList: true,
          subtree: true
        });
      }
    })();

  }; // End of initNonCritical function
  
  // Schedule non-critical initialization when idle
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      scheduleIdleWork(initNonCritical);
    });
  } else {
    scheduleIdleWork(initNonCritical);
  }
})();
