# Project Notes

작업별 학습 내용, 결정 사항, 이슈를 기록합니다.
CLAUDE.md에서 이 디렉토리를 참조합니다.

## Structure

- `learnings.md` - 기술적 발견, 패턴, 노하우
- `decisions.md` - 아키텍처/디자인 결정 기록
- `issues.md` - 알려진 이슈와 해결 방법
- `per-pr/` - PR별 노트 (PR-{number}.md)

## Topic Docs

주제별 심층 문서. **해당 영역을 건드리기 전에 먼저 읽으세요.**

| 문서 | 언제 읽나 |
|------|-----------|
| [corpus-transformer-contract.md](corpus-transformer-contract.md) | `_posts/` 코퍼스를 일괄 변환하는 스크립트를 만들거나 고칠 때 — 필수 계약 C1~C11, 함정 카탈로그 |
| [digest-proper-noun-policy.md](digest-proper-noun-policy.md) | 다이제스트 고유명사 표기(영문 canonical), allow-list 확장 |
| [digest-retranslate-security.md](digest-retranslate-security.md) | 다이제스트 번역 백필·재번역 워크플로 |
| [seo-canonical-fix.md](seo-canonical-fix.md) | canonical/share URL, `absolute_url` 금지 규칙 |
| [codeql-setup-and-fp-suppression.md](codeql-setup-and-fp-suppression.md) | CodeQL 설정, false positive 처리 |
| [ci-security-hardening-2026-07.md](ci-security-hardening-2026-07.md) | 워크플로 권한·액션 핀·시크릿 위생 |

## Usage

작업 완료 후 Claude에게 요청:
> "이번 작업에서 배운 점을 notes에 기록해줘"
