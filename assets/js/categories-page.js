// Categories page lazy-render (mirrors tags-page.js architecture).
// On scroll, populates each <section class="category-section"> stub with
// the matching post-cards from /categories-data.json. Keeps the initial
// HTML small (~250 KB target, vs ≈800 KB if every post-card were inline).

(function () {
  'use strict';

  var sections = document.querySelectorAll('section.category-section[data-category]');
  if (!sections.length) return;

  // Derive the site baseurl from /<baseurl>/categories/. Works for both
  // the empty-baseurl Vercel deploy and the /tech-blog/ GitHub Pages
  // backup without needing a <base> element.
  var baseUrl = location.pathname.replace(/\/categories\/?.*$/, '');
  var DEFAULT_FALLBACK = baseUrl + '/assets/images/og-default.png';

  var dataPromise = null;
  function loadData() {
    if (dataPromise) return dataPromise;
    dataPromise = fetch(baseUrl + '/categories-data.json', { credentials: 'same-origin' })
      .then(function (r) {
        if (!r.ok) throw new Error('categories-data.json HTTP ' + r.status);
        return r.json();
      })
      .catch(function () {
        dataPromise = null;
        return null;
      });
    return dataPromise;
  }

  function escapeHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function escapeAttr(s) {
    return escapeHtml(s);
  }

  // Mirrors _includes/post-card.html — the picture element with srcset
  // when modern variants and 525w card variants are present.
  function buildPictureHtml(post) {
    if (!post.img) return '';
    var img = post.img;
    var sizes = '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 525px';

    // Resolve the <img> src: prefer _og.png if available (svg→png plugin
    // path), otherwise fall through to the original front-matter image.
    var imgSrc = img;
    if (post.ip && img.match(/\.svg$/i)) {
      imgSrc = img.replace(/\.svg$/i, '_og.png');
    }

    // post.img may be foo.svg, foo.png, OR foo_og.png (after the
    // svg_to_png_og.rb Jekyll plugin rewrote post.image at :pre_render).
    // Strip any of those tails to recover the stem, then append the
    // variant suffix. Same logic as compute_image_flags in the plugin.
    function variant(suffix) {
      var base = img
        .replace(/_og\.png$/i, '')
        .replace(/\.png$/i, '')
        .replace(/\.svg$/i, '');
      return base + suffix;
    }

    var sources = '';
    if (post.ia) {
      var ogAvif = variant('_og.avif');
      if (post.ica) {
        var cardAvif = variant('_card.avif');
        sources += '<source srcset="' + escapeAttr(cardAvif) + ' 525w, ' +
          escapeAttr(ogAvif) + ' 1120w" type="image/avif" sizes="' + sizes + '">';
      } else {
        sources += '<source srcset="' + escapeAttr(ogAvif) + '" type="image/avif">';
      }
    }
    if (post.iw) {
      var ogWebp = variant('_og.webp');
      if (post.icw) {
        var cardWebp = variant('_card.webp');
        sources += '<source srcset="' + escapeAttr(cardWebp) + ' 525w, ' +
          escapeAttr(ogWebp) + ' 1120w" type="image/webp" sizes="' + sizes + '">';
      } else {
        sources += '<source srcset="' + escapeAttr(ogWebp) + '" type="image/webp">';
      }
    }

    return '<div class="post-card-image"><picture>' + sources +
      '<img src="' + escapeAttr(imgSrc) + '" alt="' + escapeAttr(post.t) +
      '" loading="lazy" decoding="async" width="525" height="276" ' +
      'style="aspect-ratio: 525/276" sizes="' + sizes + '" ' +
      'data-fallback="' + escapeAttr(DEFAULT_FALLBACK) + '">' +
      '</picture></div>';
  }

  function buildExcerptHtml(text) {
    if (!text) return '';
    var s = String(text);
    if (s.indexOf(' - ') !== -1) {
      var parts = s.split(' - ');
      var summary = parts[0];
      var highlights = parts.slice(1).join(' - ');
      if (summary.length > 40) summary = summary.slice(0, 40) + '…';
      if (highlights.length > 80) highlights = highlights.slice(0, 80) + '…';
      return '<div class="post-card-excerpt">' +
        '<span class="excerpt-summary">' + escapeHtml(summary) + '</span>' +
        '<span class="excerpt-highlights">' + escapeHtml(highlights) + '</span>' +
        '</div>';
    }
    if (s.length > 120) s = s.slice(0, 120) + '…';
    return '<p class="post-card-excerpt">' + escapeHtml(s) + '</p>';
  }

  function buildCardHtml(post) {
    var category = post.c || '';
    var catBadge = '';
    if (category) {
      var catClass = category.toLowerCase().replace(/\s+/g, '-');
      catBadge = '<span class="category-badge ' + escapeAttr(catClass) + '">' +
        escapeHtml(category) + '</span>';
    }

    var tagsHtml = '';
    if (post.tags && post.tags.length > 0) {
      tagsHtml = '<div class="post-card-tags">';
      for (var i = 0; i < post.tags.length; i++) {
        tagsHtml += '<span class="tag">#' + escapeHtml(String(post.tags[i]).replace(/-/g, ' ')) + '</span>';
      }
      var tn = post.tn || post.tags.length;
      if (tn > post.tags.length) {
        tagsHtml += '<span class="tag tag--more">+' + (tn - post.tags.length) + '</span>';
      }
      tagsHtml += '</div>';
    }

    return '<article class="post-card card">' +
      '<a href="' + escapeAttr(post.u) + '" class="post-card-inner" aria-label="' + escapeAttr(post.t) + '">' +
      buildPictureHtml(post) +
      '<div class="post-card-content">' +
        '<div class="post-card-meta">' + catBadge +
          '<time datetime="' + escapeAttr(post.x) + '">' + escapeHtml(post.d) + '</time>' +
        '</div>' +
        '<h2 class="post-card-title">' + escapeHtml(post.t) + '</h2>' +
        buildExcerptHtml(post.ex) +
        tagsHtml +
      '</div>' +
      '</a>' +
      '</article>';
  }

  function renderSection(section, catData) {
    if (!section || !catData) return;
    if (section.getAttribute('data-loaded') === '1') return;
    var listEl = section.querySelector('.posts-list');
    if (!listEl) return;
    var posts = catData.posts || [];
    var html = '';
    for (var i = 0; i < posts.length; i++) {
      html += buildCardHtml(posts[i]);
    }
    listEl.innerHTML = html;
    listEl.removeAttribute('aria-busy');
    section.setAttribute('data-loaded', '1');
  }

  function ensureLoaded(section) {
    if (!section || section.getAttribute('data-loaded') === '1') return;
    var key = section.getAttribute('data-category');
    if (!key) return;
    loadData().then(function (data) {
      if (!data) return;
      renderSection(section, data[key]);
    });
  }

  // Top category-card link clicks → preload data so the destination
  // section is populated by the time scroll lands.
  var topGrid = document.querySelector('.categories-page .category-grid');
  if (topGrid) {
    topGrid.addEventListener('click', function () { loadData(); }, { once: true });
  }

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          ensureLoaded(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '300px 0px' });
    sections.forEach(function (sec) { observer.observe(sec); });
  } else {
    var fallback = window.requestIdleCallback || function (cb) { return setTimeout(cb, 1000); };
    fallback(function () { sections.forEach(ensureLoaded); });
  }

  // Hash navigation (e.g. /categories/#security) → render before scroll
  // is observable, so the section content is ready when the hash target
  // becomes visible.
  function loadFromHash() {
    if (!location.hash) return;
    var slug = location.hash.replace(/^#/, '');
    var target = document.getElementById(slug);
    if (target && target.classList.contains('category-section')) {
      ensureLoaded(target);
    }
  }
  loadFromHash();
  window.addEventListener('hashchange', loadFromHash);
})();
