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
      filterBtns.forEach(function (otherBtn) {
        otherBtn.classList.remove('active');
      });
      btn.classList.add('active');
      currentFilter = btn.getAttribute('data-filter') || 'all';
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
})();
