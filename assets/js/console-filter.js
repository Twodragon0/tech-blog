/**
 * Console Filter Module
 * Consolidated console noise filtering for the entire site
 * Filters browser extension noise, CSP violations, external service errors (Giscus, AdSense, Firebase)
 *
 * Usage:
 *   <script src="/assets/js/console-filter.js"></script>
 *   <script>window.initConsoleFilter();</script>
 */

(function(window) {
  'use strict';

  // Prevent double initialization
  if (window._consoleFilterInitialized) {
    return;
  }

  /**
   * Initialize console filtering
   * Call this function once on page load
   */
  window.initConsoleFilter = function() {
    // Prevent double initialization
    if (window._consoleFilterInitialized) {
      return;
    }
    window._consoleFilterInitialized = true;

    // Store original console methods
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalLog = console.log;

    // Development mode detection
    const isDevelopment = window.location.hostname === 'localhost' ||
                         window.location.hostname === '127.0.0.1' ||
                         window.location.search.includes('debug=true');

    // Comprehensive noise patterns (consolidated from all 3 files)
    const noisePatterns = [
      // Browser extension noise
      /runtime\.lastError/i,
      /message port closed/i,
      /Unchecked runtime\.lastError/i,
      /The message port closed before a response was received/i,
      /runtime\.lastError.*message port|message port.*response was received/i,
      /📥 Received message.*NmLockState/i,
      /📤 Sending.*NmLockState/i,
      /Duration:.*ms/i,
      /cache\.agilebits\.com.*404/i,
      /notification\.js.*\[Notification\]/i,
      /DeviceTrust.*access denied/i,

      // CSP violations
      /Framing.*violates.*Content Security Policy/i,
      /frame-ancestors/i,
      /violation has been logged/i,
      /Content Security Policy.*violates/i,
      /Refused to connect.*violates.*Content Security Policy/i,
      /Refused to load.*violates.*Content Security Policy/i,
      /Loading the script.*violates.*Content Security Policy/i,
      /frame-ancestors\s*'self'|'self'\s*frame-ancestors/i,
      /report-only.*Content Security Policy|Content Security Policy.*report-only/i,
      /The violation has been logged/i,
      /X-Frame-Options may only be set via an HTTP header/i,

      // Giscus 404 errors (normal when discussion not yet created)
      /giscus\.app.*404/i,
      /discussions.*404/i,
      /GET.*giscus\.app.*404/i,
      /giscus\.app\/api\/discussions.*404/i,
      /Failed to load resource.*giscus.*404/i,
      /widget.*giscus.*404/i,
      /giscus\.app.*404.*discussions/i,
      /GET.*giscus\.app\/api\/discussions.*404/i,
      /giscus\.app\/api\/discussions.*\b404\b/i,
      /\b404\b.*Not Found.*giscus|giscus.*\b404\b.*Not Found/i,
      /\[giscus\] Discussion not found/i,
      /giscus\.app.*\d+ms/i,
      /https:\/\/giscus\.app\/.*widget.*\d+ms/i,

      // SES (Secure EcmaScript) - Google AdSense security mechanism
      /SES Removing unpermitted intrinsics/i,
      /lockdown-install/i,
      /lockdown-install\.js/i,

      // Google AdSense 400 errors (no ads available or account issues)
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

      // Google AdSense 403 errors (ad blocker or account issues)
      /googleads.*403/i,
      /googlesyndication.*403/i,
      /pagead2\.googlesyndication.*403/i,
      /Failed to load resource.*status of 403.*ads/i,
      /Failed to load resource.*status of 403.*googleads/i,
      /Failed to load resource.*status of 403.*googlesyndication/i,
      /pagead2\.googlesyndication\.com.*403/i,
      /adsbygoogle\.js.*403/i,
      /GET.*adsbygoogle.*403/i,
      /GET.*googlesyndication.*403/i,
      /net::ERR_ABORTED.*403.*googlesyndication/i,
      /googlesyndication.*net::ERR_ABORTED/i,
      /adsbygoogle.*Forbidden/i,

      // Firebase Dynamic Links (service ended August 25, 2025)
      /firebase.*dynamic.*link/i,
      /Invalid dynamic link/i,
      /firebaseapp\.com.*dynamic/i,
      /app\.goo\.gl/i,
      /firebase.*link.*invalid/i,
      /Failed to load resource.*firebase/i,
      /Failed to load resource.*app\.goo\.gl/i,
      /Network request failed.*firebase/i,
      /Network request failed.*app\.goo\.gl/i,
      /GET.*firebaseapp\.com/i,
      /GET.*app\.goo\.gl/i,

      // Favicon and image 404 errors (normal fallback behavior)
      /Failed to load resource.*404/i,
      /favicon\.png.*404/i,
      /favicon.*404/i,
      /apple-touch-icon.*404/i,
      /GET.*favicon/i,
      /GET.*apple-touch-icon/i,

      // WebP image 404 errors (fallback to original images)
      /\.webp.*404/i,
      /image.*404.*Not Found/i,
      /Failed to load image/i,
      /GET.*\.webp.*404/i,
      /assets\/images.*\.webp.*404/i,
      /Failed to load resource.*\.webp/i,
      /Failed to load resource.*\.png.*404/i,
      /diagrams\/.*\.png.*404/i,
      /diagrams\/.*\.webp.*404/i,

      // PostMessage errors
      /Failed to execute.*postMessage/i,
      /The target origin provided.*does not match/i,

      // Service Worker info messages (not errors)
      /\[Service Worker\] New version available/i,
      /Service Worker.*registered/i,
      /Service Worker.*activated/i,

      // Performance warnings (external resource delays are normal)
      /\[Performance\] Slow resource/i,
      /Slow resource.*vercel/i,
      /Slow resource.*giscus/i,
      /Slow resource.*googlesyndication/i,

      // SVG diagram loading performance warnings (slow loading is normal for large diagrams)
      /https:\/\/tech\.2twodragon\.com\/assets\/images\/diagrams\/.*\.svg.*\d+ms/i,

      // Vercel Speed Insights rate limiting
      /speed-insights.*429/i,
      /vitals.*429/i,
      /_vercel\/speed-insights.*429/i,
      /POST.*speed-insights.*429/i,
      /Too Many Requests.*speed-insights/i,
      /speed-insights.*Too Many Requests/i,

      // DevTools suggestions
      /Download the React DevTools/i,
      /Download the Apollo DevTools/i,

      // Mermaid.js errors (diagram rendering failures can be normal)
      /mermaid.*Uncaught.*promise/i,
      /mermaid.*error/i,

      // Misc parsing errors
      /Unexpected token.*at.*:\d+.*:\d+/i
    ];

    // Error message enhancement map
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

    // Check if message should be filtered
    function shouldFilter(message) {
      if (typeof message !== 'string') return false;
      return noisePatterns.some(function(pattern) {
        return pattern.test(message);
      });
    }

    // Enhance error messages
    function enhanceErrorMessage(message) {
      if (typeof message !== 'string') return null;

      for (var i = 0; i < errorMessageMap.length; i++) {
        var item = errorMessageMap[i];
        if (item.pattern.test(message)) {
          return item.replacement;
        }
      }
      return null;
    }

    // Check if message is noise (including stack traces)
    function isNoise(m) {
      if (typeof m !== 'string') {
        // Handle error objects and other types
        var msgStr = (m && m.message) || (m && m.toString && m.toString()) || String(m);
        // Also check stack trace
        if (m && m.stack) {
          msgStr += ' ' + m.stack;
        }
        m = msgStr;
      }
      return shouldFilter(m);
    }

    // Safe logging with noise filtering and message enhancement
    function safeLog(originalFn, args, level) {
      var filteredArgs = [];
      var hasEnhancedMessage = false;

      for (var i = 0; i < args.length; i++) {
        var arg = args[i];
        // Handle non-string arguments (error objects, etc.)
        var messageStr = typeof arg === 'string' ? arg :
                        (arg && arg.message) || (arg && arg.toString && arg.toString()) || '';

        if (typeof messageStr === 'string' && messageStr) {
          // Skip filtered messages
          if (shouldFilter(messageStr)) {
            continue;
          }

          // Enhance error messages
          var enhanced = enhanceErrorMessage(messageStr);
          if (enhanced) {
            hasEnhancedMessage = true;
            // Show details only in development
            if (isDevelopment) {
              if (enhanced.level === 'info') {
                originalLog.call(console, '[' + enhanced.message + ']', enhanced.details);
              } else {
                originalWarn.call(console, '[' + enhanced.message + ']', enhanced.details, '\n원본:', messageStr);
              }
            } else {
              // In production, show only important warnings
              if (enhanced.level === 'warn') {
                originalWarn.call(console, enhanced.message);
              }
              // Don't show info level in production
            }
            continue; // Don't show original message
          }
        }
        filteredArgs.push(arg);
      }

      // Log if there are filtered args and no enhanced message
      if (filteredArgs.length > 0 && !hasEnhancedMessage) {
        originalFn.apply(console, filteredArgs);
      }
    }

    // Override console methods
    console.error = function() {
      var args = Array.prototype.slice.call(arguments);
      safeLog(originalError, args, 'error');
    };

    console.warn = function() {
      var args = Array.prototype.slice.call(arguments);
      safeLog(originalWarn, args, 'warn');
    };

    console.log = function() {
      var args = Array.prototype.slice.call(arguments);
      // In production, filter debug logs
      if (!isDevelopment) {
        var filteredArgs = args.filter(function(arg) {
          if (typeof arg === 'string') {
            return !shouldFilter(arg);
          }
          return true;
        });
        if (filteredArgs.length > 0) {
          originalLog.apply(console, filteredArgs);
        }
      } else {
        // In development, use safe logging
        safeLog(originalLog, args, 'log');
      }
    };

    // Global error handler
    var originalWindowError = window.onerror;
    window.onerror = function(message, source, lineno, colno, error) {
      // Check source URL (for network errors)
      var sourceStr = source || '';
      var fullMessage = (typeof message === 'string' ? message : String(message)) + ' ' + sourceStr;

      // Filter known noise patterns
      if (shouldFilter(fullMessage)) {
        return true; // Mark as handled
      }

      // Call original handler if exists
      if (originalWindowError) {
        return originalWindowError.call(this, message, source, lineno, colno, error);
      }

      return false; // Continue default error handling
    };

    // Unhandled Promise Rejection handler
    window.addEventListener('unhandledrejection', function(event) {
      var reason = event.reason;
      var reasonStr = reason && typeof reason === 'object' ? reason.toString() : String(reason);

      // Filter known noise patterns
      if (shouldFilter(reasonStr)) {
        event.preventDefault(); // Prevent default error handling
        return;
      }
    });

    // Wrap fetch API to filter network errors
    var originalFetch = window.fetch;
    window.fetch = function() {
      var args = Array.prototype.slice.call(arguments);
      var url = typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url) || '';

      // Firebase Dynamic Links - quietly fail
      if (/firebaseapp\.com/i.test(url) || /app\.goo\.gl/i.test(url)) {
        return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
      }

      // Vercel Speed Insights vitals - suppress 429 rate limiting
      if (/_vercel\/speed-insights\/vitals/i.test(url)) {
        return originalFetch.apply(this, args)
          .then(function(response) {
            if (response.status === 429) {
              return new Response('', { status: 200, statusText: 'OK' });
            }
            return response;
          })
          .catch(function() {
            return new Response('', { status: 200, statusText: 'OK' });
          });
      }

      return originalFetch.apply(this, args).catch(function(error) {
        var errorMessage = (error && error.message) || (error && error.toString()) || '';
        var requestUrl = typeof args[0] === 'string' ? args[0] : (args[0] && args[0].url) || '';
        var fullError = errorMessage + ' ' + requestUrl;

        // Filter known noise patterns
        if (shouldFilter(fullError)) {
          return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
        }

        // Giscus 404 - quietly fail
        if (/giscus\.app/i.test(requestUrl) && (error.status === 404 || /404/i.test(errorMessage))) {
          return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
        }

        // Google AdSense 400/403 - quietly fail
        if (/(googleads|googlesyndication|doubleclick|pagead)/i.test(requestUrl) &&
            (error.status === 400 || error.status === 403 || /400|403/i.test(errorMessage))) {
          return Promise.resolve(new Response('', { status: 200, statusText: 'OK' }));
        }

        throw error;
      });
    };

    // Wrap XMLHttpRequest (legacy browser support)
    if (window.XMLHttpRequest) {
      var OriginalXHR = window.XMLHttpRequest;
      window.XMLHttpRequest = function() {
        var xhr = new OriginalXHR();
        var originalOpen = xhr.open;

        xhr.open = function(method, url) {
          var rest = Array.prototype.slice.call(arguments, 2);

          // Firebase Dynamic Links - quietly block
          if (/firebaseapp\.com/i.test(url) || /app\.goo\.gl/i.test(url)) {
            xhr.readyState = 4;
            xhr.status = 200;
            xhr.statusText = 'OK';
            xhr.responseText = '';
            return;
          }

          // Giscus 404 - quietly handle
          if (/giscus\.app/i.test(url)) {
            var originalOnError = xhr.onerror;
            xhr.onerror = function() {
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

          // Google AdSense 400/403 - quietly handle
          if (/(googleads|googlesyndication|doubleclick|pagead)/i.test(url)) {
            var originalOnErrorAds = xhr.onerror;
            xhr.onerror = function() {
              if (xhr.status === 400 || xhr.status === 403) {
                xhr.readyState = 4;
                xhr.status = 200;
                xhr.statusText = 'OK';
                xhr.responseText = '';
                return;
              }
              if (originalOnErrorAds) originalOnErrorAds.call(this);
            };
          }

          return originalOpen.apply(this, [method, url].concat(rest));
        };

        return xhr;
      };
    }

    if (isDevelopment) {
      console.log('[Console Filter] Initialized successfully');
    }
  };

})(window);
