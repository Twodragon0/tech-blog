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
