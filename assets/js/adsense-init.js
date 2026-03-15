(function () {
  'use strict';

  if (window.__adsenseSlotInitializer) {
    return;
  }

  function initializeAdsenseSlots() {
    if (!window.adsbygoogle || !window.adsbygoogle.push) {
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
    setTimeout(initializeAdsenseSlots, 300);
  }, { once: true });
})();
