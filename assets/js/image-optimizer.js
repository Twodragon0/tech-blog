// Image Optimization: CLS 최적화
// 이미지 크기 힌트를 설정하여 Cumulative Layout Shift 최소화

(function() {
  'use strict';

  // 이미지 크기 힌트 계산 (CLS 최적화)
  function setImageSizeHint(img) {
    // 입력 검증
    if (!img || typeof img !== 'object' || img.nodeType !== 1) {
      return;
    }
    
    // 이미 width/height가 있으면 스킵
    if (img.width && img.height && img.width > 0 && img.height > 0) {
      return;
    }
    
    // 부모 컨테이너 크기 기반으로 힌트 설정
    try {
      const container = img.closest && img.closest('.post-card-image, .post-image-container');
      if (container) {
        const containerWidth = container.offsetWidth || 400;
        const aspectRatio = 16 / 9; // 기본 aspect ratio
        const suggestedHeight = Math.round(containerWidth / aspectRatio);
        
        // width/height 속성 설정 (CLS 최적화)
        if (img.hasAttribute && !img.hasAttribute('width')) {
          img.setAttribute('width', containerWidth);
        }
        if (img.hasAttribute && !img.hasAttribute('height')) {
          img.setAttribute('height', suggestedHeight);
        }
      }
    } catch (e) {
      // 에러 발생 시 조용히 실패 (최적화는 선택사항)
      console.warn('[Image Optimizer] setImageSizeHint failed:', e);
    }
  }

  // 이미지 최적화 적용 (CLS 최적화만)
  function optimizeImage(img) {
    // 입력 검증: null/undefined 체크
    if (!img || typeof img !== 'object') {
      return;
    }

    // IMG 요소인지 확인
    if (img.nodeType !== 1 || img.tagName !== 'IMG') {
      return;
    }

    // 이미 처리된 이미지 스킵
    if (img.dataset && img.dataset.optimized === 'true') {
      return;
    }

    // CLS 최적화: 이미지 크기 힌트 설정
    try {
      setImageSizeHint(img);
      if (img.dataset) {
        img.dataset.optimized = 'true';
        img.dataset.format = 'original';
      }
    } catch (e) {
      // 에러 발생 시 조용히 계속 진행 (최적화는 선택사항)
      console.warn('[Image Optimizer] optimizeImage failed:', e);
      if (img.dataset) {
        img.dataset.optimized = 'true';
        img.dataset.format = 'original';
      }
    }
  }

  // 모든 이미지 최적화 (CLS 최적화 적용)
  function optimizeAllImages() {
    try {
      const images = document.querySelectorAll('img:not([data-optimized="true"])');

      images.forEach(function(img) {
        try {
          // 입력 검증
          if (!img || img.nodeType !== 1 || img.tagName !== 'IMG') {
            return;
          }

          // 모든 이미지에 CLS 최적화 적용
          if (img.complete) {
            optimizeImage(img);
          } else {
            img.addEventListener('load', function() {
              try {
                optimizeImage(img);
              } catch (e) {
                console.warn('[Image Optimizer] Failed to optimize image on load:', e);
              }
            }, { once: true });
          }
        } catch (e) {
          console.warn('[Image Optimizer] Failed to process image:', e);
        }
      });
    } catch (e) {
      console.warn('[Image Optimizer] optimizeAllImages failed:', e);
    }
  }

  // 초기화
  function init() {
    // DOM 로드 완료 후 실행
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        optimizeAllImages();
      });
    } else {
      optimizeAllImages();
    }

    // 동적으로 추가된 이미지도 처리
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
          if (node.nodeType === 1) { // Element node
            try {
              if (node.tagName === 'IMG') {
                optimizeImage(node);
              } else {
                const images = node.querySelectorAll && node.querySelectorAll('img');
                if (images && images.length > 0) {
                  images.forEach(function(img) {
                    try {
                      optimizeImage(img);
                    } catch (e) {
                      console.warn('[Image Optimizer] Failed to optimize image:', e);
                    }
                  });
                }
              }
            } catch (e) {
              console.warn('[Image Optimizer] Failed to process added node:', e);
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
