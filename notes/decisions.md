# Decisions

아키텍처와 디자인 결정을 기록합니다.

## 2026-02

- **Vercel + GitHub Pages 이중 배포**: Vercel 메인, GitHub Pages 백업
- **Giscus 댓글**: GitHub Discussions 기반, 별도 DB 불필요
- **DeepSeek Chatbot**: 비용 효율적인 AI 챗봇 (Context Caching 활용)

## 2026-03

- **ai-summary-card 인라인 변환**: 외부 include 대신 Jekyll include 방식으로 통일 (PR-67)
- **포스트 제목 한국어화**: 영문 제목을 한국어로 전환하여 SEO/가독성 향상 (PR-68)
- **SVG 이미지 차별화**: 날짜별 SVG에 고유 레이아웃/색상 적용 (타임라인 vs 대시보드)
- **API Prisma 동적 import**: DB 미설정 환경에서도 graceful 503 응답하도록 변경
- **스크립트 정리 정책**: 완료된 마이그레이션/중복 스크립트는 `scripts/_archive/`로 이동
- **모델명 통일**: 문서 전체를 Opus 4.6 / Sonnet 4.6으로 일괄 업데이트

## 2026-05

- **summary_card frontmatter (Option A) 단일 형식 채택**: ai-summary-card include의 attribute 6개(title/categories_html/tags_html/highlights_html/period/audience)를 post frontmatter의 `summary_card:` YAML 블록으로 이전, body는 `{% include ai-summary-card.html %}` 단일 라인. 모든 168 posts 적용 완료.
  - **Why**: 두 render 경로(`page.summary_card` vs `include.*` attrs)가 공존하면서 YAML escape, ASCII apostrophe, 분리자 호환성 등 다층 회귀 발생. 단일 데이터 소스(YAML)로 통일하여 escape는 Jekyll filter(`| escape`)에 위임.
  - **호환성 분리자 게이트**: `migrate_summary_cards_to_frontmatter.py`의 `_is_separator_compatible`는 byte-identity 보존을 위해 `\n      ` separator만 허용. `unify_ai_summary_block.py` 출력(' ' 또는 '\n')을 가진 36개 posts는 `--allow-separator-divergence` flag로 우회 마이그레이션 (cosmetic-only HTML whitespace delta 수용).
  - **신규 publish 경로**: `scripts/news/content_generator.py`가 처음부터 Option A YAML을 emit하도록 변경 — `_emit_summary_card_yaml()` helper 추가, security/tech-blog 양쪽 mode 변경.
  - **Idempotency guard**: `scripts/unify_ai_summary_block.py`에 frontmatter `summary_card:` 존재 시 skip하는 가드 추가 — 향후 normalize 패스가 풍부한 highlights 데이터를 `포인트 N` placeholder로 덮어쓰는 회귀 방지.
  - **Regression guard**: `scripts/tests/test_post_summary_card_format.py`에서 모든 _posts/가 bare include + summary_card frontmatter를 사용하는지 자동 검증.
