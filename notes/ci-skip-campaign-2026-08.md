# CI skip 캠페인 회고 (2026-08-18 → 08-21)

[`ci-gate-audit-2026-08.md`](ci-gate-audit-2026-08.md)가 **"이 게이트가 한 번이라도
무언가를 막은 적이 있나"** 를 물었다면, 이번은 그 다음 질문이다:
**"이 게이트가 조용히 자기 자신을 끈 적이 있나."**

PR #576–#582 7건. CI pytest 요약의 skip 7건에서 시작해 실질 0건으로 끝났지만,
가치 있는 부분은 그 숫자가 아니라 **skip이 두 가지 다른 것을 같은 글자로 보고한다**
는 발견이다.

## 중심 발견 — 요약의 `s` 한 글자가 두 가지를 덮는다

| skip 이유 | 실제 의미 | skip이 정직한가 |
|---|---|---|
| `fontTools is not installed`, `node is not on PATH`, `bundle not available` | 러너에 선택적 의존성/도구가 없다 | ✅ 로컬 개발 가능성 유지. CI는 의존성을 선언해 실제로 실행 |
| `owning post missing`, `not on disk`, `{TARGET} not found` | **테스트가 지키려던 파일이 사라졌다** | ❌ 그게 바로 회귀인데 초록으로 보고 |

pytest 요약에는 둘 다 `s`다. 그래서 두 번째 종류는 "정상적인 환경 차이"로 읽히며
몇 달을 살아남는다.

전자를 없애는 것은 **의존성 선언**(#576: `Pillow>=11.3.0`, `fonttools[woff]>=4.55.0`
를 `requirements-ci.txt`에 추가)이고, 후자를 없애는 것은 **assert 전환**(#579: 11지점)
이다. 둘을 같은 작업으로 취급하면 안 된다 — 전자를 assert로 바꾸면 개발 머신이
전부 red가 되고, 후자를 선언으로 해결할 수는 없다.

## 재발 방지를 위치가 아니라 *이유*로 고정한 것

`scripts/tests/test_skip_path_policy.py`. 처음 설계는 파일·라인 allow-list였는데
두 가지 이유로 폐기했다:

1. 무관한 skip이 이동할 때마다 스테일 된다.
2. **열려 있는 다른 PR이 skip 지점을 건드린다.** #578은 `test_post_image_class_hooks.py`
   의 `skipif`를 제거하고 런타임 헬퍼로 옮기는 중이었다. 위치 기반 allow-list는
   병합 순서 의존을 만들고, 그건 [[stacked_pr_delete_branch_closes_child]] 계열의
   사고를 부른다.

그래서 정책을 **skip 이유 문자열**에 걸었다(AST로 리터럴만 읽고, f-string 보간은
`{}`로 정규화). 환경 사실만 allow-list, 레포 산출물 부재는 거부, `importorskip`은
이유가 아니라 **모듈이 퍼스트파티인지**로 판정, `pytest.mark.skip`은 전면 금지.

결과적으로 #578이 도입한 새 skip 이유(`"{rel} not built — run build.sh first"`)는
`not built` 패턴에 걸려 통과했다 — 순서 무관이 설계대로 성립했다.

## 러너 레벨 fail-open — 파일 안을 보는 스캔으로는 절대 안 잡히는 부류

JS 스위트 감사(#581)의 결론이 예상과 달랐다. **파일 내부 fail-open은 0건**이었다:
`.skip`/`.todo`/`.skipIf`/`ctx.skip` 0, `expect(true)` 류 0, 본문 조기 return 0,
`existsSync`/env 가드 0, assertion 먹는 `try/catch` 0. 서브젝트도 모듈 최상단
`readFileSync` + `new Function`이라 소스 부재 시 throw = fail-closed.

이 레포의 교훈("게이트가 0 violations면 게이트를 먼저 의심",
[[liquid_nested_quotes_break_template_gates]])대로 **러너 종료 코드**를 재봤고
거기서 두 개가 나왔다.

**(1) 글로브가 0건 매치일 때 `node --test`는 exit 0이다.**

```
$ bash -c 'node --test api/__tests__/__nope__*.test.js'; echo $?
TAP version 13
1..0
# tests 0
# pass 0
0
```

`api/__tests__` 이름변경·이동, `.test.js` 접미사 변경이면 `npm run test:api`가
0건 실행으로 성공을 보고한다. vitest는 같은 조건에서 exit 1이므로 node:test만
해당된다.

**(2) 파일이 있고 `test()` 호출이 0개면 그 파일 자체가 1건 통과로 센다.**

```
$ printf 'const x = 1;\n' > /tmp/empty.test.js
$ node --test /tmp/empty.test.js
# tests 1 / # pass 1 / # fail 0     exit 0
```

이것이 중요한 이유: (1)을 막기 위해 `# tests >= 1` 하한을 걸었는데, (2)는 그
하한을 **통과한다**. 실제 스위트에서 한 파일을 비우면 `# tests 72 / # pass 72`로
12건이 조용히 사라진다. 런타임 카운트로는 구분 불가라서 (2)는 정적 검사로 막았다
(`api/__tests__/*.test.js`는 각각 `test(` 호출을 최소 1개 가져야 한다).

**하한을 오늘의 값으로 박지 않은 이유**: 직전 #577이 죽은 `validateUrl` 테스트
3개를 정당하게 삭제했다. 83을 박으면 그런 PR이 전부 red가 된다. 이 게이트는
"0건 수집"을 막고 "적게 수집"은 막지 않는다 — 그 한계를 워크플로 주석과 실패
메시지에 적었다.

**(3) 부수 발견 — vitest의 전수-skip 방어는 커버리지 게이트가 하고 있었다.**

```
$ npx vitest run           --testNamePattern '<매치없음>'  ->  698 skipped, exit 0
$ npx vitest run --coverage --testNamePattern '<매치없음>'  ->  exit 1
    ERROR: Coverage for lines (0%) does not meet global threshold (80%)
```

CI 스텝을 plain `npm test`로 바꾸거나 threshold를 0으로 내리면 조용히 열린다.
둘 다 가드로 고정했다(#582).

## 무장 게이트의 유일한 실질 리스크는 "CI에서도 조건 불성립"이다

`REQUIRE_*` opt-in env 패턴(#578 `REQUIRE_COMPILED_CSS`, #580 `REQUIRE_JEKYLL_BUILD`)
은 로컬은 skip, CI는 fail로 갈라놓는다. 위험은 하나뿐이다 — CI에서도 그 조건이
성립하지 않아 **영구 red**가 되는 것. 그래서 무장 전에 측정했다:

```
$ gh run view <run> --log --job <job> | grep 'SKIPPED \['
  test_auto_publish_news.py ... (PIL) x2
  test_font_tier_split.py ...  (fontTools) x2
  test_post_image_class_hooks.py::TestCompiledCss ... x3
```

7건 = deps 4 + CompiledCss 3. `test_image_content_hash`가 **한 건도 없다** →
CI에서는 bundle이 있고 fixture의 jekyll 빌드가 성공한다. 스텝 순서도 확인
(`Setup Ruby` step 1 < pytest step 6). 이 측정이 없으면 무장은 도박이다.

반대 방향의 실패 양상도 게이트로 고정했다: bundler보다 **앞에서** 무장하면
결함이 아닌 조건으로 영구 red가 된다. 순서를 별도 테스트로 뺀 이유다.

"무장 + 빌드 성공"은 로컬에서 검증 불가였다(로컬 빌드는 mise가 rbenv를 가려 실제로
깨져 있다). #533 `--verify` 배선과 같이 **PR CI를 첫 시험대로** 썼고, 결과는
`4259 passed, 3 skipped`에 `test_image_content_hash` 5건 실행·통과였다.

## 추론이 실측을 대체하지 못한 사례

병렬로 돌린 감사 세션 2건의 보고를 재측정했고, 두 지점이 달랐다.

**1. 명시적으로 "검증하지 않았다"고 적은 항목이 틀렸다.** 한 보고는
*"0건 매치 글로브는 ENOENT로 non-zero exit이므로 fail-closed다 — 이미 안전하다고
추론했으므로 파괴적으로 검증하지 않았다"* 고 적었다. 실측은 `1..0 / # tests 0 /
exit 0`이다. 정확히 그 경로가 이번에 막은 구멍이다.

**2. baseline이 스테일이었다.** 보고의 `95 tests / 29 suites`는 #577 병합(03:21)
전 트리 측정이었다 — 근거: 그 보고가 `api/chat.js:777 validateUrl`을 "존재·export됨"
으로 적었는데 #577이 그 함수를 삭제했다. 현재는 83/26이다.

정성적 결론(skip 지시자 0건 등)은 유효했고 독립 확인했다. 교훈은 보고를 버리라는
게 아니라, **"검증하지 않았다"고 적힌 줄이 가장 먼저 확인할 줄**이라는 것이다.

## 내가 걸린 함정 — 주석이 안티패턴을 언급한다

`jekyll.yml`의 `|| true`를 세면서 `'|| true' in step["run"]`으로 검사했고,
"Validate post quality" 스텝이 위반으로 나왔다. 실제로는 그 스텝의 **주석**이
`No \`|| true\`: a score under the floor must fail`이라고 설명하고 있었다.

이건 [`ci-gate-audit-2026-08.md`](ci-gate-audit-2026-08.md)가 "5개 파일에서 같은
함정"이라고 이미 기록한 것이다. 기록을 읽고도 같은 실수를 했다. 해법도 이미
그 노트에 있다 — 검사 전 주석 제거(`_uncommented`).

## 남은 열화 항목 재판정 (2026-08-21)

이전 노트의 "남은 열화 항목" 3종을 실측했다. **2건 기각, 1건 수정.**

### 기각 1 — `jekyll.yml`의 `|| true` (판정 유지, 카운트 정정)

이전 노트는 "대시보드 코멘트 스텝 내부 3곳"이라고 적었다. 주석을 제거하고 세면
**5곳**이고, 전부 두 개의 `continue-on-error: true` PR-코멘트 스텝 안이다
(step 8 `Post coverage comment` 1곳, step 15 `Post quality dashboard comment` 4곳).

분류는 유지된다 — 실제 게이트인 step 13 `Validate post quality (PR only)`는
`continue-on-error` 없음, 실제 `|| true` **0곳**, `validate_post_quality.py`를
맨몸으로 실행한다. soft 5곳은 코멘트 본문을 만드는 것뿐이다.

### 기각 2 — L22/L25 generator 베이스라인 대표 부재 (보류 유지, 근거 강화)

이전 노트는 "현재 라이브 출력이 없어 보류"라고 적었다. 이제 숫자가 있다:

| profile 마커 | 라이브 커버 |
|---|---|
| `high-quality-cover (L20 Hero+2-Card)` | **233** |
| `high-quality-cover (2025 upgraded L25-single)` (L22·L25 공통 마커) | **0** |

`grep -l "L22" assets/images/*.svg`가 13건을 주는데 전부 SVG path 좌표
(`L22 82 L29 74` = lineto 명령)다. 마커 기준으로는 0건이므로 `TARGET_SVGS`에
넣을 대표 표본이 존재하지 않는다. 보류의 전제가 살아 있다.

### 수정 — `monitoring.yml`의 Slack 채널이 한 번도 울린 적이 없다

이전 노트는 "요구 시크릿 3종 미설정(부분 동작 중)"으로만 적었다. 셋을 갈라보면
성질이 다르다:

| 시크릿 | 상태 | 판정 |
|---|---|---|
| `PAGESPEED_API_KEY` | 미설정 | 현상유지 (2026-08-11 결정, 무키 호출 가능) |
| `VERCEL_TOKEN` | 미설정 | 프로비저닝 대기 (사용자 결정, `HAS_VERCEL_TOKEN`으로 가드됨) |
| `SLACK_WEBHOOK` | **한 번도 없음** | **수정** — 아래 |

Slack 알림 스텝이 `if: failure() && env.HAS_SLACK_WEBHOOK == 'true'`였고
`SLACK_WEBHOOK`은 설정된 적이 없다. 즉 프로덕션 모니터링이 실패해도 이 채널은
**한 번도 울리지 않았다**. `vercel-firewall-backup`이 매주 성공을 보고하며 스냅샷을
한 번도 만들지 않았던 것과 같은 모양이다.

핵심은 **`SLACK_BOT_TOKEN`/`SLACK_CHANNEL_ID`는 설정돼 있고** `slack-post-notify.yml`
· `slack-category-digest.yml`이 이미 그걸 쓴다는 것이다. 새 시크릿을 요구할 이유가
없어 존재하는 자격증명으로 옮겼고(curl + `chat.postMessage`, 그 두 워크플로와 동일
패턴), 같은 이유로 fail-closed로 만들었다 — 이 스텝은 모니터링이 **이미 실패한 뒤**
에만 돌기 때문에, 여기서 시크릿이 없다는 것은 실제 장애 알림이 버려진다는 뜻이다.
`test_ci_secret_absence_guard.py`의 `FAIL_CLOSED`에 `monitoring.yml`을 추가했다.

작업 중 걸린 것: `python3 -c '...'` 안에서 `os.environ[\'KEY\']`를 썼는데 bash
단일 인용부호는 이스케이프를 허용하지 않아 `unexpected EOF`로 깨졌다. YAML에
심은 셸을 **추출해 실제로 실행**해서 잡았고, 큰따옴표로 고친 뒤 유효한 JSON
payload 생성과 fail-closed 분기(`::error::` + exit 1)를 각각 실측했다.

## 방법론 — 이번에 반복해서 통한 것

**뮤테이션이 유일한 신뢰 근거였다.** 누적 15종 전부 caught. 특히 값이 있었던 것은
*정반대 방향의 실패를 함께 고정*하는 것이다 — 무장 스텝이 bundler보다 앞으로
가면(영구 red) 실패하고, 뒤에 있으면서 무장이 없으면(영구 skip) 실패한다.

**게이트를 수정 전 상태에 대고 돌려봤다.** `git stash`로 11지점을 되돌리면 정책
게이트가 정확히 그 11개를 지목한다(`1 failed, 16 passed`). 통과하는 게이트는
증거가 아니고, **실패시켜 본 게이트만 증거다.**

**비-발견을 근거와 함께 기각했다.** `vitest.yml`의 경로 필터는 서브젝트 대비
빠짐이 없고, 크론 봇 사각지대([[ci_gates_blind_to_cron_bot_push]])는 이 워크플로에
없다 — 봇은 `_posts/**`와 `assets/images/**`만 쓰고 `assets/js`·`api`를 건드리지
않는다. schedule 추가는 #529 때 `visual-regression`에서 기각한 것과 같은 이유로
소음이다.

## 결과

| 지표 | 시작 | 끝 |
|---|---|---|
| CI pytest skip | 7 | 3 (전부 빌드 전 `TestCompiledCss`, 빌드 후 재실행에서 통과 → 실질 0) |
| 레포 산출물 부재 → skip | 11지점 | 0 |
| 러너 레벨 fail-open | 2 (미인지) | 0 |
| 신규 회귀 가드 | — | 4개 파일 (`test_skip_path_policy`, `test_ci_compiled_css_gate_guard`, `test_ci_jekyll_build_gate_guard`, `test_ci_api_test_wiring_guard` 확장) |

## 참조

- 이전 회고: [`ci-gate-audit-2026-08.md`](ci-gate-audit-2026-08.md),
  [`ci-security-hardening-2026-07.md`](ci-security-hardening-2026-07.md)
- 정책 게이트: `scripts/tests/test_skip_path_policy.py`
- 무장 패턴: `REQUIRE_COMPILED_CSS` (`jekyll.yml`), `REQUIRE_JEKYLL_BUILD` (동)
