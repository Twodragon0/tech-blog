(function () {
  'use strict';

  if (window.__headRuntimeInitialized) {
    return;
  }
  window.__headRuntimeInitialized = true;

  // defer 환경에서 document.currentScript는 null이므로 id 기반으로 읽기
  var scriptEl = document.getElementById('head-runtime-script');
  var gaId = (scriptEl && scriptEl.getAttribute('data-ga-id')) || '';
  var adsenseClient = (scriptEl && scriptEl.getAttribute('data-adsense-client')) || '';
  var kakaoAppKey = (scriptEl && scriptEl.getAttribute('data-kakao-app-key')) || '';
  var sentryDsn = (scriptEl && scriptEl.getAttribute('data-sentry-dsn')) || '';
  var sentryProductionHost = (scriptEl && scriptEl.getAttribute('data-sentry-production-host')) || '';
  var sentryAllowedHosts = (scriptEl && scriptEl.getAttribute('data-sentry-allowed-hosts')) || '';

  function runWhenBodyAvailable(callback) {
    if (document.body) {
      callback();
      return;
    }

    document.addEventListener('DOMContentLoaded', callback, { once: true });
  }

  function initConsoleFilter() {
    var initFilter = function () {
      if (window.initConsoleFilter) {
        window.initConsoleFilter();
        return;
      }
      setTimeout(initFilter, 50);
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(initFilter, { timeout: 1000 });
    } else {
      setTimeout(initFilter, 100);
    }
  }

  function applyTheme() {
    // 인라인 스크립트(#theme-init)가 이미 data-theme을 설정했으므로
    // defer 실행 시점에 테마가 없을 경우에만 폴백으로 적용
    if (document.documentElement.getAttribute('data-theme')) {
      return;
    }
    try {
      var saved = localStorage.getItem('theme');
      var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var theme = (!saved || saved === 'system') ? (systemDark ? 'dark' : 'light') : saved;
      document.documentElement.setAttribute('data-theme', theme);
    } catch (_error) {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }

  function bindCssFallback() {
    var link = document.getElementById('main-stylesheet');
    if (!link) {
      return;
    }

    link.onerror = function () {
      var style = document.createElement('style');
      style.textContent = 'body{font-family:"Noto Sans KR",-apple-system,sans-serif;margin:0;padding:0;background:#fff;color:#1a1a1a}.post-article{max-width:800px;margin:0 auto;padding:2.5rem 2rem}.post-title{font-size:clamp(1.5rem,4vw,2.25rem);margin:.5rem 0 1rem}.post-content{font-size:1.0625rem;line-height:1.8}[data-theme="dark"]{background:#0f172a;color:#f1f5f9}';
      document.head.appendChild(style);
      link.remove();
    };
  }

  function markBodyLoaded() {
    runWhenBodyAvailable(function () {
      document.body.classList.add('loaded');
    });
  }

  function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      return;
    }

    var register = function () {
      navigator.serviceWorker
        .register('/sw.js')
        .then(function (registration) {
          registration.addEventListener('updatefound', function () {
            var newWorker = registration.installing;
            if (!newWorker) {
              return;
            }
            newWorker.addEventListener('statechange', function () {
              if (newWorker.state === 'activated' && navigator.serviceWorker.controller) {
                var isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
                if (isDev) {
                  console.debug('[SW] New version ready');
                }
              }
            });
          });
        })
        .catch(function () {});

      if (navigator.serviceWorker.controller) {
        navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
      }
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(register, { timeout: 2000 });
    } else {
      window.addEventListener('load', register, { once: true });
    }
  }

  /**
   * Lazy-loads Google Analytics on the first user interaction, with a 10-12s
   * idle safety-net fallback. Rationale:
   *   - Bots and bouncers (no interaction within 10s) skip GA entirely,
   *     reducing main-thread cost (152 KB transfer + 1374ms eval per
   *     PageSpeed report) AND noise in analytics data.
   *   - Real readers trigger pointermove / scroll / keydown / touchstart /
   *     click within seconds, so the page_view event still fires.
   *   - {capture: true, passive: true} ensures we never block scroll
   *     responsiveness while waiting.
   *   - The single __gaLoadInitiated guard ensures exactly one fetch.
   */
  function loadGoogleAnalytics() {
    if (!gaId) return;
    if (window.__gaLoadInitiated) return;

    var load = function () {
      if (window.__gaLoadInitiated) return;
      window.__gaLoadInitiated = true;
      var script = document.createElement('script');
      script.async = true;
      script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(gaId);
      script.onload = function () {
        window.dataLayer = window.dataLayer || [];
        function gtag() { window.dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', gaId, { send_page_view: false });
        gtag('event', 'page_view', {
          page_path: window.location.pathname + window.location.search,
        });
      };
      document.head.appendChild(script);
    };

    // First-interaction trigger (pointermove/scroll/keydown/touchstart) - whichever fires first
    var INTERACTION_EVENTS = ['pointermove', 'scroll', 'keydown', 'touchstart', 'click'];
    var fired = false;
    var loadOnce = function () {
      if (fired) return;
      fired = true;
      INTERACTION_EVENTS.forEach(function (ev) {
        window.removeEventListener(ev, loadOnce, { passive: true, capture: true });
      });
      load();
    };
    INTERACTION_EVENTS.forEach(function (ev) {
      window.addEventListener(ev, loadOnce, { passive: true, capture: true });
    });

    // Safety net: load after 10s of inactivity so GA still captures non-bouncing
    // pageviews where the user reads without scrolling.
    var idleFallback = function () { loadOnce(); };
    if ('requestIdleCallback' in window) {
      requestIdleCallback(function () { setTimeout(idleFallback, 10000); }, { timeout: 5000 });
    } else {
      setTimeout(idleFallback, 12000);
    }
  }

  function loadAdsense() {
    if (!adsenseClient) {
      return;
    }

    var load = function () {
      if (window.__adsenseLoadInitiated) {
        return;
      }
      window.__adsenseLoadInitiated = true;

      try {
        window.adsbygoogle = window.adsbygoogle || [];
        window.adsbygoogle.pauseAdRequests = 0;
        window._adsenseLoaded = false;

        var script = document.createElement('script');
        script.async = true;
        script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + encodeURIComponent(adsenseClient);
        script.crossOrigin = 'anonymous';
        script.setAttribute('data-ad-frequency-hint', '0');
        script.onload = function () {
          window._adsenseLoaded = true;
          if (typeof window.__adsenseSlotInitializer === 'function') {
            window.__adsenseSlotInitializer();
          }
          window.dispatchEvent(new Event('adsense:ready'));
        };
        script.onerror = function () {
          window._adsenseLoaded = false;
          var ads = document.querySelectorAll('.adsbygoogle');
          for (var i = 0; i < ads.length; i += 1) {
            ads[i].style.display = 'none';
          }
        };

        document.head.appendChild(script);
      } catch (_error) {
        window._adsenseLoaded = false;
      }
    };

    function installIntersectionObserver(el) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          io.disconnect();
          load();
        }
      }, { rootMargin: '200px 0px' });
      io.observe(el);
    }

    if ('IntersectionObserver' in window) {
      var slot = document.querySelector('.adsbygoogle');
      if (slot) {
        // Slot already in DOM — observe it directly.
        installIntersectionObserver(slot);
      } else {
        // Slot not yet in DOM — watch for its insertion, bail after 30 s.
        var mutationTimeout = setTimeout(function () {
          mo.disconnect();
          // No slot appeared within 30 s; fall back to idle / load event.
          if ('requestIdleCallback' in window) {
            requestIdleCallback(load, { timeout: 5000 });
          } else {
            window.addEventListener('load', load, { once: true });
          }
        }, 30000);

        var mo = new MutationObserver(function () {
          var found = document.querySelector('.adsbygoogle');
          if (found) {
            mo.disconnect();
            clearTimeout(mutationTimeout);
            installIntersectionObserver(found);
          }
        });
        mo.observe(document.body, { childList: true, subtree: true });
      }
    } else if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 5000 });
    } else {
      window.addEventListener('load', load, { once: true });
    }
  }

  /**
   * Lazy-loads the Kakao JavaScript SDK on the first user interaction with a
   * 10-12 s idle safety-net fallback. Mirrors loadGoogleAnalytics (PR #322).
   *
   * Rationale: the only reason we ship Kakao SDK is the Kakao share button.
   * Clicking the share button is itself an interaction event, so deferring
   * the SDK behind the same interaction-listener cluster never blocks the
   * actual user flow. Bots and bouncers (no interaction) skip the ~30 KB
   * SDK transfer + Kakao.init() entirely.
   *
   * Concurrency: __kakaoLoadInitiated guards against double-fetch when the
   * idle fallback races with a real interaction.
   */
  function loadKakaoSdk() {
    if (!kakaoAppKey) {
      return;
    }
    if (window.__kakaoLoadInitiated) {
      return;
    }

    var load = function () {
      if (window.__kakaoLoadInitiated) {
        return;
      }
      window.__kakaoLoadInitiated = true;
      var script = document.createElement('script');
      script.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js';
      script.integrity = 'sha384-DKYJZ8NLiK8MN4/C5P2dtSmLQ4KwPaoqAfyA/DfmEc1VDxu4kykhOQv0b17OH4S';
      script.crossOrigin = 'anonymous';
      script.onload = function () {
        try {
          if (window.Kakao && !window.Kakao.isInitialized()) {
            window.Kakao.init(kakaoAppKey);
          }
        } catch (_e) { /* ignore init errors */ }
      };
      document.head.appendChild(script);
    };

    var INTERACTION_EVENTS = ['pointermove', 'scroll', 'keydown', 'touchstart', 'click'];
    var fired = false;
    var loadOnce = function () {
      if (fired) {
        return;
      }
      fired = true;
      INTERACTION_EVENTS.forEach(function (ev) {
        window.removeEventListener(ev, loadOnce, { passive: true, capture: true });
      });
      load();
    };
    INTERACTION_EVENTS.forEach(function (ev) {
      window.addEventListener(ev, loadOnce, { passive: true, capture: true });
    });

    // 10-12 s idle safety-net so non-interactive readers can still share
    // (the share button itself counts as interaction, so this rarely fires)
    if ('requestIdleCallback' in window) {
      requestIdleCallback(function () {
        setTimeout(loadOnce, 10000);
      }, { timeout: 5000 });
    } else {
      setTimeout(loadOnce, 12000);
    }
  }

  /**
   * Lazy-loads Sentry SDK on the first user interaction with a 10-12 s idle
   * safety-net fallback. Mirrors loadGoogleAnalytics (PR #322) and
   * loadKakaoSdk (PR #324). Bots and bouncers skip the ~30 KB SDK + 143 ms
   * reflow cost entirely.
   */
  function loadSentry() {
    if (!sentryDsn) return;
    if (window.__sentryLoadInitiated) return;

    var load = function () {
      if (window.__sentryLoadInitiated) return;
      window.__sentryLoadInitiated = true;
      // 1. Load Sentry bundle from CDN with SRI
      var bundleScript = document.createElement('script');
      bundleScript.src = 'https://browser.sentry-cdn.com/9.5.0/bundle.min.js';
      bundleScript.integrity = 'sha384-5uFF6g91sxV2Go9yGCIngIx1AD3yg6buf0YFt7PSNheVk6CneEMSH6Eap5+e+8gt';
      bundleScript.crossOrigin = 'anonymous';
      bundleScript.onload = function () {
        // 2. Load our sentry-init script after the bundle is available
        var initScript = document.createElement('script');
        initScript.src = '/assets/js/sentry-init.js';
        initScript.dataset.sentryDsn = sentryDsn;
        initScript.dataset.productionHost = sentryProductionHost;
        initScript.dataset.allowedHosts = sentryAllowedHosts;
        document.head.appendChild(initScript);
      };
      document.head.appendChild(bundleScript);
    };

    var INTERACTION_EVENTS = ['pointermove', 'scroll', 'keydown', 'touchstart', 'click'];
    var fired = false;
    var loadOnce = function () {
      if (fired) return;
      fired = true;
      INTERACTION_EVENTS.forEach(function (ev) {
        window.removeEventListener(ev, loadOnce, { passive: true, capture: true });
      });
      load();
    };
    INTERACTION_EVENTS.forEach(function (ev) {
      window.addEventListener(ev, loadOnce, { passive: true, capture: true });
    });

    if ('requestIdleCallback' in window) {
      requestIdleCallback(function () { setTimeout(loadOnce, 10000); }, { timeout: 5000 });
    } else {
      setTimeout(loadOnce, 12000);
    }
  }

  function loadFontTier2() {
    if (window.__fontTier2Loaded) {
      return;
    }
    window.__fontTier2Loaded = true;

    var trigger = function () {
      if (!('FontFace' in window) || !document.fonts) {
        return;
      }
      ['400', '700'].forEach(function (weight) {
        try {
          var f = new FontFace(
            'Noto Sans KR',
            "url('/assets/fonts/noto-sans-kr-" + weight + "-tier2.woff2') format('woff2')",
            { style: 'normal', weight: weight, display: 'swap' }
          );
          f.load().then(function (loaded) {
            document.fonts.add(loaded);
          }).catch(function () { /* ignore network/decoding errors */ });
        } catch (_e) { /* ignore */ }
      });
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(trigger, { timeout: 5000 });
    } else {
      setTimeout(trigger, 2000);
    }
  }

  applyTheme();
  initConsoleFilter();
  bindCssFallback();
  markBodyLoaded();
  registerServiceWorker();
  loadFontTier2();
  loadGoogleAnalytics();
  loadAdsense();
  loadKakaoSdk();
  loadSentry();
})();
