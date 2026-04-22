(function () {
  'use strict';

  if (window.__adsenseSlotInitializer) {
    return;
  }

  var AD_LOAD_TIMEOUT = 5000;
  var AD_CHECK_INTERVAL = 200;
  var _fallbackTimer = null;
  var _checkInterval = null;

  function hideAdSlots() {
    var slots = document.querySelectorAll('ins.adsbygoogle');
    for (var i = 0; i < slots.length; i += 1) {
      slots[i].style.display = 'none';
      slots[i].style.minHeight = '0';
      slots[i].setAttribute('data-ad-load-failed', 'true');
    }
  }

  function isAdsenseReady() {
    return (
      typeof window.adsbygoogle !== 'undefined' &&
      typeof window.adsbygoogle.push === 'function'
    );
  }

  function startFallbackGuard() {
    if (_fallbackTimer !== null) {
      return;
    }

    _fallbackTimer = setTimeout(function () {
      clearInterval(_checkInterval);
      _checkInterval = null;
      if (!isAdsenseReady()) {
        hideAdSlots();
      }
    }, AD_LOAD_TIMEOUT);

    _checkInterval = setInterval(function () {
      if (isAdsenseReady()) {
        clearTimeout(_fallbackTimer);
        clearInterval(_checkInterval);
        _fallbackTimer = null;
        _checkInterval = null;
      }
    }, AD_CHECK_INTERVAL);
  }

  function initializeAdsenseSlots() {
    if (!isAdsenseReady()) {
      return;
    }

    var slots = document.querySelectorAll('.adsbygoogle:not([data-ads-initialized])');
    for (var i = 0; i < slots.length; i += 1) {
      try {
        window.adsbygoogle.push({});
        slots[i].setAttribute('data-ads-initialized', '1');
      } catch (_error) {}
    }
  }

  window.__adsenseSlotInitializer = initializeAdsenseSlots;
  window.addEventListener('adsense:ready', initializeAdsenseSlots);
  window.addEventListener('load', function () {
    startFallbackGuard();
    setTimeout(initializeAdsenseSlots, 300);
  }, { once: true });
})();
