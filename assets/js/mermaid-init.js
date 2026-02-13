// Mermaid.js Initialization - On-demand loading, theme support, fullscreen
// Extracted from _includes/mermaid.html
(function() {
  'use strict';

  // Check if page has mermaid diagrams
  var hasMermaid = document.querySelector('.language-mermaid, pre code.mermaid');
  if (!hasMermaid) return;

  // Load mermaid.js on demand
  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js';
  script.onload = function() {
    try {
      var isDark = document.documentElement.getAttribute('data-theme') === 'dark';

      mermaid.initialize({
        startOnLoad: false,
        theme: isDark ? 'dark' : 'default',
        securityLevel: 'loose',
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
          curve: 'basis',
          padding: 15
        },
        sequence: {
          useMaxWidth: true,
          wrap: true,
          actorMargin: 80
        },
        logLevel: 'error',
        suppressErrorRendering: false
      });

      // Convert code blocks to mermaid divs with container
      document.querySelectorAll('.language-mermaid, pre code.mermaid').forEach(function(el) {
        try {
          var pre = el.closest('pre');
          if (!pre) return;
          var code = el.textContent || el.innerText;

          if (!code || !code.trim()) return;

          // Create container
          var container = document.createElement('div');
          container.className = 'mermaid-container';

          // Create toolbar
          var toolbar = document.createElement('div');
          toolbar.className = 'mermaid-toolbar';
          toolbar.innerHTML = '<button class="mermaid-fullscreen-btn" aria-label="Fullscreen" title="Fullscreen"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg></button>';

          // Create mermaid div and store original source for re-rendering
          var div = document.createElement('div');
          div.className = 'mermaid';
          div.setAttribute('data-mermaid-source', code.trim());
          div.textContent = code.trim();

          container.appendChild(toolbar);
          container.appendChild(div);
          pre.parentNode.replaceChild(container, pre);
        } catch (e) {
          console.warn('[Mermaid] Failed to convert diagram:', e);
        }
      });

      // Run Mermaid rendering
      mermaid.run({
        querySelector: '.mermaid',
        suppressErrors: false
      }).then(function() {
        // Attach fullscreen handlers after render
        document.querySelectorAll('.mermaid-fullscreen-btn').forEach(function(btn) {
          btn.addEventListener('click', function(e) {
            e.stopPropagation();
            var container = this.closest('.mermaid-container');
            if (container) {
              if (container.requestFullscreen) {
                container.requestFullscreen();
              } else if (container.webkitRequestFullscreen) {
                container.webkitRequestFullscreen();
              }
            }
          });
        });
      }).catch(function(err) {
        console.warn('[Mermaid] Rendering error (non-critical):', err);
      });
    } catch (e) {
      console.warn('[Mermaid] Initialization error:', e);
    }
  };

  script.onerror = function() {
    console.warn('[Mermaid] Failed to load mermaid.js');
  };
  document.head.appendChild(script);

  // Re-render on theme change (without page reload)
  var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.attributeName === 'data-theme' && window.mermaid) {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        mermaid.initialize({
          theme: isDark ? 'dark' : 'default',
          securityLevel: 'loose',
          flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
          sequence: { useMaxWidth: true, wrap: true },
          logLevel: 'error'
        });
        document.querySelectorAll('.mermaid[data-processed], .mermaid[data-mermaid-source]').forEach(function(el) {
          el.removeAttribute('data-processed');
          var source = el.getAttribute('data-mermaid-source');
          if (source) {
            el.innerHTML = '';
            el.textContent = source;
          }
        });
        mermaid.run({ querySelector: '.mermaid' }).catch(function() {});
      }
    });
  });
  observer.observe(document.documentElement, { attributes: true });
})();
