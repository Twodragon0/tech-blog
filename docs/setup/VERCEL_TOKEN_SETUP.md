# VERCEL_TOKEN 발급 + GitHub Secret 등록

`scripts/backup_vercel_firewall.py` (cron 매주 월 09:00 KST)가 작동하기
위해 필요한 single-purpose token. 1분 작업.

## 1. Vercel 토큰 발급

1. https://vercel.com/account/tokens 접속
2. **Create Token** 클릭
3. 입력:
   - **Token Name**: `tech-blog-firewall-backup` (식별용)
   - **Scope**: `twodragon0s-projects` (팀) — Account-wide 보다 좁게
   - **Expiration**: `90 days` (만료 후 재발급 — security best practice)
4. **Create Token** → **즉시 복사** (다시 표시 안 됨)

## 2. GitHub Secret 등록

### 옵션 A: CLI (권장)

```bash
# Twodragon0 계정 활성 상태에서
gh auth switch --user Twodragon0

# 한 번에 등록 (값은 보이지 않음 — 붙여넣기 후 Enter)
gh secret set VERCEL_TOKEN

# (선택) 프로젝트/팀 ID도 명시 — 미등록 시 script default 사용
gh secret set VERCEL_PROJECT_ID --body "prj_AONcZXgpIpZ8YXjupW9547FdTJEr"
gh secret set VERCEL_TEAM_ID --body "team_K7Ut1NIGYRvAfP68LYpOLBcA"

# 검증
gh secret list | grep VERCEL
```

### 옵션 B: Web UI

1. https://github.com/Twodragon0/tech-blog/settings/secrets/actions
2. **New repository secret**
3. **Name**: `VERCEL_TOKEN`, **Value**: (방금 복사한 토큰)
4. **Add secret**

## 3. 동작 검증

```bash
# 즉시 backup 실행 (cron 대기 안 함)
gh workflow run vercel-firewall-backup.yml

# 30초 후 결과 확인
sleep 30 && gh run list --workflow=vercel-firewall-backup.yml --limit 1

# 성공하면 main 브랜치에 새 커밋이 자동 push됨
git fetch && git log origin/main --oneline -3 | grep "vercel firewall snapshot"
```

## 4. 토큰 만료 정책

- 90일 만료 시 cron 실패 → Slack 알림(`googlebot-access-monitor.yml`처럼 추후 통합 가능)
- 갱신 절차: 1번 → 2번 반복 (기존 secret 자동 덮어쓰기)
- 만료 5일 전 알림 원할 시 `.github/workflows/secret-expiry-warn.yml` 추가 가능

## 5. 권한 최소화 체크

발급된 토큰의 노출 시 영향 범위:
- **Read** firewall config (이 cron의 유일한 사용처) ✓
- **Write** project settings (위험) — 토큰 노출 시 firewall rule 수정 가능
- **Deploy** trigger (위험) — 외부 commit 가능

→ Vercel 대시보드의 **Token scope**를 가능한 좁게 설정 (Read access on project 단일).
