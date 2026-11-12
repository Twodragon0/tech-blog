# 의존성 PR 최신 main 통합 검증

검증일: 2026-11-12 KST. 원격 병합·push는 수행하지 않았다.

- 기준 main: `8cbc65a803df2c396e0f5f42b89deba89f9b2c59`
- 격리 worktree: `/private/tmp/techblog-deps-integration-20261112`
- 로컬 통합 head: `854e656453786ec8bada465db6f0c6236099ed48`
- 순서: #798 → #800 → #782 → #760. 네 번 모두 ort 병합 성공, 충돌 없음.

| PR | 검증한 원본 head | 변경 | 판정 |
|---|---|---|---|
| [#798](https://github.com/Twodragon0/tech-blog/pull/798) | `738f7abdb3067c904c53a92f5c87e246df2126d8` | Actions pin 갱신 | 최신 main 통합 준비 완료 |
| [#800](https://github.com/Twodragon0/tech-blog/pull/800) | `5b6f2cc08eca41bdeb633dc3f75c5550775506f4` | Ruby 의존성 갱신 | 최신 main 통합 준비 완료 |
| [#782](https://github.com/Twodragon0/tech-blog/pull/782) | `32924220dbb3712e4aab1a04f9dfb6b5b892bc5f` | fonttools 하한 갱신 | 최신 main 통합 준비 완료 |
| [#760](https://github.com/Twodragon0/tech-blog/pull/760) | `f839dafa2bad64ad65fa87c2b7e0ee931073b244` | CairoSVG 하한 갱신 | 최신 main 통합 준비 완료 |

## 실행 증거

- `scripts/check_workflow_action_pins.py`: 34 workflows, 112 pins 전부 일치. floating tag 없음.
  최신 main에 추가된 workflow를 포함해 검사했다.
- 별도 venv에 정확한 `fonttools[woff]==4.66.0`, `CairoSVG==2.9.1`, Pillow 13.0.0을 설치했다.
  열린 하한 변경을 실제 버전 업그레이드와 혼동하지 않도록 새 하한 버전을 직접 검증했다.
- `test_check_workflow_action_pins.py`, `test_font_tier_split.py`, `test_font_drift_gate.py`,
  `test_rasterize_svg_covers.py`: **74 passed, 0 skipped**, 기존 tier-2 폰트 경고 1건.
  실제 WOFF2 cmap 검사도 생략되지 않았다. API 호출은 테스트 설정에서 비활성화했다.
- 실제 저장소 CairoSVG 변환 함수를 임시 SVG에 실행했다. PNG 1200×630 크기와
  두 지점의 RGB `(18, 86, 171)`, `(237, 154, 66)`을 확인했다.
- 격리 bundle의 sass-embedded 1.107.1·csv 3.3.7로 Jekyll 전체 빌드:
  **exit 0, 19.769초**. 생성한 feed.xml 존재를 확인했다.
- `git diff --check`: 통과.

## Python 소비 환경 하한 확인

실제 픽셀·폰트 실행은 격리 Python 3.14.10에서 수행했으며 Python 3.11 런타임 실행으로
표현하지 않는다. 설치 메타데이터의 Requires-Python은 fonttools 4.66.0이 `>=3.11`,
CairoSVG 2.9.1이 `>=3.10`, Pillow 13.0.0이 `>=3.11`이다.
소비 workflow의 최저 Python은 Jekyll·SVG lint의 requirements-ci 경로와
generate-images의 requirements 경로 모두 3.11이다.

pip의 `--dry-run --ignore-installed --only-binary=:all: --python-version 3.11`
및 Linux cp311, manylinux_2_28_x86_64·manylinux2014_x86_64 대상으로
위 세 정확한 버전과 전체 전이 의존성의 해석이 성공했다. 이는 Python 3.11의 패키지
메타데이터·wheel 해석 증거이며, 해당 인터프리터에서 실제 렌더링한 증거는 아니다.
보고서: `/private/tmp/techblog-deps-py311-pillow13-resolution-20261112.json`.
다른 선택적 패키지가 포함된 requirements.txt 전체 설치는 이번 최소 버전 검사 범위가 아니다.

## #761 충돌 해결과 순차 조합 확인

별도 격리 worktree의 해결 커밋 `2d42ab080dac051ecd8893ab118a8c49b6ecf9d9`는
원본 #761을 최신 main과 병합하면서 Pillow 13 요구를 보존하고 NumPy 하한을 2.5.3으로
올린다. NumPy의 Requires-Python `>=3.12`에 맞춰 visual-baseline-refresh와
visual-baseline-verify를 함께 Python 3.12로 조정하고 대응 회귀 guard를 추가했다.

해당 작업자의 검증 증거는 관련 58건 통과, 전체 hook 6549 passed·23 skipped다.
실제 Python 3.12에서 PNG fixture 5개와 cover 32개의 렌더링·비교 경로를 검증했다.
macOS에서의 결과이며 Ubuntu CI와 동일한 픽셀·폰트 환경을 보증하지 않는다.
원격 반영 뒤 Linux CI는 별도로 확인해야 한다.

위 네 PR 통합과 문서 head에 이 해결 커밋을 read-only `git merge-tree --write-tree`로
조합해 충돌 없음(exit 0)을 확인했다. 결과 tree는
`1a8daf82e61a668b08f9e25a5d87188557d1ca08`이며, 추출한 workflow 112개 pin이
모두 일관된 SHA이고 두 visual workflow 모두 Python 3.12임을 재검증했다.
따라서 #798 → #800 → #782 → #760 다음에 #761 해결 변경을 적용하는 순서도
로컬 통합 수준에서 충돌 없이 검증됐다. 원격 push·추가 병합은 수행하지 않았다.

권장 병합 순서는 위 순서를 유지한다. 실제 원격 병합 직전 head와 CI를 다시 확인한다.
미래 CI가 열린 하한보다 높은 Python 패키지 버전을 선택할 수 있으며, 이번 증거는
명시한 버전에 해당한다. 자동 병합 설정 실패는 별도 운영 조건으로 취급한다.

빌드 로그는 `/private/tmp/techblog-deps-build-20261112.log`에 보존했다.
디스크 부족으로 성공 확인 뒤 이 작업이 생성한 사이트 출력 171MiB만 삭제했다.
기존 사용자 소스·산출물과 다른 worktree는 변경하지 않았다.
