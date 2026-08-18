// Performance Monitoring (Production Only)
// Features: Long Tasks, LCP, FID, INP, CLS, Page Load, Resource Loading
// Field metrics (LCP / INP / CLS) flush at page hide in one first-party beacon
// to /api/vitals, which forwards them to GA4 as `web_vitals` events.
// Extracted from _includes/performance-monitor.html

(function() {
  'use strict';

  // Only run in production
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return;
  }

  // Wait for page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPerformanceMonitor);
  } else {
    initPerformanceMonitor();
  }

  function initPerformanceMonitor() {
    // Long Task monitoring (detect but DON'T report as error - it's a performance metric, not an error)
    // This helps identify blocking JavaScript without polluting Sentry error logs
    if ('PerformanceObserver' in window) {
      try {
        var longTaskCount = 0;
        var longTaskObserver = new PerformanceObserver(function(list) {
          for (var i = 0; i < list.getEntries().length; i++) {
            longTaskCount++;
          }
        });
        longTaskObserver.observe({ entryTypes: ['longtask'] });

        // Report summary on page unload (as metric, not error)
        window.addEventListener('beforeunload', function() {
          if (longTaskCount > 0 && typeof Sentry !== 'undefined' && Sentry.metrics) {
            // Send as metric, NOT as error
            Sentry.metrics.distribution('longtask.count', longTaskCount, {
              unit: 'none',
              tags: { page: window.location.pathname.substring(0, 50) }
            });
          }
        });
      } catch (e) {
        // Long task observer not supported - ignore silently
      }
    }
    // Web Vitals monitoring
    if ('PerformanceObserver' in window) {
      // --- Shared field-metric reporting ------------------------------------
      // Every vital is collected at page hide and delivered in ONE first-party
      // beacon to /api/vitals, which forwards to GA4 server-side.
      //
      // Not window.__track / gtag: gtag batches dataLayer pushes behind a ~5s
      // timer (measured 5003-5005ms, n=4) and vitals are pushed at hide, so
      // any session ending in a tab close or an internal link — nearly all of
      // them on a non-SPA blog — died before that timer fired. Measured 0/3
      // delivered at a 2s leave-gap vs 3/3 at 5s, with a control sendBeacon
      // from the same handler captured 1/1 at 0ms. That control is why this
      // transport was chosen. See notes/ga4-web-vitals-delivery-loss.md.
      var vitalsFlushed = false;
      var vitalsPending = [];
      var vitalsBatch = [];

      function onHidden(fn) { vitalsPending.push(fn); }

      function flushVitals() {
        if (vitalsFlushed) return;
        vitalsFlushed = true;
        for (var vi = 0; vi < vitalsPending.length; vi++) {
          try { vitalsPending[vi](); } catch (err) { /* never block unload */ }
        }
        if (!vitalsBatch.length) return;
        if (!navigator.sendBeacon) return;
        try {
          var body = JSON.stringify({
            p: window.location.pathname,
            m: vitalsBatch
          });
          navigator.sendBeacon(
            '/api/vitals',
            new Blob([body], { type: 'application/json' })
          );
        } catch (err) {
          // Never block unload for analytics.
        }
      }

      function sendVital(name, value, rating, cause) {
        var metric = { n: name, v: value, r: rating };
        if (cause) metric.c = String(cause).slice(0, 100);
        vitalsBatch.push(metric);
      }

      function rate(value, good, poor) {
        if (value <= good) return 'good';
        if (value <= poor) return 'needs-improvement';
        return 'poor';
      }

      // beforeunload does not fire reliably on mobile or when the page enters
      // the bfcache, so the flush hangs off visibilitychange with pagehide as
      // a backstop.
      document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'hidden') flushVitals();
      });
      window.addEventListener('pagehide', flushVitals);

      // Largest Contentful Paint (LCP)
      try {
        var lcpValue = 0;
        var lcpObserver = new PerformanceObserver(function(list) {
          var entries = list.getEntries();
          var lastEntry = entries[entries.length - 1];
          if (!lastEntry) return;
          // renderTime is absent for cross-origin images that lack
          // Timing-Allow-Origin; startTime is the documented fallback. Reading
          // only renderTime silently dropped LCP on exactly those pages.
          var lcp = lastEntry.renderTime || lastEntry.startTime;
          if (!lcp) return;
          lcpValue = lcp;
          // LCP threshold: 4000ms (very slow)
          if (lcp > 4000) {
            console.warn('[Performance] LCP is slow:', Math.round(lcp) + 'ms');
          }
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        onHidden(function() {
          // No entry means "not measured", which is not the same as 0.
          if (!lcpValue) return;
          sendVital('LCP', Math.round(lcpValue), rate(lcpValue, 2500, 4000));
        });
      } catch (e) {
        // LCP observer not supported
        if (window.location.hostname === 'tech.2twodragon.com' && typeof Sentry !== 'undefined' && Sentry.captureException) {
          Sentry.captureException(e, {
            tags: { errorType: 'performance_monitor_lcp' },
            level: 'warning'
          });
        }
      }

      // First Input Delay (FID)
      try {
        var fidObserver = new PerformanceObserver(function(list) {
          for (var i = 0; i < list.getEntries().length; i++) {
            var entry = list.getEntries()[i];
            if (entry.processingStart - entry.startTime > 800) {
              console.warn('[Performance] FID is slow:', (entry.processingStart - entry.startTime) + 'ms');
            }
          }
        });
        fidObserver.observe({ entryTypes: ['first-input'] });
      } catch (e) {
        // FID observer not supported
        if (window.location.hostname === 'tech.2twodragon.com' && typeof Sentry !== 'undefined' && Sentry.captureException) {
          Sentry.captureException(e, {
            tags: { errorType: 'performance_monitor_fid' },
            level: 'warning'
          });
        }
      }

      // Interaction to Next Paint (INP) — replaced FID as a Core Web Vital in
      // March 2024. FID above measures only the FIRST input's delay; INP looks
      // at every interaction's full duration, which is why a page can have a
      // fine FID and a terrible INP.
      //
      // Definition: group event entries by interactionId (one interaction can
      // emit several entries — pointerdown, pointerup, click), take each
      // group's longest duration, then report the entry at index
      // floor(interactions / 50) of the descending list. For pages with fewer
      // than 50 interactions that is simply the worst one; the index exists so
      // a single outlier does not define a long session. Only the top 10 are
      // kept, which is the cap the index can reach.
      try {
        var inpEntries = [];   // {id, duration}, kept sorted desc, max 10
        var inpCount = 0;

        function recordInteraction(entry) {
          var id = entry.interactionId;
          if (!id) return;
          for (var k = 0; k < inpEntries.length; k++) {
            if (inpEntries[k].id === id) {
              if (entry.duration > inpEntries[k].duration) {
                inpEntries[k].duration = entry.duration;
                inpEntries.sort(function(a, b) { return b.duration - a.duration; });
              }
              return;
            }
          }
          inpCount++;
          inpEntries.push({ id: id, duration: entry.duration });
          inpEntries.sort(function(a, b) { return b.duration - a.duration; });
          if (inpEntries.length > 10) inpEntries.length = 10;
        }

        var inpObserver = new PerformanceObserver(function(list) {
          var entries = list.getEntries();
          for (var n = 0; n < entries.length; n++) recordInteraction(entries[n]);
        });
        // durationThreshold requires the single-`type` form of observe().
        // 40ms is the web-vitals default: below it an interaction cannot be
        // the page's worst one, and observing everything is needless overhead.
        inpObserver.observe({ type: 'event', buffered: true, durationThreshold: 40 });
        inpObserver.observe({ type: 'first-input', buffered: true });

        onHidden(function() {
          // No interaction means the reader never touched the page. That is
          // "not measured", not 0 — reporting 0 would fake a perfect score.
          if (!inpEntries.length) return;
          var idx = Math.min(inpEntries.length - 1, Math.floor(inpCount / 50));
          var inp = Math.round(inpEntries[idx].duration);
          if (inp > 500) {
            console.warn('[Performance] INP is slow:', inp + 'ms');
          }
          sendVital('INP', inp, rate(inp, 200, 500));
        });
      } catch (e) {
        // INP observer not supported (Safari < 16.4, older Chromium)
        if (window.location.hostname === 'tech.2twodragon.com' && typeof Sentry !== 'undefined' && Sentry.captureException) {
          Sentry.captureException(e, {
            tags: { errorType: 'performance_monitor_inp' },
            level: 'warning'
          });
        }
      }

      // Cumulative Layout Shift (CLS) - detailed tracking
      var clsValue = 0;
      var clsEntries = [];

      // CLS cause analysis
      function analyzeCLSCause(entry) {
        var causes = [];
        if (entry.sources && entry.sources.length > 0) {
          entry.sources.forEach(function(source) {
            if (source.node) {
              var tagName = source.node.tagName || '';
              var className = typeof source.node.className === 'string'
                ? source.node.className
                : (source.node.className && source.node.className.baseVal || source.node.className && source.node.className.toString() || '');
              var id = source.node.id || '';

              if (tagName === 'IMG' || (className && (className.includes('image') || className.includes('img')))) {
                causes.push('Image: ' + (source.node.src || source.node.getAttribute('src') || 'unknown'));
              } else if (tagName === 'IFRAME' || (className && (className.includes('adsbygoogle') || className.includes('ad')))) {
                causes.push('Ad: ' + (source.node.src || className || 'unknown'));
              } else if (tagName === 'DIV' && className && className.includes('card')) {
                causes.push('Card: ' + className);
              } else if (tagName === 'SCRIPT') {
                causes.push('Script insertion');
              } else {
                var classNameStr = className ? (typeof className === 'string' ? className.split(' ')[0] : String(className).split(' ')[0]) : '';
                causes.push(tagName + (id ? '#' + id : '') + (classNameStr ? '.' + classNameStr : ''));
              }
            }
          });
        }
        return causes.length > 0 ? causes.join(', ') : 'unknown';
      }

      // Session-window CLS, the way Core Web Vitals actually defines it: the
      // LARGEST burst of shifts, where a burst breaks on a 1s gap or after 5s.
      // `clsValue` used to be the running SUM of every shift, which is a
      // different (and always larger) number than the one Vercel Speed
      // Insights, CrUX and Lighthouse report — so the console figure could not
      // be compared against any of them, and shipping it to GA4 under the name
      // "CLS" would have made that mismatch permanent.
      var clsSessionValue = 0;
      var clsSessionFirst = null;
      var clsSessionLast = null;
      var clsTopCause = 'unknown';

      // Unlike LCP and INP, CLS reports even at 0: a page that never shifted
      // has genuinely measured a CLS of zero.
      onHidden(function() {
        sendVital(
          'CLS',
          Math.round(clsValue * 10000) / 10000,
          rate(clsValue, 0.1, 0.25),
          clsTopCause
        );
      });

      try {
        var clsObserver = new PerformanceObserver(function(list) {
          for (var i = 0; i < list.getEntries().length; i++) {
            var entry = list.getEntries()[i];
            if (!entry.hadRecentInput) {
              var cause = analyzeCLSCause(entry);

              if (
                clsSessionLast !== null &&
                entry.startTime - clsSessionLast < 1000 &&
                entry.startTime - clsSessionFirst < 5000
              ) {
                clsSessionValue += entry.value;
              } else {
                clsSessionValue = entry.value;
                clsSessionFirst = entry.startTime;
              }
              clsSessionLast = entry.startTime;

              if (clsSessionValue > clsValue) {
                clsValue = clsSessionValue;
                clsTopCause = cause;
              }

              clsEntries.push({
                value: entry.value,
                sources: entry.sources || [],
                startTime: entry.startTime,
                cause: cause
              });

              if (clsValue > 0.1) {
                console.warn('[Performance] CLS is high:', clsValue.toFixed(6), '| Cause:', cause);
              }
            }
          }
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });

        // Final CLS report on page unload
        window.addEventListener('beforeunload', function() {
          if (clsValue > 0.25) {
            console.error('[Performance] CLS is very high:', clsValue.toFixed(6));
          }
        });
      } catch (e) {
        // CLS observer not supported
        if (window.location.hostname === 'tech.2twodragon.com' && typeof Sentry !== 'undefined' && Sentry.captureException) {
          Sentry.captureException(e, {
            tags: { errorType: 'performance_monitor_cls' },
            level: 'warning'
          });
        }
      }
    }

    // Page load time monitoring
    window.addEventListener('load', function() {
      try {
        var entries = performance.getEntriesByType('navigation');
        if (entries && entries.length > 0) {
          var nav = entries[0];
          var loadTime = Math.round(nav.loadEventEnd);
          var domReady = Math.round(nav.domContentLoadedEventEnd);

          if (loadTime > 0 && loadTime < 60000 && loadTime > 3000) {
            console.warn('[Performance] Page load is slow:', loadTime + 'ms');
          }
          if (domReady > 0 && domReady < 60000 && domReady > 5000) {
            console.warn('[Performance] DOM ready is slow:', domReady + 'ms');
          }
        }
      } catch (e) {}
    });

    // Resource loading monitoring
    if ('PerformanceObserver' in window) {
      try {
        var resourceObserver = new PerformanceObserver(function(list) {
          for (var i = 0; i < list.getEntries().length; i++) {
            var entry = list.getEntries()[i];
            var isApiRequest = entry.name.includes('/api/');
            var threshold = isApiRequest ? 8000 : 3000;

            if (entry.duration > threshold && entry.initiatorType !== 'navigation') {
              if (!isApiRequest) {
                console.warn('[Performance] Slow resource:', entry.name, Math.round(entry.duration) + 'ms');
              }
            }
          }
        });
        resourceObserver.observe({ entryTypes: ['resource'] });
      } catch (e) {
        // Resource observer not supported
        if (window.location.hostname === 'tech.2twodragon.com' && typeof Sentry !== 'undefined' && Sentry.captureException) {
          Sentry.captureException(e, {
            tags: { errorType: 'performance_monitor_resource' },
            level: 'warning'
          });
        }
      }
    }
  }
})();
