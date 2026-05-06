(function () {
  'use strict';

  var searchInput = document.getElementById('archive-search');
  if (!searchInput) {
    return;
  }

  var filterBtns = document.querySelectorAll('.archive-filter');
  var years = document.querySelectorAll('.archive-year');
  var months = document.querySelectorAll('.archive-month');
  var emptyMsg = document.querySelector('.archive-empty');
  var visibleCounter = document.getElementById('archive-visible-count');
  // Items are hydrated from /archive-data.json — start empty, refresh
  // after the JSON is rendered into the DOM.
  var items = [];

  // Derive baseurl from the current path so /archive/ → '' on Vercel
  // and /tech-blog/archive/ → '/tech-blog' on the GH Pages backup.
  var baseUrl = location.pathname.replace(/\/archive\/?.*$/, '');

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function renderItem(post) {
    var title = post.t || '';
    var titleLower = title.toLowerCase();
    var tagsArr = Array.isArray(post.tags) ? post.tags : [];
    var tagStr = tagsArr.map(function (t) { return String(t).toLowerCase(); }).join(' ');
    var cats = post.cs || (post.c ? String(post.c).toLowerCase() : '');
    var excerpt = post.ex || '';

    var cat = post.c || '';
    var catBadge = '';
    if (cat) {
      var catClass = cat.toLowerCase().replace(/\s+/g, '-');
      catBadge = '<span class="category-badge ' + escapeHtml(catClass) + '">' +
        escapeHtml(cat) + '</span>';
    }

    var tagChips = '';
    if (tagsArr.length > 0) {
      tagChips = '<span class="archive-tag-chips" aria-label="태그">';
      for (var i = 0; i < tagsArr.length; i++) {
        tagChips += '<span class="archive-tag-chip" data-tag="' +
          escapeHtml(String(tagsArr[i]).toLowerCase()) + '">' +
          escapeHtml(tagsArr[i]) + '</span>';
      }
      tagChips += '</span>';
    }

    var excerptSpan = '';
    if (excerpt) {
      excerptSpan = '<span class="archive-item-excerpt" aria-hidden="true">' +
        escapeHtml(excerpt) + '</span>';
    }

    return '<li class="archive-item" ' +
      'data-categories="' + escapeHtml(cats.trim()) + '" ' +
      'data-title="' + escapeHtml(titleLower) + '" ' +
      'data-tags="' + escapeHtml(tagStr) + '" ' +
      'data-excerpt="' + escapeHtml(excerpt) + '">' +
      '<time datetime="' + escapeHtml(post.x) + '">' + escapeHtml(post.d) + '</time>' +
      catBadge +
      '<a href="' + escapeHtml(post.u) + '" class="archive-item-title">' + escapeHtml(title) + '</a>' +
      tagChips +
      excerptSpan +
      '</li>';
  }

  function hydrateAll(data) {
    if (!data) return;
    Object.keys(data).forEach(function (year) {
      var yearSection = document.querySelector('.archive-year[data-year="' + year + '"]');
      if (!yearSection) return;
      var monthsData = data[year];
      Object.keys(monthsData).forEach(function (month) {
        var monthEl = yearSection.querySelector('.archive-month[data-month="' + month + '"]');
        if (!monthEl) return;
        var ul = monthEl.querySelector('.archive-list');
        if (!ul) return;
        var posts = monthsData[month] || [];
        var html = '';
        for (var i = 0; i < posts.length; i++) html += renderItem(posts[i]);
        ul.innerHTML = html;
        ul.removeAttribute('aria-busy');
      });
      yearSection.setAttribute('data-loaded', '1');
    });
    // Refresh DOM cache after hydration so the filter runs over the
    // freshly-injected rows.
    items = Array.prototype.slice.call(document.querySelectorAll('.archive-item'));
    bindTagChipClicks();
    applyFilters(false);
  }

  function bindTagChipClicks() {
    document.querySelectorAll('.archive-tag-chip').forEach(function (chip) {
      if (chip.__bound) return;
      chip.__bound = true;
      chip.addEventListener('click', function (e) {
        e.preventDefault();
        var tag = chip.getAttribute('data-tag') || '';
        if (!tag) return;
        searchInput.value = tag;
        currentSearch = tag;
        if (kbdHint) kbdHint.style.display = 'none';
        applyFilters(true);
        var toolbar = document.querySelector('.archive-toolbar');
        if (toolbar) toolbar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    });
  }

  function loadArchiveData() {
    fetch(baseUrl + '/archive-data.json', { credentials: 'same-origin' })
      .then(function (r) {
        if (!r.ok) throw new Error('archive-data.json HTTP ' + r.status);
        return r.json();
      })
      .then(hydrateAll)
      .catch(function () {
        // Network failure: leave the page in its empty stub state. The
        // visible count drops to zero — better than crashing the filter.
      });
  }

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
  // Note: chips are injected by hydrateAll() after archive-data.json
  // loads, so the binding happens inside hydrateAll(). The static-page
  // delegated handler stays here only for any chip that might exist
  // outside the hydrated containers.
  bindTagChipClicks();

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

  // ── Lazy hydration: fetch archive-data.json and render items ─────
  // Items render asynchronously so the initial paint shows the year
  // headers immediately, with rows filling in after JSON arrives.
  loadArchiveData();
})();
