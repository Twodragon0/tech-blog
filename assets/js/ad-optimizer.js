// Google AdSense 광고 최적화: CLS 방지를 위한 자동 컨테이너 래핑
// 광고를 .ad-container로 자동 감싸서 레이아웃 시프트 방지

(function() {
  'use strict';

  // 광고 컨테이너로 감싸기
  function wrapAdInContainer(adElement) {
    // 이미 컨테이너로 감싸져 있으면 스킵
    if (adElement.closest('.ad-container')) {
      return;
    }

    // 컨테이너 생성
    const container = document.createElement('div');
    container.className = 'ad-container';
    
    // 높이 예약 없음 (2026-08-14). 예약해 두었다가 접는 것이 곧 레이아웃
    // 시프트다. head.html 의 :has() 규칙이 unfilled 광고의 컨테이너를
    // display:none 으로 지우므로, 여기서 90/250/600px 을 잡아두면 그 순간
    // 독자가 보던 자리에서 그만큼이 사라진다. 실측 게재율은 0/4·0/3.
    // 측정: scripts/dev/measure_ad_collapse_cls.mjs (0.0575 -> 0.0039)

    // 광고를 컨테이너로 이동
    adElement.parentNode.insertBefore(container, adElement);
    container.appendChild(adElement);

    // MutationObserver로 광고 로드 감지 (iframe 추가 감지)
    // offsetHeight 읽기는 requestAnimationFrame에 묶어 강제 레이아웃을 회피.
    const observer = new MutationObserver(function() {
      const iframe = container.querySelector('iframe');
      if (!iframe) return;
      requestAnimationFrame(function() {
        if (iframe.offsetHeight > 0) {
          container.style.minHeight = 'auto';
          observer.disconnect();
        }
      });
    });

    observer.observe(container, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style']
    });

    // 10초 후 타임아웃. 예약 높이를 더 이상 잡지 않으므로 위 observer 가 하는
    // minHeight='auto' 는 사실상 no-op 이지만, 광고가 실제로 채워졌을 때
    // 컨테이너가 iframe 높이를 그대로 따르도록 두는 안전장치로 남긴다.
    setTimeout(function() {
      observer.disconnect();
    }, 10000);
  }

  // 모든 광고 요소 찾기 및 래핑
  function optimizeAds() {
    // Google AdSense 광고 요소 찾기 (adsbygoogle-noablate 포함)
    const ads = document.querySelectorAll(
      'ins.adsbygoogle, .adsbygoogle, ins.adsbygoogle-noablate, .adsbygoogle-noablate, .google-auto-placed'
    );
    
    ads.forEach(function(ad) {
      wrapAdInContainer(ad);
      // minHeight 예약 없음 — 접힐 높이를 잡아두지 않는다. contain 은 시프트가
      // 생기더라도 전파 범위를 제한하므로 유지.
      if (!ad.style.contain) {
        ad.style.display = 'block';
        ad.style.contain = 'layout style';
        ad.style.width = '100%';
      }
    });
    
    // google-auto-placed 클래스를 가진 요소들도 처리
    const autoPlacedAds = document.querySelectorAll('.google-auto-placed, [class*="google-auto-placed"]');
    autoPlacedAds.forEach(function(ad) {
      // 이미 처리된 경우 스킵
      if (!ad.closest('.ad-container')) {
        wrapAdInContainer(ad);
        // aspect-ratio 설정으로 CLS 방지
        if (!ad.style.aspectRatio) {
          ad.style.aspectRatio = 'auto';
          ad.style.display = 'block';
          ad.style.contain = 'layout style';
        }
      }
    });

    // 동적으로 추가된 광고도 처리
    if ('MutationObserver' in window) {
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === 1) { // Element node
              // 직접 추가된 광고 (adsbygoogle-noablate 포함)
              if (node.classList && (
                  node.classList.contains('adsbygoogle') || 
                  node.classList.contains('adsbygoogle-noablate') ||
                  node.tagName === 'INS' && (
                    node.classList.contains('adsbygoogle') || 
                    node.classList.contains('adsbygoogle-noablate')
                  )
                )) {
                wrapAdInContainer(node);
                // 즉시 스타일 적용
                node.style.display = 'block';
                node.style.contain = 'layout style';
                node.style.width = '100%';
              }
              
              // 하위에 있는 광고
              const ads = node.querySelectorAll && node.querySelectorAll(
                'ins.adsbygoogle, .adsbygoogle, ins.adsbygoogle-noablate, .adsbygoogle-noablate'
              );
              if (ads) {
                ads.forEach(function(ad) {
                  wrapAdInContainer(ad);
                  ad.style.display = 'block';
                  ad.style.contain = 'layout style';
                  ad.style.width = '100%';
                });
              }
            }
          });
        });
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }
  }

  // 초기화: window.load + requestIdleCallback 으로 지연하여
  // optimizeAds()의 layout-mutating 작업이 LCP 직후 critical path를
  // 떠나도록 한다 (PSI: forced reflow 38ms 출처 회피).
  function scheduleOptimize(delay) {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(optimizeAds, { timeout: delay });
    } else {
      setTimeout(optimizeAds, delay);
    }
  }

  function init() {
    var runOnLoad = function () {
      scheduleOptimize(2000);

      if (window.adsbygoogle) {
        scheduleOptimize(2500);
      } else {
        var adSenseObserver = new MutationObserver(function () {
          if (window.adsbygoogle) {
            adSenseObserver.disconnect();
            scheduleOptimize(1500);
          }
        });
        adSenseObserver.observe(document.documentElement, {
          childList: true,
          subtree: true
        });
        setTimeout(function () {
          adSenseObserver.disconnect();
          scheduleOptimize(0);
        }, 5000);
      }
    };

    if (document.readyState === 'complete') {
      runOnLoad();
    } else {
      window.addEventListener('load', runOnLoad, { once: true });
    }
  }

  // 초기화 실행
  init();
})();
