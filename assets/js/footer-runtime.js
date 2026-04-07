(function () {
  'use strict';

  if (window.__footerRuntimeInitialized) {
    return;
  }
  window.__footerRuntimeInitialized = true;

  var currentScript = document.currentScript;
  var searchScriptSrc = (currentScript && currentScript.getAttribute('data-search-src')) || '/assets/js/main-search.js';

  var searchInput = document.getElementById('search-input');
  if (searchInput) {
    var searchScriptLoaded = false;
    var loadSearchScript = function () {
      if (searchScriptLoaded) {
        return;
      }

      searchScriptLoaded = true;
      var script = document.createElement('script');
      script.src = searchScriptSrc;
      script.defer = true;
      script.onerror = function () {
        searchScriptLoaded = false;
      };
      document.body.appendChild(script);
    };

    searchInput.addEventListener('focus', loadSearchScript, { once: true, passive: true });
    setTimeout(function () {
      if (document.visibilityState === 'visible' && !searchScriptLoaded) {
        if (typeof requestIdleCallback !== 'undefined') {
          requestIdleCallback(loadSearchScript, { timeout: 2000 });
        } else {
          setTimeout(loadSearchScript, 0);
        }
      }
    }, 3000);
  }

  // Image fallback is handled by main-core.js unified handler (data-fallback attribute)

  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return;
  }

  var shouldSample = Math.random() < 0.1;
  var analyticsScript = document.createElement('script');
  analyticsScript.defer = true;
  analyticsScript.src = 'https://va.vercel-scripts.com/v1/script.js';
  analyticsScript.onerror = function () {};
  document.head.appendChild(analyticsScript);

  if (shouldSample) {
    var speedInsightsScript = document.createElement('script');
    speedInsightsScript.defer = true;
    speedInsightsScript.src = 'https://va.vercel-scripts.com/v1/speed-insights/script.js';
    speedInsightsScript.onerror = function () {};
    document.head.appendChild(speedInsightsScript);
  }
})();
