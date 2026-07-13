// Modern UI/UX JavaScript for Tech Blog - Search & Translation
// Build: 2026-02-04 - Split optimization (main-search.js)
// Lazy-loaded on search input focus

(function() {
  'use strict';

  // ============================================
  // Hybrid Search System
  // ============================================

    // Hybrid Search: Client-side (Fuse.js) + Server-side (PostgreSQL FTS)
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    let searchContainer = null;
    if (searchInput) {
      searchContainer = searchInput.closest('.search-container');
    }

    if (searchInput && searchResults) {
    if (!document.getElementById('search-enhanced-styles')) {
      const style = document.createElement('style');
      style.id = 'search-enhanced-styles';
      style.textContent = `
        .search-category{background:var(--color-primary,#4a9eff);color:#fff;font-size:.7rem;padding:1px 6px;border-radius:3px;margin-right:4px}
        .search-tag{background:var(--color-bg-secondary,#f0f0f0);color:var(--color-text-secondary,#666);font-size:.65rem;padding:1px 5px;border-radius:3px;margin-right:3px}
        .search-result-item.active{background:var(--color-bg-secondary,#f5f5f5)}
        .search-result-item mark{background:rgba(255,200,0,.3);color:inherit;padding:0 1px;border-radius:2px}
      `;
      document.head.appendChild(style);
    }

    let searchData = [];
    let searchDataLoaded = false;
    let fuseInstance = null;
    // Server-side full-text search (PostgreSQL FTS via /api/search) was fully
    // removed during the GH Pages permanent migration; only client-side
    // Fuse.js search remains.
    let activeResultIndex = -1;

    function getBaseUrl() {
      const pathname = window.location.pathname;
      if (pathname.startsWith('/tech-blog')) return '/tech-blog';
      return '';
    }

    const baseUrl = getBaseUrl();

    fetch(baseUrl + '/search.json')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then(data => {
        searchData = data;
        searchDataLoaded = true;
        initFuse();
      })
      .catch(err => {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          console.warn('Search data load failed:', err.message);
        }
        searchInput.placeholder = '검색 데이터 로드 실패';
      });

    function loadFuseJs() {
      if (window.Fuse) return Promise.resolve();
      return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.1.0/dist/fuse.min.js';
        script.integrity = 'sha384-P/y/5cwqUn6MDvJ9lCHJSaAi2EoH3JSeEdyaORsQMPgbpvA+NvvUqik7XH2YGBjb';
        script.crossOrigin = 'anonymous';
        script.onload = resolve;
        script.onerror = () => resolve();
        document.head.appendChild(script);
      });
    }

    function initFuse() {
      if (!window.Fuse || searchData.length === 0) return;
      fuseInstance = new Fuse(searchData, {
        keys: [
          { name: 'title', weight: 0.4 },
          { name: 'content', weight: 0.3 },
          { name: 'tags', weight: 0.2 },
          { name: 'category', weight: 0.1 }
        ],
        threshold: 0.35,
        includeScore: true,
        minMatchCharLength: 2,
      });
    }

    searchInput.addEventListener('focus', function onFirstFocus() {
      loadFuseJs().then(() => initFuse()).catch(function(err) {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          console.warn('[Search] Fuse.js load failed:', err);
        }
      });
      searchInput.removeEventListener('focus', onFirstFocus);
    }, { once: true });

    function clientSearch(query) {
      if (!searchDataLoaded || searchData.length === 0) return [];
      if (fuseInstance) {
        return fuseInstance.search(query).slice(0, 10).map(r => ({ ...r.item, score: r.score }));
      }
      const q = query.toLowerCase();
      return searchData.filter(item => {
        const title = (item.title || '').toLowerCase();
        const content = (item.content || '').toLowerCase();
        const tags = Array.isArray(item.tags) ? item.tags.join(' ').toLowerCase() : '';
        const category = (item.category || '').toLowerCase();
        return title.includes(q) || content.includes(q) || tags.includes(q) || category.includes(q);
      }).slice(0, 10);
    }

    function safeUrl(url) {
      if (!url) return '#';
      if (url.startsWith('/')) return url;
      try {
        const parsed = new URL(url, window.location.origin);
        if (parsed.protocol === 'https:' || parsed.protocol === 'http:') return url;
        return '#';
      } catch { return '#'; }
    }

    function escapeRegex(str) {
      return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function highlightMatch(text, query) {
      if (!query || !text) return document.createTextNode(text || '');
      const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
      const fragment = document.createDocumentFragment();
      const parts = text.split(regex);
      parts.forEach((part, i) => {
        if (i % 2 === 1) {
          const mark = document.createElement('mark');
          mark.textContent = part;
          fragment.appendChild(mark);
        } else if (part) {
          fragment.appendChild(document.createTextNode(part));
        }
      });
      return fragment;
    }

    function getExcerpt(item, query) {
      const content = (item.excerpt || item.content || '').replace(/<[^>]*>/g, '');
      const idx = content.toLowerCase().indexOf(query.toLowerCase());
      if (idx > -1) {
        const start = Math.max(0, idx - 40);
        const end = Math.min(content.length, idx + query.length + 80);
        return (start > 0 ? '...' : '') + content.substring(start, end) + (end < content.length ? '...' : '');
      }
      return content.substring(0, 120) + (content.length > 120 ? '...' : '');
    }

    function renderResults(results, query) {
      activeResultIndex = -1;
      searchResults.textContent = '';
      if (!results || results.length === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'search-result-item no-results';
        noResults.textContent = '검색 결과가 없습니다.';
        searchResults.appendChild(noResults);
        searchResults.style.display = 'block';
        return;
      }
      results.slice(0, 10).forEach(item => {
        const link = document.createElement('a');
        link.href = safeUrl(item.url);
        link.className = 'search-result-item';
        link.dataset.url = item.url || '';

        const titleDiv = document.createElement('div');
        titleDiv.className = 'search-result-title';
        titleDiv.appendChild(highlightMatch(item.title || '', query));
        link.appendChild(titleDiv);

        const metaDiv = document.createElement('div');
        metaDiv.className = 'search-result-meta';
        if (item.date) {
          metaDiv.appendChild(document.createTextNode(item.date));
        }
        if (item.category) {
          const catSpan = document.createElement('span');
          catSpan.className = 'search-category';
          catSpan.textContent = item.category;
          metaDiv.appendChild(document.createTextNode(' '));
          metaDiv.appendChild(catSpan);
        }
        if (Array.isArray(item.tags)) {
          item.tags.slice(0, 3).forEach(t => {
            const tagSpan = document.createElement('span');
            tagSpan.className = 'search-tag';
            tagSpan.textContent = t;
            metaDiv.appendChild(tagSpan);
          });
        }
        link.appendChild(metaDiv);

        const excerptDiv = document.createElement('div');
        excerptDiv.className = 'search-result-excerpt';
        excerptDiv.appendChild(highlightMatch(getExcerpt(item, query), query));
        link.appendChild(excerptDiv);

        searchResults.appendChild(link);
      });
      searchResults.style.display = 'block';
    }

    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.trim();
      if (query.length < 2) {
        searchResults.textContent = '';
        searchResults.style.display = 'none';
        return;
      }

      const clientResults = clientSearch(query);
      renderResults(clientResults, query);
    });

    searchInput.addEventListener('keydown', function(e) {
      const items = searchResults.querySelectorAll('.search-result-item:not(.no-results)');
      if (items.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeResultIndex = Math.min(activeResultIndex + 1, items.length - 1);
        items.forEach((el, i) => el.classList.toggle('active', i === activeResultIndex));
        items[activeResultIndex]?.scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeResultIndex = Math.max(activeResultIndex - 1, 0);
        items.forEach((el, i) => el.classList.toggle('active', i === activeResultIndex));
        items[activeResultIndex]?.scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && activeResultIndex >= 0) {
        e.preventDefault();
        const activeItem = items[activeResultIndex];
        if (activeItem && activeItem.tagName === 'A') activeItem.click();
      } else if (e.key === 'Escape') {
        searchResults.style.display = 'none';
        searchInput.blur();
      }
    });

    if (searchContainer) {
      document.addEventListener('click', function(event) {
        if (!searchContainer.contains(event.target)) {
          searchResults.style.display = 'none';
        }
      });
    }
  }

  // ============================================
  // Language Dropdown and Translation Engine
  // ============================================

  (async function initLanguageDropdown() {
    const langToggle = document.getElementById('lang-toggle');
    const langDropdown = document.getElementById('lang-dropdown');
    const langDropdownOverlay = document.getElementById('lang-dropdown-overlay');
    const langOptions = document.querySelectorAll('.lang-option[data-lang]');
    const googleTranslateLink = document.getElementById('header-google-translate');

    if (!langToggle || !langDropdown) return;

    // Create toast element for translation status
    let toast = document.querySelector('.translate-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'translate-toast';
      document.body.appendChild(toast);
    }

    // Set Google Translate link
    if (googleTranslateLink) {
      googleTranslateLink.href = `https://translate.google.com/translate?sl=ko&tl=en&u=${encodeURIComponent(window.location.href)}`;
    }

    // Function to open dropdown
    function openDropdown() {
      langDropdown.classList.add('active');
      if (langDropdownOverlay) {
        langDropdownOverlay.classList.add('active');
        langDropdownOverlay.setAttribute('aria-hidden', 'false');
      }
      if (langToggle) {
        langToggle.setAttribute('aria-expanded', 'true');
      }
      // Prevent body scroll on mobile when dropdown is open
      if (window.innerWidth <= 768) {
        document.body.style.overflow = 'hidden';
      }
    }

    // Function to close dropdown
    function closeDropdown() {
      langDropdown.classList.remove('active');
      if (langDropdownOverlay) {
        langDropdownOverlay.classList.remove('active');
        langDropdownOverlay.setAttribute('aria-hidden', 'true');
      }
      if (langToggle) {
        langToggle.setAttribute('aria-expanded', 'false');
      }
      // Restore body scroll
      document.body.style.overflow = '';
    }

    // Toggle dropdown
    langToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      if (langDropdown.classList.contains('active')) {
        closeDropdown();
      } else {
        openDropdown();
      }
    });

    // Close dropdown when clicking overlay
    if (langDropdownOverlay) {
      langDropdownOverlay.addEventListener('click', function(e) {
        e.stopPropagation();
        closeDropdown();
      });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!langDropdown.contains(e.target) && 
          !langToggle.contains(e.target) &&
          (!langDropdownOverlay || !langDropdownOverlay.contains(e.target))) {
        closeDropdown();
      }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && langDropdown.classList.contains('active')) {
        closeDropdown();
      }
    });

    let currentLang = 'ko';
    let originalContent = {};
    let translationCache = {};
    let isInitialized = false;

    // Remove Google injected elements (Knowledge Panel, Topics widgets, etc.)
    // These are <insertion> elements or elements with [data-ved] injected by Google Chrome
    function removeGoogleInjectedElements() {
      const selectors = [
        'insertion',
        '[data-ved]',
        '[data-google-topics]',
        '.kp-wholepage',
        '.kp-blk',
        '.g-blk',
        '.related-question-pair',
        // Google's dynamic recommendation widgets
        '[jscontroller][jsaction][jsname]'
      ];
      
      selectors.forEach(selector => {
        try {
          document.querySelectorAll(selector).forEach(el => {
            // Only remove if it looks like Google injected content (not our own elements)
            if (el.closest('.post-content') || el.closest('.post-article') || el.closest('main')) {
              el.remove();
            }
          });
        } catch (e) {
          // Silently ignore selector errors
        }
      });
    }
    
    // Run cleanup on load and periodically (Google may inject elements dynamically)
    removeGoogleInjectedElements();
    
    // Set up MutationObserver to catch dynamically injected elements
    const googleInjectionObserver = new MutationObserver((mutations) => {
      let shouldClean = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          for (const node of mutation.addedNodes) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              if (node.tagName === 'INSERTION' || 
                  node.hasAttribute('data-ved') || 
                  node.hasAttribute('data-google-topics')) {
                shouldClean = true;
                break;
              }
            }
          }
        }
        if (shouldClean) break;
      }
      if (shouldClean) {
        removeGoogleInjectedElements();
      }
    });
    
    // Observe the document body for Google injections
    if (document.body) {
      googleInjectionObserver.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    // Get language name
    function getLanguageName(lang) {
      const names = {
        'ko': '한국어',
        'en': 'English',
        'ja': '日本語',
        'zh': '中文'
      };
      return names[lang] || lang;
    }

    // Language option click handler
    // Translation is delegated to google-translate.js (Gemini AI-powered)
    // This handler only updates UI state - no MyMemory API calls
    langOptions.forEach(option => {
      option.addEventListener('click', function() {
        const targetLang = this.dataset.lang;

        if (targetLang === currentLang) {
          closeDropdown();
          return;
        }

        // Update active state
        langOptions.forEach(opt => opt.classList.remove('active'));
        this.classList.add('active');

        // Update post page language selector if exists
        const postLangBtns = document.querySelectorAll('.language-tools .lang-btn');
        postLangBtns.forEach(btn => {
          btn.classList.remove('active');
          if (btn.dataset.lang === targetLang) {
            btn.classList.add('active');
          }
        });

        // Close dropdown
        closeDropdown();

        currentLang = targetLang;
        // Actual translation handled by google-translate.js (Google Gemini AI)
      });
    });

    // Sync with post page language selector if exists
    const postLangBtns = document.querySelectorAll('.language-tools .lang-btn');
    postLangBtns.forEach(btn => {
      btn.addEventListener('click', function() {
        const targetLang = this.dataset.lang;

        // Update header dropdown active state
        langOptions.forEach(opt => {
          opt.classList.remove('active');
          if (opt.dataset.lang === targetLang) {
            opt.classList.add('active');
          }
        });

        currentLang = targetLang;
      });
    });
  })();
})();
