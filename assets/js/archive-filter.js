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
  var currentFilter = 'all';
  var currentSearch = '';

  function setActiveFilterButton(filterValue) {
    filterBtns.forEach(function (btn) {
      var v = btn.getAttribute('data-filter') || 'all';
      btn.classList.toggle('active', v === filterValue);
    });
  }

  function applyFilters() {
    var visibleCount = 0;

    items.forEach(function (item) {
      var cats = item.getAttribute('data-categories') || '';
      var title = item.getAttribute('data-title') || '';
      var matchFilter = currentFilter === 'all' || cats.indexOf(currentFilter) !== -1;
      var matchSearch = !currentSearch || title.indexOf(currentSearch) !== -1;
      var show = matchFilter && matchSearch;

      item.style.display = show ? '' : 'none';
      if (show) {
        visibleCount += 1;
      }
    });

    months.forEach(function (monthNode) {
      var visibleItems = monthNode.querySelectorAll('.archive-item:not([style*="display: none"])');
      monthNode.style.display = visibleItems.length > 0 ? '' : 'none';
    });

    years.forEach(function (yearNode) {
      var visibleMonths = yearNode.querySelectorAll('.archive-month:not([style*="display: none"])');
      yearNode.style.display = visibleMonths.length > 0 ? '' : 'none';
    });

    if (emptyMsg) {
      emptyMsg.style.display = visibleCount === 0 ? '' : 'none';
    }
    if (visibleCounter) {
      visibleCounter.textContent = String(visibleCount);
    }
  }

  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      currentFilter = btn.getAttribute('data-filter') || 'all';
      setActiveFilterButton(currentFilter);
      applyFilters();
    });
  });

  var searchTimer;
  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () {
      currentSearch = searchInput.value.toLowerCase().trim();
      applyFilters();
    }, 200);
  });

  // Keyboard shortcut: "/" focuses search, Escape clears and blurs
  document.addEventListener('keydown', function (e) {
    if (e.key === '/' && document.activeElement !== searchInput) {
      e.preventDefault();
      searchInput.focus();
    }
    if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.blur();
      searchInput.value = '';
      currentSearch = '';
      applyFilters();
    }
  });

  // Hide kbd hint when input is focused
  var kbdHint = document.querySelector('.search-kbd');
  if (kbdHint) {
    searchInput.addEventListener('focus', function () { kbdHint.style.display = 'none'; });
    searchInput.addEventListener('blur', function () {
      if (!searchInput.value) kbdHint.style.display = '';
    });
  }

  function resetAllFilters() {
    searchInput.value = '';
    currentSearch = '';
    currentFilter = 'all';
    setActiveFilterButton('all');
    applyFilters();
  }

  // Reset button in empty state
  var resetBtn = document.querySelector('.archive-empty-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      resetAllFilters();
    });
  }

  // Smooth scroll for in-page anchors (year headers and top)
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    var href = anchor.getAttribute('href');
    if (!href || href === '#') {
      return;
    }
    var id = href.slice(1);
    if (!id || id.indexOf('year-') !== 0 && id !== 'archive-top') {
      return;
    }
    anchor.addEventListener('click', function (e) {
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();
