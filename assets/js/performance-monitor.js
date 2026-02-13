// Performance Monitoring (Production Only)
// Features: Long Tasks, LCP, FID, CLS, Page Load, Resource Loading
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
      // Largest Contentful Paint (LCP)
      try {
        var lcpObserver = new PerformanceObserver(function(list) {
          var entries = list.getEntries();
          var lastEntry = entries[entries.length - 1];
          if (lastEntry && lastEntry.renderTime) {
            var lcp = lastEntry.renderTime;
            // LCP threshold: 4000ms (very slow)
            if (lcp > 4000) {
              console.warn('[Performance] LCP is slow:', Math.round(lcp) + 'ms');
            }
          }
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
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

      try {
        var clsObserver = new PerformanceObserver(function(list) {
          for (var i = 0; i < list.getEntries().length; i++) {
            var entry = list.getEntries()[i];
            if (!entry.hadRecentInput) {
              var cause = analyzeCLSCause(entry);
              clsValue += entry.value;

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
