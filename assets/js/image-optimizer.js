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

    // Skip SVG - vector graphics don't benefit from WebP
    if (originalUrl.toLowerCase().endsWith('.svg')) {
      return null;
    }

    // WebP conversion is opt-in: only convert if the build pipeline
    // has generated .webp files. To enable, add a WebP generation step
    // to the CI/CD pipeline (e.g., using cwebp or sharp) and set
    // window.IMAGE_OPTIMIZER_WEBP_ENABLED = true in the page head.
    if (!window.IMAGE_OPTIMIZER_WEBP_ENABLED) {
      return null;
    }

    // Replace extension with .webp
    const webpUrl = originalUrl.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    return webpUrl;
  }

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

  // 이미지 최적화 적용
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

    // Early exit if WebP optimization is not enabled
    if (!window.IMAGE_OPTIMIZER_WEBP_ENABLED) {
      // Still apply CLS optimization
      setImageSizeHint(img);
      if (img.dataset) {
        img.dataset.optimized = 'true';
        img.dataset.format = 'original';
      }
      return;
    }

    // CLS 최적화: 이미지 크기 힌트 설정
    try {
      setImageSizeHint(img);
    } catch (e) {
      // 에러 발생 시 계속 진행 (최적화는 선택사항)
      console.warn('[Image Optimizer] setImageSizeHint failed:', e);
    }

    // WebP를 지원하는 경우에만 변환 시도
    try {
      if (supportsWebP()) {
        const originalSrc = img.src || (img.getAttribute && img.getAttribute('src'));
        
        // src가 없으면 스킵
        if (!originalSrc) {
          if (img.dataset) {
            img.dataset.optimized = 'true';
            img.dataset.format = 'original';
          }
          return;
        }
        
        const webpUrl = getWebPUrl(originalSrc);
        
        if (webpUrl && webpUrl !== originalSrc) {
          // WebP 이미지 로드 시도
          const webpImg = new Image();
          
          webpImg.onload = function() {
            try {
              // WebP 로드 성공
              img.src = webpUrl;
              if (img.dataset) {
                img.dataset.optimized = 'true';
                img.dataset.format = 'webp';
              }
              
              // CLS 최적화: 크기 힌트 재확인
              setImageSizeHint(img);
            } catch (e) {
              console.warn('[Image Optimizer] Failed to set WebP image:', e);
            }
          };
          
          webpImg.onerror = function() {
            try {
              // WebP 파일이 없으면 원본 유지 (조용히 처리 - 404는 정상)
              // 콘솔 에러를 방지하기 위해 아무것도 로깅하지 않음
              if (img.dataset) {
                img.dataset.optimized = 'true';
                img.dataset.format = 'original';
              }
              
              // CLS 최적화: 크기 힌트 재확인
              setImageSizeHint(img);
            } catch (e) {
              // 에러 발생 시 조용히 처리 (최적화는 선택사항)
              // 콘솔 에러를 방지하기 위해 아무것도 로깅하지 않음
              if (img.dataset) {
                img.dataset.optimized = 'true';
                img.dataset.format = 'original';
              }
            }
          };
          
          webpImg.src = webpUrl;
        } else {
          if (img.dataset) {
            img.dataset.optimized = 'true';
            img.dataset.format = 'original';
          }
          setImageSizeHint(img);
        }
      } else {
        // WebP 미지원 브라우저
        if (img.dataset) {
          img.dataset.optimized = 'true';
          img.dataset.format = 'original';
        }
        setImageSizeHint(img);
      }
    } catch (e) {
      // 에러 발생 시 원본 유지하고 로깅
      console.warn('[Image Optimizer] optimizeImage failed:', e);
      if (img.dataset) {
        img.dataset.optimized = 'true';
        img.dataset.format = 'original';
      }
    }
  }

  // 모든 이미지 최적화
  function optimizeAllImages() {
    try {
      const images = document.querySelectorAll('img:not([data-optimized="true"])');
      
      images.forEach(function(img) {
        try {
          // 입력 검증
          if (!img || img.nodeType !== 1 || img.tagName !== 'IMG') {
            return;
          }
          
          // Lazy loading 이미지는 Intersection Observer로 처리
          if (img.loading === 'lazy' || (img.dataset && img.dataset.src)) {
            return; // Lazy loading 로직에서 처리
          }
          
          // 즉시 로드되는 이미지만 최적화
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

  // Lazy loading 이미지 최적화
  function setupLazyImageOptimization() {
    if (!('IntersectionObserver' in window)) {
      return; // IntersectionObserver 미지원 브라우저
    }

    const imageObserver = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          
          // 입력 검증
          if (!img || img.nodeType !== 1 || img.tagName !== 'IMG') {
            observer.unobserve(img);
            return;
          }
          
          // Lazy loading 이미지 로드 후 최적화
          if (img.dataset && img.dataset.src) {
            const originalSrc = img.dataset.src;
            const webpUrl = getWebPUrl(originalSrc);
            
            if (supportsWebP() && webpUrl && webpUrl !== originalSrc) {
              // WebP 시도
              const webpImg = new Image();
              webpImg.onload = function() {
                try {
                  img.src = webpUrl;
                  if (img.removeAttribute) {
                    img.removeAttribute('data-src');
                  }
                  if (img.dataset) {
                    img.dataset.optimized = 'true';
                    img.dataset.format = 'webp';
                  }
                  observer.unobserve(img);
                } catch (e) {
                  console.warn('[Image Optimizer] Failed to set WebP for lazy image:', e);
                  observer.unobserve(img);
                }
              };
              webpImg.onerror = function() {
                try {
                  // WebP 실패 시 원본 사용 (조용히 처리 - 404는 정상)
                  // 콘솔 에러를 방지하기 위해 아무것도 로깅하지 않음
                  img.src = originalSrc;
                  if (img.removeAttribute) {
                    img.removeAttribute('data-src');
                  }
                  if (img.dataset) {
                    img.dataset.optimized = 'true';
                    img.dataset.format = 'original';
                  }
                  observer.unobserve(img);
                } catch (e) {
                  // 에러 발생 시 조용히 처리
                  // 콘솔 에러를 방지하기 위해 아무것도 로깅하지 않음
                  if (img.dataset) {
                    img.dataset.optimized = 'true';
                    img.dataset.format = 'original';
                  }
                  observer.unobserve(img);
                }
              };
              webpImg.src = webpUrl;
            } else {
              try {
                // WebP 미지원 또는 변환 불가
                img.src = originalSrc;
                if (img.removeAttribute) {
                  img.removeAttribute('data-src');
                }
                if (img.dataset) {
                  img.dataset.optimized = 'true';
                  img.dataset.format = 'original';
                }
                observer.unobserve(img);
              } catch (e) {
                console.warn('[Image Optimizer] Failed to set original lazy image:', e);
                observer.unobserve(img);
              }
            }
          } else {
            try {
              optimizeImage(img);
              observer.unobserve(img);
            } catch (e) {
              console.warn('[Image Optimizer] Failed to optimize lazy image:', e);
              observer.unobserve(img);
            }
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
