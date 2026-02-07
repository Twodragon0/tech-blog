// Modern UI/UX JavaScript for Tech Blog - Search & Translation
// Build: 2026-02-04 - Split optimization (main-search.js)
// Lazy-loaded on search input focus

(function() {
  'use strict';

  // Wait for utilities from main-core.js
  const scheduleIdleWork = window.TechBlog?.scheduleIdleWork || ((cb) => setTimeout(cb, 1));

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
        .search-source-badge{font-size:.7rem;color:var(--text-secondary,#888);padding:4px 8px;text-align:right;opacity:.7}
        .search-category{background:var(--accent-color,#4a9eff);color:#fff;font-size:.7rem;padding:1px 6px;border-radius:3px;margin-right:4px}
        .search-tag{background:var(--bg-secondary,#f0f0f0);color:var(--text-secondary,#666);font-size:.65rem;padding:1px 5px;border-radius:3px;margin-right:3px}
        .search-result-item.active{background:var(--bg-secondary,#f5f5f5)}
        .search-result-item mark{background:rgba(255,200,0,.3);color:inherit;padding:0 1px;border-radius:2px}
      `;
      document.head.appendChild(style);
    }

    let searchData = [];
    let searchDataLoaded = false;
    let fuseInstance = null;
    let serverSearchController = null;
    let searchDebounceTimer = null;
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

    async function serverSearch(query) {
      if (serverSearchController) serverSearchController.abort();
      serverSearchController = new AbortController();
      try {
        const resp = await fetch(`${baseUrl}/api/search?q=${encodeURIComponent(query)}`, {
          signal: serverSearchController.signal,
          headers: { 'Accept': 'application/json' },
        });
        if (!resp.ok) return null;
        const data = await resp.json();
        return data.results || [];
      } catch (err) {
        if (err.name === 'AbortError') return null;
        return null;
      }
    }

    function escapeRegex(str) {
      return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function highlightMatch(text, query) {
      if (!text || !query) return text || '';
      const escaped = escapeRegex(query);
      return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark>$1</mark>');
    }

    function getExcerpt(item, query) {
      const content = item.excerpt || item.content || '';
      const idx = content.toLowerCase().indexOf(query.toLowerCase());
      if (idx > -1) {
        const start = Math.max(0, idx - 40);
        const end = Math.min(content.length, idx + query.length + 80);
        return (start > 0 ? '...' : '') + content.substring(start, end) + (end < content.length ? '...' : '');
      }
      return content.substring(0, 120) + (content.length > 120 ? '...' : '');
    }

    function mergeResults(serverResults, clientResults) {
      const seen = new Set();
      const merged = [];
      for (const item of serverResults) {
        if (!seen.has(item.url)) { seen.add(item.url); merged.push(item); }
      }
      for (const item of clientResults) {
        if (!seen.has(item.url)) { seen.add(item.url); merged.push(item); }
      }
      return merged;
    }

    function renderResults(results, query, isServer) {
      activeResultIndex = -1;
      if (!results || results.length === 0) {
        searchResults.innerHTML = '<div class="search-result-item no-results">검색 결과가 없습니다.</div>';
        searchResults.style.display = 'block';
        return;
      }
      const badge = isServer ? '<div class="search-source-badge">Full-text search</div>' : '';
      searchResults.innerHTML = badge + results.slice(0, 10).map(item => `
        <a href="${item.url}" class="search-result-item" data-url="${item.url}">
          <div class="search-result-title">${highlightMatch(item.title || '', query)}</div>
          <div class="search-result-meta">
            ${item.date || ''}
            ${item.category ? ' <span class="search-category">' + item.category + '</span>' : ''}
            ${Array.isArray(item.tags) ? item.tags.slice(0, 3).map(t => '<span class="search-tag">' + t + '</span>').join('') : ''}
          </div>
          <div class="search-result-excerpt">${highlightMatch(getExcerpt(item, query), query)}</div>
        </a>
      `).join('');
      searchResults.style.display = 'block';
    }

    searchInput.addEventListener('input', function(e) {
      const query = e.target.value.trim();
      if (query.length < 2) {
        searchResults.innerHTML = '';
        searchResults.style.display = 'none';
        clearTimeout(searchDebounceTimer);
        return;
      }

      const clientResults = clientSearch(query);
      renderResults(clientResults, query, false);

      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        serverSearch(query).then(serverResults => {
          if (serverResults && serverResults.length > 0) {
            renderResults(mergeResults(serverResults, clientResults), query, true);
          }
        }).catch(function(err) {
          if (err && err.name !== 'AbortError') {
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
              console.warn('[Search] Server search failed:', err);
            }
          }
        });
      }, 300);
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
        const url = items[activeResultIndex]?.getAttribute('data-url') || items[activeResultIndex]?.href;
        if (url) window.location.href = url;
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
    const langMenu = document.getElementById('lang-menu');
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

    function stripBrowserTranslationTags(html) {
      if (!html) return html;
      const temp = document.createElement('div');
      temp.innerHTML = html;
      
      temp.querySelectorAll('font').forEach(font => {
        const parent = font.parentNode;
        while (font.firstChild) {
          parent.insertBefore(font.firstChild, font);
        }
        parent.removeChild(font);
      });
      
      temp.querySelectorAll('span[style*="vertical-align: inherit"]').forEach(span => {
        const parent = span.parentNode;
        while (span.firstChild) {
          parent.insertBefore(span.firstChild, span);
        }
        parent.removeChild(span);
      });
      
      return temp.innerHTML;
    }
    
    function extractPureText(el) {
      if (!el) return '';
      const clone = el.cloneNode(true);
      clone.querySelectorAll('font, span[style*="vertical-align: inherit"]').forEach(n => {
        n.replaceWith(...n.childNodes);
      });
      return clone.textContent || '';
    }
    
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

    function saveOriginalContent() {
      if (isInitialized) return;

      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      if (postContent) originalContent.postContent = stripBrowserTranslationTags(postContent.innerHTML);
      if (postTitle) originalContent.postTitle = extractPureText(postTitle);
      
      if (certPage) {
        originalContent.certPage = stripBrowserTranslationTags(certPage.innerHTML);
        if (certTitle) originalContent.certTitle = extractPureText(certTitle);
      }

      originalContent.cardTitles = [];
      cardTitles.forEach((el, i) => {
        originalContent.cardTitles[i] = extractPureText(el);
      });

      originalContent.cardExcerpts = [];
      cardExcerpts.forEach((el, i) => {
        originalContent.cardExcerpts[i] = extractPureText(el);
      });

      isInitialized = true;
    }

    // Show toast notification
    function showToast(message, type) {
      toast.textContent = message;
      toast.className = 'translate-toast show ' + type;

      if (type === 'success' || type === 'error') {
        setTimeout(() => {
          toast.classList.remove('show');
        }, 3000);
      }
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

    // Check if text is already in target language (simple heuristic)
    function isAlreadyInTargetLanguage(text, targetLang) {
      if (targetLang === 'ko') {
        // Check if text contains Korean characters
        return /[가-힣]/.test(text);
      } else if (targetLang === 'en') {
        // Check if text is mostly English (has English words and few Korean characters)
        const koreanChars = (text.match(/[가-힣]/g) || []).length;
        const englishWords = (text.match(/[a-zA-Z]+/g) || []).length;
        return englishWords > koreanChars * 2 && koreanChars < text.length * 0.1;
      }
      return false;
    }

    // Split long text into chunks for translation
    function splitTextIntoChunks(text, maxLength = 500) {
      if (text.length <= maxLength) return [text];
      
      const chunks = [];
      const sentences = text.split(/([.!?]\s+|\.\s+)/);
      let currentChunk = '';
      
      for (let i = 0; i < sentences.length; i++) {
        const sentence = sentences[i];
        if ((currentChunk + sentence).length <= maxLength) {
          currentChunk += sentence;
        } else {
          if (currentChunk) chunks.push(currentChunk.trim());
          currentChunk = sentence;
        }
      }
      if (currentChunk) chunks.push(currentChunk.trim());
      
      return chunks.filter(chunk => chunk.length > 0);
    }

    // Translation cache for individual text chunks
    const textTranslationCache = {};

    // Technical terms and patterns that should NOT be translated
    const noTranslatePatterns = [
      /^[A-Z][A-Z0-9_\-\.]+$/,  // ALL_CAPS_CONSTANTS, API-KEY
      /^[a-z]+\.[a-z]+/i,       // file.ext, package.name
      /^\$[a-zA-Z_]+/,          // $variable
      /^@[a-zA-Z]+/,            // @annotation
      /^#[a-zA-Z]+/,            // #hashtag
      /^https?:\/\//,           // URLs
      /^[a-zA-Z_][a-zA-Z0-9_]*\(\)/,  // function()
      /^\d+(\.\d+)?[a-zA-Z]+$/, // 10px, 2rem
      /^[<>\/\[\]{}]+$/,        // HTML/code symbols only
    ];
    
    // Words to preserve (technical terms)
    const preserveWords = new Set([
      'API', 'SDK', 'CLI', 'GUI', 'URL', 'URI', 'DNS', 'CDN', 'SSL', 'TLS', 'HTTP', 'HTTPS',
      'JSON', 'XML', 'YAML', 'CSV', 'HTML', 'CSS', 'SQL', 'NoSQL',
      'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'GitHub', 'GitLab',
      'React', 'Vue', 'Angular', 'Node.js', 'Python', 'Java', 'Go', 'Rust',
      'DevOps', 'DevSecOps', 'FinOps', 'MLOps', 'GitOps', 'SRE',
      'CI/CD', 'IaC', 'IAM', 'VPC', 'EC2', 'S3', 'RDS', 'EKS', 'ECS', 'Lambda',
      'Sentry', 'Cloudflare', 'Vercel', 'Nginx', 'Apache',
      'CRUD', 'REST', 'GraphQL', 'gRPC', 'WebSocket',
      'OAuth', 'JWT', 'SAML', 'SSO', 'MFA', '2FA',
      'SAST', 'DAST', 'IAST', 'SCA', 'WAF', 'DDoS', 'XSS', 'CSRF', 'SQLi',
      'LCP', 'FID', 'CLS', 'TTFB', 'FCP',
    ]);
    
    // Check if text should not be translated
    function shouldSkipTranslation(text) {
      if (!text || text.trim().length === 0) return true;
      if (text.trim().length < 2) return true;
      
      // Skip if it's a technical pattern
      const trimmed = text.trim();
      if (noTranslatePatterns.some(pattern => pattern.test(trimmed))) return true;
      
      // Skip if it's a single preserved word
      if (preserveWords.has(trimmed)) return true;
      
      // Skip if mostly numbers/symbols (less than 30% letters)
      const letters = (trimmed.match(/[a-zA-Z가-힣]/g) || []).length;
      if (letters < trimmed.length * 0.3) return true;
      
      return false;
    }
    
    // Translate text using MyMemory API with retry logic
    async function translateText(text, sourceLang, targetLang, retries = 2) {
      if (!text || text.trim().length === 0) return text;
      
      // Skip technical terms
      if (shouldSkipTranslation(text)) return text;

      // Skip if already in target language
      if (isAlreadyInTargetLanguage(text, targetLang)) {
        return text;
      }

      // Check cache first
      const cacheKey = `${sourceLang}-${targetLang}-${text.substring(0, 100)}`;
      if (textTranslationCache[cacheKey]) {
        return textTranslationCache[cacheKey];
      }

      const langMap = {
        'en': 'en-US',
        'ja': 'ja-JP',
        'zh': 'zh-CN',
        'ko': 'ko-KR'
      };

      const targetLangCode = langMap[targetLang] || targetLang;
      const sourceLangCode = langMap[sourceLang] || sourceLang;

      // Handle long text by splitting into chunks (MyMemory limit: ~500 chars)
      if (text.length > 400) {
        const chunks = splitTextIntoChunks(text, 400);
        
        // Process chunks sequentially to avoid rate limiting
        const results = [];
        for (const chunk of chunks) {
          const translated = await translateText(chunk, sourceLang, targetLang, retries);
          results.push(translated || chunk);
          // Delay between chunks to avoid rate limiting
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        const translated = results.join(' ');
        textTranslationCache[cacheKey] = translated;
        return translated;
      }

      // Translate short text
      for (let attempt = 0; attempt <= retries; attempt++) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 8000);
          
          const response = await fetch(
            `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${sourceLangCode}|${targetLangCode}`,
            {
              method: 'GET',
              headers: { 'Accept': 'application/json' },
              signal: controller.signal
            }
          );
          
          clearTimeout(timeoutId);

          if (!response.ok) {
            if (response.status === 429) {
              // Rate limited - wait longer and retry
              await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
              continue;
            }
            if (attempt < retries) {
              await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
              continue;
            }
            throw new Error(`HTTP ${response.status}`);
          }

          const data = await response.json();

          // Check for rate limiting in response
          if (data.responseStatus === 429 || 
              (data.responseData && data.responseData.translatedText && 
               data.responseData.translatedText.includes('MYMEMORY WARNING'))) {
            if (attempt < retries) {
              await new Promise(resolve => setTimeout(resolve, 2000 * (attempt + 1)));
              continue;
            }
            textTranslationCache[cacheKey] = text;
            return text;
          }

          if (data.responseStatus === 200 && data.responseData && data.responseData.translatedText) {
            let translated = data.responseData.translatedText;
            
            // Filter out MyMemory warnings
            if (translated.includes('MYMEMORY WARNING') || 
                translated.includes('PLEASE SELECT') ||
                translated.includes('YOU USED ALL AVAILABLE')) {
              textTranslationCache[cacheKey] = text;
              return text;
            }
            
            // Check if translation is valid
            if (translated && translated !== text && translated.trim().length > 0) {
              textTranslationCache[cacheKey] = translated;
              return translated;
            }
          }

          textTranslationCache[cacheKey] = text;
          return text;
        } catch (error) {
          if (attempt < retries && error.name !== 'AbortError') {
            await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
            continue;
          }
          if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.warn('Translation failed:', error.message);
          }
          textTranslationCache[cacheKey] = text;
          return text;
        }
      }

      return text;
    }

    // Translate page content
    async function translatePage(targetLang) {
      saveOriginalContent();

      // Check cache
      if (translationCache[targetLang]) {
        applyTranslation(translationCache[targetLang]);
        return;
      }

      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      const translation = {};
      let totalItems = 0;
      let translatedItems = 0;

      // Count items to translate
      if (postTitle && originalContent.postTitle) totalItems++;
      if (certTitle && originalContent.certTitle) totalItems++;
      if (postContent && originalContent.postContent) {
        const textElements = postContent.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote');
        totalItems += textElements.length;
      }
      if (certPage && originalContent.certPage) {
        const textElements = certPage.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote, span.question-topic, span.question-number');
        totalItems += textElements.length;
      }
      totalItems += cardTitles.length + cardExcerpts.length;

      // Translate title first (priority)
      if (postTitle && originalContent.postTitle) {
        try {
          translation.postTitle = await translateText(originalContent.postTitle, 'ko', targetLang);
          translatedItems++;
          // Apply title immediately for better UX
          if (translation.postTitle && translation.postTitle !== originalContent.postTitle) {
            postTitle.textContent = translation.postTitle;
          }
          showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
        } catch (error) {
          translation.postTitle = originalContent.postTitle;
        }
      }
      
      // Translate certification page title
      if (certTitle && originalContent.certTitle) {
        try {
          translation.certTitle = await translateText(originalContent.certTitle, 'ko', targetLang);
          translatedItems++;
          if (translation.certTitle && translation.certTitle !== originalContent.certTitle) {
            certTitle.textContent = translation.certTitle;
          }
          showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
        } catch (error) {
          translation.certTitle = originalContent.certTitle;
        }
      }

      // Translate post content with batch processing for better performance
      if (postContent && originalContent.postContent) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = originalContent.postContent;
        const textElements = Array.from(tempDiv.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote, code:not(pre code), span:not(.highlight), div:not(.code-block):not(.highlight)')).filter(el => {
          const text = el.textContent.trim();
          // Filter out empty elements, code blocks, and elements with code children
          return text && !el.closest('pre') && !el.closest('code') && !el.querySelector('code');
        });

        // Process in batches for better performance
        const batchSize = 5;
        for (let i = 0; i < textElements.length; i += batchSize) {
          const batch = textElements.slice(i, i + batchSize);
          
          // Process batch in parallel
          const batchPromises = batch.map(async (el) => {
            const text = el.textContent.trim();
            
            // Only translate if it's mostly text content
            const hasOnlyTextChildren = Array.from(el.childNodes).every(node => 
              node.nodeType === Node.TEXT_NODE || 
              (node.nodeType === Node.ELEMENT_NODE && (node.tagName === 'STRONG' || node.tagName === 'EM' || node.tagName === 'B' || node.tagName === 'I' || node.tagName === 'A'))
            );

            if (hasOnlyTextChildren && text.length > 0) {
              try {
                const translated = await translateText(text, 'ko', targetLang);
                if (translated && translated !== text) {
                  // Preserve inline formatting by translating only text nodes
                  if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                    el.textContent = translated;
                  } else if (el.children.length === 0) {
                    el.textContent = translated;
                  } else {
                    // Has inline elements - try to preserve structure
                    const textNodes = Array.from(el.childNodes).filter(n => n.nodeType === Node.TEXT_NODE);
                    if (textNodes.length === 1) {
                      textNodes[0].textContent = translated;
                    } else {
                      el.textContent = translated;
                    }
                  }
                }
              } catch (error) {
                // Continue on error
              }
            }
          });

          await Promise.all(batchPromises);
          translatedItems += batch.length;
          
          // Update progress every batch
          if (translatedItems % 5 === 0 || i + batchSize >= textElements.length) {
            showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
          }
          
          // Small delay between batches to avoid rate limiting
          if (i + batchSize < textElements.length) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }

        translation.postContent = tempDiv.innerHTML;
      }

      // Translate card titles in parallel
      translation.cardTitles = [];
      if (cardTitles.length > 0 && originalContent.cardTitles) {
        const titlePromises = Array.from(cardTitles).map(async (el, i) => {
          if (originalContent.cardTitles[i]) {
            return await translateText(originalContent.cardTitles[i], 'ko', targetLang);
          }
          return null;
        });
        translation.cardTitles = await Promise.all(titlePromises);
        translatedItems += cardTitles.length;
        showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
      }

      // Translate card excerpts in parallel
      translation.cardExcerpts = [];
      if (cardExcerpts.length > 0 && originalContent.cardExcerpts) {
        const excerptPromises = Array.from(cardExcerpts).map(async (el, i) => {
          if (originalContent.cardExcerpts[i]) {
            return await translateText(originalContent.cardExcerpts[i], 'ko', targetLang);
          }
          return null;
        });
        translation.cardExcerpts = await Promise.all(excerptPromises);
        translatedItems += cardExcerpts.length;
      }

      // Translate certification page content
      if (certPage && originalContent.certPage) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = originalContent.certPage;
        const textElements = Array.from(tempDiv.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th, blockquote, span.question-topic, span.question-number, .question-content, .question-options, .question-answer')).filter(el => {
          const text = el.textContent.trim();
          // Filter out empty elements, code blocks, and elements with code children
          return text && !el.closest('pre') && !el.closest('code') && !el.querySelector('code') && !el.classList.contains('notranslate');
        });

        // Process in batches for better performance
        const batchSize = 5;
        for (let i = 0; i < textElements.length; i += batchSize) {
          const batch = textElements.slice(i, i + batchSize);
          
          // Process batch in parallel
          const batchPromises = batch.map(async (el) => {
            const text = el.textContent.trim();
            
            // Only translate if it's mostly text content
            const hasOnlyTextChildren = Array.from(el.childNodes).every(node => 
              node.nodeType === Node.TEXT_NODE || 
              (node.nodeType === Node.ELEMENT_NODE && (node.tagName === 'STRONG' || node.tagName === 'EM' || node.tagName === 'B' || node.tagName === 'I' || node.tagName === 'A'))
            );

            if (hasOnlyTextChildren && text.length > 0) {
              try {
                const translated = await translateText(text, 'ko', targetLang);
                if (translated && translated !== text) {
                  if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                    el.textContent = translated;
                  } else if (el.children.length === 0) {
                    el.textContent = translated;
                  } else {
                    const textNodes = Array.from(el.childNodes).filter(n => n.nodeType === Node.TEXT_NODE);
                    if (textNodes.length === 1) {
                      textNodes[0].textContent = translated;
                    } else {
                      el.textContent = translated;
                    }
                  }
                }
              } catch (error) {
                // Continue on error
              }
            }
          });

          await Promise.all(batchPromises);
          translatedItems += batch.length;
          
          // Update progress every batch
          if (translatedItems % 5 === 0 || i + batchSize >= textElements.length) {
            showToast(`번역 중... ${Math.round((translatedItems / totalItems) * 100)}%`, 'loading');
          }
          
          // Small delay between batches to avoid rate limiting
          if (i + batchSize < textElements.length) {
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }

        translation.certPage = tempDiv.innerHTML;
      }

      // Cache and apply translation
      translationCache[targetLang] = translation;
      applyTranslation(translation);
    }

    // Apply translation to page
    function applyTranslation(translation) {
      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      // Apply title translation (ensure it's applied even if already set)
      if (postTitle && translation.postTitle && translation.postTitle !== originalContent.postTitle) {
        postTitle.textContent = translation.postTitle;
      }
      
      // Apply certification page title translation
      if (certTitle && translation.certTitle && translation.certTitle !== originalContent.certTitle) {
        certTitle.textContent = translation.certTitle;
      }

      // Apply post content translation
      if (postContent && translation.postContent) {
        postContent.innerHTML = translation.postContent;
      }
      
      // Apply certification page content translation
      if (certPage && translation.certPage) {
        certPage.innerHTML = translation.certPage;
      }

      // Apply card titles
      if (translation.cardTitles) {
        cardTitles.forEach((el, i) => {
          if (translation.cardTitles[i] && translation.cardTitles[i] !== originalContent.cardTitles?.[i]) {
            el.textContent = translation.cardTitles[i];
          }
        });
      }

      // Apply card excerpts
      if (translation.cardExcerpts) {
        cardExcerpts.forEach((el, i) => {
          if (translation.cardExcerpts[i] && translation.cardExcerpts[i] !== originalContent.cardExcerpts?.[i]) {
            el.textContent = translation.cardExcerpts[i];
          }
        });
      }
    }

    // Restore original content
    function restoreOriginal() {
      const postContent = document.querySelector('.post-content');
      const postTitle = document.querySelector('.post-title');
      const certPage = document.querySelector('.certification-detail-page');
      const certTitle = certPage ? certPage.querySelector('.page-header h1') : null;
      const cardTitles = document.querySelectorAll('.post-card h3, .card h3, .card h4');
      const cardExcerpts = document.querySelectorAll('.post-card .card-excerpt, .card p');

      if (postContent && originalContent.postContent) {
        postContent.innerHTML = originalContent.postContent;
      }

      if (postTitle && originalContent.postTitle) {
        postTitle.textContent = originalContent.postTitle;
      }
      
      // Restore certification page content
      if (certPage && originalContent.certPage) {
        certPage.innerHTML = originalContent.certPage;
      }
      
      if (certTitle && originalContent.certTitle) {
        certTitle.textContent = originalContent.certTitle;
      }

      cardTitles.forEach((el, i) => {
        if (originalContent.cardTitles && originalContent.cardTitles[i]) {
          el.textContent = originalContent.cardTitles[i];
        }
      });

      cardExcerpts.forEach((el, i) => {
        if (originalContent.cardExcerpts && originalContent.cardExcerpts[i]) {
          el.textContent = originalContent.cardExcerpts[i];
        }
      });
    }

    // Language option click handler
    langOptions.forEach(option => {
      option.addEventListener('click', async function() {
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

        // Show loading
        showToast('번역 중...', 'loading');

        try {
          if (targetLang === 'ko') {
            restoreOriginal();
            showToast('원본으로 복원되었습니다', 'success');
          } else {
            await translatePage(targetLang);
            showToast(`${getLanguageName(targetLang)}로 번역되었습니다`, 'success');
          }
          currentLang = targetLang;
        } catch (error) {
          showToast('번역 실패. 다시 시도해주세요.', 'error');
        }
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
