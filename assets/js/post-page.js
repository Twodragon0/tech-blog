// Post page JavaScript - extracted from inline scripts in post.html
// Features: heading IDs, reading time, external links, progress bar, Giscus loading, lightbox
// Loaded conditionally on post pages only via defer

(function() {
  'use strict';

  // Common utility: schedule non-critical work during idle time
  var scheduleIdleWork = function(callback, timeout) {
    timeout = timeout || 2000;
    if ('requestIdleCallback' in window) {
      requestIdleCallback(callback, { timeout: timeout });
    } else {
      setTimeout(callback, 0);
    }
  };

  // ============================================
  // 1. Heading ID Generation (for TOC links)
  // ============================================

  // Generate safe ID from text (handles Korean and special characters)
  // Matches kramdown's auto_id format as closely as possible
  function generateId(text) {
    if (!text) return '';

    // Security: Use textContent instead of innerHTML to prevent XSS
    // Remove HTML tags if any by parsing safely
    var tempDiv = document.createElement('div');
    // Security: Only set textContent, not innerHTML, to prevent XSS
    tempDiv.textContent = text;
    text = tempDiv.textContent || text;

    // Remove anchor links if present
    text = text.replace(/<a[^>]*>.*?<\/a>/gi, '');

    // Trim and normalize whitespace
    text = text.trim().replace(/\s+/g, ' ');

    // Convert to lowercase
    var id = text.toLowerCase();

    // Replace spaces with hyphens (kramdown style)
    id = id.replace(/\s+/g, '-');

    // Remove special characters but keep alphanumeric, Korean, and hyphens
    // Korean Unicode ranges: \uAC00-\uD7A3 (Hangul syllables), \u3131-\u318E (Hangul Jamo)
    id = id.replace(/[^\w\uAC00-\uD7A3\u3131-\u318E-]/g, '');

    // Remove consecutive hyphens
    id = id.replace(/-+/g, '-');

    // Remove leading/trailing hyphens
    id = id.replace(/^-+|-+$/g, '');

    // If empty, use fallback
    if (!id) {
      id = 'heading';
    }

    // If starts with number, add prefix (HTML ID cannot start with number)
    if (/^\d/.test(id)) {
      id = 'heading-' + id;
    }

    // Ensure uniqueness
    var uniqueId = id;
    var counter = 1;
    while (document.getElementById(uniqueId)) {
      uniqueId = id + '-' + counter;
      counter++;
    }

    return uniqueId;
  }

  // Generate IDs for all headings in post content
  function generateHeadingIds() {
    var postContent = document.querySelector('.post-content');
    if (!postContent) return;

    var headings = postContent.querySelectorAll('h1, h2, h3, h4, h5, h6');

    headings.forEach(function(heading) {
      // Skip if already has an ID
      if (heading.id) return;

      // Get text content excluding any existing anchor links
      var text = '';
      var children = Array.from(heading.childNodes);
      children.forEach(function(node) {
        if (node.nodeType === Node.TEXT_NODE) {
          text += node.textContent;
        } else if (node.nodeType === Node.ELEMENT_NODE && !node.classList.contains('heading-anchor')) {
          text += node.textContent || node.innerText || '';
        }
      });

      // Fallback to textContent if no text found
      if (!text.trim()) {
        text = heading.textContent || heading.innerText || '';
      }

      var id = generateId(text);

      if (id) {
        heading.id = id;

        // Add anchor link icon for better UX
        if (!heading.querySelector('.heading-anchor')) {
          var anchor = document.createElement('a');
          anchor.className = 'heading-anchor';
          anchor.href = '#' + id;
          anchor.setAttribute('aria-label', 'Permalink to ' + text.trim());
          anchor.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>';

          // Insert anchor at the beginning
          heading.insertBefore(anchor, heading.firstChild);
        }
      }
    });
  }

  // Run immediately when DOM is ready (defer guarantees DOM is parsed)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', generateHeadingIds);
  } else {
    generateHeadingIds();
  }

  // ============================================
  // 2. Reading Time Calculation
  // ============================================

  function initReadingTime() {
    var content = document.querySelector('.post-content');
    if (content) {
      var text = content.textContent || content.innerText || '';
      // Hybrid reading time: Korean ~500 chars/min, English ~200 words/min
      var koreanChars = (text.match(/[\uAC00-\uD7A3]/g) || []).length;
      var englishWords = text.replace(/[\uAC00-\uD7A3]/g, '').trim().split(/\s+/).filter(Boolean).length;
      var readingTime = Math.max(1, Math.ceil((koreanChars / 500) + (englishWords / 200)));
      var readingTimeEl = document.getElementById('reading-time');
      if (readingTimeEl) {
        readingTimeEl.textContent = readingTime + ' min read';
      }
    }

    // Enhance external links in post content (non-critical)
    scheduleIdleWork(enhanceExternalLinks, 3000);
  }

  scheduleIdleWork(function() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', initReadingTime);
    } else {
      initReadingTime();
    }
  });

  // ============================================
  // 3. External Link Enhancement
  // ============================================

  function enhanceExternalLinks() {
    var postContent = document.querySelector('.post-content');
    if (!postContent) return;

    var links = postContent.querySelectorAll('a[href]');
    var currentHost = window.location.hostname;

    links.forEach(function(link) {
      var href = link.getAttribute('href');
      if (!href) return;

      // Skip if already processed or is a special link
      if (link.classList.contains('external-link-processed') ||
          href.startsWith('#') ||
          href.startsWith('mailto:') ||
          href.startsWith('tel:')) {
        return;
      }

      // Check if it's an external link
      var isExternal = (href.startsWith('http://') || href.startsWith('https://')) &&
                        !href.includes(currentHost) &&
                        !link.hasAttribute('target');

      // Check if it's an internal link that should open in new tab
      var shouldOpenNewTab = link.hasAttribute('target') &&
                              link.getAttribute('target') === '_blank';

      if (isExternal || shouldOpenNewTab) {
        // Add external link attributes for security
        if (!link.hasAttribute('target')) {
          link.setAttribute('target', '_blank');
        }
        if (!link.hasAttribute('rel')) {
          link.setAttribute('rel', 'noopener noreferrer');
        }

        // Add aria-label for accessibility
        var linkText = link.textContent.trim();
        if (!link.hasAttribute('aria-label')) {
          link.setAttribute('aria-label', linkText + ' (새 창에서 열림)');
        }

        // Add class for styling
        link.classList.add('external-link', 'external-link-processed');

        // Add title attribute if not present
        if (!link.hasAttribute('title')) {
          link.setAttribute('title', '새 창에서 열림');
        }
      }
    });
  }

  // ============================================
  // 4. Reading Progress Bar (rAF throttled)
  // ============================================

  var ticking = false;
  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        var article = document.querySelector('.post-article');
        var progressBar = document.getElementById('reading-progress');
        if (article && progressBar) {
          var articleTop = article.offsetTop;
          var articleHeight = article.offsetHeight;
          var windowHeight = window.innerHeight;
          var scrollY = window.scrollY;
          var progress = Math.min(Math.max((scrollY - articleTop + windowHeight * 0.3) / articleHeight * 100, 0), 100);
          progressBar.style.width = progress + '%';
        }
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // ============================================
  // 5. Giscus Loading State Management
  // ============================================

  document.addEventListener('DOMContentLoaded', function() {
    var giscusContainer = document.getElementById('giscus-container');
    var giscusLoading = document.getElementById('giscus-loading');

    if (giscusContainer && giscusLoading) {
      // Hide loading indicator when Giscus loads
      var observer = new MutationObserver(function(mutations) {
        var giscusFrame = giscusContainer.querySelector('iframe');
        if (giscusFrame && giscusFrame.contentDocument) {
          giscusLoading.classList.add('hidden');
          observer.disconnect();
        }
      });

      observer.observe(giscusContainer, {
        childList: true,
        subtree: true
      });

      // Maximum wait time (auto-hide loading indicator after 10 seconds)
      setTimeout(function() {
        if (!giscusLoading.classList.contains('hidden')) {
          giscusLoading.classList.add('hidden');
        }
      }, 10000);

      // Check Giscus script load
      var giscusScript = document.querySelector('script[src*="giscus.app"]');
      if (giscusScript) {
        giscusScript.addEventListener('load', function() {
          // Check after short delay
          setTimeout(function() {
            var giscusFrame = giscusContainer.querySelector('iframe');
            if (giscusFrame) {
              giscusLoading.classList.add('hidden');
            }
          }, 2000);
        });
      }
    }
  });

  // ============================================
  // 6. Image Lightbox
  // ============================================

  var lightbox = document.createElement('div');
  lightbox.id = 'image-lightbox';
  lightbox.className = 'image-lightbox';
  lightbox.setAttribute('role', 'dialog');
  lightbox.setAttribute('aria-modal', 'true');
  lightbox.setAttribute('aria-label', 'Image viewer');
  lightbox.innerHTML = '\
    <div class="lightbox-backdrop"></div>\
    <div class="lightbox-content">\
      <div class="lightbox-controls">\
        <button class="lightbox-btn lightbox-zoom-out" aria-label="축소" title="축소 (-)">\
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\
            <circle cx="11" cy="11" r="8"/>\
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>\
            <line x1="8" y1="11" x2="14" y2="11"/>\
          </svg>\
        </button>\
        <button class="lightbox-btn lightbox-zoom-in" aria-label="확대" title="확대 (+)">\
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\
            <circle cx="11" cy="11" r="8"/>\
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>\
            <line x1="11" y1="8" x2="11" y2="14"/>\
            <line x1="8" y1="11" x2="14" y2="11"/>\
          </svg>\
        </button>\
        <button class="lightbox-btn lightbox-reset" aria-label="원래 크기" title="원래 크기 (0)">\
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\
            <polyline points="15 3 21 3 21 9"/>\
            <polyline points="9 21 3 21 3 15"/>\
            <line x1="21" y1="3" x2="14" y2="10"/>\
            <line x1="3" y1="21" x2="10" y2="14"/>\
          </svg>\
        </button>\
        <button class="lightbox-btn lightbox-close" aria-label="닫기" title="닫기 (ESC)">\
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\
            <line x1="18" y1="6" x2="6" y2="18"/>\
            <line x1="6" y1="6" x2="18" y2="18"/>\
          </svg>\
        </button>\
      </div>\
      <div class="lightbox-image-wrapper">\
        <img class="lightbox-image" src="" alt="">\
      </div>\
      <div class="lightbox-caption"></div>\
      <div class="lightbox-zoom-info"></div>\
      <div class="lightbox-hint">더블클릭 또는 휠로 확대/축소</div>\
    </div>\
  ';
  document.body.appendChild(lightbox);

  var lightboxImage = lightbox.querySelector('.lightbox-image');
  var lightboxCaption = lightbox.querySelector('.lightbox-caption');
  var lightboxClose = lightbox.querySelector('.lightbox-close');
  var lightboxBackdrop = lightbox.querySelector('.lightbox-backdrop');
  var lightboxContent = lightbox.querySelector('.lightbox-content');
  var lightboxZoomIn = lightbox.querySelector('.lightbox-zoom-in');
  var lightboxZoomOut = lightbox.querySelector('.lightbox-zoom-out');
  var lightboxReset = lightbox.querySelector('.lightbox-reset');
  var lightboxZoomInfo = lightbox.querySelector('.lightbox-zoom-info');
  var lightboxHint = lightbox.querySelector('.lightbox-hint');
  var lightboxWrapper = lightbox.querySelector('.lightbox-image-wrapper');

  var currentZoom = 1;
  var isDragging = false;
  var startX = 0, startY = 0;
  var translateX = 0, translateY = 0;
  var lastTranslateX = 0, lastTranslateY = 0;
  var zoomInfoTimeout = null;

  function updateTransform() {
    lightboxImage.style.transform = 'scale(' + currentZoom + ') translate(' + (translateX / currentZoom) + 'px, ' + (translateY / currentZoom) + 'px)';
  }

  function showZoomInfo() {
    lightboxZoomInfo.textContent = Math.round(currentZoom * 100) + '%';
    lightboxZoomInfo.classList.add('visible');
    clearTimeout(zoomInfoTimeout);
    zoomInfoTimeout = setTimeout(function() {
      lightboxZoomInfo.classList.remove('visible');
    }, 1500);
  }

  function zoom(delta, centerX, centerY) {
    var oldZoom = currentZoom;
    currentZoom = Math.max(0.5, Math.min(5, currentZoom + delta));

    if (currentZoom !== oldZoom) {
      if (currentZoom > 1) {
        lightboxImage.classList.add('zoomed');
      } else {
        lightboxImage.classList.remove('zoomed');
        translateX = 0;
        translateY = 0;
      }
      updateTransform();
      showZoomInfo();
    }
  }

  function resetZoom() {
    currentZoom = 1;
    translateX = 0;
    translateY = 0;
    lightboxImage.classList.remove('zoomed');
    updateTransform();
    showZoomInfo();
  }

  function openLightbox(img) {
    var src = img.dataset.fullSrc || img.src;
    var alt = img.alt || '';

    if (!src) return;

    try {
      var decodedSrc = decodeURIComponent(src);
      if (decodedSrc !== src && /[가-힣]/.test(decodedSrc)) {
        src = decodedSrc;
      }
    } catch (e) {}

    currentZoom = 1;
    translateX = 0;
    translateY = 0;
    lightboxImage.classList.remove('zoomed', 'dragging');
    lightboxImage.style.transform = '';
    lightboxImage.style.opacity = '0';
    lightboxImage.style.display = 'block';
    lightboxImage.style.visibility = 'visible';

    lightboxCaption.style.color = 'rgba(255, 255, 255, 0.95)';
    lightboxCaption.textContent = alt;

    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';

    setTimeout(function() {
      lightboxHint.classList.add('visible');
      setTimeout(function() {
        lightboxHint.classList.remove('visible');
      }, 3000);
    }, 500);

    var handleImageLoad = function() {
      lightboxImage.style.opacity = '1';
    };

    var handleImageError = function() {
      lightboxImage.style.opacity = '0.5';
      lightboxCaption.textContent = alt ? alt + ' (이미지를 불러올 수 없습니다)' : '이미지를 불러올 수 없습니다';
      lightboxCaption.style.color = '#ff6b6b';
    };

    lightboxImage.onload = null;
    lightboxImage.onerror = null;

    var preloadImage = new Image();
    var retryCount = 0;
    var originalSrc = img.dataset.fullSrc || img.src;

    var tryLoadImage = function(imageSrc) {
      preloadImage.onload = function() {
        lightboxImage.src = imageSrc;
        lightboxImage.alt = alt;
        lightboxImage.onload = handleImageLoad;
        lightboxImage.onerror = handleImageError;
        if (lightboxImage.complete && lightboxImage.naturalHeight !== 0) {
          handleImageLoad();
        }
      };

      preloadImage.onerror = function() {
        retryCount++;
        if (retryCount === 1 && imageSrc !== originalSrc) {
          tryLoadImage(originalSrc);
        } else {
          handleImageError();
        }
      };

      preloadImage.src = imageSrc;
    };

    tryLoadImage(src);
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
    lightboxHint.classList.remove('visible');
    setTimeout(function() {
      if (!lightbox.classList.contains('active')) {
        lightboxImage.src = '';
        lightboxImage.onload = null;
        lightboxImage.onerror = null;
        resetZoom();
      }
    }, 350);
  }

  function attachImageHandlers() {
    var images = document.querySelectorAll('.clickable-image, .post-content img, .post-image img');
    images.forEach(function(img) {
      if (img.dataset.lightboxAttached === 'true') return;

      img.style.cursor = 'zoom-in';
      img.dataset.lightboxAttached = 'true';
      img.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        openLightbox(this);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachImageHandlers);
  } else {
    attachImageHandlers();
  }
  setTimeout(attachImageHandlers, 500);

  lightboxBackdrop.addEventListener('click', function(e) {
    if (e.target === lightboxBackdrop) closeLightbox();
  });

  lightboxClose.addEventListener('click', function(e) {
    e.stopPropagation();
    closeLightbox();
  });

  lightboxZoomIn.addEventListener('click', function(e) {
    e.stopPropagation();
    zoom(0.25);
  });

  lightboxZoomOut.addEventListener('click', function(e) {
    e.stopPropagation();
    zoom(-0.25);
  });

  lightboxReset.addEventListener('click', function(e) {
    e.stopPropagation();
    resetZoom();
  });

  lightboxImage.addEventListener('dblclick', function(e) {
    e.stopPropagation();
    if (currentZoom > 1) {
      resetZoom();
    } else {
      zoom(1);
    }
  });

  lightboxWrapper.addEventListener('wheel', function(e) {
    if (!lightbox.classList.contains('active')) return;
    e.preventDefault();
    var delta = e.deltaY > 0 ? -0.15 : 0.15;
    zoom(delta);
  }, { passive: false });

  lightboxImage.addEventListener('mousedown', function(e) {
    if (currentZoom <= 1) return;
    e.preventDefault();
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    lastTranslateX = translateX;
    lastTranslateY = translateY;
    lightboxImage.classList.add('dragging');
  });

  document.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    translateX = lastTranslateX + (e.clientX - startX);
    translateY = lastTranslateY + (e.clientY - startY);
    updateTransform();
  });

  document.addEventListener('mouseup', function() {
    if (isDragging) {
      isDragging = false;
      lightboxImage.classList.remove('dragging');
    }
  });

  var touchStartDistance = 0;
  var initialZoom = 1;

  lightboxImage.addEventListener('touchstart', function(e) {
    if (e.touches.length === 2) {
      touchStartDistance = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      initialZoom = currentZoom;
    } else if (e.touches.length === 1 && currentZoom > 1) {
      isDragging = true;
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
      lastTranslateX = translateX;
      lastTranslateY = translateY;
    }
  }, { passive: true });

  lightboxImage.addEventListener('touchmove', function(e) {
    if (e.touches.length === 2) {
      var distance = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      var scale = distance / touchStartDistance;
      currentZoom = Math.max(0.5, Math.min(5, initialZoom * scale));
      if (currentZoom > 1) {
        lightboxImage.classList.add('zoomed');
      } else {
        lightboxImage.classList.remove('zoomed');
      }
      updateTransform();
    } else if (isDragging && e.touches.length === 1) {
      translateX = lastTranslateX + (e.touches[0].clientX - startX);
      translateY = lastTranslateY + (e.touches[0].clientY - startY);
      updateTransform();
    }
  }, { passive: true });

  lightboxImage.addEventListener('touchend', function() {
    isDragging = false;
    if (currentZoom <= 1) {
      translateX = 0;
      translateY = 0;
      updateTransform();
    }
    showZoomInfo();
  });

  document.addEventListener('keydown', function(e) {
    if (!lightbox.classList.contains('active')) return;

    switch(e.key) {
      case 'Escape': closeLightbox(); break;
      case '+': case '=': zoom(0.25); break;
      case '-': zoom(-0.25); break;
      case '0': resetZoom(); break;
    }
  });

  lightboxContent.addEventListener('click', function(e) {
    if (e.target === lightboxContent || e.target === lightboxWrapper) {
      closeLightbox();
    }
  });
})();
