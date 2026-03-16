(function () {
  'use strict';

  var giscusContainer = document.getElementById('giscus-container');
  var loadingEl = document.getElementById('giscus-loading');
  var commentsCountEl = document.getElementById('comments-count');
  var errorEl = document.getElementById('giscus-error');
  var retryBtn = document.getElementById('giscus-retry-btn');

  if (!giscusContainer) {
    return;
  }

  var giscusLoaded = false;
  var retryCount = 0;
  var locale = (document.documentElement.getAttribute('lang') || 'ko').toLowerCase();
  var messages = {
    ko: {
      empty: '아직 댓글이 없습니다. 첫 댓글을 남겨보세요.',
      loadFailed: '댓글 위젯을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.',
      retryFailed: '댓글을 가져오지 못했습니다. 다시 시도해주세요.',
      retry: '다시 시도',
    },
    en: {
      empty: 'No comments yet. Be the first to start the discussion.',
      loadFailed: 'Failed to load the comments widget. Please try again.',
      retryFailed: 'Unable to fetch comments. Please retry.',
      retry: 'Retry',
    },
    ja: {
      empty: 'まだコメントはありません。最初のコメントを残してください。',
      loadFailed: 'コメントウィジェットを読み込めませんでした。しばらくして再試行してください。',
      retryFailed: 'コメントを取得できませんでした。再試行してください。',
      retry: '再試行',
    },
  };
  var giscusConfig = {
    repo: giscusContainer.getAttribute('data-repo') || '',
    repoId: giscusContainer.getAttribute('data-repo-id') || '',
    category: giscusContainer.getAttribute('data-category') || '',
    categoryId: giscusContainer.getAttribute('data-category-id') || '',
    mapping: giscusContainer.getAttribute('data-mapping') || 'pathname',
    strict: giscusContainer.getAttribute('data-strict') || '0',
    reactionsEnabled: giscusContainer.getAttribute('data-reactions-enabled') || '1',
    emitMetadata: giscusContainer.getAttribute('data-emit-metadata') || '1',
    inputPosition: giscusContainer.getAttribute('data-input-position') || 'top',
    lang: giscusContainer.getAttribute('data-lang') || 'ko',
    crossorigin: 'anonymous',
  };

  function hideLoading() {
    if (!loadingEl) {
      return;
    }
    loadingEl.classList.add('hidden');
    loadingEl.style.display = 'none';
  }

  function showLoading() {
    if (!loadingEl) {
      return;
    }
    loadingEl.classList.remove('hidden');
    loadingEl.style.display = '';
  }

  function showErrorMessage(text) {
    if (!errorEl) {
      return;
    }
    var message = errorEl.querySelector('.giscus-error-text');
    if (message) {
      message.textContent = text;
    }
    if (retryBtn) {
      retryBtn.textContent = t('retry');
    }
    errorEl.classList.remove('hidden');
    errorEl.style.display = '';
  }

  function hideErrorMessage() {
    if (!errorEl) {
      return;
    }
    errorEl.classList.add('hidden');
    errorEl.style.display = 'none';
  }

  function getTheme() {
    return localStorage.getItem('theme') === 'light' ? 'light' : 'dark_dimmed';
  }

  function t(key) {
    if (locale.indexOf('en') === 0) {
      return messages.en[key];
    }
    if (locale.indexOf('ja') === 0) {
      return messages.ja[key];
    }
    return messages.ko[key];
  }

  function syncErrorTheme(theme) {
    if (!errorEl) {
      return;
    }
    var activeTheme = theme || getTheme();
    if (activeTheme === 'light') {
      errorEl.setAttribute('data-theme-variant', 'light');
    } else {
      errorEl.setAttribute('data-theme-variant', 'dark');
    }
  }

  function cleanupContainer() {
    var scripts = giscusContainer.querySelectorAll('script[src*="giscus.app/client.js"]');
    var iframes = giscusContainer.querySelectorAll('iframe[src*="giscus.app"]');
    scripts.forEach(function (node) { node.remove(); });
    iframes.forEach(function (node) { node.remove(); });
  }

  function appendGiscusScript() {
    var script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.async = true;
    script.crossOrigin = giscusConfig.crossorigin;
    script.setAttribute('data-repo', giscusConfig.repo);
    script.setAttribute('data-repo-id', giscusConfig.repoId);
    script.setAttribute('data-category', giscusConfig.category);
    script.setAttribute('data-category-id', giscusConfig.categoryId);
    script.setAttribute('data-mapping', giscusConfig.mapping);
    script.setAttribute('data-strict', giscusConfig.strict);
    script.setAttribute('data-reactions-enabled', giscusConfig.reactionsEnabled);
    script.setAttribute('data-emit-metadata', giscusConfig.emitMetadata);
    script.setAttribute('data-input-position', giscusConfig.inputPosition);
    script.setAttribute('data-theme', getTheme());
    script.setAttribute('data-lang', giscusConfig.lang);
    script.setAttribute('data-loading', 'lazy');

    script.onerror = function () {
      hideLoading();
      showErrorMessage(t('loadFailed'));
      giscusLoaded = false;
    };

    giscusContainer.appendChild(script);
  }

  function loadGiscus(forceReload) {
    if (giscusLoaded && !forceReload) {
      return;
    }

    giscusLoaded = true;
    hideErrorMessage();
    showLoading();
    if (forceReload) {
      cleanupContainer();
    }
    appendGiscusScript();
  }

  function updateReactionCounts(reactions) {
    var reactionMap = {
      THUMBS_UP: 'thumbsUp',
      HEART: 'heart',
      ROCKET: 'rocket',
      EYES: 'eyes',
    };
    var labelMap = {
      thumbsUp: '유용해요',
      heart: '좋아요',
      rocket: '대단해요',
      eyes: '관심있어요',
    };

    Object.keys(reactionMap).forEach(function (key) {
      var reactionType = reactionMap[key];
      var el = document.getElementById('reaction-' + reactionType);
      if (el && reactions[key] !== undefined) {
        el.textContent = reactions[key];
        el.setAttribute('aria-label', labelMap[reactionType] + ' ' + reactions[key] + '개');
      }
    });
  }

  window.addEventListener('message', function (event) {
    if (event.origin !== 'https://giscus.app') {
      return;
    }

    if (!event.data || !event.data.giscus) {
      return;
    }

    var payload = event.data.giscus;
    var discussion = payload.discussion;
    var type = payload.type;

    if (discussion && commentsCountEl) {
      var count = discussion.totalCommentCount || 0;
      commentsCountEl.textContent = count;
      commentsCountEl.style.display = count > 0 ? 'inline-flex' : 'none';
      commentsCountEl.setAttribute('aria-label', '댓글 ' + count + '개');
    }

    if (type === 'ready' || discussion) {
      hideLoading();
      hideErrorMessage();
    }

    if (type === 'error') {
      hideLoading();
      var notFound = retryCount < 1;
      showErrorMessage(notFound ? t('empty') : t('retryFailed'));
      giscusLoaded = false;
    }

    if (discussion && discussion.reactions) {
      updateReactionCounts(discussion.reactions);
    }
  });

  document.querySelectorAll('.reaction-card').forEach(function (btn) {
    var reactionType = btn.getAttribute('data-reaction');
    var savedState = localStorage.getItem('reaction-' + reactionType);
    if (savedState === 'active') {
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
    }

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var isActive = this.classList.contains('active');
      if (isActive) {
        this.classList.remove('active');
        this.setAttribute('aria-pressed', 'false');
        localStorage.removeItem('reaction-' + reactionType);
      } else {
        document.querySelectorAll('.reaction-card').forEach(function (node) {
          node.classList.remove('active');
          node.setAttribute('aria-pressed', 'false');
          localStorage.removeItem('reaction-' + node.getAttribute('data-reaction'));
        });
        this.classList.add('active');
        this.setAttribute('aria-pressed', 'true');
        localStorage.setItem('reaction-' + reactionType, 'active');
      }

      var giscusFrame = giscusContainer.querySelector('iframe');
      if (giscusFrame) {
        setTimeout(function () {
          giscusFrame.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      }
    });

    btn.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.click();
      }
    });
  });

  document.addEventListener('themeChanged', function (e) {
    var theme = e.detail === 'light' ? 'light' : 'dark_dimmed';
    syncErrorTheme(theme);
    var giscusFrame = giscusContainer.querySelector('iframe');
    if (giscusFrame && giscusFrame.contentWindow) {
      giscusFrame.contentWindow.postMessage({ giscus: { setConfig: { theme: theme } } }, 'https://giscus.app');
    }
  });

  if (retryBtn) {
    retryBtn.addEventListener('click', function () {
      retryCount += 1;
      loadGiscus(true);
    });
  }

  syncErrorTheme();

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          loadGiscus(false);
          observer.disconnect();
        }
      });
    }, { rootMargin: '400px' });
    observer.observe(giscusContainer);

    setTimeout(function () {
      if (!giscusLoaded && document.visibilityState === 'visible') {
        loadGiscus(false);
      }
    }, 8000);
  } else {
    setTimeout(function () {
      loadGiscus(false);
    }, 1000);
  }

  setTimeout(hideLoading, 12000);
})();
