(function () {
  'use strict';

  var searchInput = document.getElementById('archive-search');
  if (!searchInput) {
    return;
  }

  var filterBtns = document.querySelectorAll('.archive-filter');
  var items = Array.prototype.slice.call(document.querySelectorAll('.archive-item'));
  var years = document.querySelectorAll('.archive-year');
  var months = document.querySelectorAll('.archive-month');
  var emptyMsg = document.querySelector('.archive-empty');
  var visibleCounter = document.getElementById('archive-visible-count');

  // ── localStorage persistence ─────────────────────────────────────
  var LS_FILTER = 'archive_filter';
  var LS_SEARCH = 'archive_search';

  function loadState() {
    try {
      return {
        filter: localStorage.getItem(LS_FILTER) || 'all',
        search: localStorage.getItem(LS_SEARCH) || ''
      };
    } catch (_) {
      return { filter: 'all', search: '' };
    }
  }

  function saveState(filter, search) {
    try {
      localStorage.setItem(LS_FILTER, filter);
      localStorage.setItem(LS_SEARCH, search);
    } catch (_) {}
  }

  var saved = loadState();
  var currentFilter = saved.filter;
  var currentSearch = saved.search;

  // Restore search input value
  if (currentSearch) {
    searchInput.value = currentSearch;
  }

  // ── Filter button state ──────────────────────────────────────────
  function setActiveFilterButton(filterValue) {
    filterBtns.forEach(function (btn) {
      var v = btn.getAttribute('data-filter') || 'all';
      btn.classList.toggle('active', v === filterValue);
    });
  }

  // Restore active filter button
  setActiveFilterButton(currentFilter);

  // ── Apply filters with fade animation ────────────────────────────
  function applyFilters(animate) {
    var visibleCount = 0;

    items.forEach(function (item) {
      var cats = item.getAttribute('data-categories') || '';
      var title = item.getAttribute('data-title') || '';
      var tags = item.getAttribute('data-tags') || '';
      var matchFilter = currentFilter === 'all' || cats.indexOf(currentFilter) !== -1;
      var matchSearch = !currentSearch ||
        title.indexOf(currentSearch) !== -1 ||
        tags.indexOf(currentSearch) !== -1;
      var show = matchFilter && matchSearch;

      if (show) {
        visibleCount += 1;
        item.classList.remove('is-hidden', 'is-filtering-out');
        if (animate) {
          item.classList.remove('is-filtering-in');
          // Force reflow to restart animation
          void item.offsetWidth;
          item.classList.add('is-filtering-in');
        }
      } else {
        item.classList.add('is-hidden');
        item.classList.remove('is-filtering-in', 'is-filtering-out');
      }
    });

    months.forEach(function (monthNode) {
      var hasVisible = monthNode.querySelector('.archive-item:not(.is-hidden)');
      monthNode.style.display = hasVisible ? '' : 'none';
    });

    years.forEach(function (yearNode) {
      var hasVisible = yearNode.querySelector('.archive-month:not([style*="display: none"])');
      yearNode.style.display = hasVisible ? '' : 'none';
    });

    if (emptyMsg) {
      emptyMsg.style.display = visibleCount === 0 ? '' : 'none';
    }
    if (visibleCounter) {
      visibleCounter.textContent = String(visibleCount);
    }

    saveState(currentFilter, currentSearch);
  }

  // ── Filter buttons ───────────────────────────────────────────────
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      currentFilter = btn.getAttribute('data-filter') || 'all';
      setActiveFilterButton(currentFilter);
      applyFilters(true);
    });
  });

  // ── Search input ─────────────────────────────────────────────────
  var searchTimer;
  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () {
      currentSearch = searchInput.value.toLowerCase().trim();
      applyFilters(true);
    }, 180);
  });

  // ── Keyboard shortcuts ───────────────────────────────────────────
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
    if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.blur();
      searchInput.value = '';
      currentSearch = '';
      applyFilters(true);
    }
  });

  // ── Kbd hint visibility ──────────────────────────────────────────
  var kbdHint = document.querySelector('.search-kbd');
  if (kbdHint) {
    searchInput.addEventListener('focus', function () { kbdHint.style.display = 'none'; });
    searchInput.addEventListener('blur', function () {
      if (!searchInput.value) kbdHint.style.display = '';
    });
    if (currentSearch) kbdHint.style.display = 'none';
  }

  // ── Reset button ─────────────────────────────────────────────────
  function resetAllFilters() {
    searchInput.value = '';
    currentSearch = '';
    currentFilter = 'all';
    setActiveFilterButton('all');
    if (kbdHint) kbdHint.style.display = '';
    applyFilters(true);
  }

  var resetBtn = document.querySelector('.archive-empty-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', resetAllFilters);
  }

  // ── Tag chip clicks (filter by tag via search) ───────────────────
  document.querySelectorAll('.archive-tag-chip').forEach(function (chip) {
    chip.addEventListener('click', function (e) {
      e.preventDefault();
      var tag = chip.getAttribute('data-tag') || '';
      if (!tag) return;
      searchInput.value = tag;
      currentSearch = tag;
      if (kbdHint) kbdHint.style.display = 'none';
      applyFilters(true);
      // Scroll to toolbar
      var toolbar = document.querySelector('.archive-toolbar');
      if (toolbar) {
        toolbar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  });

  // ── Smooth scroll for in-page anchors ───────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    var href = anchor.getAttribute('href');
    if (!href || href === '#') return;
    var id = href.slice(1);
    if (!id || (id.indexOf('year-') !== 0 && id !== 'archive-top')) return;
    anchor.addEventListener('click', function (e) {
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Scroll progress bar ──────────────────────────────────────────
  var progressBar = document.getElementById('archive-scroll-bar');
  if (progressBar) {
    var ticking = false;
    function updateProgress() {
      var archivePage = document.querySelector('.archive-page');
      if (!archivePage) return;
      var rect = archivePage.getBoundingClientRect();
      var pageTop = rect.top + window.pageYOffset;
      var pageHeight = archivePage.offsetHeight;
      var viewportH = window.innerHeight;
      var scrolled = window.pageYOffset - pageTop;
      var scrollable = pageHeight - viewportH;
      var pct = scrollable > 0 ? Math.min(100, Math.max(0, (scrolled / scrollable) * 100)) : 0;
      progressBar.style.width = pct + '%';
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(updateProgress);
        ticking = true;
      }
    }, { passive: true });

    updateProgress();
  }

  // ── Stats counter animation (IntersectionObserver) ───────────────
  var statNumbers = document.querySelectorAll('[data-stat-number]');
  if (statNumbers.length && 'IntersectionObserver' in window) {
    var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function animateCount(el, target, duration) {
      if (prefersReduced) return;
      var start = 0;
      var startTime = null;

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        // Ease out cubic
        var eased = 1 - Math.pow(1 - progress, 3);
        var current = Math.round(eased * target);
        el.textContent = String(current);
        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          el.textContent = String(target);
        }
      }

      requestAnimationFrame(step);
    }

    var statsObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseInt(el.getAttribute('data-stat-number'), 10);
        if (!isNaN(target) && el.id !== 'archive-visible-count') {
          animateCount(el, target, 800);
        }
        statsObserver.unobserve(el);
      });
    }, { threshold: 0.5 });

    statNumbers.forEach(function (el) {
      // Don't animate the live counter
      if (el.id !== 'archive-visible-count') {
        statsObserver.observe(el);
      }
    });
  }

  // ── Initial filter application (no animation on first load) ──────
  applyFilters(false);
})();
