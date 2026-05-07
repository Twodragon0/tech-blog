# IndexNow Setup Guide

IndexNow는 Bing, Yandex 등 참여 검색엔진에 URL 변경을 즉시 알리는 프로토콜입니다.
**Google은 IndexNow에 참여하지 않습니다** — Google 색인은 GSC(Search Console)를 사용하세요.

## 작동 방식

```
1. 블로그에 _posts/ 변경 push
2. deploy-pages workflow 실행 (GH Pages 배포)
3. indexnow-ping workflow 자동 트리거
4. scripts/indexnow_ping.py → sitemap.xml의 모든 URL을 3개 엔드포인트에 POST
   - https://api.indexnow.org/IndexNow
   - https://www.bing.com/indexnow
   - https://yandex.com/indexnow
5. 각 엔드포인트가 키 파일을 fetch해 소유권 검증 후 URL 큐 등록
```

## 키 파일 위치

키: `890b921a9bdd4a155d198c6c0487a14f`

| 파일 | URL |
|------|-----|
| `890b921a9bdd4a155d198c6c0487a14f.txt` | `https://tech.2twodragon.com/890b921a9bdd4a155d198c6c0487a14f.txt` |
| `.well-known/890b921a9bdd4a155d198c6c0487a14f.txt` | `https://tech.2twodragon.com/.well-known/890b921a9bdd4a155d198c6c0487a14f.txt` |

두 파일 내용 모두 키 값 그 자체: `890b921a9bdd4a155d198c6c0487a14f`

**주의**: IndexNow 키는 secret이 아닙니다. 소유권 검증용 공개 토큰입니다.
커밋에 포함되고 GitHub Actions 환경변수에 평문으로 사용해도 안전합니다.

## 로컬 실행

```bash
# 사전 조건: sitemap.xml이 루트에 있거나 _site/에 Jekyll 빌드된 버전이 있어야 함

# 전체 sitemap 제출
python3 scripts/indexnow_ping.py

# 특정 URL만 제출 (배포 직후 새 포스트 빠른 색인용)
python3 scripts/indexnow_ping.py --urls \
  https://tech.2twodragon.com/your-new-post/ \
  https://tech.2twodragon.com/another-post/

# 드라이런 (payload만 출력, 실제 POST 없음)
python3 scripts/indexnow_ping.py --dry-run

# 환경변수로 키 오버라이드
INDEXNOW_KEY=your_key python3 scripts/indexnow_ping.py --dry-run
```

### 드라이런 출력 예시

```json
{
  "host": "tech.2twodragon.com",
  "key": "890b...4f",
  "keyLocation": "https://tech.2twodragon.com/890b921a9bdd4a155d198c6c0487a14f.txt",
  "urlList": [
    "https://tech.2twodragon.com/",
    "https://tech.2twodragon.com/post-a/",
    ...
  ]
}
```

## GitHub Actions 트리거 조건

`.github/workflows/indexnow-ping.yml`:

- **자동**: `Deploy Jekyll to GitHub Pages` workflow가 `main` 브랜치에서 `success`로 완료된 후
- **조건**: `_posts/`, `sitemap.xml`, `_config.yml` 중 하나가 변경된 commit인 경우에만 ping
- **수동**: GitHub Actions UI → "Run workflow" → dry_run 체크박스 선택 가능
- **실패 무시**: `continue-on-error: true` — ping 실패해도 배포 상태에 영향 없음

## 응답 코드 의미

| 코드 | 의미 | 처리 |
|------|------|------|
| 200 | URL 등록 완료 | 정상 |
| 202 | 수신됨, 키 검증 대기 | 정상 (키 파일 배포 직후 첫 실행 시 자주 발생) |
| 400 | 잘못된 형식 | payload 확인 필요 |
| 422 | URL 형식 오류 | urlList 내 URL 확인 |
| 429 | Rate limited | 30초 후 1회 재시도, 실패 시 non-fatal |

## Key Rotation (키 교체)

1. 새 키 생성: `python3 -c "import secrets; print(secrets.token_hex(16))"`
2. 루트에 새 키 파일 생성: `<new_key>.txt` (내용: 키 값)
3. `.well-known/<new_key>.txt` 동일하게 생성
4. `_config.yml`의 `indexnow_key:` 값 업데이트
5. `.github/workflows/indexnow-ping.yml`의 `INDEXNOW_KEY` 값 업데이트
6. 구 키 파일 삭제 (선택 — 남겨둬도 무관)
7. 커밋 & push → 새 키로 자동 적용

## Bing Webmaster Tools에서 효과 확인

배포 후 1주일 후:

1. [Bing Webmaster Tools](https://www.bing.com/webmasters) 접속
2. 좌측 메뉴 → **URL Submission** → **IndexNow**
3. "Submitted URLs" 섹션에서 제출된 URL 수, 성공/실패 수 확인
4. **Crawl** → **Crawl Statistics** 에서 crawl 빈도 증가 여부 확인

### 기대 효과

| 지표 | 변경 전 | 변경 후 (1-2주) |
|------|---------|----------------|
| Bing 색인 지연 | 며칠 ~ 1주 | 수 시간 이내 |
| Yandex 색인 지연 | 며칠 | 수 시간 이내 |
| Crawl 빈도 | 낮음 | 변경 감지 즉시 크롤 |

## 주의사항

- **Google**: IndexNow 미참여. 새 포스트는 GSC → URL 검사 → 색인 요청으로 별도 처리
- **sitemap.xml**: Jekyll이 `jekyll-sitemap` gem으로 자동 생성. 로컬 빌드(`bundle exec jekyll build`) 후 `_site/sitemap.xml` 확인
- **URL 수**: 현재 약 150-200건으로 IndexNow 10,000건 제한에 여유 있음
- **비용**: IndexNow API 사용 무료

## 관련 파일

| 파일 | 역할 |
|------|------|
| `890b921a9bdd4a155d198c6c0487a14f.txt` | 루트 키 파일 |
| `.well-known/890b921a9bdd4a155d198c6c0487a14f.txt` | .well-known 키 파일 |
| `_config.yml` → `indexnow_key` | 키 설정 |
| `scripts/indexnow_ping.py` | ping 스크립트 |
| `scripts/tests/test_indexnow_ping.py` | pytest 테스트 |
| `.github/workflows/indexnow-ping.yml` | 자동화 workflow |
