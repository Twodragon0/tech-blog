# Twodragon0's Tech Blog

**DevSecOps, DevOps, FinOps 전문 기술 블로그**

클라우드 보안, 인프라 자동화, 비용 최적화에 대한 실무 경험과 최신 트렌드를 공유합니다.

## 🎯 주요 주제

- **DevSecOps**: CI/CD 보안, SAST/DAST, 컨테이너 보안, 보안 자동화
- **DevOps**: 인프라 자동화, Kubernetes, 컨테이너 오케스트레이션, 모니터링
- **FinOps**: 클라우드 비용 최적화, 리소스 관리, 비용 거버넌스
- **Cloud Security**: AWS/GCP/Azure 보안 아키텍처, 보안 모범 사례
- **Security Incident Response**: 보안 사고 분석, Post-Mortem, 대응 전략

## 📁 구조

```
tech-blog/
├── _posts/          # 블로그 포스트 (Markdown)
├── _layouts/        # Jekyll 레이아웃 파일
├── _includes/        # 재사용 가능한 컴포넌트
├── assets/           # CSS, JS, 이미지 등 정적 파일
├── _config.yml       # Jekyll 설정 파일
└── Gemfile          # Ruby 의존성 관리
```

## 🚀 로컬 실행

```bash
# 의존성 설치
bundle install

# 로컬 서버 실행 (http://localhost:4000/tech-blog)
bundle exec jekyll serve
```

## 💬 댓글 시스템 (Giscus)

이 블로그는 [Giscus](https://giscus.app)를 사용하여 GitHub Discussions 기반 댓글 시스템을 제공합니다.

- **Repository**: [Twodragon0/tech-blog](https://github.com/Twodragon0/tech-blog)
- **Discussions**: [블로그 Discussions](https://github.com/Twodragon0/tech-blog/discussions)

## 🔄 자동 배포

GitHub Actions를 통해 자동으로 배포됩니다.

- **배포 URL**: https://twodragon0.github.io/tech-blog
- **워크플로우**: `.github/workflows/jekyll.yml`

## 🛠 기술 스택

- **Static Site Generator**: Jekyll 4.3
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions
- **Comments**: Giscus (GitHub Discussions)
- **Theme**: Custom (Minima 기반)

## 📝 라이선스

이 블로그의 모든 콘텐츠는 개인의 학습과 지식 공유를 목적으로 작성되었습니다.

## 🤝 기여

버그 리포트나 개선 제안은 [Issues](https://github.com/Twodragon0/tech-blog/issues)를 통해 제안해주세요.

## 🤖 AI 어시스턴트 활용 가이드

이 프로젝트는 Cursor, Claude 등 AI 어시스턴트를 활용한 콘텐츠 작성을 지원합니다.

### 주요 문서
- **`.cursorrules`**: Cursor AI 설정 및 프로젝트 규칙
- **`BEST_PRACTICES.md`**: 작업 가이드라인 및 모범 사례
- **`GEMINI_IMAGE_GUIDE.md`**: 이미지 생성 가이드
- **`POST_VISUALIZATION_CHECKLIST.md`**: 시각화 체크리스트

### AI 어시스턴트 활용 시
1. 포스트 작성 요청 시 제목, 카테고리, 태그, 핵심 내용을 명확히 전달
2. 코드 작성 요청 시 사용 기술 스택 및 보안 요구사항 명시
3. 이미지 생성 요청 시 `GEMINI_IMAGE_GUIDE.md`의 템플릿 참조
4. 모든 코드는 보안 모범 사례를 따르고 민감 정보 제거 필수

자세한 내용은 `.cursorrules` 및 `BEST_PRACTICES.md`를 참조하세요.
