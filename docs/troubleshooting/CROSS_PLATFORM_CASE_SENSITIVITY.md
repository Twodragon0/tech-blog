# Cross-Platform Filesystem Case-Sensitivity Pitfall

**Last verified**: 2026-05-27 (after the `Amazon_Q_DeveloperAnd` / `AWSIn` drift incident)

이 저장소는 macOS (APFS, 기본 case-insensitive) 환경에서 작성되어 Linux 기반
CI (case-sensitive ext4/xfs) 와 Vercel 빌드로 배포된다. 두 환경의 동작 차이는
파일 이름 대소문자만 다른 변종이 공존할 때 조용히 깨지는 클래스의 버그를
유발하므로, 이 문서는 그 패턴과 예방 게이트를 정리한다.

## Symptom

CI 또는 PR 워크플로에서 다음 중 하나가 보이면 본 케이스에 해당한다:

```
[svg-lint] DRIFT: _data/digest_covers/2025-05-24-Amazon_Q_DeveloperAnd_*.yml
  expected: assets/images/2025-05-24-Amazon_Q_DeveloperAnd_*.svg
  actual:   (file not present on this commit)
```

또는 `upgrade_digest_cover.py --check` 가 로컬에서 통과했는데도 CI 의 SVG
Compliance Lint job 만 빨갛게 나오는 상황이 전형적이다. macOS 로컬에서는
`DeveloperAnd.svg` 와 `Developerand.svg` 가 같은 inode 를 가리키므로 차이가
보이지 않지만, Linux 에서는 두 파일이 별개로 존재해야 한다.

## Root cause

세 가지 신호가 동시에 일어나야 발현된다:

1. **macOS APFS 기본값이 case-insensitive** — 파일 이름 대소문자가 달라도
   같은 파일로 본다. (HFS+ 와 동일한 디폴트 호환 동작.)
2. **Linux 파일시스템은 case-sensitive** — `FooBar` 와 `foobar` 는 별개
   파일이며, 한 쪽만 커밋되어 있으면 다른 쪽 경로는 존재하지 않는다.
3. **Git 의 `core.ignorecase=true` 기본값** — macOS 에서 클론된 저장소는
   기본적으로 대소문자 차이를 변경으로 인식하지 않는다. 결과적으로 이미 커밋된
   소문자 파일을 대문자로 덮어써도 `git status` 가 깨끗하게 보일 수 있다.

## 2026-05-27 의 실제 사례

| 위치 | spec slug | 포스트 `image:` 필드 |
|------|-----------|------------------|
| `_data/digest_covers/2025-05-24-Amazon_Q_DeveloperAnd_*.yml` | `Amazon_Q_DeveloperAnd_..._And_AWS` | `/assets/images/2025-05-24-Amazon_Q_Developerand_..._and_AWS.svg` |
| `_data/digest_covers/2025-10-03-AWSIn_*.yml` | `AWSIn_Database_..._Guide` | `/assets/images/2025-10-03-AWSin_Database_..._Guide.svg` |

스펙 slug 가 포스트 파일명 케이싱을 따랐지만 (`DeveloperAnd`, `AWSIn`),
실제 커밋된 SVG 와 포스트 `image:` 필드는 lowercase 변종을 사용했다
(`Developerand`, `AWSin`). 로컬에서는 양쪽이 같은 파일을 가리키므로 통과,
CI 에서는 drift 로 검출.

수정은 두 단계로 진행:

- `ebff34a1` — 5 개 spec 의 slug 를 포스트 `image:` 가 참조하는 소문자
  변종에 맞춰 정렬, 재렌더.
- `ff741d9d` — option B items 11-15 신규 스펙은 처음부터 소문자 변종으로
  작성.

## Recommended local git config

저장소 루트에서 한 번만 실행:

```bash
git config core.ignorecase false
```

전역(`--global`)이 아니라 저장소 단위만 변경하라. 다른 프로젝트는 영향이
없으며, 이 저장소에서만 케이스 차이가 즉시 변경으로 노출된다.

부작용으로 인지해야 할 점:

- 과거에 macOS 에서 대소문자만 다르게 작업해 둔 파일이 있다면 클론 직후
  `git status` 가 다수의 untracked 항목으로 보일 수 있다. `git mv` 로 케이스를
  정정해 한 쪽으로 통일하면 사라진다.
- IDE 의 파일 색인이 케이스 다름을 별 파일로 보기 시작하므로, "Find in
  Files" 결과가 늘어 보일 수 있다.

확인:

```bash
git config core.ignorecase
# false 가 출력되어야 함
```

## 현재 작동 중인 자동 게이트

오늘(2026-05-27) 이후로 두 개의 enforce 모드 게이트가 추가되어 같은 버그
클래스를 차단한다.

| 게이트 | 위치 | 실행 시점 |
|--------|------|-----------|
| `<title>`/`<desc>` non-ASCII 차단 | `scripts/check_svg_title_ascii.py` (commit `64823037`) | pre-commit (staged) + svg-lint CI (--all) |
| spec slug ↔ 포스트 `image:` 일치 검증 | `scripts/check_spec_slug_consistency.py` (follow-up commit) | pre-commit (staged) + svg-lint CI (--all) |

기존부터 있던 `python3 scripts/upgrade_digest_cover.py --all --check` 도
drift 를 잡지만, 그건 SVG 렌더 결과의 바이트 차이를 보는 사후 게이트라
slug 만 다르고 콘텐츠가 동일한 케이스는 빠질 수 있다. 위 두 신규 게이트가
filename 레이어를 먼저 차단한다.

## 드리프트가 CI 에서 검출되었을 때 복구 절차

1. **불일치 식별** — CI 로그에서 spec 경로와 expected/actual 파일명을
   확인. 또는 로컬에서:
   ```bash
   python3 scripts/check_spec_slug_consistency.py --all
   ```

2. **표준 케이싱 결정** — 일반적으로 포스트 `image:` 필드의 케이싱이 권위
   있는 소스 (Jekyll 이 실제 빌드에 사용하는 경로). spec slug 와 SVG
   파일명을 그 케이싱에 맞춘다.

3. **spec 파일 이름 + slug 필드 갱신**:
   ```bash
   git mv _data/digest_covers/2025-05-24-Amazon_Q_DeveloperAnd_*.yml \
          _data/digest_covers/2025-05-24-Amazon_Q_Developerand_*.yml
   sed -i '' 's|^slug: Amazon_Q_DeveloperAnd_|slug: Amazon_Q_Developerand_|' \
      _data/digest_covers/2025-05-24-*.yml
   ```

4. **SVG + raster 재생성**:
   ```bash
   python3 scripts/upgrade_digest_cover.py --spec _data/digest_covers/2025-05-24-*.yml
   # 그리고 raster 변형 — scripts/_rebuild_all_l20_rasters.py:build_one 패턴 참조
   ```

5. **로컬 검증** (Linux 동작 시뮬레이션):
   ```bash
   python3 scripts/check_spec_slug_consistency.py --all
   python3 scripts/upgrade_digest_cover.py --all --check
   python3 scripts/check_svg_title_ascii.py --all
   ```

6. **단일 atomic commit 으로 묶어 push** — spec 이름/slug/SVG/rasters 가
   같은 케이싱으로 정렬된 상태가 같은 커밋에 들어가야 PR 검토자가 이해
   하기 쉽다.

## 신규 포스트/스펙 작성 시 사전 체크리스트

- [ ] 새 `_data/digest_covers/{date}-{slug}.yml` 작성 시 `slug:` 필드는
      포스트 front matter 의 `image:` 가 가리키는 SVG 파일명을 그대로
      복사해 만든다 (포스트 markdown 파일명을 베끼면 안 된다 — 케이싱이
      다를 수 있다).
- [ ] 커밋 직전 `python3 scripts/check_spec_slug_consistency.py --staged`
      를 직접 실행. pre-commit 훅이 동일한 검증을 수행하지만, 수동 실행으로
      한 번 더 확인한다.
- [ ] 신규 클론 직후 `git config core.ignorecase false` 를 적용했는지
      확인.
- [ ] 케이스 차이로 의심되는 변경이 있다면 푸시 전 draft PR 을 띄워 CI
      결과를 확인. macOS 로컬 통과가 Linux 통과를 보장하지 않는다.

## Related

- [ERROR_ANALYSIS_AND_FIXES.md](ERROR_ANALYSIS_AND_FIXES.md) — Jekyll/Liquid
  빌드 에러 분석
- [MISSING_IMAGES_ISSUE.md](MISSING_IMAGES_ISSUE.md) — 이미지 참조 누락 패턴
  (SVG 변종 케이싱 누락 사례와 유사)
- [VERCEL_SECURITY_CHECKPOINT_FIX.md](VERCEL_SECURITY_CHECKPOINT_FIX.md) —
  Vercel 빌드 환경(AL2023) 차이 이슈
- 게이트 스크립트: `scripts/check_svg_title_ascii.py`,
  `scripts/check_spec_slug_consistency.py`,
  `scripts/upgrade_digest_cover.py`
