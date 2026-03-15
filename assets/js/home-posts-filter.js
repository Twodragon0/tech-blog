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
  var currentFilter = 'recent';
  var showCount = PAGE_SIZE;

  var showMoreBtn = document.createElement('button');
  showMoreBtn.className = 'btn btn-secondary btn-lg posts-show-more';
  showMoreBtn.type = 'button';
  showMoreBtn.innerHTML =
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg> More';
  footer.insertBefore(showMoreBtn, footer.firstChild);

  function getFilteredCards(filter) {
    if (filter === 'recent') {
      return allCards;
    }

    return allCards.filter(function (card) {
      var cats = (card.getAttribute('data-category') || '').split(' ');
      return cats.indexOf(filter) !== -1;
    });
  }

  function renderPosts() {
    var filtered = getFilteredCards(currentFilter);
    var totalFiltered = filtered.length;
    var remaining = 0;

    allCards.forEach(function (card) {
      card.style.display = 'none';
    });

    filtered.slice(0, showCount).forEach(function (card) {
      card.style.display = '';
    });

    var emptyMsg = panel.querySelector('.posts-empty');
    if (totalFiltered === 0) {
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

    if (showCount < totalFiltered) {
      remaining = totalFiltered - showCount;
      showMoreBtn.style.display = '';
      showMoreBtn.innerHTML =
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="6 9 12 15 18 9"/></svg> More (' +
        remaining +
        ')';
    } else {
      showMoreBtn.style.display = 'none';
    }

    tabs.forEach(function (tab) {
      var sort = tab.getAttribute('data-sort') || 'recent';
      var count = getFilteredCards(sort).length;
      var badge = tab.querySelector('.tab-count');

      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'tab-count';
        tab.appendChild(badge);
      }
      badge.textContent = String(count);
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
      currentFilter = tab.getAttribute('data-sort') || 'recent';
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
