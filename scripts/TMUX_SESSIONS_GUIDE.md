# tmux 세션 사용 가이드

tech.2twodragon.com과 edu.2twodragon.com 블로그 작업을 위한 tmux 세션 관리 가이드입니다.

## 📋 세션 정보

| 세션명 | 블로그 | 디렉토리 |
|--------|--------|----------|
| `blog-tech` | tech.2twodragon.com | `/xx/tech-blog` |
| `blog-edu` | edu.2twodragon.com | `/xx/online-course` |

## 🚀 세션 생성

```bash
# 스크립트 실행
./scripts/setup_tmux_sessions.sh

# 또는 절대 경로로
/xx/tech-blog/scripts/setup_tmux_sessions.sh
```

## 🔌 세션 연결

### 일반 터미널에서

```bash
# tech 블로그 세션 연결
tmux attach -t blog-tech

# edu 블로그 세션 연결 (다른 터미널 창에서)
tmux attach -t blog-edu
```

### Cursor IDE에서 활용하기

#### 방법 1: Cursor 통합 터미널 사용

1. **Cursor에서 터미널 열기**: `Ctrl + \`` (백틱) 또는 `View > Terminal`
2. **세션 연결**:
   ```bash
   # tech 블로그 세션
   tmux attach -t blog-tech
   
   # edu 블로그 세션 (새 터미널 탭에서)
   tmux attach -t blog-edu
   ```

#### 방법 2: Cursor에서 프로젝트 열기

각 블로그 디렉토리를 Cursor에서 별도 창으로 열 수 있습니다:

```bash
# tech 블로그 프로젝트 열기
code "/xx/tech-blog"

# edu 블로그 프로젝트 열기
code "/xx/online-course"
```

또는 Cursor에서:
- `File > Open Folder...` → 해당 디렉토리 선택

#### 방법 3: Cursor 터미널 분할 활용

1. **첫 번째 터미널**: `tmux attach -t blog-tech`
2. **터미널 분할**: `Ctrl + Shift + 5` (또는 터미널 메뉴에서 Split Terminal)
3. **두 번째 터미널**: `tmux attach -t blog-edu`

이렇게 하면 Cursor에서 두 세션을 동시에 모니터링할 수 있습니다.

## 🛠️ 유용한 명령어

### 세션 관리

```bash
# 모든 세션 목록 보기
tmux list-sessions

# 세션 상태 확인 (경로 포함)
tmux list-sessions -F "#{session_name}: #{session_path}"

# 세션 종료
tmux kill-session -t blog-tech
tmux kill-session -t blog-edu

# 모든 세션 종료
tmux kill-session -t blog-tech && tmux kill-session -t blog-edu
```

### tmux 기본 명령어

세션 내에서 사용하는 단축키 (기본 prefix: `Ctrl + b`):

```bash
# 세션에서 나가기 (세션은 유지)
Ctrl + b, d

# 새 윈도우 생성
Ctrl + b, c

# 윈도우 전환
Ctrl + b, n  # 다음 윈도우
Ctrl + b, p  # 이전 윈도우

# 패널 분할
Ctrl + b, %  # 세로 분할
Ctrl + b, "  # 가로 분할

# 패널 이동
Ctrl + b, 화살표 키

# 스크롤 모드
Ctrl + b, [
```

## 💡 Cursor IDE 워크플로우 예시

### 시나리오 1: tech 블로그 작업

```bash
# 1. Cursor에서 tech-blog 디렉토리 열기
# 2. Cursor 터미널에서 세션 연결
tmux attach -t blog-tech

# 3. Jekyll 서버 실행 (세션 내에서)
bundle exec jekyll serve

# 4. 세션에서 나가기 (서버는 계속 실행)
Ctrl + b, d

# 5. 나중에 다시 연결
tmux attach -t blog-tech
```

### 시나리오 2: 두 블로그 동시 작업

```bash
# Cursor 터미널 1
tmux attach -t blog-tech

# Cursor 터미널 2 (분할 또는 새 탭)
tmux attach -t blog-edu
```

### 시나리오 3: Cursor에서 프로젝트별로 창 분리

1. **tech 블로그**: Cursor 창 1에서 열기
2. **edu 블로그**: Cursor 창 2에서 열기 (`File > New Window`)
3. 각 창의 터미널에서 해당 세션 연결

## 🔄 세션 재생성

기존 세션이 문제가 있거나 재시작이 필요한 경우:

```bash
# 기존 세션 종료
tmux kill-session -t blog-tech
tmux kill-session -t blog-edu

# 스크립트로 재생성
./scripts/setup_tmux_sessions.sh
```

## 📝 주의사항

1. **세션은 백그라운드에서 계속 실행됩니다**
   - 터미널을 닫아도 세션은 유지됩니다
   - 서버나 프로세스가 실행 중이면 계속 실행됩니다

2. **디렉토리 확인**
   - 각 세션은 해당 디렉토리에서 시작됩니다
   - `pwd` 명령어로 확인 가능합니다

3. **Cursor 통합 터미널**
   - Cursor의 통합 터미널에서도 tmux를 완전히 사용할 수 있습니다
   - 터미널 분할 기능과 함께 사용하면 더욱 편리합니다

## 🆘 문제 해결

### 세션이 보이지 않는 경우

```bash
# 세션 목록 확인
tmux list-sessions

# 세션이 없다면 재생성
./scripts/setup_tmux_sessions.sh
```

### tmux가 설치되지 않은 경우

```bash
# Homebrew로 설치
brew install tmux

# 설치 확인
tmux -V
```

### 경로 문제

스크립트의 경로가 올바른지 확인:

```bash
# tech-blog 경로 확인
ls "/Users/twodragon/twodragon114@gmail.com - Google Drive/내 드라이브/tech-blog"

# online-course 경로 확인
ls "/Users/twodragon/twodragon114@gmail.com - Google Drive/내 드라이브/online-course"
```

## 📚 참고 자료

- [tmux 공식 문서](https://github.com/tmux/tmux/wiki)
- [Cursor 터미널 가이드](https://cursor.sh/docs)

---

<section class="related-posts">
  <div class="related-header">
    <h3>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
      </svg>
      Related Posts
    </h3>
  </div>
  <div class="related-grid">
    <a href="/2026/01/08/Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_Security_Architecture_And_GitHub_DevSecOps_Practical.html" class="related-item">
      <div class="related-content">
        <span class="related-category">Security</span>
        <h4>클라우드 보안 과정 8기 6주차: AWS WAF/CloudFront 보안 아키텍처 및 GitHub DevSecOps 실전</h4>
        <p class="related-excerpt">AWS WAF/CloudFront 보안 아키텍처(OAI/OAC, WAF 규칙, Geo-blocking), GitHub DevSecOps 실전(CodeQL, Dependabot, Secret Scanning), 실전 보안 패치 사례(SSRF 수정, Data Masking), 테크 블로그 보안 개선(Jekyll, CodeQL 기반 취약점 진단), Amazon Q Developer 활용까지 실무 중심 정리.</p>
      </div>
      <div class="related-meta">
        <span class="related-date">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          2026. 01. 08
        </span>
        <span class="related-arrow">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </span>
      </div>
    </a>
    <a href="/2025/06/06/Cloud_Security_Course_7Batch_-_8Week_CI_CDAnd_Kubernetes_Security_Practical_Guide.html" class="related-item">
      <div class="related-content">
        <span class="related-category">Kubernetes</span>
        <h4>클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드</h4>
        <p class="related-excerpt">CI/CD 파이프라인 보안: GitHub Actions 보안 설정(permissions 최소화, Secret 관리), SAST/DAST 통합(Semgrep, SonarQube, Gitleaks, Trivy, OWASP ZAP), Secret 스캐닝, 의존성 취약점 스캔</p>
      </div>
      <div class="related-meta">
        <span class="related-date">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          2025. 06. 06
        </span>
        <span class="related-arrow">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </span>
      </div>
    </a>
    <a href="/2026/01/16/Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.html" class="related-item">
      <div class="related-content">
        <span class="related-category">Incident</span>
        <h4>[Post-Mortem] Next.js SSR 에러 및 Cloudflare 차단으로 인한 ALB 5XX 에러 인시던트 분석</h4>
        <p class="related-excerpt">Post-Mortem: Next.js SSR 환경에서 location 객체 접근으로 인한 5XX 에러 및 Cloudflare IP 차단 인시던트 분석. 배포 후 발생한 ReferenceError: location is not defined 에러, ALB Target Group Health Check 실패, Cloudflare WAF 차단 패턴 분석, 근본 원인 분석 및 재발 방지 대책까지 실무 중심 정리.</p>
      </div>
      <div class="related-meta">
        <span class="related-date">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="16" y1="2" x2="16" y2="6"></line>
            <line x1="8" y1="2" x2="8" y2="6"></line>
            <line x1="3" y1="10" x2="21" y2="10"></line>
          </svg>
          2026. 01. 16
        </span>
        <span class="related-arrow">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </span>
      </div>
    </a>
  </div>
</section>
