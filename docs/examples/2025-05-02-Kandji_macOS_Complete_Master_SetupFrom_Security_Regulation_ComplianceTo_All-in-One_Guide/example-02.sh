#!/bin/bash
# ISMS-P 핵심 통제 항목 자동 점검
echo "=== ISMS-P 컴플라이언스 점검 ==="

# 2.5.1 암호화: FileVault 상태
fv_status=$(fdesetup status)
echo "[2.5.1] FileVault: $fv_status"

# 2.4.1 패스워드 정책 확인
pw_min=$(pwpolicy -getaccountpolicies 2>/dev/null | grep -c "minLength")
echo "[2.4.1] 패스워드 정책 적용: $pw_min 항목"

# 2.6.1 Gatekeeper 상태
gk_status=$(spctl --status)
echo "[2.6.1] Gatekeeper: $gk_status"

# 2.7.1 마지막 업데이트 확인
last_update=$(softwareupdate --history | tail -1)
echo "[2.7.1] 최근 업데이트: $last_update"
