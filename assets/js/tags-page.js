(function () {
  'use strict';

  /* -------------------------------------------------------
     DOM refs
  ------------------------------------------------------- */
  var input       = document.getElementById('tag-search');
  var tagCloud    = document.querySelector('.tag-cloud');
  var sections    = document.querySelectorAll('.tag-section');
  var emptyEl     = document.getElementById('tags-search-empty');
  var sortBtns    = document.querySelectorAll('.tags-sort-btn');
  var clearBtn    = document.getElementById('tags-clear-btn');
  var filterStatus = document.getElementById('tags-filter-status');
  var selectedBadge = document.getElementById('tags-selected-badge');

  if (!input || !tagCloud) return;

  /* -------------------------------------------------------
     State
  ------------------------------------------------------- */
  var selectedTags = [];   // array of slugified tag names
  var currentSort  = loadPref('tags-sort', 'alpha');
  var timer;

  /* -------------------------------------------------------
     localStorage helpers
  ------------------------------------------------------- */
  function savePref(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }

  function loadPref(key, fallback) {
    try {
      var v = localStorage.getItem(key);
      return v !== null ? JSON.parse(v) : fallback;
    } catch (e) { return fallback; }
  }

  /* -------------------------------------------------------
     Restore persisted state
  ------------------------------------------------------- */
  (function restoreState() {
    // Restore sort
    var saved = loadPref('tags-sort', 'alpha');
    currentSort = saved;
    sortBtns.forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-sort') === currentSort);
    });
    applySortToDom(currentSort);

    // Restore selected tags
    var savedTags = loadPref('tags-selected', []);
    if (Array.isArray(savedTags) && savedTags.length > 0) {
      savedTags.forEach(function (slug) {
        var el = tagCloud.querySelector('[data-tag="' + slug + '"]');
        if (el) selectedTags.push(slug);
      });
      applyMultiFilter();
    }
  })();

  /* -------------------------------------------------------
     Tag cloud: multi-select clicks
  ------------------------------------------------------- */
  tagCloud.addEventListener('click', function (e) {
    var tag = e.target.closest('.tag[data-tag]');
    if (!tag) return;

    var slug = tag.getAttribute('data-tag');
    var href = tag.getAttribute('href');

    // If no tags were selected yet and user just wants to scroll: allow
    // But if we're toggling selection, prevent default scroll
    var idx = selectedTags.indexOf(slug);
    if (idx === -1) {
      // Add to selection
      e.preventDefault();
      selectedTags.push(slug);
    } else {
      // Deselect
      e.preventDefault();
      selectedTags.splice(idx, 1);
      // If now empty, allow natural scroll on next click; for now just clear
    }

    savePref('tags-selected', selectedTags);
    applyMultiFilter();

    // If exactly one tag selected (just added), scroll to section smoothly
    if (selectedTags.length === 1 && idx === -1 && href) {
      var target = document.getElementById(href.slice(1));
      if (target) {
        setTimeout(function () {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 80);
      }
    }
  });

  function applyMultiFilter() {
    var cloudTags = tagCloud.querySelectorAll('.tag[data-tag]');

    if (selectedTags.length === 0) {
      // No selection — reset everything
      cloudTags.forEach(function (t) {
        t.classList.remove('tag--selected', 'tag--dimmed');
      });
      sections.forEach(function (sec) {
        sec.classList.remove('tag-section--dimmed');
        if (!sec.getAttribute('data-search-hidden')) {
          sec.style.display = '';
        }
      });
      if (filterStatus) filterStatus.hidden = true;
      return;
    }

    // Update cloud visual states
    cloudTags.forEach(function (t) {
      var slug = t.getAttribute('data-tag');
      var isSelected = selectedTags.indexOf(slug) !== -1;
      t.classList.toggle('tag--selected', isSelected);
      t.classList.toggle('tag--dimmed', !isSelected);
    });

    // Show/dim sections
    sections.forEach(function (sec) {
      var sectionTag = sec.getAttribute('data-section-tag');
      var match = selectedTags.indexOf(sectionTag) !== -1;
      if (match) {
        sec.classList.remove('tag-section--dimmed');
        sec.style.display = '';
      } else {
        sec.classList.add('tag-section--dimmed');
        // Still visible but dimmed — don't hide, just dim
        sec.style.display = '';
      }
    });

    // Update badge
    if (filterStatus && selectedBadge) {
      filterStatus.hidden = false;
      selectedBadge.textContent = selectedTags.length + '개 선택됨';
    }

    savePref('tags-selected', selectedTags);
  }

  /* -------------------------------------------------------
     Clear all button
  ------------------------------------------------------- */
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      selectedTags = [];
      savePref('tags-selected', []);
      applyMultiFilter();
    });
  }

  /* -------------------------------------------------------
     Search filter
  ------------------------------------------------------- */
  function updateEmptyState(visibleTagCount) {
    if (!emptyEl) return;
    var show = visibleTagCount === 0 && input.value.trim().length > 0;
    emptyEl.hidden = !show;
    emptyEl.setAttribute('aria-hidden', show ? 'false' : 'true');
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      var q = input.value.toLowerCase().trim();
      var visibleTags = 0;
      var cloudTags = tagCloud.querySelectorAll('.tag[data-tag]');

      cloudTags.forEach(function (tag) {
        var name = (tag.getAttribute('data-tag-name') || tag.textContent).toLowerCase();
        var match = !q || name.indexOf(q) !== -1;
        tag.style.display = match ? '' : 'none';
        if (match) visibleTags += 1;
      });

      sections.forEach(function (sec) {
        var header = sec.querySelector('.tag-section-header');
        var name = header ? header.textContent.toLowerCase() : '';
        var visible = !q || name.indexOf(q) !== -1;
        sec.style.display = visible ? '' : 'none';
        sec.setAttribute('data-search-hidden', visible ? '' : '1');
      });

      // Also hide letter dividers if their letter group is fully hidden
      updateLetterDividers();
      updateEmptyState(visibleTags);
    }, 200);
  });

  /* -------------------------------------------------------
     Keyboard shortcuts
  ------------------------------------------------------- */
  var kbdHint = input.parentElement ? input.parentElement.querySelector('.search-kbd') : null;

  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
    if (e.key === 'Escape' && document.activeElement === input) {
      input.blur();
      input.value = '';
      input.dispatchEvent(new Event('input'));
    }
  });

  if (kbdHint) {
    input.addEventListener('focus', function () { kbdHint.style.display = 'none'; });
    input.addEventListener('blur', function () {
      if (!input.value) kbdHint.style.display = '';
    });
  }

  /* -------------------------------------------------------
     Sort
  ------------------------------------------------------- */
  if (sortBtns.length > 0) {
    sortBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        sortBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        currentSort = btn.getAttribute('data-sort');
        savePref('tags-sort', currentSort);
        applySortToDom(currentSort);
      });
    });
  }

  function applySortToDom(sortType) {
    var cloudTags = Array.prototype.slice.call(tagCloud.querySelectorAll('.tag[data-tag]'));
    var dividers  = Array.prototype.slice.call(tagCloud.querySelectorAll('.tag-letter-divider'));

    // Remove all tags and dividers from DOM temporarily
    cloudTags.forEach(function (t) { tagCloud.removeChild(t); });
    dividers.forEach(function (d) { tagCloud.removeChild(d); });

    if (sortType === 'count') {
      // Frequency sort: highest count first, no letter dividers
      tagCloud.classList.remove('sort-alpha');
      cloudTags.sort(function (a, b) {
        return (parseInt(b.getAttribute('data-count')) || 0) -
               (parseInt(a.getAttribute('data-count')) || 0);
      });
      cloudTags.forEach(function (t) {
        t.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        t.style.opacity = '0';
        tagCloud.appendChild(t);
      });
      // Fade in
      requestAnimationFrame(function () {
        cloudTags.forEach(function (t, i) {
          setTimeout(function () {
            t.style.opacity = '';
            t.style.transform = '';
          }, i * 6);
        });
      });
    } else {
      // Alpha sort: A-Z with letter dividers
      tagCloud.classList.add('sort-alpha');
      cloudTags.sort(function (a, b) {
        var na = (a.getAttribute('data-tag-name') || '').toLowerCase();
        var nb = (b.getAttribute('data-tag-name') || '').toLowerCase();
        return na.localeCompare(nb, 'ko');
      });

      // Group by first letter and interleave dividers
      var currentLetter = null;
      var dividerMap = {};
      dividers.forEach(function (d) {
        dividerMap[d.getAttribute('data-letter')] = d;
      });

      cloudTags.forEach(function (t, i) {
        var letter = t.getAttribute('data-letter') || '';
        if (letter !== currentLetter) {
          var div = dividerMap[letter];
          if (div) tagCloud.appendChild(div);
          currentLetter = letter;
        }
        t.style.transition = 'opacity 0.2s ease';
        t.style.opacity = '0';
        tagCloud.appendChild(t);
      });

      requestAnimationFrame(function () {
        cloudTags.forEach(function (t, i) {
          setTimeout(function () { t.style.opacity = ''; }, i * 6);
        });
      });
    }
  }

  /* -------------------------------------------------------
     Letter divider visibility (for search + alpha sort)
  ------------------------------------------------------- */
  function updateLetterDividers() {
    if (!tagCloud.classList.contains('sort-alpha')) return;
    var dividers = tagCloud.querySelectorAll('.tag-letter-divider');
    dividers.forEach(function (div) {
      var letter = div.getAttribute('data-letter');
      // Check if any visible tag with this letter exists
      var hasTags = tagCloud.querySelector(
        '.tag[data-letter="' + letter + '"]:not([style*="display: none"]):not([style*="display:none"])'
      );
      div.style.display = hasTags ? '' : 'none';
    });
  }

  /* -------------------------------------------------------
     Related tag pills — scroll to section on click
  ------------------------------------------------------- */
  document.querySelectorAll('.tag-related-pill').forEach(function (pill) {
    pill.addEventListener('click', function (e) {
      var slug = pill.getAttribute('data-related-tag');
      if (!slug) return;
      var target = document.getElementById(slug);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

})();
