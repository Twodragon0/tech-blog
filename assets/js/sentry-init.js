(function () {
  'use strict';

  var script = document.currentScript;
  var dsn = (script && script.getAttribute('data-sentry-dsn')) || '';
  var productionHost = (script && script.getAttribute('data-production-host')) || 'tech.2twodragon.com';

  if (!dsn) {
    return;
  }

  function initSentry() {
    if (typeof Sentry === 'undefined') {
      return;
    }

    var isProduction = window.location.hostname === productionHost;
    var isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    var MONTHLY_LIMIT = 5000;
    var MONTHLY_KEY = 'se_month';
    var MONTHLY_TS = 'se_ts';
    var errorCounts = {};
    var sensitivePatterns = [
      /password/i, /token/i, /secret/i, /api[_-]?key/i,
      /authorization/i, /bearer/i, /credential/i,
      /private[_-]?key/i, /sk-[a-zA-Z0-9]+/i,
    ];
    var ignorePatterns = [
      /content security policy/i, /csp/i,
      /chrome-extension/i, /moz-extension/i,
      /resizeobserver loop/i, /network error/i,
      /script error/i, /failed to load/i,
      /load link/i, /long task/i, /layout shift/i,
    ];

    function getMonthlyCount() {
      try {
        var ts = parseInt(localStorage.getItem(MONTHLY_TS) || '0', 10);
        var count = parseInt(localStorage.getItem(MONTHLY_KEY) || '0', 10);
        var now = Date.now();
        if ((now - ts) > 30 * 24 * 60 * 60 * 1000 || ts === 0) {
          localStorage.setItem(MONTHLY_KEY, '0');
          localStorage.setItem(MONTHLY_TS, String(now));
          return 0;
        }
        return count;
      } catch (_error) {
        return 0;
      }
    }

    function incrementMonthly() {
      try {
        var count = getMonthlyCount() + 1;
        localStorage.setItem(MONTHLY_KEY, String(count));
        return count;
      } catch (_error) {
        return 0;
      }
    }

    function getDynamicSampleRate() {
      if (!isProduction) {
        return 0;
      }
      var count = getMonthlyCount();
      if (count > MONTHLY_LIMIT * 0.9) {
        return 0.3;
      }
      if (count > MONTHLY_LIMIT * 0.8) {
        return 0.5;
      }
      if (count > MONTHLY_LIMIT * 0.6) {
        return 0.75;
      }
      return 1;
    }

    function containsSensitive(text) {
      if (!text) {
        return false;
      }
      return sensitivePatterns.some(function (pattern) {
        return pattern.test(text);
      });
    }

    function isNoiseError(message) {
      if (!message) {
        return false;
      }
      var lower = message.toLowerCase();
      return ignorePatterns.some(function (pattern) {
        return pattern.test(lower);
      }) || lower === '' || lower === 'unknown error';
    }

    function isThrottled(key) {
      var now = Date.now();
      var entry = errorCounts[key];
      if (!entry || (now - entry.ts) > 3600000) {
        errorCounts[key] = { count: 1, ts: now };
        return false;
      }
      entry.count += 1;
      if (entry.count > 8) {
        return Math.random() > 0.3;
      }
      return false;
    }

    Sentry.init({
      dsn: dsn,
      environment: isProduction ? 'production' : (isDev ? 'development' : 'preview'),
      release: (function () {
        if (typeof window !== 'undefined' && window.VERCEL_GIT_COMMIT_SHA) {
          return 'tech-blog@' + window.VERCEL_GIT_COMMIT_SHA.substring(0, 7);
        }
        if (isProduction) {
          var date = new Date();
          return 'tech-blog@' + date.getFullYear() + String(date.getMonth() + 1).padStart(2, '0') + String(date.getDate()).padStart(2, '0');
        }
        return undefined;
      })(),
      integrations: [
        Sentry.browserTracingIntegration({
          tracePropagationTargets: ['localhost', /^https:\/\/tech\.2twodragon\.com/],
        }),
        Sentry.replayIntegration({
          maskAllText: true,
          blockAllMedia: true,
          maskAllInputs: true,
          networkDetailAllowUrls: [],
        }),
      ],
      sampleRate: getDynamicSampleRate(),
      tracesSampleRate: isProduction ? 0.01 : 0,
      replaysSessionSampleRate: 0,
      replaysOnErrorSampleRate: isProduction ? 0.5 : 0,
      maxBreadcrumbs: 30,
      attachStacktrace: true,
      allowUrls: [/https?:\/\/(www\.)?tech\.2twodragon\.com/],
      ignoreErrors: ['fb_xd_fragment', 'top.GLOBALS', /^Non-Error promise rejection/, /ResizeObserver loop/],
      beforeSend: function (event, hint) {
        if (!isProduction) {
          return null;
        }

        var error = hint && hint.originalException;
        if (error && error.message && isNoiseError(error.message)) {
          return null;
        }
        if (event.message && isNoiseError(event.message)) {
          return null;
        }

        if (event.exception && event.exception.values && event.exception.values[0]) {
          var exc = event.exception.values[0];
          var hasOurCode = exc.stacktrace && exc.stacktrace.frames && exc.stacktrace.frames.some(function (frame) {
            if (!frame.filename) {
              return false;
            }
            try {
              if (frame.filename.indexOf('/assets/js/') === 0) {
                return true;
              }
              var url = new URL(frame.filename, window.location.origin);
              return url.hostname === productionHost;
            } catch (_error) {
              return false;
            }
          });

          if (!hasOurCode && (!exc.value || isNoiseError(exc.value))) {
            return null;
          }
        }

        var key = event.fingerprint ? event.fingerprint.join('-') : (event.message || 'unknown');
        if (isThrottled(key.substring(0, 60))) {
          return null;
        }

        if (event.request && event.request.url) {
          try {
            var requestUrl = new URL(event.request.url);
            ['token', 'key', 'password', 'secret', 'api_key', 'access_token', 'auth'].forEach(function (name) {
              requestUrl.searchParams.delete(name);
            });
            event.request.url = requestUrl.toString();
          } catch (_error) {}
          delete event.request.cookies;
        }

        if (event.exception && event.exception.values) {
          event.exception.values.forEach(function (exception) {
            if (!exception.stacktrace || !exception.stacktrace.frames) {
              return;
            }
            exception.stacktrace.frames.forEach(function (frame) {
              if (frame.filename) {
                frame.filename = frame.filename.replace(/\/Users\/[^/]+/g, '/Users/***');
                frame.filename = frame.filename.replace(/\/home\/[^/]+/g, '/home/***');
              }
              if (frame.vars) {
                Object.keys(frame.vars).forEach(function (variableName) {
                  if (containsSensitive(variableName) || containsSensitive(String(frame.vars[variableName] || ''))) {
                    frame.vars[variableName] = '***REDACTED***';
                  }
                });
              }
            });
          });
        }

        var count = incrementMonthly();
        if (isDev && count > MONTHLY_LIMIT * 0.8) {
          console.warn('[Sentry] Monthly event limit warning:', count, '/', MONTHLY_LIMIT);
        }

        if (event.breadcrumbs && event.breadcrumbs.length > 8) {
          event.breadcrumbs = event.breadcrumbs.slice(-8);
        }

        return event;
      },
      beforeBreadcrumb: function (breadcrumb) {
        if (!isProduction) {
          return null;
        }
        if (breadcrumb.category === 'console' && breadcrumb.level === 'log') {
          return null;
        }
        if (breadcrumb.message && containsSensitive(breadcrumb.message)) {
          return null;
        }
        return breadcrumb;
      },
    });

    window.addEventListener('error', function (event) {
      if (!isProduction || typeof Sentry === 'undefined') {
        return;
      }
      if (event.error && event.error.__sentry_captured__) {
        return;
      }
      var captured = event.error || new Error(event.message || 'Unknown error');
      captured.__sentry_captured__ = true;
      Sentry.captureException(captured, {
        tags: { errorType: 'global_error', handled: false },
        extra: {
          filename: (event.filename || 'unknown').substring(0, 100),
          lineno: event.lineno || 0,
          colno: event.colno || 0,
        },
      });
    }, true);

    window.addEventListener('unhandledrejection', function (event) {
      if (!isProduction || typeof Sentry === 'undefined') {
        return;
      }
      if (event.reason && event.reason.__sentry_captured__) {
        return;
      }
      if (event.defaultPrevented) {
        return;
      }
      var captured = event.reason instanceof Error ? event.reason : new Error(String(event.reason || 'Unhandled Promise Rejection'));
      captured.__sentry_captured__ = true;
      Sentry.captureException(captured, {
        tags: { errorType: 'unhandled_promise_rejection', handled: false },
      });
    });
  }

  if (typeof Sentry !== 'undefined') {
    initSentry();
  } else {
    window.addEventListener('load', function () {
      if (typeof Sentry !== 'undefined') {
        initSentry();
      }
    });
  }
})();
