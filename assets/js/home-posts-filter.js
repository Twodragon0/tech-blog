(function () {
  'use strict';

  var panel = document.getElementById('posts-panel');
  var postsList = document.querySelector('.posts-list');
  var footer = document.querySelector('.posts-footer');
  if (!panel || !postsList || !footer) {
    return;
  }

  var PAGE_SIZE = 12;
  var tabs = document.querySelectorAll('.posts-tab');
  var viewBtns = document.querySelectorAll('.view-btn');
  var allCards = Array.prototype.slice.call(document.querySelectorAll('.post-card[data-category]'));
  var currentFilter = 'latest';
  var showCount = PAGE_SIZE;
  var categoryModes = {
    security: true,
    devsecops: true,
    cloud: true,
    kubernetes: true,
    blockchain: true,
  };

  var showMoreBtn = document.createElement('button');
  showMoreBtn.className = 'btn btn-secondary btn-lg posts-show-more';
  showMoreBtn.type = 'button';
  showMoreBtn.innerHTML =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg> More';
  footer.insertBefore(showMoreBtn, footer.firstChild);

  // Defensive rAF shim: every modern browser ships requestAnimationFrame, but
  // we fall back to setTimeout(fn, 0) for non-browser environments (e.g. JSDOM
  // without rAF, server-side prerender). Behavior is preserved either way.
  var scheduleFrame =
    (typeof window !== 'undefined' && typeof window.requestAnimationFrame === 'function')
      ? function (cb) { return window.requestAnimationFrame(cb); }
      : function (cb) { return setTimeout(cb, 0); };

  function toInt(value) {
    var parsed = Number.parseInt(String(value || ''), 10);
    if (Number.isNaN(parsed)) {
      return 0;
    }
    return parsed;
  }

  function sortCards(cards, mode) {
    var copied = cards.slice();
    copied.sort(function (a, b) {
      var aDate = toInt(a.getAttribute('data-date'));
      var bDate = toInt(b.getAttribute('data-date'));
      var aPopularity = 0;
      var bPopularity = 0;

      if (mode === 'popular') {
        aPopularity = toInt(a.getAttribute('data-popularity'));
        bPopularity = toInt(b.getAttribute('data-popularity'));
        if (aPopularity !== bPopularity) {
          return bPopularity - aPopularity;
        }
      }

      return bDate - aDate;
    });
    return copied;
  }

  function getFilteredCards(mode) {
    if (mode === 'latest' || mode === 'popular') {
      return sortCards(allCards, mode);
    }

    var filtered = allCards.filter(function (card) {
      var cats = (card.getAttribute('data-category') || '').split(' ');
      return cats.indexOf(mode) !== -1;
    });

    return sortCards(filtered, 'latest');
  }

  // Single-pass tab-count tally: walk allCards ONCE, accumulate per-category
  // counters. Replaces the previous 7 × N (= 210 iterations for 30 cards) loop
  // that called getFilteredCards(sort) for each tab.
  function computeTabCounts() {
    var counts = { __total: allCards.length };
    var categoryKeys = Object.keys(categoryModes);
    for (var k = 0; k < categoryKeys.length; k++) {
      counts[categoryKeys[k]] = 0;
    }

    for (var i = 0; i < allCards.length; i++) {
      var attr = allCards[i].getAttribute('data-category') || '';
      var cats = attr.split(' ');
      for (var j = 0; j < cats.length; j++) {
        var cat = cats[j];
        if (cat && Object.prototype.hasOwnProperty.call(categoryModes, cat)) {
          counts[cat] += 1;
        }
      }
    }

    return counts;
  }

  // @perf
  // -----------------------------------------------------------------------
  // renderPosts() uses a strict READ → COMPUTE → WRITE phase separation to
  // avoid forced synchronous layout (FSL / "layout thrashing"):
  //
  //   1. READ phase (synchronous): query DOM state, snapshot all `allCards`
  //      attributes via getFilteredCards / computeTabCounts. No `.style.x = …`
  //      writes happen here, so the browser can serve cached layout values
  //      without flushing pending style invalidations.
  //
  //   2. COMPUTE phase: derive the visible/hidden card set, the tab badge
  //      counts (in a single O(N) pass — not O(N × tabCount)), the empty
  //      state, and the "show more" button state into plain variables.
  //
  //   3. WRITE phase (rAF): inside a single requestAnimationFrame callback,
  //      apply ALL style mutations in one batch. The browser performs ONE
  //      style/layout pass for the whole render instead of one per card.
  //
  // Estimated savings on the homepage: ~50–100 ms of Style & Layout work per
  // tab/sort interaction (was 30 cards × 2 writes + 7 tabs × full re-filter →
  // now 30 cards × 1 write + 7 badge writes, all batched into 1 rAF).
  // -----------------------------------------------------------------------
  function renderPosts() {
    // ---- READ + COMPUTE (no DOM writes) ----
    var filtered = getFilteredCards(currentFilter);
    var totalFiltered = filtered.length;
    var visibleSlice = filtered.slice(0, showCount);
    var visibleSet = new Set(visibleSlice);
    var remaining = showCount < totalFiltered ? totalFiltered - showCount : 0;
    var hasResults = totalFiltered > 0;
    var tabCounts = computeTabCounts();
    var existingEmptyMsg = panel.querySelector('.posts-empty');

    // Build the tab→count plan once. categoryModes[sort] gates whether the
    // tab is a category filter (count = matching cards) or a sort tab
    // (count = all cards), preserving the original behavior.
    var tabPlan = [];
    for (var t = 0; t < tabs.length; t++) {
      var tab = tabs[t];
      var sort = tab.getAttribute('data-sort') || 'latest';
      var count = categoryModes[sort] ? (tabCounts[sort] || 0) : tabCounts.__total;
      tabPlan.push({ tab: tab, count: count });
    }

    // ---- WRITE (batched into one rAF) ----
    scheduleFrame(function () {
      // Card visibility: assign once per card. Was previously 2 writes/card
      // (hide all, then unhide visible). One write/card is enough.
      for (var i = 0; i < allCards.length; i++) {
        var card = allCards[i];
        card.style.display = visibleSet.has(card) ? '' : 'none';
      }

      // Empty-state message.
      var emptyMsg = existingEmptyMsg;
      if (!hasResults) {
        if (!emptyMsg) {
          emptyMsg = document.createElement('div');
          emptyMsg.className = 'posts-empty';
          panel.appendChild(emptyMsg);
        }
        emptyMsg.textContent = 'No posts found in this category.';
        emptyMsg.style.display = '';
      } else if (emptyMsg) {
        emptyMsg.style.display = 'none';
      }

      // Show-more button state.
      if (remaining > 0) {
        showMoreBtn.style.display = '';
        showMoreBtn.innerHTML =
          '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg> More (' +
          remaining +
          ')';
      } else {
        showMoreBtn.style.display = 'none';
      }

      // Tab badges: one DOM write per tab from the precomputed plan, no card
      // re-iteration here.
      for (var p = 0; p < tabPlan.length; p++) {
        var entry = tabPlan[p];
        var badge = entry.tab.querySelector('.tab-count');
        if (!badge) {
          badge = document.createElement('span');
          badge.className = 'tab-count';
          entry.tab.appendChild(badge);
        }
        badge.textContent = String(entry.count);
      }
    });
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (otherTab) {
        otherTab.classList.remove('active');
        otherTab.setAttribute('aria-selected', 'false');
      });

      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      currentFilter = tab.getAttribute('data-sort') || 'latest';
      showCount = PAGE_SIZE;
      renderPosts();
    });
  });

  showMoreBtn.addEventListener('click', function () {
    showCount += PAGE_SIZE;
    renderPosts();
  });

  viewBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      viewBtns.forEach(function (otherBtn) {
        otherBtn.classList.remove('active');
        otherBtn.setAttribute('aria-pressed', 'false');
      });

      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');

      var view = btn.getAttribute('data-view');
      if (view === 'list') {
        postsList.classList.add('posts-list--list-view');
      } else {
        postsList.classList.remove('posts-list--list-view');
      }

      try {
        localStorage.setItem('postsView', view || 'grid');
      } catch (_error) {}
    });
  });

  var saved = null;
  try {
    saved = localStorage.getItem('postsView');
    if (saved === 'list') {
      postsList.classList.add('posts-list--list-view');
      viewBtns.forEach(function (btn) {
        var isList = btn.getAttribute('data-view') === 'list';
        btn.classList.toggle('active', isList);
        btn.setAttribute('aria-pressed', isList ? 'true' : 'false');
      });
    }
  } catch (_error) {}

  renderPosts();
})();
