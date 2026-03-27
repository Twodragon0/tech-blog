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

  function loadGoogleAnalytics() {
    if (!gaId) {
      return;
    }

    var load = function () {
      var script = document.createElement('script');
      script.async = true;
      script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(gaId);
      script.onload = function () {
        window.dataLayer = window.dataLayer || [];
        function gtag() {
          window.dataLayer.push(arguments);
        }

        gtag('js', new Date());
        gtag('config', gaId, { send_page_view: false });
        gtag('event', 'page_view', {
          page_path: window.location.pathname + window.location.search,
        });
      };

      document.head.appendChild(script);
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 3000 });
    } else {
      window.addEventListener('load', load, { once: true });
    }
  }

  function loadAdsense() {
    if (!adsenseClient) {
      return;
    }

    var load = function () {
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

    if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 5000 });
    } else {
      window.addEventListener('load', load, { once: true });
    }
  }

  function loadKakaoSdk() {
    if (!kakaoAppKey) {
      return;
    }

    var load = function () {
      var script = document.createElement('script');
      script.src = 'https://t1.kakaocdn.net/kakao_js_sdk/2.7.4/kakao.min.js';
      script.integrity = 'sha384-DKYJZ8NLiK8MN4/C5P2dtSmLQ4KwPaoqAfyA/DfmEc1VDxu4kykhOQv0b17OH4S';
      script.crossOrigin = 'anonymous';
      script.onload = function () {
        if (window.Kakao && !window.Kakao.isInitialized()) {
          window.Kakao.init(kakaoAppKey);
        }
      };
      document.head.appendChild(script);
    };

    if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 3000 });
    } else {
      window.addEventListener('load', load, { once: true });
    }
  }

  // Activate non-blocking Google Fonts (media="print" → "all")
  var gfonts = document.getElementById('gfonts');
  if (gfonts) {
    gfonts.media = 'all';
  }

  applyTheme();
  initConsoleFilter();
  bindCssFallback();
  markBodyLoaded();
  registerServiceWorker();
  loadGoogleAnalytics();
  loadAdsense();
  loadKakaoSdk();
})();
