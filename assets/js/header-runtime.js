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

  toggle.addEventListener('click', loadTranslate, { once: true, passive: true });

  try {
    var pref = localStorage.getItem('preferredLang');
    if (pref && pref !== 'system' && pref !== 'ko') {
      loadTranslate();
    }
  } catch (_error) {}
})();
