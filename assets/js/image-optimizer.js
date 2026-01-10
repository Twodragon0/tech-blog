// Image Optimization: WebP Support with Fallback
// 자동으로 WebP 형식을 시도하고, 지원하지 않으면 원본 형식으로 fallback

(function() {
  'use strict';

  // WebP 지원 여부 확인
  function supportsWebP() {
    if (typeof window === 'undefined') return false;
    
    // 이미 확인한 경우 캐시 사용
    if (window.webpSupported !== undefined) {
      return window.webpSupported;
    }

    // Canvas를 사용한 WebP 지원 확인
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    
    try {
      const dataURL = canvas.toDataURL('image/webp');
      window.webpSupported = dataURL.indexOf('data:image/webp') === 0;
    } catch (e) {
      window.webpSupported = false;
    }
    
    return window.webpSupported;
  }

  // 이미지 경로를 WebP로 변환
  function getWebPUrl(originalUrl) {
    if (!originalUrl) return null;
    
    // 이미 WebP인 경우 그대로 반환
    if (originalUrl.toLowerCase().endsWith('.webp')) {
      return originalUrl;
    }

    // 확장자 교체
    const webpUrl = originalUrl.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    
    // 같은 디렉토리에 WebP 파일이 있다고 가정
    return webpUrl;
  }

  // 이미지 크기 힌트 계산 (CLS 최적화)
  function setImageSizeHint(img) {
    // 이미 width/height가 있으면 스킵
    if (img.width && img.height && img.width > 0 && img.height > 0) {
      return;
    }
    
    // 부모 컨테이너 크기 기반으로 힌트 설정
    const container = img.closest('.post-card-image, .post-image-container');
    if (container) {
      const containerWidth = container.offsetWidth || 400;
      const aspectRatio = 16 / 9; // 기본 aspect ratio
      const suggestedHeight = Math.round(containerWidth / aspectRatio);
      
      // width/height 속성 설정 (CLS 최적화)
      if (!img.hasAttribute('width')) {
        img.setAttribute('width', containerWidth);
      }
      if (!img.hasAttribute('height')) {
        img.setAttribute('height', suggestedHeight);
      }
    }
  }

  // 이미지 최적화 적용
  function optimizeImage(img) {
    // 이미 처리된 이미지 스킵
    if (img.dataset.optimized === 'true') {
      return;
    }

    // CLS 최적화: 이미지 크기 힌트 설정
    setImageSizeHint(img);

    // WebP를 지원하는 경우에만 변환 시도
    if (supportsWebP()) {
      const originalSrc = img.src || img.getAttribute('src');
      const webpUrl = getWebPUrl(originalSrc);
      
      if (webpUrl && webpUrl !== originalSrc) {
        // WebP 이미지 로드 시도
        const webpImg = new Image();
        
        webpImg.onload = function() {
          // WebP 로드 성공
          img.src = webpUrl;
          img.dataset.optimized = 'true';
          img.dataset.format = 'webp';
          
          // CLS 최적화: 크기 힌트 재확인
          setImageSizeHint(img);
        };
        
        webpImg.onerror = function() {
          // WebP 파일이 없으면 원본 유지
          img.dataset.optimized = 'true';
          img.dataset.format = 'original';
          
          // CLS 최적화: 크기 힌트 재확인
          setImageSizeHint(img);
        };
        
        webpImg.src = webpUrl;
      } else {
        img.dataset.optimized = 'true';
        img.dataset.format = 'original';
        setImageSizeHint(img);
      }
    } else {
      // WebP 미지원 브라우저
      img.dataset.optimized = 'true';
      img.dataset.format = 'original';
      setImageSizeHint(img);
    }
  }

  // 모든 이미지 최적화
  function optimizeAllImages() {
    const images = document.querySelectorAll('img:not([data-optimized="true"])');
    
    images.forEach(function(img) {
      // Lazy loading 이미지는 Intersection Observer로 처리
      if (img.loading === 'lazy' || img.dataset.src) {
        return; // Lazy loading 로직에서 처리
      }
      
      // 즉시 로드되는 이미지만 최적화
      if (img.complete) {
        optimizeImage(img);
      } else {
        img.addEventListener('load', function() {
          optimizeImage(img);
        }, { once: true });
      }
    });
  }

  // Lazy loading 이미지 최적화
  function setupLazyImageOptimization() {
    if (!('IntersectionObserver' in window)) {
      return; // IntersectionObserver 미지원 브라우저
    }

    const imageObserver = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          
          // Lazy loading 이미지 로드 후 최적화
          if (img.dataset.src) {
            const originalSrc = img.dataset.src;
            const webpUrl = getWebPUrl(originalSrc);
            
            if (supportsWebP() && webpUrl && webpUrl !== originalSrc) {
              // WebP 시도
              const webpImg = new Image();
              webpImg.onload = function() {
                img.src = webpUrl;
                img.removeAttribute('data-src');
                img.dataset.optimized = 'true';
                img.dataset.format = 'webp';
                observer.unobserve(img);
              };
              webpImg.onerror = function() {
                // WebP 실패 시 원본 사용
                img.src = originalSrc;
                img.removeAttribute('data-src');
                img.dataset.optimized = 'true';
                img.dataset.format = 'original';
                observer.unobserve(img);
              };
              webpImg.src = webpUrl;
            } else {
              // WebP 미지원 또는 변환 불가
              img.src = originalSrc;
              img.removeAttribute('data-src');
              img.dataset.optimized = 'true';
              img.dataset.format = 'original';
              observer.unobserve(img);
            }
          } else {
            optimizeImage(img);
            observer.unobserve(img);
          }
        }
      });
    }, {
      rootMargin: '50px' // 50px 전에 미리 로드
    });

    // Lazy loading 이미지 관찰 시작
    document.querySelectorAll('img[loading="lazy"], img[data-src]').forEach(function(img) {
      imageObserver.observe(img);
    });
  }

  // 초기화
  function init() {
    // DOM 로드 완료 후 실행
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        optimizeAllImages();
        setupLazyImageOptimization();
      });
    } else {
      optimizeAllImages();
      setupLazyImageOptimization();
    }

    // 동적으로 추가된 이미지도 처리
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
          if (node.nodeType === 1) { // Element node
            if (node.tagName === 'IMG') {
              optimizeImage(node);
            } else {
              const images = node.querySelectorAll && node.querySelectorAll('img');
              if (images) {
                images.forEach(optimizeImage);
              }
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

  // 초기화 실행
  init();
})();
