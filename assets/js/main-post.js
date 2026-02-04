// Modern UI/UX JavaScript for Tech Blog - Post Features
// Build: 2026-02-04 - Split optimization (main-post.js)
// Loaded conditionally on post pages only

(function() {
  'use strict';

  // Wait for utilities from main-core.js
  const scheduleIdleWork = window.TechBlog?.scheduleIdleWork || ((cb) => setTimeout(cb, 1));
  const yieldToMain = window.TechBlog?.yieldToMain || (() => new Promise(r => setTimeout(r, 0)));

  // ============================================
  // Reading Progress Bar
  // ============================================

  // Reading Progress Bar (for post pages)
  const postArticle = document.querySelector('.post-article');
  if (postArticle) {
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--color-primary), var(--color-devsecops));
      width: 0%;
      z-index: 9999;
      transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    // Use passive listener for scroll events (improves FID)
    window.addEventListener('scroll', function() {
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const progress = (scrollTop / (documentHeight - windowHeight)) * 100;
      progressBar.style.width = Math.min(progress, 100) + '%';
    }, { passive: true });
  }

  // ============================================
  // Code Block Enhancement with Copy Button
  // ============================================

  // Enhanced Code Block with Language Label and Copy Button
  // Use a Set to track processed code blocks and prevent duplicates
  const processedBlocks = new Set();
  
  // Only process .highlight divs to avoid duplicates
  document.querySelectorAll('.highlight').forEach(highlightDiv => {
    // Skip if already processed
    if (processedBlocks.has(highlightDiv)) {
      return;
    }
    
    // Mark as processed
    processedBlocks.add(highlightDiv);
    
    const pre = highlightDiv.querySelector('pre');
    const codeBlock = pre ? pre.querySelector('code') : null;
    
    if (!codeBlock || !pre) return;

    // Detect language from class names
    // Rouge typically adds classes like: .highlight.python, .highlight .language-python, etc.
    let language = 'code';
    
    // Priority order: highlight div > pre > code
    const highlightClasses = Array.from(highlightDiv.classList);
    const preClasses = Array.from(pre.classList);
    const codeClasses = Array.from(codeBlock.classList);
    
    // Check for Mermaid first (special handling needed)
    const isMermaid = highlightClasses.some(cls => cls === 'mermaid' || cls === 'language-mermaid') ||
                     preClasses.some(cls => cls === 'mermaid' || cls === 'language-mermaid') ||
                     codeClasses.some(cls => cls === 'mermaid' || cls === 'language-mermaid' || cls.startsWith('language-mermaid'));
    
    if (isMermaid) {
      language = 'MERMAID';
    } else {
      // Check highlight div classes first (Rouge often adds language class here)
      let langMatch = highlightClasses.find(cls => 
        cls !== 'highlight' && 
        /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
      );
      
      if (!langMatch) {
        // Check pre element classes
        langMatch = preClasses.find(cls => 
          cls !== 'highlight' && 
          /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
        );
      }
      
      if (!langMatch) {
        // Check code element classes (most common: language-xxx)
        langMatch = codeClasses.find(cls => 
          cls.startsWith('language-') || 
          /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
        );
        
        if (langMatch && langMatch.startsWith('language-')) {
          language = langMatch.replace('language-', '').toUpperCase();
        } else if (langMatch) {
          language = langMatch.toUpperCase();
        }
      } else {
        language = langMatch.toUpperCase();
      }
    }

    // Language name mapping for better display
    const langMap = {
      'PYTHON': 'Python',
      'JAVASCRIPT': 'JavaScript',
      'JS': 'JavaScript',
      'BASH': 'Bash',
      'SH': 'Shell',
      'YAML': 'YAML',
      'YML': 'YAML',
      'JSON': 'JSON',
      'HTML': 'HTML',
      'CSS': 'CSS',
      'SQL': 'SQL',
      'GO': 'Go',
      'RUST': 'Rust',
      'JAVA': 'Java',
      'PHP': 'PHP',
      'RUBY': 'Ruby',
      'TYPESCRIPT': 'TypeScript',
      'TS': 'TypeScript',
      'DOCKERFILE': 'Dockerfile',
      'DOCKER': 'Docker',
      'MAKEFILE': 'Makefile',
      'MAKE': 'Make',
      'MARKDOWN': 'Markdown',
      'MD': 'Markdown',
      'XML': 'XML',
      'INI': 'INI',
      'TOML': 'TOML',
      'PROPERTIES': 'Properties',
      'CONF': 'Config',
      'CONFIG': 'Config',
      'MERMAID': 'Mermaid'
    };
    
    const displayLang = langMap[language] || language;

    // Set language attribute for CSS
    highlightDiv.setAttribute('data-lang', displayLang);
    
    // Mark Mermaid blocks for special handling
    if (isMermaid) {
      highlightDiv.classList.add('mermaid-block');
    }
    
    // Ensure highlight div is positioned relatively
    if (!highlightDiv.style.position) {
      highlightDiv.style.position = 'relative';
    }

    // Ensure pre element is positioned relatively for button positioning
    if (!pre.style.position) {
      pre.style.position = 'relative';
    }

    // Create copy button with improved UI/UX
    const button = document.createElement('button');
    button.className = 'copy-code-btn';
    if (isMermaid) {
      button.classList.add('mermaid-copy-btn');
    }
    button.setAttribute('aria-label', 'Copy code to clipboard');
    button.setAttribute('type', 'button');
    button.setAttribute('title', 'Copy');
    button.innerHTML = `
      <svg class="copy-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
    `;

    // Append button to highlight div (positioned at top-right via CSS)
    highlightDiv.appendChild(button);

    // Store original code text for Mermaid blocks (before rendering)
    const originalCodeText = codeBlock.textContent || codeBlock.innerText;

    // Copy functionality with visual feedback
    button.addEventListener('click', async (e) => {
      e.stopPropagation();
      e.preventDefault();

      // For Mermaid blocks, use original code text; for others, use current text
      let textToCopy = isMermaid ? originalCodeText : (codeBlock.textContent || codeBlock.innerText || originalCodeText);

      const copyIcon = button.querySelector('.copy-icon');
      const checkIcon = button.querySelector('.check-icon');

      try {
        await navigator.clipboard.writeText(textToCopy);

        // Visual feedback - show check icon
        button.classList.add('copied');
        if (copyIcon) copyIcon.style.display = 'none';
        if (checkIcon) checkIcon.style.display = 'block';
        button.setAttribute('title', 'Copied!');

        setTimeout(() => {
          button.classList.remove('copied');
          if (copyIcon) copyIcon.style.display = 'block';
          if (checkIcon) checkIcon.style.display = 'none';
          button.setAttribute('title', 'Copy');
        }, 2000);
      } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
          document.execCommand('copy');
          button.classList.add('copied');
          if (copyIcon) copyIcon.style.display = 'none';
          if (checkIcon) checkIcon.style.display = 'block';
          button.setAttribute('title', 'Copied!');
          setTimeout(() => {
            button.classList.remove('copied');
            if (copyIcon) copyIcon.style.display = 'block';
            if (checkIcon) checkIcon.style.display = 'none';
            button.setAttribute('title', 'Copy');
          }, 2000);
        } catch (fallbackErr) {
          button.classList.add('error');
          button.setAttribute('title', 'Failed to copy');
          setTimeout(() => {
            button.classList.remove('error');
            button.setAttribute('title', 'Copy');
          }, 2000);
        }
        document.body.removeChild(textArea);
      }
    });
  });
  
  // Also handle standalone pre code blocks (not wrapped in .highlight)
  document.querySelectorAll('pre code').forEach(codeBlock => {
    const pre = codeBlock.parentElement;
    if (pre.tagName === 'PRE' && !pre.closest('.highlight')) {
      // Check if already processed
      if (processedBlocks.has(pre)) {
        return;
      }
      processedBlocks.add(pre);
      
      // Wrap in highlight div
      const highlightDiv = document.createElement('div');
      highlightDiv.className = 'highlight';
      pre.parentNode.insertBefore(highlightDiv, pre);
      highlightDiv.appendChild(pre);
      
      // Process the newly created highlight div
      const newPre = highlightDiv.querySelector('pre');
      const newCodeBlock = newPre ? newPre.querySelector('code') : null;
      
      if (newCodeBlock && newPre) {
        // Detect language for language badge display
        let language = 'code';
        const codeClasses = Array.from(newCodeBlock.classList);
        const langMatch = codeClasses.find(cls => 
          cls.startsWith('language-') || 
          /^(python|javascript|js|bash|sh|yaml|yml|json|html|css|sql|go|rust|java|php|ruby|typescript|ts|dockerfile|docker|makefile|make|markdown|md|xml|ini|toml|properties|conf|config|text|plain)$/i.test(cls)
        );
        
        if (langMatch) {
          language = langMatch.replace('language-', '').toUpperCase();
        }
        
        const langMap = {
          'PYTHON': 'Python', 'JAVASCRIPT': 'JavaScript', 'JS': 'JavaScript',
          'BASH': 'Bash', 'SH': 'Shell', 'YAML': 'YAML', 'YML': 'YAML',
          'JSON': 'JSON', 'HTML': 'HTML', 'CSS': 'CSS', 'SQL': 'SQL',
          'GO': 'Go', 'RUST': 'Rust', 'JAVA': 'Java', 'PHP': 'PHP',
          'RUBY': 'Ruby', 'TYPESCRIPT': 'TypeScript', 'TS': 'TypeScript',
          'DOCKERFILE': 'Dockerfile', 'DOCKER': 'Docker', 'MAKEFILE': 'Makefile',
          'MAKE': 'Make', 'MARKDOWN': 'Markdown', 'MD': 'Markdown',
          'XML': 'XML', 'INI': 'INI', 'TOML': 'TOML', 'PROPERTIES': 'Properties',
          'CONF': 'Config', 'CONFIG': 'Config'
        };
        
        const displayLang = langMap[language] || language;
        highlightDiv.setAttribute('data-lang', displayLang);
        highlightDiv.style.position = 'relative';

        // Create copy button for standalone code blocks
        const button = document.createElement('button');
        button.className = 'copy-code-btn';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.setAttribute('type', 'button');
        button.setAttribute('title', 'Copy');
        button.innerHTML = `
          <svg class="copy-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <svg class="check-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display:none">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;

        highlightDiv.appendChild(button);

        button.addEventListener('click', async (e) => {
          e.stopPropagation();
          e.preventDefault();
          const text = newCodeBlock.textContent || newCodeBlock.innerText;
          const copyIcon = button.querySelector('.copy-icon');
          const checkIcon = button.querySelector('.check-icon');

          try {
            await navigator.clipboard.writeText(text);
            button.classList.add('copied');
            if (copyIcon) copyIcon.style.display = 'none';
            if (checkIcon) checkIcon.style.display = 'block';
            button.setAttribute('title', 'Copied!');
            setTimeout(() => {
              button.classList.remove('copied');
              if (copyIcon) copyIcon.style.display = 'block';
              if (checkIcon) checkIcon.style.display = 'none';
              button.setAttribute('title', 'Copy');
            }, 2000);
          } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-9999px';
            document.body.appendChild(textArea);
            textArea.select();
            try {
              document.execCommand('copy');
              button.classList.add('copied');
              if (copyIcon) copyIcon.style.display = 'none';
              if (checkIcon) checkIcon.style.display = 'block';
              button.setAttribute('title', 'Copied!');
              setTimeout(() => {
                button.classList.remove('copied');
                if (copyIcon) copyIcon.style.display = 'block';
                if (checkIcon) checkIcon.style.display = 'none';
                button.setAttribute('title', 'Copy');
              }, 2000);
            } catch (fallbackErr) {
              button.classList.add('error');
              button.setAttribute('title', 'Failed to copy');
              setTimeout(() => {
                button.classList.remove('error');
                button.setAttribute('title', 'Copy');
              }, 2000);
            }
            document.body.removeChild(textArea);
          }
        });
      }
    }
  });

  // ============================================
  // Table Wrapper for Mobile Responsiveness
  // ============================================

    // Table wrapper for mobile responsiveness with enhanced scroll UX
    (function initTableWrapper() {
      'use strict';
      
      // 스크롤 타이머 ID 저장용
      const scrollTimers = new WeakMap();
      
      // 테이블 래퍼 생성 및 스크롤 이벤트 설정
      const wrapTables = () => {
        const postContent = document.querySelector('.post-content');
        if (!postContent) return;
        
        const tables = postContent.querySelectorAll('table:not(.chat-table)');
        tables.forEach(table => {
          // 이미 래퍼로 감싸져 있으면 스킵
          if (table.parentElement && table.parentElement.classList.contains('table-wrapper')) {
            // 이미 래퍼가 있으면 스크롤 이벤트만 설정
            setupScrollBehavior(table.parentElement);
            return;
          }
          
          // 래퍼 생성
          const wrapper = document.createElement('div');
          wrapper.className = 'table-wrapper';
          
          // 테이블을 래퍼로 이동
          table.parentNode.insertBefore(wrapper, table);
          wrapper.appendChild(table);
          
          // 스크롤 동작 설정
          setupScrollBehavior(wrapper);
        });
      };
      
      // 스크롤 동작 설정 (스크롤 힌트 숨기기/보이기)
      const setupScrollBehavior = (wrapper) => {
        // 이미 설정된 경우 스킵
        if (wrapper.dataset.scrollSetup === 'true') return;
        wrapper.dataset.scrollSetup = 'true';
        
        let scrollTimeout;
        
        // 스크롤 시작 시 힌트 숨김 - passive for better FID
        wrapper.addEventListener('scroll', () => {
          // 스크롤 중 표시
          wrapper.classList.add('is-scrolling');

          // 기존 타이머 클리어
          if (scrollTimeout) {
            clearTimeout(scrollTimeout);
          }

          // 스크롤 종료 후 1.5초 뒤 힌트 다시 표시
          scrollTimeout = setTimeout(() => {
            wrapper.classList.remove('is-scrolling');
          }, 1500);
        }, { passive: true });
        
        // 터치 시작 시 힌트 숨김
        wrapper.addEventListener('touchstart', () => {
          wrapper.classList.add('is-scrolling');
        }, { passive: true });
        
        // 터치 종료 후 힌트 다시 표시
        wrapper.addEventListener('touchend', () => {
          if (scrollTimeout) {
            clearTimeout(scrollTimeout);
          }
          scrollTimeout = setTimeout(() => {
            wrapper.classList.remove('is-scrolling');
          }, 1500);
        }, { passive: true });
        
        // 초기 상태: 스크롤 가능 여부 확인 후 힌트 표시/숨김
        const checkScrollable = () => {
          const isScrollable = wrapper.scrollWidth > wrapper.clientWidth;
          if (!isScrollable) {
            wrapper.classList.add('no-scroll-hint');
          } else {
            wrapper.classList.remove('no-scroll-hint');
          }
        };
        
        // 초기 체크 (약간 지연)
        setTimeout(checkScrollable, 100);
        
        // 리사이즈 시 재체크
        window.addEventListener('resize', () => {
          clearTimeout(scrollTimers.get(wrapper));
          scrollTimers.set(wrapper, setTimeout(checkScrollable, 200));
        }, { passive: true });
      };
      
      // 초기 실행
      wrapTables();
      
      // 동적으로 추가된 콘텐츠를 위한 MutationObserver
      const observer = new MutationObserver((mutations) => {
        let shouldWrap = false;
        mutations.forEach((mutation) => {
          if (mutation.addedNodes.length > 0) {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === 1) { // Element node
                if (node.tagName === 'TABLE' || node.querySelector('table')) {
                  shouldWrap = true;
                }
              }
            });
          }
        });
        
        if (shouldWrap) {
          wrapTables();
        }
      });
      
      const postContent = document.querySelector('.post-content');
      if (postContent) {
        observer.observe(postContent, {
          childList: true,
          subtree: true
        });
      }
    })();

  // ============================================
  // Korean Image Filename URL Encoding Fix
  // ============================================

    /**
     * 경로를 안전하게 검증하고 정제합니다 (XSS 방지)
     * @param {string} path - 검증할 경로
     * @returns {string|null} - 정제된 경로 또는 null (안전하지 않은 경우)
     */
    function sanitizeImagePath(path) {
      if (!path || typeof path !== 'string') {
        return null;
      }
      
      // 위험한 프로토콜 제거 (javascript:, data:, vbscript: 등)
      const dangerousProtocols = /^(javascript|data|vbscript|file|about|chrome):/i;
      if (dangerousProtocols.test(path.trim())) {
        return null;
      }
      
      // HTML 태그나 스크립트 태그 제거
      if (/<[^>]*>/i.test(path)) {
        return null;
      }
      
      // 경로 정규화: 상대 경로 또는 절대 경로만 허용
      // 허용되는 패턴: /path/to/file, ./path, ../path, path/to/file
      const trimmedPath = path.trim();
      
      // 절대 경로인 경우 (/)로 시작
      if (trimmedPath.startsWith('/')) {
        // assets/images로 시작하는 경로만 허용 (보안 강화)
        if (trimmedPath.startsWith('/assets/images/') || 
            trimmedPath.startsWith('/assets/') ||
            trimmedPath.startsWith('/images/')) {
          // 경로에서 위험한 문자 제거
          const sanitized = trimmedPath.replace(/[<>"']/g, '');
          return sanitized;
        }
        return null;
      }
      
      // 상대 경로인 경우
      if (trimmedPath.startsWith('./') || trimmedPath.startsWith('../') || 
          !trimmedPath.includes('://')) {
        // 경로에서 위험한 문자 제거
        const sanitized = trimmedPath.replace(/[<>"']/g, '');
        return sanitized;
      }
      
      // 외부 URL은 허용하지 않음 (보안 정책)
      return null;
    }
    
    function fixImageUrls() {
      const images = document.querySelectorAll('img.post-image, img[src*="assets/images"], img.clickable-image');
      images.forEach(img => {
        const src = img.getAttribute('src');
        const dataFullSrc = img.getAttribute('data-full-src');
        const dataOriginalSrc = img.getAttribute('data-original-src');
        let retryCount = 0;
        const maxRetries = 4;
        
        // 이미지 로드 전에 경로를 미리 수정 - 디코딩된 경로를 먼저 시도
        if (src && !img.complete) {
          try {
            // URL 인코딩된 경로를 디코딩
            const decodedSrc = decodeURIComponent(src);
            
            // 디코딩된 경로에 한글이 있으면, 디코딩된 경로(한글 파일명)로 먼저 시도
            if (decodedSrc !== src && /[가-힣]/.test(decodedSrc)) {
              // 서버가 한글 파일명을 직접 처리할 수 있는 경우를 위해 디코딩된 경로로 먼저 시도
              const sanitized = sanitizeImagePath(decodedSrc);
              if (sanitized) {
                img.src = sanitized;
                if (dataFullSrc) {
                  img.setAttribute('data-full-src', sanitized);
                }
              }
            }
          } catch (e) {
            // 디코딩 실패 시 원본 유지
          }
        }
        
        // 이미지 로드 실패 시 여러 방법으로 재시도
        img.addEventListener('error', function() {
          if (retryCount >= maxRetries) {
            // 모든 재시도 실패 시 조용히 처리
            return;
          }
          
          retryCount++;
          const currentSrc = this.getAttribute('src');
          
          // 방법 1: URL 인코딩된 경로를 완전히 디코딩하여 한글 파일명으로 변환
          if (retryCount === 1) {
            try {
              const decodedSrc = decodeURIComponent(currentSrc);
              if (decodedSrc !== currentSrc && /[가-힣]/.test(decodedSrc)) {
                // 디코딩된 경로로 재시도 (서버가 한글 파일명을 직접 처리할 수 있는 경우)
                const sanitized = sanitizeImagePath(decodedSrc);
                if (sanitized) {
                  this.src = sanitized;
                  if (dataFullSrc) {
                    this.setAttribute('data-full-src', sanitized);
                  }
                  return;
                }
              }
            } catch (e) {
              // 디코딩 실패
            }
          }
          
          // 방법 2: data-original-src가 있으면 원본 경로로 재시도
          if (retryCount === 2 && dataOriginalSrc) {
            // 원본 경로를 그대로 사용 (Jekyll이 생성한 경로)
            const originalPath = dataOriginalSrc.startsWith('/') ? dataOriginalSrc : '/' + dataOriginalSrc;
            const sanitized = sanitizeImagePath(originalPath);
            if (sanitized) {
              this.src = sanitized;
              if (dataFullSrc) {
                this.setAttribute('data-full-src', sanitized);
              }
              return;
            }
          }
          
          // 방법 3: 경로를 분해하여 파일명만 다시 인코딩
          if (retryCount === 3) {
            try {
              const decodedSrc = decodeURIComponent(currentSrc);
              const pathParts = decodedSrc.split('/');
              const filename = pathParts[pathParts.length - 1];
              
              if (filename && /[가-힣]/.test(filename)) {
                // 파일명만 다시 인코딩 (경로는 그대로)
                const encodedFilename = encodeURIComponent(filename);
                pathParts[pathParts.length - 1] = encodedFilename;
                const newSrc = pathParts.join('/');
                const sanitized = sanitizeImagePath(newSrc);
                if (sanitized) {
                  this.src = sanitized;
                  if (dataFullSrc) {
                    this.setAttribute('data-full-src', sanitized);
                  }
                  return;
                }
              }
            } catch (e) {
              // 처리 실패
            }
          }
          
          // 방법 4: data-original-src를 기반으로 상대 경로 재구성
          if (retryCount === 4 && dataOriginalSrc) {
            try {
              // 원본 경로에서 파일명만 추출하여 디코딩된 경로로 재구성
              const pathParts = dataOriginalSrc.split('/');
              const filename = pathParts[pathParts.length - 1];
              if (filename && /[가-힣]/.test(filename)) {
                // 파일명이 한글이면 디코딩된 경로로 재구성
                pathParts[pathParts.length - 1] = filename;
                const newSrc = pathParts.join('/');
                const finalPath = newSrc.startsWith('/') ? newSrc : '/' + newSrc;
                const sanitized = sanitizeImagePath(finalPath);
                if (sanitized) {
                  this.src = sanitized;
                  if (dataFullSrc) {
                    this.setAttribute('data-full-src', sanitized);
                  }
                }
              }
            } catch (e) {
              // 처리 실패
            }
          }
        }, { once: false });
      });
    }

  // DOM 로드 후 실행 (defer to idle time)
  scheduleIdleWork(() => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fixImageUrls);
    } else {
      fixImageUrls();
    }

    // 동적으로 추가된 이미지도 처리
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
          fixImageUrls();
        }
      });
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  });

  console.debug('Tech Blog Post Features initialized');
})();
