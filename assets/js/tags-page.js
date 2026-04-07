(function () {
  'use strict';

  var input = document.getElementById('tag-search');
  if (!input) {
    return;
  }

  var tags = document.querySelectorAll('.tag-cloud .tag');
  var sections = document.querySelectorAll('.tag-section');
  var emptyEl = document.getElementById('tags-search-empty');
  var timer;

  function updateEmptyState(visibleTagCount) {
    if (!emptyEl) {
      return;
    }
    var show = visibleTagCount === 0 && input.value.trim().length > 0;
    emptyEl.hidden = !show;
    emptyEl.setAttribute('aria-hidden', show ? 'false' : 'true');
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      var q = input.value.toLowerCase().trim();
      var visibleTags = 0;
      tags.forEach(function (tag) {
        var name = tag.textContent.toLowerCase();
        var match = !q || name.indexOf(q) !== -1;
        tag.style.display = match ? '' : 'none';
        if (match) {
          visibleTags += 1;
        }
      });
      sections.forEach(function (sec) {
        var header = sec.querySelector('.tag-section-header');
        var name = header ? header.textContent.toLowerCase() : '';
        sec.style.display = !q || name.indexOf(q) !== -1 ? '' : 'none';
      });
      updateEmptyState(visibleTags);
    }, 200);
  });
})();
