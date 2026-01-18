### 2.1 Dependabot

프로젝트에서 사용하는 라이브러리(의존성)의 취약점을 자동으로 탐지하고, 보안 패치가 적용된 버전으로 업데이트하는 PR을 생성해 줍니다.

#### Dependabot 설정 예시

> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule: { interval: "weekly", day: "monday" }
    open-pull-requests-limit: 10
    labels: ["dependencies", "security"]
  - package-ecosystem: "pip"
    directory: "/scripts"
    schedule: { interval: "weekly" }
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "monthly" }
```

#### Dependabot 알림 설정

> **참고**: Dependabot 알림 설정 관련 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot)를 참조하세요.

```yaml
# .github/dependabot.yml (계속)
updates:
  - package-ecosystem: "npm"
    directory: "/"
    # 보안 업데이트는 즉시 알림
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-patch"]
    # High/Critical 취약점은 즉시 PR 생성
    allow:
      - dependency-type: "direct"
```
