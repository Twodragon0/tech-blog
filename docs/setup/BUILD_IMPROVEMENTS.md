# 빌드 프로세스 개선 사항

## 개요
GitHub Actions와 Vercel의 빌드 프로세스를 일관되게 만들고, 에러 처리를 개선했습니다.

## 주요 변경 사항

### 1. GitHub Actions 워크플로우 개선 (`.github/workflows/jekyll.yml`)

#### 변경 전
- `bundle exec jekyll build`를 직접 실행
- build.sh를 사용하지 않아 Vercel과 빌드 프로세스가 불일치

#### 변경 후
- **build.sh 사용**: Vercel과 동일한 빌드 스크립트 사용
- **Node.js 설정 추가**: terser를 위한 Node.js 환경 구성
- **Python 설정 추가**: favicon 생성을 위한 Python 환경 구성
- **의존성 설치 개선**: npm ci, pip install 추가
- **환경 변수 일치**: Vercel과 동일한 환경 변수 사용 (LANG=C.UTF-8)

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- name: Build with build.sh (consistent with Vercel)
  run: |
    chmod +x build.sh
    export BASEURL="${{ steps.pages.outputs.base_path }}"
    ./build.sh
```

### 2. build.sh 스크립트 개선

#### 변경 사항
1. **baseurl 지원**: GitHub Pages를 위한 BASEURL 환경 변수 지원
2. **terser 에러 처리 개선**: 
   - 로컬 terser 우선 사용
   - npx fallback
   - 실패 시 경고만 출력하고 계속 진행 (선택적 단계)
3. **의존성 확인 강화**: terser 사용 전 의존성 확인

```bash
# baseurl 지원
BASEURL="${BASEURL:-}"
if [ -n "$BASEURL" ]; then
    BUILD_ARGS="$BUILD_ARGS --baseurl $BASEURL"
fi

# terser 에러 처리 개선
if [ -f "node_modules/.bin/terser" ]; then
    ./node_modules/.bin/terser ...
elif npx --yes terser ...; then
    log "✅ JavaScript minified successfully"
else
    log "WARNING: terser command failed, using unminified JS"
fi
```

### 3. Vercel 설정 개선 (`vercel.json`)

#### 변경 사항
- **Pillow 설치 실패 허용**: `|| true` 추가하여 Pillow 설치 실패 시에도 빌드 계속
- **npm ci 우선 사용**: 더 빠르고 안정적인 의존성 설치

```json
"installCommand": "(python3 -m pip install --quiet --no-cache-dir Pillow || pip3 install --quiet --no-cache-dir Pillow || true) && npm ci || npm install && bundle install --jobs 4 --retry 3"
```

## 빌드 프로세스 일관성

### 공통 빌드 스크립트
- **build.sh**: GitHub Actions와 Vercel 모두에서 사용
- **환경 변수**: LANG=C.UTF-8, LC_ALL=C.UTF-8, LANGUAGE=C.UTF-8
- **의존성 설치 순서**: Python → Node.js → Ruby

### 빌드 단계
1. 환경 설정 (Ruby, Node.js, Python)
2. 의존성 설치 (Pillow, npm packages, Ruby gems)
3. Favicon 생성 (선택적)
4. Jekyll 빌드
5. JavaScript minification (선택적)

## 에러 처리 개선

### 선택적 단계
- **Favicon 생성**: 실패해도 기존 favicon.png 사용
- **JavaScript minification**: 실패해도 unminified JS 사용
- **Pillow 설치**: 실패해도 빌드 계속

### 필수 단계
- **Ruby/Bundle 설치**: 실패 시 빌드 중단
- **Jekyll 빌드**: 실패 시 빌드 중단

## 테스트 방법

### 로컬 테스트
```bash
# 빌드 스크립트 직접 실행
chmod +x build.sh
./build.sh

# baseurl 테스트
BASEURL="/blog" ./build.sh
```

### GitHub Actions 테스트
1. main 브랜치에 push
2. Actions 탭에서 워크플로우 확인
3. 빌드 로그 확인

### Vercel 테스트
1. Vercel 대시보드에서 배포 확인
2. 빌드 로그 확인
3. 배포된 사이트 확인

## 문제 해결

### 빌드 실패 시 확인 사항
1. **Ruby 버전**: `.ruby-version` 확인 (3.3.0)
2. **의존성 설치**: bundle install, npm install 성공 여부
3. **환경 변수**: LANG, LC_ALL 설정 확인
4. **권한**: build.sh 실행 권한 확인 (`chmod +x build.sh`)

### 일반적인 문제
- **terser 실패**: 선택적 단계이므로 경고만 출력되고 빌드 계속
- **Pillow 실패**: 선택적 단계이므로 경고만 출력되고 빌드 계속
- **baseurl 문제**: BASEURL 환경 변수 확인

## 향후 개선 사항
- [ ] 빌드 캐싱 최적화
- [ ] 빌드 시간 단축
- [ ] 에러 메시지 개선
- [ ] 빌드 로그 가독성 향상
