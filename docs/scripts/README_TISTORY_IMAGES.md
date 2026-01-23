# Tistory 이미지 가져오기 스크립트

이 스크립트는 모든 포스트의 `original_url`에서 tistory 블로그 이미지를 자동으로 가져와서 로컬에 저장하고 포스트에 추가합니다.

## 설치 방법

### 1. 필요한 패키지 설치

```bash
# macOS에서 시스템 패키지 관리자 사용 시
pip3 install --break-system-packages beautifulsoup4 lxml

# 또는 가상 환경 사용 (권장)
python3 -m venv venv
source venv/bin/activate
pip install beautifulsoup4 lxml
```

### 2. 스크립트 실행 권한 확인

```bash
chmod +x scripts/fetch_tistory_images.py
```

## 사용 방법

### 테스트 모드 (첫 번째 포스트만)

```bash
cd /Users/yong/Desktop/tech-blog
python3 scripts/fetch_tistory_images.py --test
```

### 전체 포스트 처리

```bash
cd /Users/yong/Desktop/tech-blog
python3 scripts/fetch_tistory_images.py
```

### 기존 이미지 강제 재다운로드

```bash
cd /Users/yong/Desktop/tech-blog
python3 scripts/fetch_tistory_images.py --force
```

### 가상 환경 사용 시

```bash
cd /Users/yong/Desktop/tech-blog
source venv/bin/activate
python3 scripts/fetch_tistory_images.py
```

## 동작 방식

1. **포스트 스캔**: `_posts/` 디렉토리의 모든 마크다운 파일을 스캔합니다.
2. **URL 확인**: 각 포스트의 `original_url` 필드에서 tistory 블로그 URL을 확인합니다.
3. **이미지 추출**: tistory 블로그 페이지에서 이미지 URL을 추출합니다.
4. **이미지 다운로드**: 추출한 이미지를 `assets/images/` 디렉토리에 저장합니다.
5. **포스트 업데이트**: 포스트 파일에 이미지 참조를 추가합니다.

## 이미지 저장 위치

- 저장 경로: `assets/images/[포스트파일명]_image.[확장자]`
- 예시: `assets/images/2025-11-04-Zscaler_완벽_가이드_SSL_검사_샌드박스_AI_광고_유해_사이트_완벽_차단_image.png`

## 이미지 삽입 위치

이미지는 다음 우선순위로 삽입됩니다:

1. **서론 섹션 끝**: `## 서론` 섹션이 있으면 그 끝 부분에 삽입
2. **첫 번째 섹션 앞**: 서론이 없으면 첫 번째 `##` 섹션 앞에 삽입
3. **본문 시작**: 섹션이 없으면 본문 시작 부분에 삽입

## 주의사항

- 이미 존재하는 이미지는 다시 다운로드하지 않습니다.
- 이미 포스트에 이미지가 있으면 추가하지 않습니다.
- Rate limiting을 위해 각 포스트 처리 사이에 2초 대기합니다.
- 네트워크 오류 시 해당 포스트는 건너뜁니다.

## 문제 해결

### 패키지 설치 오류

```bash
# macOS에서 externally-managed-environment 오류 시
pip3 install --break-system-packages beautifulsoup4 lxml
```

### 이미지가 다운로드되지 않는 경우

1. tistory 블로그 URL이 올바른지 확인
2. 네트워크 연결 확인
3. tistory 블로그가 공개되어 있는지 확인

### 이미지가 포스트에 추가되지 않는 경우

1. 포스트 파일의 front matter 형식 확인
2. 이미지가 이미 포스트에 있는지 확인
3. 포스트 파일의 인코딩이 UTF-8인지 확인

## 예제 출력

```
🚀 Starting Tistory image fetch process...

📚 Found 29 post file(s)

📄 Processing: 2025-11-04-Zscaler_완벽_가이드_SSL_검사_샌드박스_AI_광고_유해_사이트_완벽_차단.md
  📥 Fetching: https://twodragon.tistory.com/698
  ✅ Found 1 image(s)
    📥 Downloading: https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=...
    ✅ Saved: 2025-11-04-Zscaler_완벽_가이드_SSL_검사_샌드박스_AI_광고_유해_사이트_완벽_차단_image.png
    ✅ Added image reference to post

============================================================
✅ Processed: 29 post(s)
✅ Success: 29 image(s)
❌ Failed: 0 image(s)
============================================================
```
