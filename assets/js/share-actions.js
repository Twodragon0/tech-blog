// Share buttons - external event handlers (CSP-safe, no inline onclick)
(function() {
  'use strict';

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('[data-share-action]');
    if (!btn) return;

    var action = btn.getAttribute('data-share-action');
    var url = btn.getAttribute('data-share-url') || '';
    var title = btn.getAttribute('data-share-title') || '';
    var desc = btn.getAttribute('data-share-desc') || '';

    if (action === 'kakao') {
      if (typeof shareKakao === 'function') {
        shareKakao(url, title, desc);
      }
    } else if (action === 'copy') {
      if (typeof copyToClipboard === 'function') {
        copyToClipboard(url);
      }
    }
  });
})();
