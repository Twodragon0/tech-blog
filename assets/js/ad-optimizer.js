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
    
    // 광고 타입에 따라 최소 높이 설정
    const adData = adElement.getAttribute('data-ad-slot') || 
                   adElement.getAttribute('data-ad-format') || '';
    
    // 광고 포맷에 따른 높이 설정
    if (adData.includes('horizontal') || adData.includes('banner')) {
      container.style.minHeight = '90px'; // 728x90 또는 970x90
    } else if (adData.includes('vertical') || adData.includes('sidebar')) {
      container.style.minHeight = '600px'; // 300x600 또는 160x600
    } else if (adData.includes('rectangle')) {
      container.style.minHeight = '250px'; // 300x250
    } else {
      container.style.minHeight = '250px'; // 기본값
    }

    // 광고를 컨테이너로 이동
    adElement.parentNode.insertBefore(container, adElement);
    container.appendChild(adElement);

    // 광고 로드 완료 감지
    const checkAdLoaded = setInterval(function() {
      const iframe = container.querySelector('iframe');
      if (iframe && iframe.offsetHeight > 0) {
        // 광고가 로드되면 플레이스홀더 제거
        container.style.minHeight = 'auto';
        clearInterval(checkAdLoaded);
      }
    }, 100);

    // 10초 후 타임아웃
    setTimeout(function() {
      clearInterval(checkAdLoaded);
      // 광고가 로드되지 않아도 최소 높이 유지 (CLS 방지)
    }, 10000);
  }

  // 모든 광고 요소 찾기 및 래핑
  function optimizeAds() {
    // Google AdSense 광고 요소 찾기
    const ads = document.querySelectorAll('ins.adsbygoogle, .adsbygoogle');
    
    ads.forEach(function(ad) {
      wrapAdInContainer(ad);
    });

    // 동적으로 추가된 광고도 처리
    if ('MutationObserver' in window) {
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === 1) { // Element node
              // 직접 추가된 광고
              if (node.classList && (node.classList.contains('adsbygoogle') || 
                  node.tagName === 'INS' && node.classList.contains('adsbygoogle'))) {
                wrapAdInContainer(node);
              }
              
              // 하위에 있는 광고
              const ads = node.querySelectorAll && node.querySelectorAll('ins.adsbygoogle, .adsbygoogle');
              if (ads) {
                ads.forEach(wrapAdInContainer);
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

  // 초기화
  function init() {
    // DOM 로드 완료 후 실행
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', optimizeAds);
    } else {
      optimizeAds();
    }

    // AdSense 스크립트 로드 후에도 실행
    if (window.adsbygoogle) {
      // 이미 로드된 경우
      setTimeout(optimizeAds, 1000);
    } else {
      // 로드 대기
      const checkAdSense = setInterval(function() {
        if (window.adsbygoogle) {
          clearInterval(checkAdSense);
          setTimeout(optimizeAds, 1000);
        }
      }, 100);

      // 5초 후 타임아웃
      setTimeout(function() {
        clearInterval(checkAdSense);
        optimizeAds(); // 타임아웃 후에도 실행
      }, 5000);
    }
  }

  // 초기화 실행
  init();
})();
