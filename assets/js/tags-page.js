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

  // Keyboard shortcut: "/" focuses search, Escape clears and blurs
  var kbdHint = input.parentElement.querySelector('.search-kbd');
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
    if (e.key === 'Escape' && document.activeElement === input) {
      input.blur();
      input.value = '';
      var evt = new Event('input');
      input.dispatchEvent(evt);
    }
  });

  if (kbdHint) {
    input.addEventListener('focus', function () { kbdHint.style.display = 'none'; });
    input.addEventListener('blur', function () {
      if (!input.value) kbdHint.style.display = '';
    });
  }

  // Sort functionality
  var sortBtns = document.querySelectorAll('.tags-sort-btn');
  var tagCloud = document.querySelector('.tag-cloud');

  if (sortBtns.length > 0 && tagCloud) {
    sortBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        sortBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        var sortType = btn.getAttribute('data-sort');
        var tagArr = Array.prototype.slice.call(tags);

        tagArr.sort(function (a, b) {
          if (sortType === 'count') {
            var countA = parseInt(a.querySelector('.tag-count').textContent) || 0;
            var countB = parseInt(b.querySelector('.tag-count').textContent) || 0;
            return countB - countA;
          }
          return a.textContent.trim().toLowerCase().localeCompare(b.textContent.trim().toLowerCase());
        });

        tagArr.forEach(function (tag) {
          tagCloud.appendChild(tag);
        });
      });
    });
  }

  // Smooth scroll for tag anchors
  document.querySelectorAll('.tag-cloud .tag').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var href = anchor.getAttribute('href');
      if (!href || href.charAt(0) !== '#') return;
      var target = document.getElementById(href.slice(1));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
