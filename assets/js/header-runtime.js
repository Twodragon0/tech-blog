(function () {
  'use strict';

  var script = document.currentScript;
  var translateSrc = (script && script.getAttribute('data-translate-src')) || '/assets/js/google-translate.js';
  var loaded = false;
  var toggle = document.getElementById('lang-toggle');

  if (!toggle) {
    return;
  }

  var loadTranslate = function () {
    if (loaded) {
      return;
    }
    loaded = true;
    var node = document.createElement('script');
    node.src = translateSrc;
    node.defer = true;
    document.body.appendChild(node);
  };

  // The FIRST toggle click is only observable here — google-translate.js has not
  // loaded yet, so its own handler cannot see it. Without this, usage data for the
  // translation feature would start at the second click and understate demand.
  toggle.addEventListener('click', function () {
    if (window.__track) {
      window.__track('lang_toggle_open', { first_open: true });
    }
  }, { once: true, passive: true });

  toggle.addEventListener('click', loadTranslate, { once: true, passive: true });

  try {
    var pref = localStorage.getItem('preferredLang');
    if (pref && pref !== 'system' && pref !== 'ko') {
      loadTranslate();
    }
  } catch (_error) {}
})();
