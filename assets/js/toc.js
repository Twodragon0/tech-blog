// Table of Contents (TOC) functionality
// Handles TOC expand/collapse, smooth scrolling, and active section highlighting

(function() {
  const tocToggle = document.getElementById('toc-toggle');
  const tocContent = document.getElementById('toc-content');
  const tocCount = document.getElementById('toc-count');
  const tocItems = document.querySelectorAll('.toc-card-item');

  if (!tocToggle || !tocContent) return;

  // 항목 수 표시
  if (tocCount && tocItems.length > 0) {
    tocCount.textContent = tocItems.length + '개 섹션';
  }

  // 기본 설정
  const maxPreview = 6;
  let isExpanded = false;

  // 6개 초과 시 일부만 표시, 아니면 버튼 숨김
  if (tocItems.length > maxPreview) {
    tocItems.forEach((item, index) => {
      if (index >= maxPreview) {
        item.classList.add('toc-hidden');
      }
    });
    tocToggle.querySelector('.btn-text').textContent = '+' + (tocItems.length - maxPreview) + ' 더보기';
  } else {
    tocToggle.style.display = 'none';
  }

  // 토글 버튼 클릭
  tocToggle.addEventListener('click', function() {
    isExpanded = !isExpanded;

    if (isExpanded) {
      // 전체 펼치기
      tocItems.forEach(item => item.classList.remove('toc-hidden'));
      tocToggle.querySelector('.btn-text').textContent = '접기';
      tocToggle.classList.add('expanded');
    } else {
      // 접기
      if (tocItems.length > maxPreview) {
        tocItems.forEach((item, index) => {
          if (index >= maxPreview) {
            item.classList.add('toc-hidden');
          }
        });
        tocToggle.querySelector('.btn-text').textContent = '+' + (tocItems.length - maxPreview) + ' 더보기';
      }
      tocToggle.classList.remove('expanded');
    }
  });

  // Update TOC links after headings get IDs
  function updateTocLinks() {
    const tocLinks = document.querySelectorAll('.toc-card-item');
    tocLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (!href || href === '#') return;

      const targetId = href.substring(1);
      const targetEl = document.getElementById(targetId);

      if (!targetEl) {
        const linkText = link.textContent.trim();
        const headings = document.querySelectorAll('.post-content h2');

        headings.forEach(heading => {
          const headingText = heading.textContent.trim().replace(/^#+\s*/, '');
          if (headingText === linkText && heading.id) {
            link.setAttribute('href', '#' + heading.id);
          }
        });
      }
    });
  }

  setTimeout(updateTocLinks, 100);
  setTimeout(updateTocLinks, 500);

  // 스무스 스크롤
  document.querySelectorAll('.toc-card-item').forEach(link => {
    link.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (!href || href === '#') return;

      const targetId = href.substring(1);
      let targetEl = document.getElementById(targetId);

      if (!targetEl) {
        const linkText = this.textContent.trim();
        const headings = document.querySelectorAll('.post-content h2');

        headings.forEach(heading => {
          const headingText = heading.textContent.trim().replace(/^#+\s*/, '');
          if (headingText === linkText) {
            targetEl = heading;
          }
        });
      }

      if (targetEl) {
        e.preventDefault();
        const headerHeight = document.querySelector('.site-header')?.offsetHeight || 70;
        const targetPosition = targetEl.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
        history.pushState(null, null, '#' + (targetEl.id || targetId));
      }
    });
  });

  // 스크롤 시 현재 섹션 하이라이트
  let ticking = false;
  window.addEventListener('scroll', function() {
    if (!ticking) {
      requestAnimationFrame(function() {
        highlightCurrentSection();
        ticking = false;
      });
      ticking = true;
    }
  });

  function highlightCurrentSection() {
    const scrollPosition = window.pageYOffset + 100;

    tocItems.forEach(item => {
      const href = item.getAttribute('href');
      if (!href) return;

      const targetId = href.substring(1);
      let section = document.getElementById(targetId);

      if (!section) {
        const linkText = item.textContent.trim();
        const headings = document.querySelectorAll('.post-content h2');

        headings.forEach(heading => {
          const headingText = heading.textContent.trim().replace(/^#+\s*/, '');
          if (headingText === linkText) {
            section = heading;
          }
        });
      }

      if (section) {
        const sectionTop = section.offsetTop;
        const sectionBottom = sectionTop + section.offsetHeight;

        if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
          tocItems.forEach(i => i.classList.remove('active'));
          item.classList.add('active');
        }
      }
    });
  }

  highlightCurrentSection();
})();
