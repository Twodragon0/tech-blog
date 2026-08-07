# 기여 가이드 (Contributing)

이 저장소는 [Twodragon's Tech Blog](https://tech.2twodragon.com)의 소스입니다.
Jekyll 기반 정적 사이트이며, 콘텐츠(`_posts/`)와 자동화 스크립트(`scripts/`)가
같은 저장소에서 관리됩니다.

기여 전에 [행동 강령](CODE_OF_CONDUCT.md)과 [보안 정책](SECURITY.md)을 읽어주세요.

---

## 1. 어떤 기여를 환영하나요

| 유형 | 채널 | 비고 |
| :--- | :--- | :--- |
| 포스트 오탈자·사실 오류 정정 | [이슈](../../issues/new?template=post_correction.yml) 또는 PR | 가장 환영합니다 |
| 깨진 링크·이미지 신고 | [버그 리포트](../../issues/new?template=bug_report.yml) | |
| 사이트 버그 (렌더링, 다크모드, 접근성) | [버그 리포트](../../issues/new?template=bug_report.yml) | 재현 절차 필수 |
| 자동화 스크립트 개선 | PR | 테스트 동반 필수 (§5) |
| 새 포스트 주제 제안 | [토론](../../discussions) | |
| **보안 취약점** | **이슈 금지.** [SECURITY.md](SECURITY.md) 절차 | 비공개 신고 |

> 포스트 본문의 **논조·의견**은 저자 개인의 것입니다. 사실 관계 오류가 아닌
> 관점 차이는 이슈보다 토론(Discussions)이 적합합니다.

---

## 2. 개발 환경 준비

```bash
# 1) 저장소 클론
git clone https://github.com/Twodragon0/tech-blog.git
cd tech-blog

# 2) Ruby / Node / Python 의존성
bundle install
npm ci
python3 -m pip install -r scripts/requirements.txt

# 3) Git hooks 설치 (필수 — 품질 게이트가 여기서 돕니다)
bash scripts/install-hooks.sh

# 4) 로컬 서버
bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload
```

`install-hooks.sh`는 `core.hooksPath`를 `.githooks/`로 설정합니다.
`.git/hooks/`에 직접 심볼릭 링크를 만들지 마세요 — 무시됩니다.

---

## 3. 브랜치와 커밋

**브랜치 네이밍**

| 접두사 | 용도 |
| :--- | :--- |
| `feat/` | 새 기능 |
| `fix/` | 버그 수정 |
| `refactor/` | 동작 변화 없는 구조 개선 |
| `docs/` | 문서 |
| `chore/` | 빌드·설정·의존성 |

**커밋 메시지** — [Conventional Commits](https://www.conventionalcommits.org/) 형식:

```
<type>(<scope>): <한 줄 요약>

<본문: 왜 이 변경이 필요한지>
```

```bash
git commit -m "fix(news): 카드 요약 마침표 백필"
git commit -m "feat(cover): L20 advisory emblem 회전 추가"
git commit -m "docs: CONTRIBUTING 추가"
```

- 요약은 한국어 또는 영어 모두 가능합니다.
- 한 커밋에 한 가지 논리적 변경만 담아주세요.
- `Co-Authored-By: Claude` 트레일러는 사용하지 않습니다.

---

## 4. 포스트 기여 규칙

포스트를 추가·수정할 때 pre-commit 게이트가 강제하는 규칙입니다.

| 규칙 | 근거 |
| :--- | :--- |
| 파일명 `YYYY-MM-DD-English_Title.md` — **한글 금지** | URL 안정성 |
| `date:`는 `09:00:00 +0900` 이상 | 사이트가 UTC 고정이라 KST 00–09시는 URL 날짜가 하루 밀립니다 |
| 이미지 파일명·SVG `<title>`/`<desc>`는 **ASCII만** | 크로스 플랫폼 대소문자·인코딩 함정 |
| 코드 블록에 언어 태그 필수 (` ```bash `) | 렌더링·접근성 |
| 산문 속 맨 URL 금지 — 마크다운 링크로 | 맨 URL은 텍스트로 렌더됩니다 |
| API 키·토큰·비밀번호는 더미값(`your-api-key-here`) | 시크릿 위생 |
| FAQ 섹션 추가 금지 | 편집 방침 |

새 포스트는 `python3 scripts/check_posts.py`로 검증할 수 있습니다.

> **커버 SVG / 커버 생성기를 건드리는 PR**은 별도 규칙이 있습니다.
> `generate_post_images.py --force`를 코퍼스 전체에 돌리지 마세요 —
> spec 기반 커버를 덮어써 드리프트·정직성(honesty) 게이트가 깨집니다.

---

## 5. 스크립트·코드 기여 규칙

`scripts/` 아래 Python을 변경하면 **테스트가 반드시 동반되어야 합니다.**

```bash
# Python 테스트 (pre-commit이 자동 실행)
python3 -m pytest scripts/tests/ -q

# JS 테스트
npm test

# 린트 / 타입
npm run lint        # ruff check + mypy
npm run lint:fix    # 자동 수정
```

추가 요구사항:

- `auto_publish_news.py`의 템플릿 분기를 추가하면
  `scripts/tests/test_news_templates.py`에 케이스를 함께 추가합니다.
  분기 순서 = 우선순위이므로 구체적 키워드를 일반 키워드보다 먼저 둡니다.
- 커버리지 하한(`--cov-fail-under=40`)을 낮추는 변경은 받지 않습니다.
- CI 게이트(워크플로의 임계값, 액션 SHA 핀, 필수 체크)를 **완화하는** 변경은
  근거를 PR 본문에 명시해야 합니다.

---

## 6. Pull Request 절차

1. 포크 또는 브랜치를 만들고 작업합니다. `main`에 직접 커밋하지 않습니다.
2. 로컬에서 검증을 통과시킵니다 (§5). pre-commit이 12단계 게이트를 돕니다.
3. PR을 열고 [PR 템플릿](.github/PULL_REQUEST_TEMPLATE.md)을 채웁니다.
4. CI가 모두 green인지 확인합니다.
   - `svg-lint` / `check-svg`는 **변경 파일이 아니라 코퍼스 전체**를 스캔합니다.
     내 변경과 무관해 보이는 실패라면 `main`의 기존 회귀일 수 있으니
     `git log`로 최근 크론 발행 포스트를 먼저 의심하세요.
5. 리뷰 피드백을 반영합니다.

**PR 크기**: 리뷰 가능한 단위로 쪼개주세요. 코퍼스 전체 변환처럼 파일 수가
많은 PR은 (a) 변환기 코드와 (b) 생성된 결과물을 분리하면 리뷰가 쉬워집니다.

---

## 7. 라이선스

기여하신 내용은 이 저장소의 [MIT 라이선스](LICENSE)로 배포됩니다.
포스트 본문에 인용하는 외부 자료는 출처를 명시하고 원 저작권을 존중해주세요.
